"""
Investment models for tracking student investments and interest.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class InvestmentTransactionType(str, enum.Enum):
    """Types of investment transactions."""
    INVEST = "INVEST"  # Initial investment or additional deposit
    INTEREST = "INTEREST"  # Monthly interest credit
    WITHDRAW = "WITHDRAW"  # Withdrawal from investment


class Investment(Base):
    """
    Student investment account.
    
    Each investment has:
    - Current balance
    - Monthly interest rate (user-defined)
    - Interest is credited monthly via scheduled task
    """
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True, index=True)
    
    # Investment Details
    balance = Column(Numeric(10, 2), nullable=False, default=0.00)
    monthly_interest_rate = Column(Numeric(5, 2), nullable=False, default=0.00)  # Percentage (e.g., 5.00 for 5%)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="investments")
    transactions = relationship("InvestmentTransaction", back_populates="investment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Investment(id={self.id}, student_id={self.student_id}, balance={self.balance})>"


class InvestmentTransaction(Base):
    """
    Investment transaction log (append-only).
    
    All investment changes are logged:
    - INVEST: Initial or additional deposits
    - INTEREST: Monthly interest credits
    - WITHDRAW: Withdrawals
    
    This ensures complete audit trail of all investment activity.
    """
    __tablename__ = "investment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False, index=True)
    
    # Transaction Details
    transaction_type = Column(SQLEnum(InvestmentTransactionType), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    
    # Metadata
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    investment = relationship("Investment", back_populates="transactions")
    
    def __repr__(self):
        return f"<InvestmentTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"
