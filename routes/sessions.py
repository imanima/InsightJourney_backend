"""
Sessions routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from services import get_neo4j_service, get_session_service, get_auth_service
import jwt

# Configure logger
logger = logging.getLogger(__name__)

# Create router with prefix to avoid conflicts with health endpoint
router = APIRouter(prefix="/sessions")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    transcript: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    status: str = "pending"
    analysis_status: Optional[str] = None

    class Config:
        from_attributes = True

# Authentication dependency
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Get current user ID from JWT token"""
    try:
        auth_service = get_auth_service()
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id_or_email = payload.get("sub")
        
        # If it's an email, get the user ID
        if "@" in str(user_id_or_email):
            neo4j_service = get_neo4j_service()
            user = neo4j_service.get_user_by_email(user_id_or_email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user["userId"]
        
        return user_id_or_email
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Routes
@router.post("", response_model=Session)
async def create_session(
    session: SessionCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new session"""
    try:
        logger.info(f"Creating new session with title: {session.title}")
        
        # Get session service
        session_service = get_session_service()
        
        # Prepare session data for creation
        session_data = {
            "userId": current_user_id,
            "title": session.title,
            "description": session.description or "",
            "transcript": session.transcript or "",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "status": "pending",
            "analysis_status": "pending"
        }
        
        # Create session using the real service
        session_id = session_service.create_session(session_data)
        
        if not session_id:
            logger.error("Failed to create session in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session in database"
            )
        
        logger.info(f"Successfully created session with ID: {session_id}")
        
        # Return the created session in the correct format
        return {
            "id": session_id,
            "title": session.title,
            "description": session.description or "",
            "transcript": session.transcript or "",
            "user_id": current_user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "pending",
            "analysis_status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("", response_model=List[Session])
async def get_sessions(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all sessions for the current user"""
    try:
        # Get session service
        session_service = get_session_service()
        
        # Get sessions from database
        sessions = session_service.get_user_sessions(current_user_id)
        
        # Convert to response format
        result = []
        for session_data in sessions:
            result.append({
                "id": session_data.get("id"),
                "title": session_data.get("title", ""),
                "description": session_data.get("description", ""),
                "transcript": session_data.get("transcript", ""),
                "user_id": session_data.get("userId", current_user_id),
                "created_at": datetime.fromisoformat(session_data.get("created_at", datetime.now().isoformat())),
                "updated_at": datetime.fromisoformat(session_data.get("updated_at", datetime.now().isoformat())),
                "status": session_data.get("status", "pending"),
                "analysis_status": session_data.get("analysis_status", "pending")
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a specific session by ID"""
    try:
        logger.info(f"Getting session {session_id}")
        
        # Get session service
        session_service = get_session_service()
        
        # Get session from database
        session_data = session_service.get_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Check if user owns this session
        if session_data.get("userId") != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Return session data
        return {
            "id": session_data.get("id"),
            "title": session_data.get("title", ""),
            "description": session_data.get("description", ""),
            "transcript": session_data.get("transcript", ""),
            "user_id": session_data.get("userId", ""),
            "created_at": datetime.fromisoformat(session_data.get("created_at", datetime.now().isoformat())),
            "updated_at": datetime.fromisoformat(session_data.get("updated_at", datetime.now().isoformat())),
            "status": session_data.get("status", "pending"),
            "analysis_status": session_data.get("analysis_status", "pending")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete a session"""
    try:
        logger.info(f"Deleting session {session_id}")
        
        # Get session service
        session_service = get_session_service()
        
        # Get session from database to verify it exists and user owns it
        session_data = session_service.get_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Check if user owns this session
        if session_data.get("userId") != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete the session
        session_service.delete_session(session_id, current_user_id)
        
        logger.info(f"Successfully deleted session {session_id}")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 