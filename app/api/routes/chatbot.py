"""
Chatbot route for answering budget-related questions.
Groq-powered AI chatbot with access to student's budget and expense data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel, Field
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List
import logging

from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student
from app.models.expense import Expense
from app.models.investment import Investment
from app.config import settings
from app.services.chatbot_service import GroqChatbotService

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Schema for chat message."""
    message: str = Field(..., min_length=1, max_length=500)
    history: Optional[List[dict]] = Field(default=None)


class ChatResponse(BaseModel):
    """Schema for chat response."""
    reply: str
    data: dict = {}
    ai_powered: bool = True


class ReportResponse(BaseModel):
    """Schema for report response."""
    report_markdown: str


def get_budget_info(db: Session, student: Student) -> dict:
    """Get comprehensive budget information for the student."""
    budget_start = student.budget_start_date

    if budget_start.month == 12:
        next_month_start = date(budget_start.year + 1, 1, 1)
    else:
        next_month_start = date(budget_start.year, budget_start.month + 1, 1)

    month_end = next_month_start - timedelta(days=1)
    today = date.today()
    days_remaining = max((next_month_start - today).days, 0)
    days_elapsed = (today - budget_start).days

    total_spent = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date >= budget_start,
            Expense.expense_date <= month_end
        )
    ).scalar() or Decimal("0.00")

    remaining = student.monthly_budget - total_spent

    today_spent = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date == today
        )
    ).scalar() or Decimal("0.00")

    additional_spent = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.student_id == student.id,
            Expense.expense_date >= budget_start,
            Expense.expense_date <= month_end,
            Expense.is_additional == True
        )
    ).scalar() or Decimal("0.00")

    daily_allowance = remaining / days_remaining if days_remaining > 0 else Decimal("0.00")

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


@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    chat: ChatMessage,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask the AI-powered budget chatbot a question.

    The chatbot has access to your budget, expenses, and investment data
    and provides personalized financial advice.
    """
    info = get_budget_info(db, student)

    if not info["budget_setup_complete"]:
        return ChatResponse(
            reply=(
                "It looks like you haven't set up your budget yet! "
                "Please go to the Dashboard and set up your monthly budget "
                "and daily expense categories first."
            ),
            data=info,
            ai_powered=False
        )

    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured, using fallback response")
        return ChatResponse(
            reply=GroqChatbotService.get_fallback_response(info),
            data=info,
            ai_powered=False
        )

    try:
        reply = await GroqChatbotService.get_groq_response(
            user_message=chat.message,
            budget_info=info,
            conversation_history=chat.history
        )

        return ChatResponse(
            reply=reply,
            data=info,
            ai_powered=True
        )

    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")

        return ChatResponse(
            reply=GroqChatbotService.get_fallback_response(info),
            data=info,
            ai_powered=False
        )

@router.post("/report", response_model=ReportResponse)
async def generate_report(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive financial report in Markdown format.
    """
    info = get_budget_info(db, student)

    if not info["budget_setup_complete"]:
        return ReportResponse(
            report_markdown="# Financial Report\n\nIt looks like you haven't set up your budget yet! Please go to the Dashboard and set up your monthly budget first."
        )

    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured, cannot generate report")
        return ReportResponse(
            report_markdown="# Financial Report\n\nAI features are currently unavailable because the Groq API key is not configured."
        )

    try:
        report = await GroqChatbotService.get_financial_report(info)
        return ReportResponse(report_markdown=report)
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return ReportResponse(
            report_markdown=f"# Financial Report\n\nAn error occurred while generating the report. Please try again later."
        )
