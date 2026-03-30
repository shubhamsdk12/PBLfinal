"""
Chatbot route for answering budget-related questions.
Rule-based chatbot that has access to the student's budget and expense data.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel, Field
from datetime import date, timedelta
from decimal import Decimal
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student
from app.models.expense import Expense
from app.models.investment import Investment

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatMessage(BaseModel):
    """Schema for chat message."""
    message: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    """Schema for chat response."""
    reply: str
    data: dict = {}


def get_budget_info(db: Session, student: Student) -> dict:
    """Get comprehensive budget information for the student."""
    budget_start = student.budget_start_date
    
    # Calculate month end
    if budget_start.month == 12:
        next_month_start = date(budget_start.year + 1, 1, 1)
    else:
        next_month_start = date(budget_start.year, budget_start.month + 1, 1)
    
    month_end = next_month_start - timedelta(days=1)
    today = date.today()
    days_remaining = max((next_month_start - today).days, 0)
    days_elapsed = (today - budget_start).days
    
    # Total spent this month
    total_spent = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date >= budget_start,
            Expense.expense_date <= month_end
        )
    ).scalar() or Decimal("0.00")
    
    remaining = student.monthly_budget - total_spent
    
    # Today's expenses
    today_spent = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date == today
        )
    ).scalar() or Decimal("0.00")
    
    # Additional expenses this month
    additional_spent = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date >= budget_start,
            Expense.expense_date <= month_end,
            Expense.is_additional == True
        )
    ).scalar() or Decimal("0.00")
    
    daily_allowance = remaining / days_remaining if days_remaining > 0 else Decimal("0.00")
    
    # Investment info
    investment = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    investment_balance = float(investment.balance) if investment else 0.0
    
    return {
        "monthly_budget": float(student.monthly_budget),
        "total_spent": float(total_spent),
        "remaining_budget": float(remaining),
        "today_spent": float(today_spent),
        "additional_spent": float(additional_spent),
        "days_remaining": days_remaining,
        "days_elapsed": days_elapsed,
        "daily_allowance": float(daily_allowance),
        "investment_balance": investment_balance,
        "budget_setup_complete": student.budget_setup_complete,
    }


def process_message(message: str, info: dict) -> str:
    """Process the user's message and return a response based on budget data."""
    msg = message.lower().strip()
    
    if not info["budget_setup_complete"]:
        return (
            "It looks like you haven't set up your budget yet! "
            "Please go to the Dashboard and set up your monthly budget and daily expense categories first."
        )
    
    # Greeting
    if any(word in msg for word in ["hi", "hello", "hey", "howdy"]):
        return (
            f"Hello! 👋 Your current budget status:\n"
            f"• Monthly Budget: ₹{info['monthly_budget']:.2f}\n"
            f"• Spent so far: ₹{info['total_spent']:.2f}\n"
            f"• Remaining: ₹{info['remaining_budget']:.2f}\n"
            f"• Days left: {info['days_remaining']}\n\n"
            f"Ask me anything about your finances!"
        )
    
    # Remaining budget
    if any(word in msg for word in ["remaining", "left", "balance", "how much"]):
        status_emoji = "✅" if info["remaining_budget"] > 0 else "🚨"
        return (
            f"{status_emoji} Your remaining budget is ₹{info['remaining_budget']:.2f} "
            f"for {info['days_remaining']} days.\n"
            f"Daily allowance: ₹{info['daily_allowance']:.2f}/day."
        )
    
    # Today's spending
    if "today" in msg:
        return (
            f"📅 Today's spending: ₹{info['today_spent']:.2f}\n"
            f"Your daily allowance is ₹{info['daily_allowance']:.2f}."
        )
    
    # Total spent
    if any(word in msg for word in ["spent", "total", "expense"]):
        return (
            f"📊 This month's spending:\n"
            f"• Total spent: ₹{info['total_spent']:.2f}\n"
            f"• Additional (unplanned): ₹{info['additional_spent']:.2f}\n"
            f"• Budget used: {(info['total_spent'] / info['monthly_budget'] * 100) if info['monthly_budget'] > 0 else 0:.1f}%"
        )
    
    # Investment
    if any(word in msg for word in ["invest", "saving", "savings"]):
        if info["investment_balance"] > 0:
            return f"💰 Your investment balance is ₹{info['investment_balance']:.2f}."
        else:
            return "💰 You don't have an investment account yet. Go to the Investments tab to create one!"
    
    # Over budget
    if any(word in msg for word in ["over", "exceed", "danger", "risk", "warning"]):
        if info["remaining_budget"] < 0:
            return (
                f"🚨 You're over budget by ₹{abs(info['remaining_budget']):.2f}! "
                f"Consider reducing expenses or withdrawing from investments "
                f"(balance: ₹{info['investment_balance']:.2f})."
            )
        elif info["remaining_budget"] < info["monthly_budget"] * 0.2:
            return (
                f"⚠️ Budget is running low! Only ₹{info['remaining_budget']:.2f} left "
                f"for {info['days_remaining']} days. Be careful with spending!"
            )
        else:
            return f"✅ You're within budget! ₹{info['remaining_budget']:.2f} remaining for {info['days_remaining']} days."
    
    # Daily allowance
    if any(word in msg for word in ["daily", "allowance", "per day"]):
        return f"📆 Your daily allowance is ₹{info['daily_allowance']:.2f} for the remaining {info['days_remaining']} days."
    
    # Budget health / status / summary
    if any(word in msg for word in ["status", "summary", "health", "overview", "budget"]):
        health = "Healthy ✅" if info["remaining_budget"] > info["monthly_budget"] * 0.3 else (
            "Caution ⚠️" if info["remaining_budget"] > 0 else "Critical 🚨"
        )
        return (
            f"📋 Budget Summary:\n"
            f"• Monthly Budget: ₹{info['monthly_budget']:.2f}\n"
            f"• Total Spent: ₹{info['total_spent']:.2f}\n"
            f"• Remaining: ₹{info['remaining_budget']:.2f}\n"
            f"• Days Left: {info['days_remaining']}\n"
            f"• Daily Allowance: ₹{info['daily_allowance']:.2f}\n"
            f"• Investment: ₹{info['investment_balance']:.2f}\n"
            f"• Health: {health}"
        )
    
    # Help
    if any(word in msg for word in ["help", "what can", "commands"]):
        return (
            "🤖 I can help you with:\n"
            "• \"What's my remaining budget?\" — Check remaining funds\n"
            "• \"How much did I spend today?\" — Today's expenses\n"
            "• \"Show my total expenses\" — Monthly spending breakdown\n"
            "• \"Am I over budget?\" — Budget risk check\n"
            "• \"What's my daily allowance?\" — Per-day spending limit\n"
            "• \"Budget summary\" — Full overview\n"
            "• \"Investment status\" — Check investments"
        )
    
    # Default response
    return (
        f"🤖 I'm your budget assistant! Here's a quick summary:\n"
        f"• Remaining: ₹{info['remaining_budget']:.2f} for {info['days_remaining']} days\n"
        f"• Daily allowance: ₹{info['daily_allowance']:.2f}\n\n"
        f"Type \"help\" to see what I can answer!"
    )


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(
    chat: ChatMessage,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask the budget chatbot a question.
    The chatbot has access to your budget, expenses, and investment data.
    """
    info = get_budget_info(db, student)
    reply = process_message(chat.message, info)
    
    return ChatResponse(
        reply=reply,
        data=info
    )
