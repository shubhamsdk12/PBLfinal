"""
Pydantic schemas for Investment models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from app.models.investment import InvestmentTransactionType


class InvestmentBase(BaseModel):
    """Base investment schema."""
    monthly_interest_rate: Decimal = Field(..., ge=0, le=100, decimal_places=2)


class InvestmentCreate(InvestmentBase):
    """Schema for creating a new investment."""
    initial_balance: Decimal = Field(..., ge=0, decimal_places=2)


class InvestmentUpdate(BaseModel):
    """Schema for updating investment."""
    monthly_interest_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)


class InvestmentResponse(InvestmentBase):
    """Schema for investment response."""
    id: int
    student_id: int
    balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InvestmentTransactionResponse(BaseModel):
    """Schema for investment transaction response."""
    id: int
    investment_id: int
    transaction_type: InvestmentTransactionType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvestmentWithdrawRequest(BaseModel):
    """Schema for investment withdrawal request."""
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    notes: Optional[str] = None


class InvestmentDepositRequest(BaseModel):
    """Schema for investment deposit request."""
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    notes: Optional[str] = None


class InvestmentSummaryResponse(BaseModel):
    """Schema for investment summary response."""
    investment: InvestmentResponse
    transactions: List[InvestmentTransactionResponse]
    total_invested: Decimal
    total_interest_earned: Decimal
    total_withdrawn: Decimal
    
    class Config:
        from_attributes = True
