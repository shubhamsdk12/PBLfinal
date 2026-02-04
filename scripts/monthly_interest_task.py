"""
Scheduled task for crediting monthly interest to investments.

This script should be run once per month (e.g., via cron job or scheduled task).
It credits interest to all active investments based on their monthly interest rate.

Usage:
    python scripts/monthly_interest_task.py
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.investment import Investment
from app.services.investment_service import InvestmentService


def credit_monthly_interest():
    """Credit monthly interest to all investments."""
    db = SessionLocal()
    try:
        investments = db.query(Investment).filter(
            Investment.balance > 0
        ).all()
        
        if not investments:
            print("No investments found with positive balance.")
            return
        
        print(f"Processing {len(investments)} investment(s)...")
        
        for investment in investments:
            try:
                InvestmentService.credit_interest(db, investment)
                print(f"✅ Credited interest to investment {investment.id} "
                      f"(Student ID: {investment.student_id}, "
                      f"Balance: ${investment.balance:.2f})")
            except Exception as e:
                print(f"❌ Error crediting interest to investment {investment.id}: {e}")
        
        print(f"\n✅ Monthly interest credit complete!")
        
    except Exception as e:
        print(f"❌ Error during interest credit: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Running monthly interest credit task on {date.today()}...")
    credit_monthly_interest()
