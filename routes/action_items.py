"""
Action Items routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from services import get_neo4j_service, get_action_item_service, get_auth_service
import jwt

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class ActionItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: str
    priority: Optional[str] = "medium"
    status: Optional[str] = "not_started"
    topic: Optional[str] = None

class ActionItemCreate(ActionItemBase):
    pass

class ActionItem(ActionItemBase):
    id: str
    session_id: Optional[str] = None
    session_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

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
@router.get("/action-items")
async def get_all_user_action_items(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all action items for the current user across all sessions"""
    try:
        action_item_service = get_action_item_service()
        action_items = action_item_service.get_all_user_action_items(current_user_id)
        return {"actionItems": action_items}
    except Exception as e:
        logger.error(f"Error getting user action items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/sessions/{session_id}/action-items", response_model=ActionItem)
async def create_action_item(
    session_id: str,
    action_item: ActionItemCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new action item for a session"""
    try:
        action_item_service = get_action_item_service()
        data = action_item.dict()
        result = action_item_service.create_action_item(session_id, data)
        return result
    except Exception as e:
        logger.error(f"Error creating action item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/sessions/{session_id}/action-items")
async def get_action_items(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all action items for a session"""
    try:
        action_item_service = get_action_item_service()
        action_items = action_item_service.get_action_items(session_id)
        return {"actionItems": action_items}
    except Exception as e:
        logger.error(f"Error getting action items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/sessions/{session_id}/action-items/{action_item_id}", response_model=ActionItem)
async def update_action_item(
    session_id: str,
    action_item_id: str,
    data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id)
):
    """Update an action item"""
    try:
        action_item_service = get_action_item_service()
        result = action_item_service.update_action_item(session_id, action_item_id, data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action item not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating action item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/sessions/{session_id}/action-items/{action_item_id}")
async def delete_action_item(
    session_id: str,
    action_item_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete an action item"""
    try:
        action_item_service = get_action_item_service()
        success = action_item_service.delete_action_item(session_id, action_item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action item not found"
            )
        return {"message": "Action item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting action item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 