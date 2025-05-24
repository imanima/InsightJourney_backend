"""
Session Service Module

This module provides a service layer for working with session data.
It interfaces with the Neo4j service to perform database operations.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import uuid
from .neo4j_service import Neo4jService
from .errors import (
    ServiceError, SessionError, ValidationError, 
    DatabaseError, NotFoundError, handle_error
)

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing session data and operations"""
    
    def __init__(self, neo4j_service: Neo4jService):
        """Initialize the session service"""
        self.neo4j_service = neo4j_service
        self.logger = logging.getLogger(__name__)
        
    def _validate_session_data(self, session_data: Dict[str, Any]) -> None:
        """Validate session data before processing."""
        if not session_data:
            raise ValidationError("Session data is required", "MISSING_DATA")
            
        required_fields = ['userId', 'title', 'date']
        missing_fields = [field for field in required_fields if not session_data.get(field)]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                "MISSING_FIELDS",
                {"missing_fields": missing_fields}
            )
            
        # Validate date format
        try:
            datetime.strptime(session_data['date'], '%Y-%m-%d')
        except ValueError:
            raise ValidationError(
                "Invalid date format. Expected YYYY-MM-DD",
                "INVALID_DATE_FORMAT"
            )
        
    def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new session"""
        return self.neo4j_service.create_session(session_data)
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data"""
        return self.neo4j_service.get_session_data(session_id)
    
    def get_session_with_relationships(self, session_id: str) -> Dict[str, Any]:
        """Get session data with all relationships"""
        return self.neo4j_service.get_session_with_relationships(session_id)
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update an existing session"""
        return self.neo4j_service.update_session(session_id, session_data)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        return self.neo4j_service.delete_session(session_id)
    
    def add_emotion(self, session_id: str, emotion_data: Dict[str, Any]) -> str:
        """Add an emotion to a session"""
        try:
            self.logger.debug(f"Adding emotion to session {session_id}: {emotion_data}")
            result = self.neo4j_service.add_emotion_to_session(session_id, emotion_data)
            self.logger.debug(f"Result from add_emotion_to_session: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error adding emotion: {str(e)}", exc_info=True)
            return None
    
    def add_topic(self, session_id: str, topic_data: Dict[str, Any]) -> str:
        """Add a topic to the database (but not directly to the session)"""
        try:
            # Create a topic node without relating it to the session
            topic_name = topic_data.get('name')
            if not topic_name:
                self.logger.error("Topic name is required")
                return None
                
            with self.neo4j_service.driver.session() as session:
                # Ensure the topic exists
                topic_id = self.neo4j_service._generate_id("T")
                result = session.run("""
                    MERGE (t:Topic {name: $topic_name})
                    ON CREATE SET t.id = $topic_id, 
                                  t.description = $description,
                                  t.created_at = $timestamp,
                                  t.updated_at = $timestamp
                    ON MATCH SET t.updated_at = $timestamp
                    RETURN t.id
                """, 
                topic_name=topic_name,
                topic_id=topic_id,
                description=topic_data.get('description', ''),
                timestamp=topic_data.get('timestamp', self.neo4j_service._ensure_timestamps({})['created_at'])
                )
                
                record = result.single()
                if record:
                    return record["t.id"]
                return None
        except Exception as e:
            self.logger.error(f"Error adding topic: {str(e)}")
            return None
    
    def add_insight(self, session_id: str, insight_data: Dict[str, Any]) -> str:
        """Add an insight to a session"""
        try:
            self.logger.debug(f"Adding insight to session {session_id}: {insight_data}")
            result = self.neo4j_service.add_insight_to_session(session_id, insight_data)
            self.logger.debug(f"Result from add_insight_to_session: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error adding insight: {str(e)}", exc_info=True)
            return None
    
    def add_belief(self, session_id: str, belief_data: Dict[str, Any]) -> str:
        """Add a belief to a session"""
        try:
            self.logger.debug(f"Adding belief to session {session_id}: {belief_data}")
            result = self.neo4j_service.add_belief_to_session(session_id, belief_data)
            self.logger.debug(f"Result from add_belief_to_session: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error adding belief: {str(e)}", exc_info=True)
            return None
    
    def add_challenge(self, session_id: str, challenge_data: Dict[str, Any]) -> str:
        """Add a challenge to a session"""
        try:
            self.logger.debug(f"Adding challenge to session {session_id}: {challenge_data}")
            result = self.neo4j_service.add_challenge_to_session(session_id, challenge_data)
            self.logger.debug(f"Result from add_challenge_to_session: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error adding challenge: {str(e)}", exc_info=True)
            return None
    
    def add_action_item(self, session_id: str, action_data: Dict[str, Any]) -> str:
        """Add an action item to a session"""
        try:
            self.logger.debug(f"Adding action item to session {session_id}: {action_data}")
            result = self.neo4j_service.add_action_item_to_session(session_id, action_data)
            self.logger.debug(f"Result from add_action_item_to_session: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error adding action item: {str(e)}", exc_info=True)
            return None

    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        try:
            return self.neo4j_service.get_user_sessions(user_id)
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            return []

    def add_session_elements(self, session_id: str, elements: Dict[str, Any]) -> None:
        """Add elements (emotions, topics, etc.) to an existing session."""
        try:
            # Validate session exists
            if not self.neo4j_service.get_session_data(session_id):
                raise NotFoundError(
                    f"Session {session_id} not found",
                    "SESSION_NOT_FOUND"
                )
                
            # Validate elements
            if not elements:
                raise ValidationError(
                    "No elements provided to add",
                    "MISSING_ELEMENTS"
                )
                
            # Add each element type with error handling
            for element_type, items in elements.items():
                if not items:
                    continue
                    
                try:
                    for item in items:
                        if element_type == 'emotions':
                            self.neo4j_service.add_emotion_to_session(session_id, item)
                        elif element_type == 'topics':
                            self.add_topic(session_id, item)
                        elif element_type == 'insights':
                            self.neo4j_service.add_insight_to_session(session_id, item)
                        elif element_type == 'action_items':
                            self.neo4j_service.add_action_item_to_session(session_id, item)
                except Exception as e:
                    logger.error(f"Error adding {element_type} to session {session_id}: {str(e)}")
                    raise SessionError(
                        f"Failed to add {element_type} to session",
                        "ELEMENT_ADD_ERROR",
                        {
                            "element_type": element_type,
                            "original_error": str(e)
                        }
                    )
                    
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding elements to session {session_id}: {str(e)}")
            raise SessionError(
                "Failed to add elements to session",
                "SESSION_UPDATE_ERROR",
                {"original_error": str(e)}
            )
            
    def delete_session(self, session_id: str, user_id: str) -> None:
        """Delete a session and all its elements."""
        try:
            # Verify session exists and belongs to user
            session_data = self.neo4j_service.get_session_data(session_id)
            if not session_data:
                raise NotFoundError(
                    f"Session {session_id} not found",
                    "SESSION_NOT_FOUND"
                )
                
            if session_data.get('userId') != user_id:
                raise ValidationError(
                    "Session does not belong to user",
                    "UNAUTHORIZED_ACCESS"
                )
                
            # Delete session
            try:
                self.neo4j_service.delete_session(session_id)
                logger.info(f"Successfully deleted session {session_id}")
            except Exception as e:
                logger.error(f"Database error deleting session {session_id}: {str(e)}")
                raise DatabaseError(
                    "Failed to delete session from database",
                    "DB_DELETE_ERROR",
                    {"original_error": str(e)}
                )
                
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting session {session_id}: {str(e)}")
            raise SessionError(
                "Failed to delete session",
                "SESSION_DELETE_ERROR",
                {"original_error": str(e)}
            ) 