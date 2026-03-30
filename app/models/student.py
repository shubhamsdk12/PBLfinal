"""
Student model for managing student accounts and monthly budgets.
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    """
    Student account with monthly budget management.

    Each student has:
    - Monthly budget amount
    - Budget start date (for monthly reset calculation)
    - Remaining budget (calculated from expenses)
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    # Budget Configuration
    monthly_budget = Column(Numeric(10, 2), nullable=False, default=0.00)
    budget_start_date = Column(Date, nullable=False)  # First day of current budget cycle
    remaining_budget = Column(Numeric(10, 2), nullable=False, default=0.00)

    # Flag to indicate if budget setup is complete
    budget_setup_complete = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    expenses = relationship("Expense", back_populates="student", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="student", cascade="all, delete-orphan")
    budget_snapshots = relationship("MonthlyBudgetSnapshot", back_populates="student", cascade="all, delete-orphan")
    ai_alerts = relationship("AIAlert", back_populates="student", cascade="all, delete-orphan")
    category_budgets = relationship("StudentCategoryBudget", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, email={self.email}, remaining_budget={self.remaining_budget})>"


class StudentCategoryBudget(Base):
    """
    Daily budget allocation per category for each student.

    This allows students to set how much they plan to spend daily on each category.
    E.g., Food: ₹100/day, Travel: ₹50/day, etc.
    """
    __tablename__ = "student_category_budgets"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False, index=True)

    # Daily budget for this category
    daily_budget = Column(Numeric(10, 2), nullable=False, default=0.00)

    # Whether this category is active in the daily checklist
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="category_budgets")
    category = relationship("ExpenseCategory")

    @property
    def category_name(self) -> str:
        """Return the category name."""
        return self.category.name if self.category else None

    def __repr__(self):
        return f"<StudentCategoryBudget(student_id={self.student_id}, category_id={self.category_id}, daily={self.daily_budget})>"
