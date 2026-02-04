"""
Expense-related models for tracking daily expenses and categories.
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ExpenseCategory(Base):
    """
    Master list of expense categories (e.g., Food, Transport, Entertainment).
    Used to define available categories for daily expense templates.
    """
    __tablename__ = "expense_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    daily_templates = relationship("DailyExpenseTemplate", back_populates="category")
    expenses = relationship("Expense", back_populates="category")
    
    def __repr__(self):
        return f"<ExpenseCategory(id={self.id}, name={self.name})>"


class DailyExpenseTemplate(Base):
    """
    Fixed daily expense checklist template.
    Frontend shows this list every day with checkboxes.
    Only checked items are saved as Expense records.
    """
    __tablename__ = "daily_expense_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)  # Order in checklist
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    category = relationship("ExpenseCategory", back_populates="daily_templates")
    
    def __repr__(self):
        return f"<DailyExpenseTemplate(id={self.id}, category_id={self.category_id})>"


class Expense(Base):
    """
    Individual expense transaction record.
    
    This is append-only - expenses are never modified or deleted.
    Each expense represents a checked item from the daily checklist.
    """
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False, index=True)
    
    # Expense Details
    amount = Column(Numeric(10, 2), nullable=False)
    expense_date = Column(Date, nullable=False, index=True)  # Date of expense
    is_additional = Column(Boolean, default=False, nullable=False)  # True if unplanned/additional expense
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    student = relationship("Student", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense(id={self.id}, student_id={self.student_id}, amount={self.amount}, date={self.expense_date})>"


class MonthlyBudgetSnapshot(Base):
    """
    Monthly budget snapshots for historical tracking.
    Created at the start of each month to track budget vs actual spending.
    """
    __tablename__ = "monthly_budget_snapshot"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    
    # Snapshot Data
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    budgeted_amount = Column(Numeric(10, 2), nullable=False)
    total_spent = Column(Numeric(10, 2), nullable=False, default=0.00)
    remaining_budget = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="budget_snapshots")
    
    def __repr__(self):
        return f"<MonthlyBudgetSnapshot(id={self.id}, student_id={self.student_id}, month={self.month}/{self.year})>"
