"""
Pydantic schemas for Student model.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Annotated
from pydantic import PlainSerializer

# Serialize Decimal as float for JSON
DecimalFloat = Annotated[Decimal, PlainSerializer(lambda x: float(x), return_type=float)]


class StudentBase(BaseModel):
    """Base student schema with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)
    monthly_budget: DecimalFloat = Field(..., ge=0)
    budget_start_date: date


class StudentCreate(StudentBase):
    """Schema for creating a new student (internal use)."""
    password_hash: str


class StudentUpdate(BaseModel):
    """Schema for updating student information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    monthly_budget: Optional[DecimalFloat] = Field(None, ge=0)
    budget_start_date: Optional[date] = None
    budget_setup_complete: Optional[bool] = None


class StudentResponse(BaseModel):
    """Schema for student response."""
    id: int
    email: str
    name: str
    monthly_budget: DecimalFloat
    budget_start_date: date
    remaining_budget: DecimalFloat
    budget_setup_complete: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetStatusResponse(BaseModel):
    """Schema for budget status response."""
    student_id: int
    monthly_budget: DecimalFloat
    remaining_budget: DecimalFloat
    total_spent: DecimalFloat
    budget_start_date: date
    days_elapsed: int
    days_remaining: int
    daily_budget_allowance: DecimalFloat  # Remaining budget / remaining days
    budget_health: str  # "Healthy", "Caution", "Critical"

    model_config = ConfigDict(from_attributes=True)


# --- Category Budget Schemas ---

class CategoryBudgetBase(BaseModel):
    """Base schema for category budget."""
    category_id: int
    daily_budget: DecimalFloat = Field(..., ge=0)
    is_active: bool = True


class CategoryBudgetCreate(CategoryBudgetBase):
    """Schema for creating category budget."""
    pass


class CategoryBudgetUpdate(BaseModel):
    """Schema for updating category budget."""
    daily_budget: Optional[DecimalFloat] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryBudgetResponse(CategoryBudgetBase):
    """Schema for category budget response."""
    id: int
    student_id: int
    category_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetSetupItem(BaseModel):
    """Single item in budget setup - category with daily budget."""
    category_id: int
    category_name: str
    daily_budget: DecimalFloat = Field(..., ge=0)
    is_active: bool = True


class BudgetSetupRequest(BaseModel):
    """Request to set up category budgets."""
    monthly_budget: DecimalFloat = Field(..., ge=0)
    budget_start_date: date
    category_budgets: List[BudgetSetupItem]


class BudgetSetupResponse(BaseModel):
    """Response after budget setup."""
    student: StudentResponse
    category_budgets: List[CategoryBudgetResponse]
