"""
Authentication utility functions.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model for authentication
class User(BaseModel):
    id: str
    email: str
    name: str
    is_admin: bool = False
    created_at: Optional[datetime] = None
    disabled: bool = False

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token from the Authorization header
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # This is a simplified version for development
        # In production, this would validate the JWT token
        
        # Mock user data for testing - replace with actual JWT validation
        user = User(
            id="test_user_id",
            email="test@example.com",
            name="Test User",
            is_admin=False,
            created_at=datetime.now(),
            disabled=False
        )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) 