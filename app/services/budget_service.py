"""
Budget service for managing student budgets and calculating budget status.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from decimal import Decimal
from app.models.student import Student
from app.models.expense import Expense, MonthlyBudgetSnapshot
from app.schemas.student import BudgetStatusResponse


class BudgetService:
    """Service for budget-related operations."""
    
    @staticmethod
    def calculate_remaining_budget(
        db: Session,
        student: Student,
        current_date: date = None
    ) -> Decimal:
        """
        Calculate remaining budget based on expenses in current month.
        
        This is the source of truth for remaining budget calculation.
        """
        if current_date is None:
            current_date = date.today()
        
        budget_start = student.budget_start_date
        
        # Calculate month end
        if budget_start.month == 12:
            next_month_start = date(budget_start.year + 1, 1, 1)
        else:
            next_month_start = date(budget_start.year, budget_start.month + 1, 1)
        
        month_end = next_month_start - timedelta(days=1)
        
        # Sum all expenses in current budget cycle
        total_spent = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.student_id == student.id,
                Expense.expense_date >= budget_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or Decimal("0.00")
        
        remaining = student.monthly_budget - total_spent
        return remaining
    
    @staticmethod
    def update_remaining_budget(
        db: Session,
        student: Student,
        current_date: date = None
    ) -> Student:
        """
        Update student's remaining budget based on current expenses.
        """
        if current_date is None:
            current_date = date.today()
        
        remaining = BudgetService.calculate_remaining_budget(db, student, current_date)
        student.remaining_budget = remaining
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def get_budget_status(
        db: Session,
        student: Student,
        current_date: date = None
    ) -> BudgetStatusResponse:
        """
        Get comprehensive budget status including health metrics.
        """
        if current_date is None:
            current_date = date.today()
        
        budget_start = student.budget_start_date
        
        # Calculate month boundaries
        if budget_start.month == 12:
            next_month_start = date(budget_start.year + 1, 1, 1)
        else:
            next_month_start = date(budget_start.year, budget_start.month + 1, 1)
        
        month_end = next_month_start - timedelta(days=1)
        days_elapsed = (current_date - budget_start).days
        days_remaining = (next_month_start - current_date).days
        
        # Calculate total spent
        total_spent = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.student_id == student.id,
                Expense.expense_date >= budget_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or Decimal("0.00")
        
        # Update remaining budget
        remaining_budget = BudgetService.calculate_remaining_budget(db, student, current_date)
        student.remaining_budget = remaining_budget
        db.commit()
        
        # Calculate daily allowance
        daily_allowance = remaining_budget / days_remaining if days_remaining > 0 else Decimal("0.00")
        
        # Determine budget health
        from app.services.ai_service import AIService
        budget_health = AIService.calculate_budget_health(
            remaining_budget,
            student.monthly_budget,
            days_remaining
        )
        
        return BudgetStatusResponse(
            student_id=student.id,
            monthly_budget=student.monthly_budget,
            remaining_budget=remaining_budget,
            total_spent=total_spent,
            budget_start_date=budget_start,
            days_elapsed=days_elapsed,
            days_remaining=days_remaining,
            daily_budget_allowance=daily_allowance,
            budget_health=budget_health
        )
    
    @staticmethod
    def reset_monthly_budget(
        db: Session,
        student: Student,
        new_start_date: date = None
    ) -> Student:
        """
        Reset monthly budget for new month.
        Creates a snapshot of previous month and resets budget.
        """
        if new_start_date is None:
            # Calculate next month start
            current_start = student.budget_start_date
            if current_start.month == 12:
                new_start_date = date(current_start.year + 1, 1, 1)
            else:
                new_start_date = date(current_start.year, current_start.month + 1, 1)
        
        # Create snapshot of previous month
        previous_month = student.budget_start_date.month
        previous_year = student.budget_start_date.year
        
        # Calculate total spent in previous month
        month_start = student.budget_start_date
        month_end = new_start_date - timedelta(days=1)
        
        total_spent = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.student_id == student.id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or Decimal("0.00")
        
        # Create snapshot
        snapshot = MonthlyBudgetSnapshot(
            student_id=student.id,
            month=previous_month,
            year=previous_year,
            budgeted_amount=student.monthly_budget,
            total_spent=total_spent,
            remaining_budget=student.remaining_budget
        )
        db.add(snapshot)
        
        # Reset budget
        student.budget_start_date = new_start_date
        student.remaining_budget = student.monthly_budget
        db.commit()
        db.refresh(student)
        
        return student
