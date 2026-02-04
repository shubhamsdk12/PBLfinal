"""
API routes for student management and budget operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, BudgetStatusResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new student account.
    Typically called after Supabase Auth registration.
    """
    # Check if student already exists
    existing = db.query(Student).filter(
        Student.supabase_user_id == student_data.supabase_user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student account already exists"
        )
    
    # Create student
    student = Student(
        supabase_user_id=student_data.supabase_user_id,
        email=student_data.email,
        name=student_data.name,
        monthly_budget=student_data.monthly_budget,
        budget_start_date=student_data.budget_start_date,
        remaining_budget=student_data.monthly_budget  # Initially, remaining = monthly
    )
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return student


@router.get("/me", response_model=StudentResponse)
def get_current_student_info(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated student's information.
    """
    # Update remaining budget before returning
    BudgetService.update_remaining_budget(db, student)
    return student


@router.put("/me", response_model=StudentResponse)
def update_student_info(
    student_data: StudentUpdate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current student's information.
    """
    if student_data.name is not None:
        student.name = student_data.name
    
    if student_data.monthly_budget is not None:
        # If budget changes, adjust remaining budget proportionally
        if student.monthly_budget > 0:
            ratio = student_data.monthly_budget / student.monthly_budget
            student.remaining_budget = student.remaining_budget * ratio
        else:
            student.remaining_budget = student_data.monthly_budget
        
        student.monthly_budget = student_data.monthly_budget
    
    if student_data.budget_start_date is not None:
        student.budget_start_date = student_data.budget_start_date
        # Reset remaining budget when start date changes
        student.remaining_budget = student.monthly_budget
    
    db.commit()
    db.refresh(student)
    return student


@router.get("/me/budget-status", response_model=BudgetStatusResponse)
def get_budget_status(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive budget status including health metrics.
    """
    return BudgetService.get_budget_status(db, student)


@router.post("/me/reset-budget", response_model=StudentResponse)
def reset_monthly_budget(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset monthly budget for new month.
    Creates a snapshot of previous month and resets budget.
    """
    return BudgetService.reset_monthly_budget(db, student)
