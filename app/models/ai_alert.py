"""
AI Alert model for storing advisory alerts and suggestions.
AI agents only create alerts - they never modify financial data.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AlertType(str, enum.Enum):
    """Types of AI-generated alerts."""
    BUDGET_RISK = "BUDGET_RISK"  # Budget running low
    FIXED_EXPENSE_RISK = "FIXED_EXPENSE_RISK"  # Fixed expenses at risk
    INVESTMENT_SUGGESTION = "INVESTMENT_SUGGESTION"  # Suggestion to invest/withdraw
    SPENDING_PATTERN = "SPENDING_PATTERN"  # Spending pattern analysis
    GENERAL = "GENERAL"  # General advisory message


class AlertSeverity(str, enum.Enum):
    """Severity levels for alerts."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AIAlert(Base):
    """
    AI-generated advisory alerts and suggestions.
    
    These are read-only from AI perspective - AI only creates alerts,
    never modifies budgets, expenses, or investments.
    """
    __tablename__ = "ai_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    
    # Alert Details
    alert_type = Column(SQLEnum(AlertType), nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, default=AlertSeverity.INFO)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="ai_alerts")
    
    def __repr__(self):
        return f"<AIAlert(id={self.id}, student_id={self.student_id}, type={self.alert_type}, severity={self.severity})>"
