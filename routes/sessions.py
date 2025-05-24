"""
Sessions routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from services import get_neo4j_service

# Configure logger
logger = logging.getLogger(__name__)

# Create router with prefix to avoid conflicts with health endpoint
router = APIRouter(prefix="/sessions")

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

# Routes
@router.post("", response_model=Session)
async def create_session(
    session: SessionCreate
):
    """Create a new session"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Mock session creation
        return {
            "id": "test_session_id",
            "title": session.title,
            "description": session.description,
            "transcript": session.transcript,
            "user_id": "test_user_id",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "pending",
            "analysis_status": None
        }
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("", response_model=List[Session])
async def get_sessions():
    """Get all sessions for the current user"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Return mock sessions
        return [
            {
                "id": "test_session_id",
                "title": "Test Session",
                "description": "A test session",
                "transcript": "Sample transcript text",
                "user_id": "test_user_id",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": "completed",
                "analysis_status": "completed"
            }
        ]
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str
):
    """Get a specific session by ID"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Return mock session
        return {
            "id": session_id,
            "title": "Test Session",
            "description": "A test session",
            "transcript": "Sample transcript text",
            "user_id": "test_user_id",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "completed",
            "analysis_status": "completed"
        }
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 