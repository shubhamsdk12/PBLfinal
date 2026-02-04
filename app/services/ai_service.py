"""
AI Rule Evaluation Service (Advisory Only).

⚠️ IMPORTANT: This AI service ONLY reads data and creates alerts.
It NEVER modifies budgets, expenses, or investments automatically.

The AI evaluates rules based on:
- Current expenses
- Remaining budget
- Remaining days in budget cycle
- Investment balances
- Spending patterns

And generates advisory alerts only.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List
from app.models.student import Student
from app.models.expense import Expense
from app.models.investment import Investment
from app.models.ai_alert import AIAlert, AlertType, AlertSeverity
from app.schemas.ai_alert import AIAlertCreate


class AIService:
    """AI rule evaluation service for generating advisory alerts."""
    
    @staticmethod
    def calculate_budget_health(
        remaining_budget: Decimal,
        monthly_budget: Decimal,
        days_remaining: int
    ) -> str:
        """
        Calculate budget health status based on remaining budget and days.
        
        Returns:
            "Healthy", "Caution", or "Critical"
        """
        if monthly_budget == 0:
            return "Critical"
        
        budget_used_percentage = (1 - (remaining_budget / monthly_budget)) * 100
        
        # Critical: Less than 20% budget remaining OR negative budget
        if remaining_budget < 0 or budget_used_percentage > 80:
            return "Critical"
        
        # Caution: Between 50-80% used OR daily allowance is insufficient
        if budget_used_percentage > 50:
            if days_remaining > 0:
                daily_allowance = remaining_budget / days_remaining
                # If daily allowance is less than 10% of monthly budget per day
                avg_daily_budget = monthly_budget / 30
                if daily_allowance < (avg_daily_budget * 0.5):
                    return "Critical"
            return "Caution"
        
        return "Healthy"
    
    @staticmethod
    def evaluate_budget_rules(
        db: Session,
        student: Student,
        current_date: date = None
    ) -> List[AIAlertCreate]:
        """
        Evaluate budget-related rules and generate alerts.
        
        Rules evaluated:
        1. Budget running low (Critical/Warning)
        2. Daily allowance insufficient
        3. Budget exhausted
        """
        if current_date is None:
            current_date = date.today()
        
        alerts = []
        
        # Calculate days in budget cycle
        budget_start = student.budget_start_date
        # Calculate next month's start date
        if budget_start.month == 12:
            next_month_start = date(budget_start.year + 1, 1, 1)
        else:
            next_month_start = date(budget_start.year, budget_start.month + 1, 1)
        
        days_elapsed = (current_date - budget_start).days
        days_remaining = (next_month_start - current_date).days
        
        # Calculate total spent this month
        month_start = budget_start
        month_end = next_month_start - timedelta(days=1)
        
        total_spent = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.student_id == student.id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or Decimal("0.00")
        
        remaining_budget = student.remaining_budget
        monthly_budget = student.monthly_budget
        
        # Calculate budget health
        budget_health = AIService.calculate_budget_health(
            remaining_budget,
            monthly_budget,
            days_remaining
        )
        
        # Rule 1: Budget exhausted (Critical)
        if remaining_budget < 0:
            alerts.append(AIAlertCreate(
                student_id=student.id,
                alert_type=AlertType.BUDGET_RISK,
                severity=AlertSeverity.CRITICAL,
                title="Budget Exhausted",
                message=f"Your budget has been exceeded by ${abs(remaining_budget):.2f}. "
                       f"Consider reviewing your expenses or adjusting your budget."
            ))
        
        # Rule 2: Budget running critically low
        elif budget_health == "Critical" and remaining_budget >= 0:
            daily_allowance = remaining_budget / days_remaining if days_remaining > 0 else Decimal("0.00")
            alerts.append(AIAlertCreate(
                student_id=student.id,
                alert_type=AlertType.BUDGET_RISK,
                severity=AlertSeverity.CRITICAL,
                title="Budget Running Critically Low",
                message=f"You have ${remaining_budget:.2f} remaining for {days_remaining} days. "
                       f"Daily allowance: ${daily_allowance:.2f}. "
                       f"Consider reducing non-essential expenses."
            ))
        
        # Rule 3: Budget caution warning
        elif budget_health == "Caution":
            daily_allowance = remaining_budget / days_remaining if days_remaining > 0 else Decimal("0.00")
            alerts.append(AIAlertCreate(
                student_id=student.id,
                alert_type=AlertType.BUDGET_RISK,
                severity=AlertSeverity.WARNING,
                title="Budget Caution",
                message=f"You have ${remaining_budget:.2f} remaining for {days_remaining} days. "
                       f"Daily allowance: ${daily_allowance:.2f}. "
                       f"Monitor your spending to stay within budget."
            ))
        
        # Rule 4: Daily allowance insufficient
        if days_remaining > 0 and remaining_budget > 0:
            daily_allowance = remaining_budget / days_remaining
            avg_daily_budget = monthly_budget / 30
            if daily_allowance < (avg_daily_budget * 0.3):
                alerts.append(AIAlertCreate(
                    student_id=student.id,
                    alert_type=AlertType.BUDGET_RISK,
                    severity=AlertSeverity.WARNING,
                    title="Low Daily Allowance",
                    message=f"Your daily allowance (${daily_allowance:.2f}) is significantly below average. "
                           f"Consider adjusting spending patterns."
                ))
        
        return alerts
    
    @staticmethod
    def evaluate_investment_rules(
        db: Session,
        student: Student
    ) -> List[AIAlertCreate]:
        """
        Evaluate investment-related rules and generate suggestions.
        
        Rules evaluated:
        1. Suggest investing leftover budget at month-end
        2. Suggest withdrawing if needed for expenses
        """
        alerts = []
        
        investment = db.query(Investment).filter(
            Investment.student_id == student.id
        ).first()
        
        # Rule 1: Suggest investing if significant leftover budget
        if student.remaining_budget > 100:  # Threshold: $100
            current_date = date.today()
            budget_start = student.budget_start_date
            
            # Check if near month-end (within 3 days)
            if budget_start.month == 12:
                next_month_start = date(budget_start.year + 1, 1, 1)
            else:
                next_month_start = date(budget_start.year, budget_start.month + 1, 1)
            
            days_remaining = (next_month_start - current_date).days
            
            if days_remaining <= 3:
                alerts.append(AIAlertCreate(
                    student_id=student.id,
                    alert_type=AlertType.INVESTMENT_SUGGESTION,
                    severity=AlertSeverity.INFO,
                    title="Consider Investing Leftover Budget",
                    message=f"You have ${student.remaining_budget:.2f} remaining this month. "
                           f"Consider investing this amount to earn interest."
                ))
        
        # Rule 2: Suggest withdrawal if budget is negative and investment exists
        if student.remaining_budget < 0 and investment and investment.balance > 0:
            withdrawal_suggestion = min(abs(student.remaining_budget), investment.balance)
            alerts.append(AIAlertCreate(
                student_id=student.id,
                alert_type=AlertType.INVESTMENT_SUGGESTION,
                severity=AlertSeverity.WARNING,
                title="Consider Withdrawing from Investment",
                message=f"Your budget is negative by ${abs(student.remaining_budget):.2f}. "
                       f"Consider withdrawing ${withdrawal_suggestion:.2f} from your investment "
                       f"(current balance: ${investment.balance:.2f})."
            ))
        
        return alerts
    
    @staticmethod
    def evaluate_spending_patterns(
        db: Session,
        student: Student,
        current_date: date = None
    ) -> List[AIAlertCreate]:
        """
        Evaluate spending patterns and generate insights.
        
        Rules evaluated:
        1. Unusual spending spikes
        2. High additional expenses
        """
        if current_date is None:
            current_date = date.today()
        
        alerts = []
        
        budget_start = student.budget_start_date
        if budget_start.month == 12:
            next_month_start = date(budget_start.year + 1, 1, 1)
        else:
            next_month_start = date(budget_start.year, budget_start.month + 1, 1)
        
        month_start = budget_start
        month_end = next_month_start - timedelta(days=1)
        
        # Calculate additional expenses
        additional_expenses = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.student_id == student.id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end,
                Expense.is_additional == True
            )
        ).scalar() or Decimal("0.00")
        
        total_expenses = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.student_id == student.id,
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            )
        ).scalar() or Decimal("0.00")
        
        # Rule: High additional expenses (>30% of total)
        if total_expenses > 0:
            additional_percentage = (additional_expenses / total_expenses) * 100
            if additional_percentage > 30:
                alerts.append(AIAlertCreate(
                    student_id=student.id,
                    alert_type=AlertType.SPENDING_PATTERN,
                    severity=AlertSeverity.WARNING,
                    title="High Unplanned Expenses",
                    message=f"Your unplanned expenses (${additional_expenses:.2f}) represent "
                           f"{additional_percentage:.1f}% of total spending. "
                           f"Consider planning ahead to better manage your budget."
                ))
        
        return alerts
    
    @staticmethod
    def evaluate_all_rules(
        db: Session,
        student: Student,
        current_date: date = None
    ) -> List[AIAlert]:
        """
        Evaluate all AI rules and create alerts in database.
        
        This is the main entry point for AI evaluation.
        It reads all relevant data, evaluates rules, and creates alerts.
        
        ⚠️ This function ONLY creates alerts - it never modifies financial data.
        """
        if current_date is None:
            current_date = date.today()
        
        # Collect all alerts from different rule sets
        all_alerts = []
        
        # Budget rules
        all_alerts.extend(AIService.evaluate_budget_rules(db, student, current_date))
        
        # Investment rules
        all_alerts.extend(AIService.evaluate_investment_rules(db, student))
        
        # Spending pattern rules
        all_alerts.extend(AIService.evaluate_spending_patterns(db, student, current_date))
        
        # Create alert records in database
        created_alerts = []
        for alert_data in all_alerts:
            # Check if similar alert already exists (avoid duplicates)
            existing = db.query(AIAlert).filter(
                and_(
                    AIAlert.student_id == alert_data.student_id,
                    AIAlert.alert_type == alert_data.alert_type,
                    AIAlert.title == alert_data.title,
                    AIAlert.is_resolved == False,
                    func.date(AIAlert.created_at) == current_date
                )
            ).first()
            
            if not existing:
                alert = AIAlert(**alert_data.model_dump())
                db.add(alert)
                created_alerts.append(alert)
        
        db.commit()
        
        # Refresh alerts to get IDs
        for alert in created_alerts:
            db.refresh(alert)
        
        return created_alerts
