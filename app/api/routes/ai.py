"""
API routes for AI alerts and advisory system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timezone
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student
from app.models.ai_alert import AIAlert
from app.schemas.ai_alert import AIAlertResponse, AIAlertUpdate
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/evaluate", response_model=List[AIAlertResponse])
def evaluate_ai_rules(
    current_date: Optional[date] = Query(None, description="Date for evaluation (defaults to today)"),
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger AI rule evaluation and generate alerts.
    
    This endpoint evaluates all AI rules based on:
    - Current expenses
    - Remaining budget
    - Remaining days
    - Investment balances
    
    ⚠️ The AI only creates alerts - it never modifies financial data.
    """
    alerts = AIService.evaluate_all_rules(db, student, current_date)
    return alerts


@router.get("/alerts", response_model=List[AIAlertResponse])
def get_ai_alerts(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated alerts for current student.
    """
    query = db.query(AIAlert).filter(AIAlert.student_id == student.id)
    
    if is_read is not None:
        query = query.filter(AIAlert.is_read == is_read)
    
    if is_resolved is not None:
        query = query.filter(AIAlert.is_resolved == is_resolved)
    
    alerts = query.order_by(AIAlert.created_at.desc()).all()
    return alerts


@router.get("/alerts/unread", response_model=List[AIAlertResponse])
def get_unread_alerts(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unread AI alerts for current student.
    """
    alerts = db.query(AIAlert).filter(
        AIAlert.student_id == student.id,
        AIAlert.is_read == False
    ).order_by(AIAlert.created_at.desc()).all()
    
    return alerts


@router.put("/alerts/{alert_id}", response_model=AIAlertResponse)
def update_alert(
    alert_id: int,
    alert_data: AIAlertUpdate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update alert status (mark as read/resolved).
    """
    alert = db.query(AIAlert).filter(
        AIAlert.id == alert_id,
        AIAlert.student_id == student.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert_data.is_read is not None:
        alert.is_read = alert_data.is_read
        if alert_data.is_read and not alert.read_at:
            alert.read_at = datetime.now(timezone.utc)
    
    if alert_data.is_resolved is not None:
        alert.is_resolved = alert_data.is_resolved
        if alert_data.is_resolved and not alert.resolved_at:
            alert.resolved_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an AI alert.
    """
    alert = db.query(AIAlert).filter(
        AIAlert.id == alert_id,
        AIAlert.student_id == student.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return None
