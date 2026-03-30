"""
API routes for student management and budget operations.
Student creation is handled by /auth/register — these routes manage budget & profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student, StudentCategoryBudget
from app.models.expense import ExpenseCategory
from app.schemas.student import (
    StudentUpdate,
    StudentResponse,
    BudgetStatusResponse,
    CategoryBudgetResponse,
    BudgetSetupRequest,
    BudgetSetupResponse,
)
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/students", tags=["students"])


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

    if student_data.budget_setup_complete is not None:
        student.budget_setup_complete = student_data.budget_setup_complete

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


# --- Category Budget Endpoints ---

@router.get("/me/category-budgets", response_model=List[CategoryBudgetResponse])
def get_category_budgets(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all category budgets for the current student.
    """
    budgets = db.query(StudentCategoryBudget).filter(
        StudentCategoryBudget.student_id == student.id
    ).all()
    return budgets


@router.post("/me/budget-setup", response_model=BudgetSetupResponse)
def setup_budget(
    setup_data: BudgetSetupRequest,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete budget setup - sets monthly budget and per-category daily budgets.
    This is the main endpoint for initial budget configuration.
    """
    # Update student's monthly budget
    student.monthly_budget = setup_data.monthly_budget
    student.remaining_budget = setup_data.monthly_budget
    student.budget_start_date = setup_data.budget_start_date
    student.budget_setup_complete = True

    # Delete existing category budgets
    db.query(StudentCategoryBudget).filter(
        StudentCategoryBudget.student_id == student.id
    ).delete()

    # Create new category budgets
    created_budgets = []
    for item in setup_data.category_budgets:
        # Verify category exists
        category = db.query(ExpenseCategory).filter(
            ExpenseCategory.id == item.category_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {item.category_id} not found"
            )

        cat_budget = StudentCategoryBudget(
            student_id=student.id,
            category_id=item.category_id,
            daily_budget=item.daily_budget,
            is_active=item.is_active
        )
        db.add(cat_budget)
        created_budgets.append(cat_budget)

    db.commit()
    db.refresh(student)

    # Refresh all budgets
    for budget in created_budgets:
        db.refresh(budget)

    return BudgetSetupResponse(
        student=student,
        category_budgets=created_budgets
    )


@router.put("/me/category-budgets/{category_id}", response_model=CategoryBudgetResponse)
def update_category_budget(
    category_id: int,
    daily_budget: Decimal,
    is_active: bool = True,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific category budget.
    """
    cat_budget = db.query(StudentCategoryBudget).filter(
        StudentCategoryBudget.student_id == student.id,
        StudentCategoryBudget.category_id == category_id
    ).first()

    if not cat_budget:
        # Create new if doesn't exist
        category = db.query(ExpenseCategory).filter(
            ExpenseCategory.id == category_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found"
            )

        cat_budget = StudentCategoryBudget(
            student_id=student.id,
            category_id=category_id,
            daily_budget=daily_budget,
            is_active=is_active
        )
        db.add(cat_budget)
    else:
        cat_budget.daily_budget = daily_budget
        cat_budget.is_active = is_active

    db.commit()
    db.refresh(cat_budget)
    return cat_budget
