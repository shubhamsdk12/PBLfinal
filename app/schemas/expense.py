"""
Pydantic schemas for Expense models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List


class ExpenseCategoryResponse(BaseModel):
    """Schema for expense category response."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DailyExpenseTemplateResponse(BaseModel):
    """Schema for daily expense template response."""
    id: int
    category_id: int
    category_name: str
    display_order: int
    is_active: bool
    
    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    """Base expense schema."""
    category_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    expense_date: date
    is_additional: bool = False
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""
    pass


class ExpenseResponse(ExpenseBase):
    """Schema for expense response."""
    id: int
    student_id: int
    category_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DailyChecklistItem(BaseModel):
    """Schema for a single item in the daily expense checklist."""
    category_id: int
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    is_checked: bool = False  # Only checked items are saved


class DailyChecklistSubmit(BaseModel):
    """Schema for submitting daily expense checklist."""
    expense_date: date
    items: List[DailyChecklistItem] = Field(..., min_items=0)
    additional_expenses: Optional[List[ExpenseCreate]] = Field(
        default=None,
        description="Additional unplanned expenses"
    )


class DailyChecklistResponse(BaseModel):
    """Schema for daily checklist response (what to show on frontend)."""
    expense_date: date
    templates: List[DailyExpenseTemplateResponse]
    today_expenses: List[ExpenseResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
