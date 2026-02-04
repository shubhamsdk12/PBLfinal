"""
Pydantic schemas for AI Alert models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.ai_alert import AlertType, AlertSeverity


class AIAlertBase(BaseModel):
    """Base AI alert schema."""
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)


class AIAlertCreate(AIAlertBase):
    """Schema for creating an AI alert (used by AI service)."""
    student_id: int


class AIAlertUpdate(BaseModel):
    """Schema for updating alert status (mark as read/resolved)."""
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None


class AIAlertResponse(AIAlertBase):
    """Schema for AI alert response."""
    id: int
    student_id: int
    is_read: bool
    is_resolved: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
