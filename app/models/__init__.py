"""
SQLAlchemy database models.
All models are imported here for Alembic migrations.
"""
from app.models.student import Student
from app.models.expense import ExpenseCategory, DailyExpenseTemplate, Expense, MonthlyBudgetSnapshot
from app.models.investment import Investment, InvestmentTransaction
from app.models.ai_alert import AIAlert

__all__ = [
    "Student",
    "ExpenseCategory",
    "DailyExpenseTemplate",
    "Expense",
    "MonthlyBudgetSnapshot",
    "Investment",
    "InvestmentTransaction",
    "AIAlert",
]
