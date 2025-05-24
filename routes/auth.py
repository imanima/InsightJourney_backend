"""
Authentication routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError  # Import correct JWT exceptions
import secrets
import uuid
from services import get_neo4j_service, get_auth_service, Neo4jService, AuthService

# Configure logger
logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(prefix="/auth")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_admin: bool = False
    created_at: datetime
    disabled: Optional[bool] = None

    class Config:
        from_attributes = True

class PasswordUpdateRequest(BaseModel):
    current_password: str
    new_password: str

class ApiKeyResponse(BaseModel):
    api_key: str
    expires_at: Optional[datetime] = None

class UserCredential(BaseModel):
    type: str = Field(..., description="Type of credential: 'password' or 'api_key'")
    value: str = Field(..., description="The credential value")
    expires_at: Optional[datetime] = None

# Routes
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login a user"""
    try:
        # Get auth service
        auth_service = get_auth_service()
        
        # Login user
        success, response, error_message = auth_service.login_user(
            email=form_data.username,
            password=form_data.password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message or "Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return {
            "access_token": response.get("access_token"),
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

def create_access_token(data: dict):
    """Create JWT token"""
    import os
    from datetime import datetime, timedelta
    
    # JWT configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=User)
async def register(
    user: UserCreate
):
    """Register a new user"""
    try:
        # Get the auth service
        auth_service = get_auth_service()
        
        # Register user using auth service
        success, response, error_message = auth_service.register_user(
            email=user.email,
            password=user.password,
            name=user.name or ""
        )
        
        if not success:
            # Check for duplicate user error
            if error_message and "already exists" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message or "Registration failed"
                )
            
        user_data = response.get("user", {})
        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "is_admin": False,
            "created_at": datetime.now(),
            "disabled": False
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme)
):
    """Logout current user"""
    # In a JWT-based system, the client should discard the token
    # Here we just return success as there's no server-side session
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=User)
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """Get current user info"""
    try:
        # Get auth service
        auth_service = get_auth_service()
        
        # Log token info for debugging
        logger.info(f"Verifying token: {token[:10]}...")
        
        # Extract token payload directly first for detailed logging
        try:
            payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
            user_id_or_email = payload.get("sub")
            logger.info(f"Token decoded successfully, subject: {user_id_or_email}")
        except Exception as token_error:
            logger.error(f"Token decode error: {str(token_error)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Determine if subject is an email or user ID
        is_email = "@" in str(user_id_or_email) if user_id_or_email else False
        
        # Get user information based on token subject type
        user = None
        if is_email:
            logger.info(f"Looking up user by email: {user_id_or_email}")
            user = auth_service.user_service.get_user_by_email(user_id_or_email)
        else:
            logger.info(f"Looking up user by ID: {user_id_or_email}")
            user = auth_service.user_service.get_user_by_id(user_id_or_email)
        
        if not user:
            logger.error(f"User not found for token subject: {user_id_or_email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
            
        logger.info(f"User found: {user.get('userId', 'unknown')}")
        
        # Return user data in expected format
        return {
            "id": user.get("userId"),
            "email": user.get("email"),
            "name": user.get("name", ""),
            "is_admin": user.get("is_admin", False),
            "created_at": datetime.fromisoformat(user.get("created_at", datetime.now().isoformat())),
            "disabled": user.get("disabled", False)
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# New routes for managing credentials
@router.put("/credentials/password", status_code=status.HTTP_200_OK)
async def update_password(
    password_data: PasswordUpdateRequest,
    token: str = Depends(oauth2_scheme)
):
    """Update the current user's password"""
    try:
        # Get auth service
        auth_service = get_auth_service()
        
        # Extract user_id from token
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update password
        success, error_message = auth_service.change_password(
            user_id, password_data.current_password, password_data.new_password
        )
        
        if not success:
            # Check for specific error types
            if error_message and "incorrect" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message or "Failed to update password"
                )
        
        return {"message": "Password updated successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/credentials/api-key", response_model=ApiKeyResponse)
async def generate_api_key(
    token: str = Depends(oauth2_scheme)
):
    """Generate a new API key for the current user"""
    try:
        # Get services
        neo4j_service = get_neo4j_service()
        auth_service = get_auth_service()
        
        # Extract user_id from token
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate API key
        api_key = f"ij-{secrets.token_hex(16)}"
        expiration = datetime.utcnow() + timedelta(days=90)  # API key valid for 90 days
        
        # Store API key in user properties
        with neo4j_service.driver.session() as session:
            result = session.run("""
                MATCH (u:User {userId: $userId})
                SET u.apiKey = $apiKey,
                    u.apiKeyExpires = $expires
                RETURN u
            """, 
            userId=user_id, 
            apiKey=api_key,
            expires=expiration.isoformat())
            
            if not result.single():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        return {
            "api_key": api_key,
            "expires_at": expiration
        }
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/credentials", response_model=List[UserCredential])
async def get_user_credentials(
    token: str = Depends(oauth2_scheme)
):
    """Get all credentials for the current user"""
    try:
        # Get services
        neo4j_service = get_neo4j_service()
        auth_service = get_auth_service()
        
        # Extract user_id from token
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user data
        user = neo4j_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        credentials = []
        
        # Add password credential (masked)
        if user.get("password_hash"):
            credentials.append({
                "type": "password",
                "value": "********",  # Masked for security
                "expires_at": None
            })
        
        # Add API key if exists
        if user.get("apiKey"):
            expires_at = None
            if user.get("apiKeyExpires"):
                try:
                    expires_at = datetime.fromisoformat(user["apiKeyExpires"])
                except:
                    pass
            
            credentials.append({
                "type": "api_key",
                "value": user["apiKey"],
                "expires_at": expires_at
            })
        
        return credentials
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error getting user credentials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.delete("/credentials/api-key", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    token: str = Depends(oauth2_scheme)
):
    """Revoke the current user's API key"""
    try:
        # Get services
        neo4j_service = get_neo4j_service()
        auth_service = get_auth_service()
        
        # Extract user_id from token
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Remove API key from user properties
        with neo4j_service.driver.session() as session:
            result = session.run("""
                MATCH (u:User {userId: $userId})
                REMOVE u.apiKey
                REMOVE u.apiKeyExpires
                RETURN u
            """, userId=user_id)
            
            if not result.single():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        return {"message": "API key revoked successfully"}
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 