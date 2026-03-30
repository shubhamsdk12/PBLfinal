"""
Pydantic schemas for Expense models.
"""
from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Annotated
from pydantic import PlainSerializer

# Serialize Decimal as float for JSON
DecimalFloat = Annotated[Decimal, PlainSerializer(lambda x: float(x), return_type=float)]


class ExpenseCategoryResponse(BaseModel):
    """Schema for expense category response."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyExpenseTemplateResponse(BaseModel):
    """Schema for daily expense template response."""
    id: int
    category_id: int
    category_name: str
    daily_budget: DecimalFloat = 0.0  # Student's daily budget for this category
    display_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    """Base expense schema."""
    category_id: Optional[int] = None
    amount: DecimalFloat = Field(..., gt=0)
    expense_date: date
    is_additional: bool = False
    custom_category: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_category(self):
        """Ensure either category_id or custom_category is provided for additional expenses."""
        if self.is_additional and not self.category_id and not self.custom_category:
            raise ValueError("Additional expenses must have either category_id or custom_category")
        if not self.is_additional and not self.category_id:
            raise ValueError("Regular expenses must have a category_id")
        return self


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""
    pass


class ExpenseResponse(BaseModel):
    """Schema for expense response."""
    id: int
    student_id: int
    category_id: Optional[int] = None
    amount: DecimalFloat
    expense_date: date
    is_additional: bool
    custom_category: Optional[str] = None
    category_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='wrap')
    @classmethod
    def populate_category_name(cls, values, handler):
        """Populate category_name from ORM relationship or custom_category."""
        model = handler(values)
        if model.category_name is None:
            # Try to get from ORM object's relationship
            if hasattr(values, 'category') and values.category is not None:
                model.category_name = values.category.name
            elif hasattr(values, 'custom_category') and values.custom_category:
                model.category_name = values.custom_category
        return model


class DailyChecklistItem(BaseModel):
    """Schema for a single item in the daily expense checklist."""
    category_id: int
    amount: DecimalFloat = Field(..., ge=0)
    is_checked: bool = False  # Only checked items are saved


class AdditionalExpenseCreate(BaseModel):
    """Schema for creating an additional expense with custom category."""
    amount: DecimalFloat = Field(..., gt=0)
    expense_date: date
    custom_category: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class DailyChecklistSubmit(BaseModel):
    """Schema for submitting daily expense checklist."""
    expense_date: date
    items: List[DailyChecklistItem] = Field(default_factory=list)
    additional_expenses: Optional[List[AdditionalExpenseCreate]] = Field(
        default=None,
        description="Additional unplanned expenses with custom categories"
    )


class DailyChecklistResponse(BaseModel):
    """Schema for daily checklist response (what to show on frontend)."""
    expense_date: date
    templates: List[DailyExpenseTemplateResponse]
    today_expenses: List[ExpenseResponse] = Field(default_factory=list)
    total_daily_budget: DecimalFloat = 0.0  # Sum of all category daily budgets

    model_config = ConfigDict(from_attributes=True)
