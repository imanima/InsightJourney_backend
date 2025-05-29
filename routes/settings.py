"""
Settings routes for the FastAPI application.
Provides user settings and admin settings management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from services import get_neo4j_service, get_auth_service
import jwt

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/settings")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for settings
class UserSettings(BaseModel):
    notifications: Optional[bool] = True
    dark_mode: Optional[bool] = False
    reminder_frequency: Optional[str] = "weekly"
    privacy_mode: Optional[bool] = False
    max_sessions: Optional[int] = 10
    max_duration: Optional[int] = 3600
    allowed_file_types: Optional[List[str]] = ["mp3", "wav", "m4a", "txt"]
    gpt_model: Optional[str] = "gpt-4.1-mini"
    transcription_model: Optional[str] = "gpt-4o-transcribe"
    max_tokens: Optional[int] = 1500
    temperature: Optional[float] = 0.7
    system_prompt_template: Optional[str] = None
    analysis_prompt_template: Optional[str] = None
    home_page_version: Optional[str] = "empowerment"  # "empowerment" or "therapy"

class AdminSettings(BaseModel):
    gpt_model: Optional[str] = "gpt-4"
    transcription_model: Optional[str] = "gpt-4o-transcribe"
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7
    system_prompt_template: Optional[str] = None
    analysis_prompt_template: Optional[str] = None
    available_topics: Optional[List[str]] = None
    analysis_elements: Optional[List[Dict[str, Any]]] = None
    max_sessions: Optional[int] = 50
    max_duration: Optional[int] = 7200
    allowed_file_types: Optional[List[str]] = ["mp3", "wav", "m4a", "txt", "pdf"]

class AnalysisElement(BaseModel):
    name: str
    enabled: bool = True
    description: Optional[str] = ""
    system_instructions: Optional[str] = ""
    analysis_instructions: Optional[str] = ""
    categories: Optional[List[str]] = []
    format_template: Optional[str] = ""
    prompt_template: Optional[str] = ""
    requires_topic: Optional[bool] = True
    requires_timestamp: Optional[bool] = True
    additional_fields: Optional[List[str]] = []

# Helper function to get current user ID from token
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Extract user ID from JWT token"""
    try:
        auth_service = get_auth_service()
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Helper function to check admin privileges
async def get_current_admin_user(current_user_id: str = Depends(get_current_user_id)) -> str:
    """Verify user has admin privileges"""
    try:
        neo4j_service = get_neo4j_service()
        user = neo4j_service.get_user_by_id(current_user_id)
        
        if not user or not user.get('is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return current_user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin privileges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying admin privileges"
        )

# User Settings Routes
@router.get("/user", response_model=UserSettings)
async def get_user_settings(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current user's settings"""
    try:
        neo4j_service = get_neo4j_service()
        settings = neo4j_service.get_user_settings(current_user_id)
        
        if not settings:
            # Return default settings if none exist
            return UserSettings()
        
        # Map Neo4j settings to our model
        return UserSettings(
            notifications=settings.get('notifications', True),
            dark_mode=settings.get('dark_mode', False),
            reminder_frequency=settings.get('reminder_frequency', 'weekly'),
            privacy_mode=settings.get('privacy_mode', False),
            max_sessions=settings.get('max_sessions', 10),
            max_duration=settings.get('max_duration', 3600),
            allowed_file_types=settings.get('allowed_file_types', ["mp3", "wav", "m4a", "txt"]),
            gpt_model=settings.get('gpt_model', 'gpt-4.1-mini'),
            transcription_model=settings.get('transcription_model', 'gpt-4o-transcribe'),
            max_tokens=settings.get('max_tokens', 1500),
            temperature=settings.get('temperature', 0.7),
            system_prompt_template=settings.get('system_prompt_template'),
            analysis_prompt_template=settings.get('analysis_prompt_template'),
            home_page_version=settings.get('home_page_version', 'empowerment')
        )
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user settings"
        )

