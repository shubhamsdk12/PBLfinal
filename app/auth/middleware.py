"""
Supabase JWT authentication middleware.
Verifies JWT tokens from Supabase Auth and extracts user information.
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
    Verify Supabase JWT token and return decoded payload.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        Decoded JWT payload with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        # Decode JWT token using Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase tokens may not have aud claim
        )
        
        # Extract user ID from token
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
            detail=f"Invalid token: {str(e)}"
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
    supabase_user_id = payload.get("sub")
    
    student = db.query(Student).filter(
        Student.supabase_user_id == supabase_user_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found. Please register first."
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
        supabase_user_id = payload.get("sub")
        student = db.query(Student).filter(
            Student.supabase_user_id == supabase_user_id
        ).first()
        return student
    except HTTPException:
        return None
