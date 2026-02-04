"""
Pydantic schemas for Student model.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class StudentBase(BaseModel):
    """Base student schema with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)
    monthly_budget: Decimal = Field(..., ge=0, decimal_places=2)
    budget_start_date: date


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    supabase_user_id: str = Field(..., min_length=1)


class StudentUpdate(BaseModel):
    """Schema for updating student information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    monthly_budget: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    budget_start_date: Optional[date] = None


class StudentResponse(StudentBase):
    """Schema for student response."""
    id: int
    supabase_user_id: str
    remaining_budget: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BudgetStatusResponse(BaseModel):
    """Schema for budget status response."""
    student_id: int
    monthly_budget: Decimal
    remaining_budget: Decimal
    total_spent: Decimal
    budget_start_date: date
    days_elapsed: int
    days_remaining: int
    daily_budget_allowance: Decimal  # Remaining budget / remaining days
    budget_health: str  # "Healthy", "Caution", "Critical"
    
    class Config:
        from_attributes = True