@router.put("/user")
async def update_user_settings(
    settings: UserSettings,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user's settings"""
    try:
        neo4j_service = get_neo4j_service()
        
        # Convert Pydantic model to dict, excluding None values
        settings_dict = settings.dict(exclude_none=True)
        
        # Save settings to Neo4j
        success = neo4j_service.save_user_settings(current_user_id, settings_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user settings"
            )
        
        return {"message": "Settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings"
        )

# Admin Settings Routes
@router.get("/admin", response_model=AdminSettings)
async def get_admin_settings(
    current_admin_id: str = Depends(get_current_admin_user)
):
    """Get admin settings (admin only)"""
    try:
        neo4j_service = get_neo4j_service()
        settings = neo4j_service.get_user_settings(current_admin_id)
        
        if not settings:
            # Return default admin settings
            return AdminSettings()
        
        # Map Neo4j settings to admin model
        return AdminSettings(
            gpt_model=settings.get('gpt_model', 'gpt-4'),
            transcription_model=settings.get('transcription_model', 'gpt-4o-transcribe'),
            max_tokens=settings.get('max_tokens', 2000),
            temperature=settings.get('temperature', 0.7),
            system_prompt_template=settings.get('system_prompt_template'),
            analysis_prompt_template=settings.get('analysis_prompt_template'),
            available_topics=settings.get('available_topics', [
                "Work", "Relationships", "Health", "Family", "Personal Growth", "Other"
            ]),
            analysis_elements=settings.get('analysis_elements', []),
            max_sessions=settings.get('max_sessions', 50),
            max_duration=settings.get('max_duration', 7200),
            allowed_file_types=settings.get('allowed_file_types', ["mp3", "wav", "m4a", "txt", "pdf"])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get admin settings"
        )

@router.put("/admin")
async def update_admin_settings(
    settings: AdminSettings,
    current_admin_id: str = Depends(get_current_admin_user)
):
    """Update admin settings (admin only)"""
    try:
        neo4j_service = get_neo4j_service()
        
        # Convert Pydantic model to dict, excluding None values
        settings_dict = settings.dict(exclude_none=True)
        
        # Validate settings data
        if "max_sessions" in settings_dict and not isinstance(settings_dict["max_sessions"], int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_sessions must be an integer"
            )
        if "max_duration" in settings_dict and not isinstance(settings_dict["max_duration"], int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_duration must be an integer"
            )
        if "allowed_file_types" in settings_dict and not isinstance(settings_dict["allowed_file_types"], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="allowed_file_types must be a list"
            )
        if "analysis_elements" in settings_dict and not isinstance(settings_dict["analysis_elements"], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="analysis_elements must be a list"
            )
        
        # Save settings to Neo4j
        success = neo4j_service.save_user_settings(current_admin_id, settings_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save admin settings"
            )
        
        logger.info("Admin settings updated successfully")
        return {"message": "Admin settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating admin settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update admin settings"
        )

# Admin User Management Routes
@router.get("/admin/users")
async def get_all_users(
    current_admin_id: str = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    try:
        neo4j_service = get_neo4j_service()
        
        # Get all users from Neo4j
        with neo4j_service.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                RETURN u.userId AS id, u.email AS email, u.name AS name, 
                       u.is_admin AS is_admin, u.created_at AS created_at,
                       u.last_login AS last_login
                ORDER BY u.created_at DESC
                """
            )
            users = [dict(record) for record in result]
        
        # Fetch home_page_version for each user from their settings
        for user in users:
            user_settings = neo4j_service.get_user_settings(user['id'])
            user['home_page_version'] = user_settings.get('home_page_version', 'empowerment') if user_settings else 'empowerment'
        
        return {"users": users}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: Dict[str, Any],
    current_admin_id: str = Depends(get_current_admin_user)
):
    """Update user information (admin only)"""
    try:
        neo4j_service = get_neo4j_service()
        
        # Get current user
        user = neo4j_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Handle home_page_version separately as it goes to user settings
        if 'home_page_version' in user_data:
            home_page_version = user_data.pop('home_page_version')
            
            # Get current settings
            current_settings = neo4j_service.get_user_settings(user_id) or {}
            
            # Update home page version
            current_settings['home_page_version'] = home_page_version
            
            # Save updated settings
            settings_success = neo4j_service.save_user_settings(user_id, current_settings)
            
            if not settings_success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user home page version"
                )
        
        # Only allow updating certain user profile fields
        allowed_fields = ['is_admin', 'disabled']
        update_data = {k: v for k, v in user_data.items() if k in allowed_fields}
        
        # Update user properties if there are any valid fields
        if update_data:
            result = neo4j_service.update_user(user_id, update_data)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user"
                )
        
        return {"message": "User updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.put("/admin/users/{user_id}/home-page-version")
async def update_user_home_page_version(
    user_id: str,
    version_data: Dict[str, str],
    current_admin_id: str = Depends(get_current_admin_user)
):
    """Update a user's home page version (admin only)"""
    try:
        version = version_data.get('home_page_version')
        if version not in ['empowerment', 'therapy']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid home page version. Must be 'empowerment' or 'therapy'"
            )
        
        neo4j_service = get_neo4j_service()
        
        # Check if user exists
        user = neo4j_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get current settings
        current_settings = neo4j_service.get_user_settings(user_id) or {}
        
        # Update home page version
        current_settings['home_page_version'] = version
        
        # Save updated settings
        success = neo4j_service.save_user_settings(user_id, current_settings)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user home page version"
            )
        
        return {
            "message": "User home page version updated successfully",
            "user_id": user_id,
            "home_page_version": version
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user home page version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user home page version"
        )

