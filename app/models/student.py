"""
Student model for managing student accounts and monthly budgets.
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
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
    # Supabase Auth user ID (from JWT token)
    supabase_user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # Budget Configuration
    monthly_budget = Column(Numeric(10, 2), nullable=False, default=0.00)
    budget_start_date = Column(Date, nullable=False)  # First day of current budget cycle
    remaining_budget = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    expenses = relationship("Expense", back_populates="student", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="student", cascade="all, delete-orphan")
    budget_snapshots = relationship("MonthlyBudgetSnapshot", back_populates="student", cascade="all, delete-orphan")
    ai_alerts = relationship("AIAlert", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(id={self.id}, email={self.email}, remaining_budget={self.remaining_budget})>"
