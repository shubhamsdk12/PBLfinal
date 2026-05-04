"""
API routes for expense management and daily checklist.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student, StudentCategoryBudget
from app.models.expense import Expense, ExpenseCategory, DailyExpenseTemplate
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    DailyChecklistSubmit,
    DailyChecklistResponse,
    DailyExpenseTemplateResponse,
    ExpenseCategoryResponse,
    AdditionalExpenseCreate,
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
    Get daily expense checklist based on student's category budgets.

    Returns the categories the student has set up budgets for,
    along with any expenses already recorded for the specified date.
    """
    if expense_date is None:
        expense_date = date.today()

    # Get student's category budgets (these are the categories to show in checklist)
    category_budgets = db.query(StudentCategoryBudget).filter(
        StudentCategoryBudget.student_id == student.id,
        StudentCategoryBudget.is_active == True
    ).all()

    # If student has no category budgets, fall back to default templates
    if not category_budgets:
        templates = db.query(DailyExpenseTemplate).join(ExpenseCategory).filter(
            DailyExpenseTemplate.is_active == True
        ).order_by(DailyExpenseTemplate.display_order).all()

        template_responses = []
        for i, template in enumerate(templates):
            template_responses.append(DailyExpenseTemplateResponse(
                id=template.id,
                category_id=template.category_id,
                category_name=template.category.name,
                daily_budget=Decimal("0.00"),
                display_order=i + 1,
                is_active=template.is_active
            ))
    else:
        # Use student's category budgets
        template_responses = []
        for i, cat_budget in enumerate(category_budgets):
            template_responses.append(DailyExpenseTemplateResponse(
                id=cat_budget.id,
                category_id=cat_budget.category_id,
                category_name=cat_budget.category.name,
                daily_budget=cat_budget.daily_budget,
                display_order=i + 1,
                is_active=cat_budget.is_active
            ))

    # Get expenses for the specified date
    today_expenses = db.query(Expense).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date == expense_date
        )
    ).all()

    # Calculate total daily budget
    total_daily_budget = sum(t.daily_budget for t in template_responses)

    return DailyChecklistResponse(
        expense_date=expense_date,
        templates=template_responses,
        today_expenses=today_expenses,
        total_daily_budget=total_daily_budget
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
    Unchecked categories are ignored (no expense for that category today).

    Also supports additional/unplanned expenses with custom categories.
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

            # Check if expense already exists for this category and date
            existing_expense = db.query(Expense).filter(
                and_(
                    Expense.student_id == student.id,
                    Expense.category_id == item.category_id,
                    Expense.expense_date == checklist_data.expense_date,
                    Expense.is_additional == False
                )
            ).first()

            if existing_expense:
                # Update amount if it changed
                if existing_expense.amount != item.amount:
                    existing_expense.amount = item.amount
                created_expenses.append(existing_expense)
            else:
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

    # Process additional expenses with custom categories
    if checklist_data.additional_expenses:
        for additional in checklist_data.additional_expenses:
            expense = Expense(
                student_id=student.id,
                category_id=None,  # No predefined category
                amount=additional.amount,
                expense_date=additional.expense_date,
                is_additional=True,
                custom_category=additional.custom_category,
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


@router.post("/additional", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_additional_expense(
    expense_data: AdditionalExpenseCreate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an additional expense with a custom category.
    This is for unplanned expenses that don't fit predefined categories.
    """
    expense = Expense(
        student_id=student.id,
        category_id=None,
        amount=expense_data.amount,
        expense_date=expense_data.expense_date,
        is_additional=True,
        custom_category=expense_data.custom_category,
        notes=expense_data.notes
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    # Update remaining budget
    BudgetService.update_remaining_budget(db, student, expense_data.expense_date)

    return expense


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a single expense record.
    """
    # Verify category exists if provided
    if expense_data.category_id:
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
        custom_category=expense_data.custom_category,
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
