"""
API routes for investment management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import get_db
from app.auth.middleware import get_current_user
from app.models.student import Student
from app.models.investment import Investment
from app.schemas.investment import (
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentResponse,
    InvestmentSummaryResponse,
    InvestmentWithdrawRequest,
    InvestmentDepositRequest
)
from app.services.investment_service import InvestmentService

router = APIRouter(prefix="/investments", tags=["investments"])


@router.post("/", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def create_investment(
    investment_data: InvestmentCreate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new investment account for current student.
    """
    # Check if investment already exists
    existing = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Investment account already exists. Use update endpoint to modify."
        )
    
    investment = InvestmentService.create_investment(
        db,
        student.id,
        investment_data.initial_balance,
        investment_data.monthly_interest_rate
    )
    
    return investment


@router.get("/me", response_model=InvestmentResponse)
def get_my_investment(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current student's investment account.
    """
    investment = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found. Create one first."
        )
    
    return investment


@router.put("/me", response_model=InvestmentResponse)
def update_investment(
    investment_data: InvestmentUpdate,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update investment settings (e.g., interest rate).
    """
    investment = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    if investment_data.monthly_interest_rate is not None:
        investment.monthly_interest_rate = investment_data.monthly_interest_rate
    
    db.commit()
    db.refresh(investment)
    
    return investment


@router.get("/me/summary", response_model=InvestmentSummaryResponse)
def get_investment_summary(
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive investment summary with transaction history.
    """
    investment = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    return InvestmentService.get_investment_summary(db, investment)


@router.post("/me/deposit", response_model=InvestmentResponse)
def deposit_to_investment(
    deposit_data: InvestmentDepositRequest,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deposit money into investment account.
    """
    investment = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    investment = InvestmentService.deposit(
        db,
        investment,
        deposit_data.amount,
        deposit_data.notes
    )
    
    return investment


@router.post("/me/withdraw", response_model=InvestmentResponse)
def withdraw_from_investment(
    withdraw_data: InvestmentWithdrawRequest,
    student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Withdraw money from investment account.
    """
    investment = db.query(Investment).filter(
        Investment.student_id == student.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    try:
        investment = InvestmentService.withdraw(
            db,
            investment,
            withdraw_data.amount,
            withdraw_data.notes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return investment
