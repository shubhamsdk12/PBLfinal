"""
Demo Accounts Generator for Smart Student Expense & Budget System.

Creates 5 demo accounts showcasing different AI alert conditions:

1. Budget Healthy - Good spending habits, no alerts
2. Budget Caution - Moderate spending, warning alerts
3. Budget Critical - Overspent, critical alerts
4. Investment Suggestion - Near month-end with leftover budget
5. High Additional Expenses - Many unplanned expenses

Usage: python scripts/create_demo_accounts.py
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from decimal import Decimal
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.student import Student, StudentCategoryBudget
from app.models.expense import Expense, ExpenseCategory
from app.models.investment import Investment, InvestmentTransaction, InvestmentTransactionType
from app.models.ai_alert import AIAlert
from app.services.ai_service import AIService
from app.services.budget_service import BudgetService

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo password (same for all demo accounts for easy testing)
DEMO_PASSWORD = "demo123"
DEMO_PASSWORD_HASH = pwd_context.hash(DEMO_PASSWORD)


def get_or_create_categories(db: Session) -> dict:
    """Get existing categories or create default ones."""
    categories = db.query(ExpenseCategory).all()
    if not categories:
        # Create default categories
        default_cats = [
            {"name": "Food", "description": "Meals and groceries"},
            {"name": "Travel", "description": "Transportation"},
            {"name": "Snacks", "description": "Snacks and beverages"},
            {"name": "Entertainment", "description": "Leisure activities"},
            {"name": "Printing / Misc", "description": "Miscellaneous items"},
            {"name": "Shopping", "description": "General shopping"},
            {"name": "Utilities", "description": "Bills and utilities"},
            {"name": "Health", "description": "Medical expenses"},
        ]
        for cat_data in default_cats:
            cat = ExpenseCategory(**cat_data)
            db.add(cat)
        db.commit()
        categories = db.query(ExpenseCategory).all()

    return {cat.name: cat for cat in categories}


def delete_demo_accounts(db: Session):
    """Delete existing demo accounts to start fresh."""
    demo_emails = [
        "healthy@demo.com",
        "caution@demo.com",
        "critical@demo.com",
        "investor@demo.com",
        "unplanned@demo.com",
    ]
    for email in demo_emails:
        student = db.query(Student).filter(Student.email == email).first()
        if student:
            # Delete related records (cascades should handle this, but being explicit)
            db.query(AIAlert).filter(AIAlert.student_id == student.id).delete()
            db.query(Expense).filter(Expense.student_id == student.id).delete()
            db.query(StudentCategoryBudget).filter(StudentCategoryBudget.student_id == student.id).delete()
            investment = db.query(Investment).filter(Investment.student_id == student.id).first()
            if investment:
                db.query(InvestmentTransaction).filter(InvestmentTransaction.investment_id == investment.id).delete()
                db.delete(investment)
            db.delete(student)
    db.commit()
    print("[OK] Cleared existing demo accounts")


def create_category_budgets(db: Session, student: Student, categories: dict, budgets: dict):
    """Create category budgets for a student."""
    for cat_name, daily_budget in budgets.items():
        if cat_name in categories:
            cat_budget = StudentCategoryBudget(
                student_id=student.id,
                category_id=categories[cat_name].id,
                daily_budget=Decimal(str(daily_budget)),
                is_active=True
            )
            db.add(cat_budget)
    db.commit()


def create_expenses(db: Session, student: Student, categories: dict, expense_list: list):
    """Create expenses for a student."""
    for exp_data in expense_list:
        category = categories.get(exp_data.get("category"))
        expense = Expense(
            student_id=student.id,
            category_id=category.id if category else None,
            amount=Decimal(str(exp_data["amount"])),
            expense_date=exp_data["date"],
            is_additional=exp_data.get("is_additional", False),
            custom_category=exp_data.get("custom_category"),
            notes=exp_data.get("notes"),
        )
        db.add(expense)
    db.commit()


def create_demo_account_1_healthy(db: Session, categories: dict):
    """Create Demo Account 1: Budget Healthy - Good spending habits."""
    print("\n[1] Creating 'Budget Healthy' account...")

    today = date.today()
    month_start = date(today.year, today.month, 1)

    student = Student(
        email="healthy@demo.com",
        name="Rahul Sharma (Healthy Budget)",
        password_hash=DEMO_PASSWORD_HASH,
        monthly_budget=Decimal("5000.00"),
        budget_start_date=month_start,
        remaining_budget=Decimal("3500.00"),
        budget_setup_complete=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create category budgets
    create_category_budgets(db, student, categories, {
        "Food": 80,
        "Travel": 40,
        "Snacks": 20,
        "Entertainment": 30,
    })

    # Create moderate expenses (well within budget)
    expenses = []
    for i in range(min(15, (today - month_start).days)):
        exp_date = month_start + timedelta(days=i)
        expenses.extend([
            {"category": "Food", "amount": 70, "date": exp_date},
            {"category": "Travel", "amount": 30, "date": exp_date},
        ])
    create_expenses(db, student, categories, expenses)

    # Update remaining budget
    BudgetService.update_remaining_budget(db, student)

    # Evaluate AI rules
    AIService.evaluate_all_rules(db, student)

    print(f"    Email: healthy@demo.com")
    print(f"    Budget: ₹5,000 | Remaining: ₹{student.remaining_budget:.2f}")
    print(f"    Status: HEALTHY - No critical alerts expected")


def create_demo_account_2_caution(db: Session, categories: dict):
    """Create Demo Account 2: Budget Caution - Moderate spending, warning alerts."""
    print("\n[2] Creating 'Budget Caution' account...")

    today = date.today()
    month_start = date(today.year, today.month, 1)

    student = Student(
        email="caution@demo.com",
        name="Priya Patel (Budget Warning)",
        password_hash=DEMO_PASSWORD_HASH,
        monthly_budget=Decimal("4000.00"),
        budget_start_date=month_start,
        remaining_budget=Decimal("1200.00"),
        budget_setup_complete=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create category budgets
    create_category_budgets(db, student, categories, {
        "Food": 100,
        "Travel": 50,
        "Snacks": 30,
        "Entertainment": 40,
        "Shopping": 50,
    })

    # Create higher expenses (spending faster than budget allows)
    expenses = []
    for i in range(min(15, (today - month_start).days)):
        exp_date = month_start + timedelta(days=i)
        expenses.extend([
            {"category": "Food", "amount": 110, "date": exp_date},
            {"category": "Travel", "amount": 60, "date": exp_date},
            {"category": "Entertainment", "amount": 50, "date": exp_date},
        ])
    create_expenses(db, student, categories, expenses)

    # Update remaining budget
    BudgetService.update_remaining_budget(db, student)

    # Evaluate AI rules
    AIService.evaluate_all_rules(db, student)

    print(f"    Email: caution@demo.com")
    print(f"    Budget: ₹4,000 | Remaining: ₹{student.remaining_budget:.2f}")
    print(f"    Status: CAUTION - Warning alerts about budget pace")


def create_demo_account_3_critical(db: Session, categories: dict):
    """Create Demo Account 3: Budget Critical - Overspent, critical alerts."""
    print("\n[3] Creating 'Budget Critical' account...")

    today = date.today()
    month_start = date(today.year, today.month, 1)

    student = Student(
        email="critical@demo.com",
        name="Amit Kumar (Overspent)",
        password_hash=DEMO_PASSWORD_HASH,
        monthly_budget=Decimal("3000.00"),
        budget_start_date=month_start,
        remaining_budget=Decimal("-500.00"),  # Already overspent
        budget_setup_complete=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create category budgets (daily budgets that are too low for actual spending)
    create_category_budgets(db, student, categories, {
        "Food": 60,
        "Travel": 30,
        "Snacks": 20,
        "Entertainment": 40,
    })

    # Create heavy expenses that exceed budget
    expenses = []
    for i in range(min(20, (today - month_start).days)):
        exp_date = month_start + timedelta(days=i)
        expenses.extend([
            {"category": "Food", "amount": 120, "date": exp_date},
            {"category": "Travel", "amount": 50, "date": exp_date},
            {"category": "Entertainment", "amount": 80, "date": exp_date},
        ])
    create_expenses(db, student, categories, expenses)

    # Update remaining budget
    BudgetService.update_remaining_budget(db, student)

    # Create investment for withdrawal suggestion
    investment = Investment(
        student_id=student.id,
        balance=Decimal("1000.00"),
        monthly_interest_rate=Decimal("5.00"),
    )
    db.add(investment)
    db.commit()

    # Evaluate AI rules - should trigger critical alerts and withdrawal suggestion
    AIService.evaluate_all_rules(db, student)

    print(f"    Email: critical@demo.com")
    print(f"    Budget: ₹3,000 | Remaining: ₹{student.remaining_budget:.2f}")
    print(f"    Investment: ₹1,000.00")
    print(f"    Status: CRITICAL - Budget exhausted, withdrawal suggestion")


def create_demo_account_4_investor(db: Session, categories: dict):
    """Create Demo Account 4: Investment Suggestion - Near month-end with leftover."""
    print("\n[4] Creating 'Investor Ready' account...")

    today = date.today()
    # Set budget start to earlier in the month so we're near month-end
    month_start = date(today.year, today.month, 1)

    student = Student(
        email="investor@demo.com",
        name="Neha Singh (Investor)",
        password_hash=DEMO_PASSWORD_HASH,
        monthly_budget=Decimal("6000.00"),
        budget_start_date=month_start,
        remaining_budget=Decimal("500.00"),  # Good leftover near month-end
        budget_setup_complete=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create category budgets
    create_category_budgets(db, student, categories, {
        "Food": 100,
        "Travel": 60,
        "Snacks": 30,
        "Entertainment": 50,
    })

    # Create expenses that leave some budget remaining
    expenses = []
    for i in range(min(25, (today - month_start).days)):
        exp_date = month_start + timedelta(days=i)
        expenses.extend([
            {"category": "Food", "amount": 90, "date": exp_date},
            {"category": "Travel", "amount": 50, "date": exp_date},
            {"category": "Snacks", "amount": 20, "date": exp_date},
        ])
    create_expenses(db, student, categories, expenses)

    # Update remaining budget
    BudgetService.update_remaining_budget(db, student)

    # Create existing investment portfolio
    investment = Investment(
        student_id=student.id,
        balance=Decimal("2500.00"),
        monthly_interest_rate=Decimal("4.50"),
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)

    # Add investment transaction history
    transactions = [
        InvestmentTransaction(
            investment_id=investment.id,
            transaction_type=InvestmentTransactionType.INVEST,
            amount=Decimal("2000.00"),
            balance_before=Decimal("0.00"),
            balance_after=Decimal("2000.00"),
            notes="Initial investment",
        ),
        InvestmentTransaction(
            investment_id=investment.id,
            transaction_type=InvestmentTransactionType.INTEREST,
            amount=Decimal("90.00"),
            balance_before=Decimal("2000.00"),
            balance_after=Decimal("2090.00"),
            notes="Monthly interest at 4.5%",
        ),
        InvestmentTransaction(
            investment_id=investment.id,
            transaction_type=InvestmentTransactionType.INVEST,
            amount=Decimal("410.00"),
            balance_before=Decimal("2090.00"),
            balance_after=Decimal("2500.00"),
            notes="Additional deposit from savings",
        ),
    ]
    for txn in transactions:
        db.add(txn)
    db.commit()

    # Evaluate AI rules - should suggest investing leftover
    AIService.evaluate_all_rules(db, student)

    print(f"    Email: investor@demo.com")
    print(f"    Budget: ₹6,000 | Remaining: ₹{student.remaining_budget:.2f}")
    print(f"    Investment: ₹2,500.00 at 4.5%/month")
    print(f"    Status: HEALTHY - Investment suggestion if near month-end")


def create_demo_account_5_unplanned(db: Session, categories: dict):
    """Create Demo Account 5: High Additional Expenses - Many unplanned expenses."""
    print("\n[5] Creating 'High Unplanned Expenses' account...")

    today = date.today()
    month_start = date(today.year, today.month, 1)

    student = Student(
        email="unplanned@demo.com",
        name="Vikram Rao (Unplanned Spender)",
        password_hash=DEMO_PASSWORD_HASH,
        monthly_budget=Decimal("5000.00"),
        budget_start_date=month_start,
        remaining_budget=Decimal("1500.00"),
        budget_setup_complete=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Create category budgets
    create_category_budgets(db, student, categories, {
        "Food": 80,
        "Travel": 40,
        "Snacks": 25,
        "Entertainment": 35,
    })

    # Create mix of planned and unplanned expenses (heavy on unplanned)
    expenses = []
    for i in range(min(20, (today - month_start).days)):
        exp_date = month_start + timedelta(days=i)
        # Regular expenses
        expenses.extend([
            {"category": "Food", "amount": 75, "date": exp_date},
            {"category": "Travel", "amount": 35, "date": exp_date},
        ])
        # Add unplanned expenses every few days
        if i % 3 == 0:
            expenses.append({
                "category": None,
                "amount": 150,
                "date": exp_date,
                "is_additional": True,
                "custom_category": "Movie & Dinner Out",
                "notes": "Unplanned outing with friends",
            })
        if i % 5 == 0:
            expenses.append({
                "category": None,
                "amount": 200,
                "date": exp_date,
                "is_additional": True,
                "custom_category": "Online Shopping",
                "notes": "Impulse purchase",
            })
        if i % 7 == 0:
            expenses.append({
                "category": None,
                "amount": 100,
                "date": exp_date,
                "is_additional": True,
                "custom_category": "Coffee & Snacks",
                "notes": "Cafe visits",
            })

    create_expenses(db, student, categories, expenses)

    # Update remaining budget
    BudgetService.update_remaining_budget(db, student)

    # Evaluate AI rules - should show spending pattern alerts
    AIService.evaluate_all_rules(db, student)

    print(f"    Email: unplanned@demo.com")
    print(f"    Budget: ₹5,000 | Remaining: ₹{student.remaining_budget:.2f}")
    print(f"    Status: SPENDING PATTERN ALERT - High unplanned expenses warning")


def main():
    """Main function to create all demo accounts."""
    print("=" * 60)
    print("Demo Accounts Generator")
    print("Smart Student Expense & Budget System")
    print("=" * 60)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Delete existing demo accounts
        delete_demo_accounts(db)

        # Get or create categories
        categories = get_or_create_categories(db)
        print(f"\n[OK] Found {len(categories)} expense categories")

        # Create all demo accounts
        create_demo_account_1_healthy(db, categories)
        create_demo_account_2_caution(db, categories)
        create_demo_account_3_critical(db, categories)
        create_demo_account_4_investor(db, categories)
        create_demo_account_5_unplanned(db, categories)

        print("\n" + "=" * 60)
        print("Demo Accounts Created Successfully!")
        print("=" * 60)
        print("\nLogin Credentials (same password for all):")
        print("-" * 40)
        print("Password: demo123")
        print("-" * 40)
        print("1. healthy@demo.com   - Healthy budget, no alerts")
        print("2. caution@demo.com   - Budget warning alerts")
        print("3. critical@demo.com  - Critical alerts + withdrawal suggestion")
        print("4. investor@demo.com  - Good saver with investment portfolio")
        print("5. unplanned@demo.com - High unplanned expenses alert")
        print("-" * 40)
        print("\nUse the Alerts page to see AI-generated recommendations!")
        print("Use the Chatbot to ask questions about each account's budget!")

    except Exception as e:
        print(f"\n[ERROR] Failed to create demo accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
