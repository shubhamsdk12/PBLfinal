"""
Investment service for managing student investments and transactions.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from decimal import Decimal
import httpx
from app.config import settings
from app.models.investment import Investment, InvestmentTransaction, InvestmentTransactionType
from app.schemas.investment import InvestmentSummaryResponse, MarketNewsResponse, MarketNewsItemResponse


logger = logging.getLogger(__name__)


class InvestmentService:
    """Service for investment-related operations."""

    MARKETAUX_NEWS_URL = "https://api.marketaux.com/v1/news/all"

    MUTUAL_FUND_KEYWORDS = {
        "mutual fund", "mutual funds", "fund inflow", "sip", "systematic investment plan",
        "asset management", "amc", "index fund", "etf", "equity fund", "debt fund"
    }
    FD_KEYWORDS = {
        "fixed deposit", "fd rates", "deposit rates", "interest rates", "rate cut", "rate hike",
        "bond yields", "treasury yield", "fixed income", "safe return", "capital protection"
    }
    FINANCE_KEYWORDS = {
        "finance", "financial", "market", "markets", "investment", "investing", "bank", "banking",
        "stock", "stocks", "equity", "mutual fund", "fund", "funds", "fixed deposit", "fd",
        "economy", "economic", "inflation", "interest rate", "rates", "bond", "yield", "nifty", "sensex",
        "trade", "trading", "tariff", "tariffs", "gdp", "revenue", "profit", "earnings",
        "shares", "commodity", "commodities", "oil", "gold", "crypto", "bitcoin", "dollar",
        "wall street", "dow", "nasdaq", "s&p", "federal reserve", "fed", "treasury",
        "budget", "tax", "taxes", "capital", "asset", "assets", "portfolio", "hedge",
        "recession", "rally", "bull", "bear", "ipo", "merger", "acquisition",
        "retail", "consumer", "spending", "price", "prices", "cost", "growth",
        "debt", "credit", "loan", "mortgage", "insurance", "wealth", "savings",
        "business", "company", "corporate", "industry", "sector",
    }

    @staticmethod
    def _build_suggestions(text: str) -> list[str]:
        """Build conservative investment suggestions from article text."""
        lower_text = text.lower()
        suggestions = []

        if any(keyword in lower_text for keyword in InvestmentService.MUTUAL_FUND_KEYWORDS):
            suggestions.append("Review mutual fund SIP opportunities")

        if any(keyword in lower_text for keyword in InvestmentService.FD_KEYWORDS):
            suggestions.append("Check fixed deposit options for stable returns")

        if "inflation" in lower_text or "volatility" in lower_text or "risk" in lower_text:
            suggestions.append("Prefer diversified low-risk allocation")

        if not suggestions:
            suggestions.append("Track market trend before choosing investment products")

        return suggestions

    @staticmethod
    def _is_finance_related(text: str) -> bool:
        """Return True when article text is finance-related."""
        lower_text = text.lower()
        return any(keyword in lower_text for keyword in InvestmentService.FINANCE_KEYWORDS)
    
    @staticmethod
    def create_investment(
        db: Session,
        student_id: int,
        initial_balance: Decimal,
        monthly_interest_rate: Decimal
    ) -> Investment:
        """
        Create a new investment account for a student.
        """
        investment = Investment(
            student_id=student_id,
            balance=initial_balance,
            monthly_interest_rate=monthly_interest_rate
        )
        db.add(investment)
        db.commit()
        db.refresh(investment)
        
        # Create initial INVEST transaction
        InvestmentService.add_transaction(
            db,
            investment.id,
            InvestmentTransactionType.INVEST,
            initial_balance,
            Decimal("0.00"),
            initial_balance,
            "Initial investment"
        )
        
        return investment
    
    @staticmethod
    def add_transaction(
        db: Session,
        investment_id: int,
        transaction_type: InvestmentTransactionType,
        amount: Decimal,
        balance_before: Decimal,
        balance_after: Decimal,
        notes: str = None
    ) -> InvestmentTransaction:
        """
        Add an investment transaction (append-only log).
        """
        transaction = InvestmentTransaction(
            investment_id=investment_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            notes=notes
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def deposit(
        db: Session,
        investment: Investment,
        amount: Decimal,
        notes: str = None
    ) -> Investment:
        """
        Deposit money into investment.
        """
        balance_before = investment.balance
        investment.balance += amount
        balance_after = investment.balance
        
        db.commit()
        db.refresh(investment)
        
        # Log transaction
        InvestmentService.add_transaction(
            db,
            investment.id,
            InvestmentTransactionType.INVEST,
            amount,
            balance_before,
            balance_after,
            notes or "Additional deposit"
        )
        
        return investment
    
    @staticmethod
    def withdraw(
        db: Session,
        investment: Investment,
        amount: Decimal,
        notes: str = None
    ) -> Investment:
        """
        Withdraw money from investment.
        """
        if investment.balance < amount:
            raise ValueError(f"Insufficient balance. Available: ₹{investment.balance:.2f}, Requested: ₹{amount:.2f}")
        
        balance_before = investment.balance
        investment.balance -= amount
        balance_after = investment.balance
        
        db.commit()
        db.refresh(investment)
        
        # Log transaction
        InvestmentService.add_transaction(
            db,
            investment.id,
            InvestmentTransactionType.WITHDRAW,
            amount,
            balance_before,
            balance_after,
            notes or "Withdrawal"
        )
        
        return investment
    
    @staticmethod
    def credit_interest(
        db: Session,
        investment: Investment
    ) -> Investment:
        """
        Credit monthly interest to investment.
        This is called by a scheduled task once per month.
        """
        if investment.balance <= 0:
            return investment  # No interest on zero balance
        
        interest_amount = (investment.balance * investment.monthly_interest_rate) / 100
        balance_before = investment.balance
        investment.balance += interest_amount
        balance_after = investment.balance
        
        db.commit()
        db.refresh(investment)
        
        # Log transaction
        InvestmentService.add_transaction(
            db,
            investment.id,
            InvestmentTransactionType.INTEREST,
            interest_amount,
            balance_before,
            balance_after,
            f"Monthly interest at {investment.monthly_interest_rate}%"
        )
        
        return investment
    
    @staticmethod
    def get_investment_summary(
        db: Session,
        investment: Investment
    ) -> InvestmentSummaryResponse:
        """
        Get comprehensive investment summary with transaction history.
        """
        transactions = db.query(InvestmentTransaction).filter(
            InvestmentTransaction.investment_id == investment.id
        ).order_by(InvestmentTransaction.created_at.desc()).all()
        
        # Calculate totals
        total_invested = db.query(func.sum(InvestmentTransaction.amount)).filter(
            and_(
                InvestmentTransaction.investment_id == investment.id,
                InvestmentTransaction.transaction_type == InvestmentTransactionType.INVEST
            )
        ).scalar() or Decimal("0.00")
        
        total_interest = db.query(func.sum(InvestmentTransaction.amount)).filter(
            and_(
                InvestmentTransaction.investment_id == investment.id,
                InvestmentTransaction.transaction_type == InvestmentTransactionType.INTEREST
            )
        ).scalar() or Decimal("0.00")
        
        total_withdrawn = db.query(func.sum(InvestmentTransaction.amount)).filter(
            and_(
                InvestmentTransaction.investment_id == investment.id,
                InvestmentTransaction.transaction_type == InvestmentTransactionType.WITHDRAW
            )
        ).scalar() or Decimal("0.00")
        
        return InvestmentSummaryResponse(
            investment=investment,
            transactions=transactions,
            total_invested=total_invested,
            total_interest_earned=total_interest,
            total_withdrawn=total_withdrawn
        )

    # Simple in-memory cache for news: {cache_key: (timestamp, MarketNewsResponse)}
    _news_cache: dict = {}
    _CACHE_TTL_SECONDS = 300  # 5 minutes

    @staticmethod
    def get_market_news(limit: int = 10) -> MarketNewsResponse:
        """
        Fetch live finance news from MarketAux API and curate investment-focused suggestions.

        - Fetches financial news for popular symbols (TSLA, AMZN, MSFT, AAPL, GOOGL)
        - Caches results for 5 minutes to avoid rate-limit issues
        - Enriches articles with investment suggestions based on content
        """
        if not settings.MARKETAUX_API_TOKEN:
            logger.warning("MARKETAUX_API_TOKEN is empty – cannot fetch market news")
            return MarketNewsResponse(
                items=[],
                fetched_at=datetime.now(timezone.utc),
                note="MARKETAUX_API_TOKEN is not configured. Add it to .env to fetch live market news."
            )

        # Check cache first
        cache_key = f"news_{limit}"
        cached = InvestmentService._news_cache.get(cache_key)
        if cached:
            cached_time, cached_response = cached
            age = (datetime.now(timezone.utc) - cached_time).total_seconds()
            if age < InvestmentService._CACHE_TTL_SECONDS:
                logger.info(f"Returning cached market news ({age:.0f}s old)")
                return cached_response

        try:
            logger.info("Fetching MarketAux news…")
            response = httpx.get(
                InvestmentService.MARKETAUX_NEWS_URL,
                params={
                    "symbols": "TSLA,AMZN,MSFT,AAPL,GOOGL",
                    "filter_entities": "true",
                    "language": "en",
                    "api_token": settings.MARKETAUX_API_TOKEN,
                    "limit": min(limit, 50),
                },
                timeout=15.0,
            )
            response.raise_for_status()
            payload = response.json()
            raw_items = payload.get("data", [])
            logger.info(f"MarketAux returned {len(raw_items)} articles")
        except Exception as exc:
            logger.warning(f"MarketAux request failed: {exc}")
            result = MarketNewsResponse(
                items=[],
                fetched_at=datetime.now(timezone.utc),
                note="Failed to fetch market news. Please try again shortly."
            )
            # Cache failure for 60 seconds to avoid hammering the API
            InvestmentService._news_cache[cache_key] = (datetime.now(timezone.utc), result)
            return result

        if not raw_items:
            logger.warning("MarketAux returned empty results")
            result = MarketNewsResponse(
                items=[],
                fetched_at=datetime.now(timezone.utc),
                note="No market news available right now. Try again shortly."
            )
            InvestmentService._news_cache[cache_key] = (datetime.now(timezone.utc), result)
            return result

        # De-duplicate by URL
        seen_urls: set[str] = set()
        unique_items = []
        for item in raw_items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)

        # Build curated response — MarketAux returns finance news,
        # so we accept all articles and enrich with investment suggestions.
        curated_items: list[MarketNewsItemResponse] = []
        for item in unique_items:
            title = item.get("title") or ""
            description = item.get("description") or ""
            url = item.get("url")
            if not title or not url:
                continue

            full_text = f"{title} {description}"
            suggestions = InvestmentService._build_suggestions(full_text)

            # MarketAux published_at is ISO format string
            published_at_str = item.get("published_at", "")
            try:
                published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                published_at = datetime.now(timezone.utc)

            curated_items.append(
                MarketNewsItemResponse(
                    headline=title,
                    summary=description,
                    url=url,
                    source=item.get("source"),
                    published_at=published_at,
                    image_url=item.get("image_url"),
                    suggestions=suggestions,
                )
            )

            if len(curated_items) >= limit:
                break

        logger.info(f"Curated {len(curated_items)} articles from {len(raw_items)} total")

        note = None
        if not curated_items:
            note = "No market news available right now. Try again shortly."

        result = MarketNewsResponse(
            items=curated_items,
            fetched_at=datetime.now(timezone.utc),
            note=note,
        )

        # Cache successful results
        InvestmentService._news_cache[cache_key] = (datetime.now(timezone.utc), result)

        return result

