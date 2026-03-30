"""
Authentication routes for local JWT-based auth.
Handles user registration, login, and profile retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
from app.database import get_db
from app.models.student import Student
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Schemas ---

class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    """Schema for auth response with JWT token."""
    token: str
    student: dict


class StudentProfile(BaseModel):
    """Schema for student profile response."""
    id: int
    email: str
    name: str
    monthly_budget: float
    budget_start_date: str
    budget_setup_complete: bool
    remaining_budget: float
    created_at: str


# --- Helpers ---

def create_access_token(student_id: int) -> str:
    """Create a JWT access token for the given student."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(student_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def student_to_dict(student: Student) -> dict:
    """Convert a Student model to a dict for the response."""
    return {
        "id": student.id,
        "email": student.email,
        "name": student.name,
        "monthly_budget": float(student.monthly_budget),
        "budget_start_date": str(student.budget_start_date),
        "budget_setup_complete": student.budget_setup_complete,
        "remaining_budget": float(student.remaining_budget),
        "created_at": str(student.created_at) if student.created_at else None,
    }


# --- Routes ---

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    Creates a student record with hashed password and returns a JWT token.
    """
    # Check if email already exists
    existing = db.query(Student).filter(Student.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Hash password and create student
    hashed_password = pwd_context.hash(data.password)

    student = Student(
        email=data.email,
        name=data.name,
        password_hash=hashed_password,
        monthly_budget=0.00,
        budget_start_date=date.today(),
        remaining_budget=0.00,
        budget_setup_complete=False,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    # Generate JWT token
    token = create_access_token(student.id)

    return AuthResponse(
        token=token,
        student=student_to_dict(student)
    )


@router.post("/login", response_model=AuthResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Returns a JWT token on success.
    """
    # Find student by email
    student = db.query(Student).filter(Student.email == data.email).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not pwd_context.verify(data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_access_token(student.id)

    return AuthResponse(
        token=token,
        student=student_to_dict(student)
    )


@router.get("/me")
def get_me(
    student: Student = Depends(get_current_user),
):
    """
    Get current authenticated user profile.
    """
    return student_to_dict(student)