# Admin Statistics Route
@router.get("/admin/stats")
async def get_admin_stats(
    current_admin_id: str = Depends(get_current_admin_user)
):
    """Get admin statistics (admin only)"""
    try:
        neo4j_service = get_neo4j_service()
        
        # Get admin users
        admin_users = neo4j_service.get_admin_users()
        
        # Get all statistics from Neo4j
        with neo4j_service.driver.session() as session:
            # Get user count
            result = session.run("MATCH (u:User) RETURN count(u) AS count")
            total_users = result.single()["count"]
            
            # Get session count
            result = session.run("MATCH (s:Session) RETURN count(s) AS count")
            total_sessions = result.single()["count"]
            
            # Get recent users
            result = session.run(
                """
                MATCH (u:User)
                RETURN u.userId AS id, u.email AS email, u.name AS name, 
                       u.created_at AS created_at, u.last_login AS last_login
                ORDER BY u.created_at DESC LIMIT 5
                """
            )
            recent_users = [dict(record) for record in result]
            
            # Get recent sessions
            result = session.run(
                """
                MATCH (s:Session)
                RETURN s.id AS id, s.title AS title, s.userId AS user_id,
                       s.created_at AS created_at
                ORDER BY s.created_at DESC LIMIT 5
                """
            )
            recent_sessions = [dict(record) for record in result]
            
            # Get most active users
            result = session.run(
                """
                MATCH (u:User {userId: s.userId}), (s:Session)
                WITH u, count(s) AS session_count
                WHERE session_count > 0
                RETURN u.userId AS id, u.email AS email, u.name AS name,
                       session_count
                ORDER BY session_count DESC LIMIT 5
                """
            )
            active_users = [dict(record) for record in result]
        
        logger.info("Admin statistics retrieved successfully")
        return {
            "stats": {
                "total_users": total_users,
                "total_sessions": total_sessions,
                "admin_users": admin_users,
                "recent_users": recent_users,
                "recent_sessions": recent_sessions,
                "active_users": active_users
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get admin statistics"
        )

# Default Prompt Template Route
@router.get("/default-prompt")
async def get_default_prompt_template(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the default analysis prompt template"""
    try:
        # Import here to avoid circular imports
        from services.analysis_service import PROMPT_TEMPLATE, VALID_EMOTIONS, VALID_TOPICS
        
        return {
            "analysis_prompt_template": PROMPT_TEMPLATE,
            "valid_emotions": VALID_EMOTIONS,
            "valid_topics": VALID_TOPICS,
            "description": "Default prompt template used for analyzing therapy session transcripts"
        }
    except Exception as e:
        logger.error(f"Error getting default prompt template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get default prompt template"
        )

# Add OPTIONS handler for CORS preflight requests
@router.options("/user")
@router.options("/admin")
@router.options("/admin/users")
@router.options("/admin/users/{user_id}")
@router.options("/admin/users/{user_id}/home-page-version")
@router.options("/admin/stats")
@router.options("/default-prompt")
async def options_handler():
    """Handle CORS preflight requests"""
    return {"message": "OK"} 