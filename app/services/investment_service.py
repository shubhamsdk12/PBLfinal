"""
Investment service for managing student investments and transactions.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from app.models.investment import Investment, InvestmentTransaction, InvestmentTransactionType
from app.schemas.investment import InvestmentSummaryResponse


class InvestmentService:
    """Service for investment-related operations."""
    
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
            raise ValueError(f"Insufficient balance. Available: ${investment.balance:.2f}, Requested: ${amount:.2f}")
        
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
