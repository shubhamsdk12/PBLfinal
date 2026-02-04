"""
API routes for expense management and daily checklist.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from typing import List, Optional
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student
from app.models.expense import Expense, ExpenseCategory, DailyExpenseTemplate
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    DailyChecklistSubmit,
    DailyChecklistResponse,
    DailyExpenseTemplateResponse,
    ExpenseCategoryResponse
)
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/categories", response_model=List[ExpenseCategoryResponse])
def get_expense_categories(
    db: Session = Depends(get_db)
):
    """
    Get all available expense categories.
    """
    categories = db.query(ExpenseCategory).all()
    return categories


@router.get("/daily-checklist", response_model=DailyChecklistResponse)
def get_daily_checklist(
    expense_date: Optional[date] = Query(None, description="Date for checklist (defaults to today)"),
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily expense checklist template and today's expenses.
    
    Returns the fixed list of expense categories to show on frontend,
    along with any expenses already recorded for the specified date.
    """
    if expense_date is None:
        expense_date = date.today()
    
    # Get active daily expense templates (ordered)
    templates = db.query(DailyExpenseTemplate).join(ExpenseCategory).filter(
        DailyExpenseTemplate.is_active == True
    ).order_by(DailyExpenseTemplate.display_order).all()
    
    # Get expenses for the specified date
    today_expenses = db.query(Expense).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date == expense_date
        )
    ).all()
    
    # Format template response with category names
    template_responses = []
    for template in templates:
        template_responses.append(DailyExpenseTemplateResponse(
            id=template.id,
            category_id=template.category_id,
            category_name=template.category.name,
            display_order=template.display_order,
            is_active=template.is_active
        ))
    
    return DailyChecklistResponse(
        expense_date=expense_date,
        templates=template_responses,
        today_expenses=today_expenses
    )


@router.post("/daily-checklist", response_model=List[ExpenseResponse], status_code=status.HTTP_201_CREATED)
def submit_daily_checklist(
    checklist_data: DailyChecklistSubmit,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit daily expense checklist.
    
    Only checked items (is_checked=True) are saved as Expense records.
    Unchecked categories are ignored.
    
    Also supports additional/unplanned expenses via additional_expenses field.
    """
    created_expenses = []
    
    # Process checked items from checklist
    for item in checklist_data.items:
        if item.is_checked and item.amount > 0:
            # Verify category exists
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.id == item.category_id
            ).first()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense category {item.category_id} not found"
                )
            
            # Create expense record
            expense = Expense(
                student_id=student.id,
                category_id=item.category_id,
                amount=item.amount,
                expense_date=checklist_data.expense_date,
                is_additional=False
            )
            db.add(expense)
            created_expenses.append(expense)
    
    # Process additional expenses
    if checklist_data.additional_expenses:
        for additional in checklist_data.additional_expenses:
            # Verify category exists
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.id == additional.category_id
            ).first()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense category {additional.category_id} not found"
                )
            
            expense = Expense(
                student_id=student.id,
                category_id=additional.category_id,
                amount=additional.amount,
                expense_date=additional.expense_date,
                is_additional=True,
                notes=additional.notes
            )
            db.add(expense)
            created_expenses.append(expense)
    
    db.commit()
    
    # Update remaining budget
    BudgetService.update_remaining_budget(db, student, checklist_data.expense_date)
    
    # Refresh expenses to get IDs
    for expense in created_expenses:
        db.refresh(expense)
    
    return created_expenses


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a single expense record (for additional/unplanned expenses).
    """
    # Verify category exists
    category = db.query(ExpenseCategory).filter(
        ExpenseCategory.id == expense_data.category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense category {expense_data.category_id} not found"
        )
    
    expense = Expense(
        student_id=student.id,
        category_id=expense_data.category_id,
        amount=expense_data.amount,
        expense_date=expense_data.expense_date,
        is_additional=expense_data.is_additional,
        notes=expense_data.notes
    )
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    # Update remaining budget
    BudgetService.update_remaining_budget(db, student, expense_data.expense_date)
    
    return expense


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get expenses for current student with optional date filtering.
    """
    query = db.query(Expense).filter(Expense.student_id == student.id)
    
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    
    expenses = query.order_by(Expense.expense_date.desc(), Expense.created_at.desc()).all()
    
    return expenses


@router.get("/today", response_model=List[ExpenseResponse])
def get_today_expenses(
    expense_date: Optional[date] = Query(None, description="Date to query (defaults to today)"),
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get expenses for a specific date (defaults to today).
    """
    if expense_date is None:
        expense_date = date.today()
    
    expenses = db.query(Expense).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date == expense_date
        )
    ).order_by(Expense.created_at.desc()).all()
    
    return expenses
