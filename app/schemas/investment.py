"""
Pydantic schemas for Investment models.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Annotated
from pydantic import PlainSerializer
from app.models.investment import InvestmentTransactionType

# Serialize Decimal as float for JSON
DecimalFloat = Annotated[Decimal, PlainSerializer(lambda x: float(x), return_type=float)]


class InvestmentBase(BaseModel):
    """Base investment schema."""
    monthly_interest_rate: DecimalFloat = Field(..., ge=0, le=100)


class InvestmentCreate(InvestmentBase):
    """Schema for creating a new investment."""
    initial_balance: DecimalFloat = Field(..., ge=0)


class InvestmentUpdate(BaseModel):
    """Schema for updating investment."""
    monthly_interest_rate: Optional[DecimalFloat] = Field(None, ge=0, le=100)


class InvestmentResponse(InvestmentBase):
    """Schema for investment response."""
    id: int
    student_id: int
    balance: DecimalFloat
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InvestmentTransactionResponse(BaseModel):
    """Schema for investment transaction response."""
    id: int
    investment_id: int
    transaction_type: InvestmentTransactionType
    amount: DecimalFloat
    balance_before: DecimalFloat
    balance_after: DecimalFloat
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestmentWithdrawRequest(BaseModel):
    """Schema for investment withdrawal request."""
    amount: DecimalFloat = Field(..., gt=0)
    notes: Optional[str] = None


class InvestmentDepositRequest(BaseModel):
    """Schema for investment deposit request."""
    amount: DecimalFloat = Field(..., gt=0)
    notes: Optional[str] = None


class InvestmentSummaryResponse(BaseModel):
    """Schema for investment summary response."""
    investment: InvestmentResponse
    transactions: List[InvestmentTransactionResponse]
    total_invested: DecimalFloat
    total_interest_earned: DecimalFloat
    total_withdrawn: DecimalFloat

    model_config = ConfigDict(from_attributes=True)


class MarketNewsItemResponse(BaseModel):
    """Schema for a curated market news item."""
    headline: str
    summary: Optional[str] = None
    url: str
    source: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)


class MarketNewsResponse(BaseModel):
    """Schema for market news feed."""
    items: List[MarketNewsItemResponse] = Field(default_factory=list)
    fetched_at: datetime
    note: Optional[str] = None
