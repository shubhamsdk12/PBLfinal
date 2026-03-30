"""
Local JWT authentication middleware.
Verifies JWT tokens signed by our backend and extracts user information.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from app.config import settings
from app.database import get_db
from app.models.student import Student

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify local JWT token and return decoded payload.

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        Decoded JWT payload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )


def get_current_user(
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Student:
    """
    Get current authenticated student from database.

    Args:
        payload: Decoded JWT payload
        db: Database session

    Returns:
        Student model instance

    Raises:
        HTTPException: If student not found
    """
    student_id = int(payload.get("sub"))

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found."
        )

    return student


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[Student]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None

    try:
        payload = verify_token(credentials)
        student_id = int(payload.get("sub"))
        student = db.query(Student).filter(
            Student.id == student_id
        ).first()
        return student
    except HTTPException:
        return None
