"""
Neo4j Service Module

This module provides a service layer for interacting with the Neo4j graph database.
It handles all database operations for the Insight Journey application.
"""

from neo4j import GraphDatabase
import uuid
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List
import time
from neo4j.exceptions import ClientError, ServiceUnavailable, AuthError, SessionExpired
import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from .errors import (
    ServiceError, DatabaseError, ValidationError,
    NotFoundError, handle_error
)

# Configure logger
logger = logging.getLogger(__name__)

class Neo4jService:
    """Service for managing Neo4j database operations"""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j service"""
        self.logger = logging.getLogger(__name__)
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self._ensure_driver()
    
    async def initialize(self):
        """Initialize the Neo4j driver (kept for backwards compatibility)"""
        self._ensure_driver()
        self.logger.info("Neo4j driver initialized via compatible method")
    
    async def close(self):
        """Close the Neo4j driver (kept for backwards compatibility)"""
        if self.driver:
            self.driver.close()
            self.driver = None
    
    async def check_connection(self) -> bool:
        """Check if the connection to Neo4j is working"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                return bool(result.single())
        except Exception as e:
            self.logger.error(f"Connection check failed: {str(e)}")
            return False
    
    def _ensure_driver(self):
        """Ensure the driver is initialized"""
        if self.driver is None:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password)
                )
                self.logger.info("Neo4j driver initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Neo4j driver: {str(e)}")
                raise
    
    def get_version(self) -> str:
        """Get the Neo4j server version"""
        try:
            server_info = self.driver.get_server_info()
            return server_info.agent
        except Exception as e:
            self.logger.error(f"Failed to get Neo4j version: {str(e)}")
            return "unknown"
    
    #######################
    # Utility Methods
    #######################

    def _handle_error(self, error: Exception, operation: str) -> None:
        """Handle Neo4j errors consistently"""
        self.logger.error(f"Error during {operation}: {str(error)}")
        if isinstance(error, ServiceUnavailable):
            raise DatabaseError("Database service unavailable")
        elif isinstance(error, AuthError):
            raise DatabaseError("Authentication failed")
        else:
            raise DatabaseError(f"Database operation failed: {str(error)}")

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID for nodes"""
        return f"{prefix}_{str(uuid.uuid4())}"

    def _ensure_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure created_at and updated_at timestamps are present"""
        now = datetime.now().isoformat()
        if 'created_at' not in data:
            data['created_at'] = now
        if 'updated_at' not in data:
            data['updated_at'] = now
        return data
        
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    #######################
    # User Management
    #######################

    def create_user(self, email: str, password_hash: str, name: str = "", is_admin: bool = False, original_email: str = None) -> str:
        """Create a new user node with hashed data and a separate EmailLookup node for authentication"""
        try:
            # Generate a UUID for the user
            user_id = f"U_{uuid.uuid4()}"
            
            # Create timestamp
            created_at = self._get_timestamp()
            
            # If original_email is not provided, assume email is already hashed
            email_for_lookup = original_email if original_email else email
                
            # Create user node with hashed data and separate email lookup
            with self.driver.session() as session:
                # The transaction ensures both the User and EmailLookup nodes are created atomically
                result = session.execute_write(self._create_user_tx, 
                                              user_id=user_id,
                                              email=email,  # This is the hashed email
                                              password_hash=password_hash,
                                              name=name,
                                              is_admin=is_admin,
                                              created_at=created_at,
                                              original_email=email_for_lookup)  # Original email for lookup
                
                return user_id
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
            
    def _create_user_tx(self, tx, user_id, email, password_hash, name, is_admin, created_at, original_email):
        """Transaction function to create a user and email lookup in a single atomic operation"""
        # Create the user with anonymized data
        tx.run("""
            CREATE (u:User {
                userId: $userId,
                email: $email,
                password_hash: $password_hash,
                name: $name,
                is_admin: $is_admin,
                created_at: $created_at,
                last_login: $created_at,
                disabled: false
            })
            RETURN u
        """, userId=user_id, email=email, password_hash=password_hash, 
               name=name, is_admin=is_admin, created_at=created_at)
               
        # Create email lookup for authentication
        tx.run("""
            CREATE (e:EmailLookup {
                email: $email,
                userId: $userId
            })
        """, email=original_email, userId=user_id)
        
        return True

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email address using the EmailLookup node"""
        try:
            with self.driver.session() as session:
                # First find the userId from EmailLookup
                result = session.run("""
                    MATCH (e:EmailLookup {email: $email})
                    RETURN e.userId as userId
                """, email=email)
                
                record = result.single()
                if not record:
                    return None
                    
                user_id = record["userId"]
                
                # Then get the user by ID
                return self.get_user_by_id(user_id)
                
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by their ID"""
        try:
            with self.driver.session() as session:
                # Get user data
                result = session.run(
                    "MATCH (u:User {userId: $userId}) RETURN u",
                    userId=user_id
                )
                record = result.single()
                if not record:
                    return None
                    
                user = record["u"]
                
                # Get original email from EmailLookup if needed for responses
                lookup_result = session.run(
                    "MATCH (e:EmailLookup {userId: $userId}) RETURN e.email as email",
                    userId=user_id
                )
                lookup_record = lookup_result.single()
                display_email = lookup_record["email"] if lookup_record else user["email"]
                
                return {
                    "userId": user["userId"],
                    "name": user["name"],  # This is hashed 
                    "email": display_email,  # Use original for display/API responses
                    "hashed_email": user["email"],  # Keep the hashed version
                    "password_hash": user.get("password_hash"),
                    "is_admin": user.get("is_admin", False),
                    "status": user.get("status", "active"),
                    "disabled": user.get("disabled", False),
                    "last_login": user.get("last_login"),
                    "created_at": user.get("created_at")
                }
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None

    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user attributes"""
        try:
            # Ensure password is hashed if being updated
            if 'password' in kwargs:
                kwargs['password_hash'] = generate_password_hash(kwargs.pop('password'))
            
            # Add updated_at timestamp
            kwargs['updated_at'] = datetime.now().isoformat()
            
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {userId: $user_id})
                    SET u += $updates
                    RETURN u
                """, user_id=user_id, updates=kwargs)
                
                return bool(result.single())
        except Exception as e:
            self._handle_error(e, "update_user")

    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all their associated data"""
        try:
            with self.driver.session() as session:
                # Delete user and all their relationships
                result = session.run("""
                    MATCH (u:User {userId: $user_id})
                    OPTIONAL MATCH (u)-[r]-()
                    DELETE r, u
                    RETURN count(u) as deleted
                """, user_id=user_id)
                
                record = result.single()
                return record and record["deleted"] > 0
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {str(e)}")
            return False

    def save_user_settings(self, user_id: str, settings_data: Dict[str, Any]) -> bool:
        """Save user settings to Neo4j"""
        try:
            with self.driver.session() as session:
                # Check if settings already exist
                result = session.run("""
                    MATCH (u:User {userId: $user_id})-[:HAS_SETTINGS]->(s:UserSettings)
                    RETURN s
                """, user_id=user_id)
                
                record = result.single()
                
                # Update existing settings
                if record:
                    result = session.run("""
                        MATCH (u:User {userId: $user_id})-[:HAS_SETTINGS]->(s:UserSettings)
                        SET s += $settings,
                            s.updated_at = $timestamp
                        RETURN s
                    """, 
                    user_id=user_id,
                    settings=settings_data,
                    timestamp=datetime.now().isoformat())
                # Create new settings
                else:
                    settings_id = self._generate_id("S")
                    result = session.run("""
                        MATCH (u:User {userId: $user_id})
                        CREATE (s:UserSettings {
                            id: $settings_id,
                            created_at: $timestamp,
                            updated_at: $timestamp
                        })
                        SET s += $settings
                        CREATE (u)-[r:HAS_SETTINGS {created_at: $timestamp}]->(s)
                        RETURN s
                    """, 
                    user_id=user_id,
                    settings_id=settings_id,
                    settings=settings_data,
                    timestamp=datetime.now().isoformat())
                
                return bool(result.single())
        except Exception as e:
            self._handle_error(e, "save_user_settings")
            return False

    def get_user_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings from Neo4j"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {userId: $user_id})-[:HAS_SETTINGS]->(s:UserSettings)
                    RETURN s
                """, user_id=user_id)
                
                record = result.single()
                if record:
                    return dict(record["s"])
                return None
        except Exception as e:
            self._handle_error(e, "get_user_settings")
            return None

    def delete_user_settings(self, user_id: str) -> bool:
        """Delete user settings from Neo4j"""
        try:
            with self.driver.session() as session:
                return delete_user_settings(session, user_id)
        except Exception as e:
            self._handle_error(e, "delete_user_settings")
            return False

    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)
                    RETURN s
                    ORDER BY s.created_at DESC
                """, user_id=user_id)
                
                sessions = []
                for record in result:
                    session_data = dict(record["s"])
                    sessions.append(session_data)
                return sessions
        except Exception as e:
            self._handle_error(e, "get_user_sessions")
            return []

    def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {id: $user_id})
                    SET u.last_login = $timestamp
                    RETURN u
                """, user_id=user_id, timestamp=datetime.now().isoformat())
                
                return bool(result.single())
        except Exception as e:
            self._handle_error(e, "update_user_last_login")

    def get_all_users(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all users, optionally including inactive ones"""
        try:
            with self.driver.session() as session:
                query = """
                    MATCH (u:User)
                    WHERE $include_inactive OR u.status = 'active'
                    RETURN u
                    ORDER BY u.created_at DESC
                """
                result = session.run(query, include_inactive=include_inactive)
                return [dict(record["u"]) for record in result]
        except Exception as e:
            self._handle_error(e, "get_all_users")

    def update_user_status(self, user_id: str, status: str) -> bool:
        """Update user status (active/inactive)"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {id: $user_id})
                    SET u.status = $status, u.updated_at = $timestamp
                    RETURN u
                """, user_id=user_id, status=status, timestamp=datetime.now().isoformat())
                
                return bool(result.single())
        except Exception as e:
            self._handle_error(e, "update_user_status")

    #######################
    # Session Management
    #######################

    def create_session(self, data: Dict[str, Any]) -> str:
        """Create a new session based on the provided data"""
        try:
            # Extract user ID from data
            user_id = data.pop('userId', None)
            if not user_id:
                self.logger.error("No user ID provided for session creation")
                return None

            with self.driver.session() as session:
                # 1. Find the current LastSession before creating a new one
                result = session.run("""
                    MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session {isLastSession: true})
                    RETURN s.id as previous_session_id
                """, user_id=user_id)
                
                record = result.single()
                previous_session_id = record["previous_session_id"] if record else None
                
                # 2. Create the new session (this handles LastSession flag update)
                new_session_id = self.create_session_node(user_id, data)
                if not new_session_id:
                    self.logger.error("Failed to create new session")
                    return None
                
                # 3. If there was a previous session, create the NEXT_SESSION relationship
                if previous_session_id:
                    self.logger.info(f"Linking previous session {previous_session_id} to new session {new_session_id}")
                    session.run("""
                        MATCH (prev:Session {id: $prev_id})
                        MATCH (next:Session {id: $next_id})
                        MERGE (prev)-[r:NEXT_SESSION]->(next)
                        ON CREATE SET r.created_at = $timestamp
                    """, 
                    prev_id=previous_session_id,
                    next_id=new_session_id,
                    timestamp=datetime.now().isoformat())
                
                return new_session_id
        except Exception as e:
            self._handle_error(e, "create_session")
            return None

    def create_session_node(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create a new session node"""
        try:
            with self.driver.session() as session:
                # First, find and update the previous LastSession
                session.run("""
                    MATCH (s:Session {isLastSession: true})
                    SET s.isLastSession = false
                """)
                
                # Prepare session data
                session_id = self._generate_id("S")
                session_data = self._ensure_timestamps(session_data)
                
                self.logger.info(f"Creating session node with data: {session_data}")
                
                # Create new session and create HAS_SESSION relationship from User to Session
                result = session.run("""
                    MATCH (u:User {userId: $user_id})
                    CREATE (s:Session {
                        id: $session_id,
                        title: $title,
                        date: $date,
                        description: $description,
                        transcript: $transcript,
                        status: $status,
                        analysis_status: $analysis_status,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        userId: $user_id
                    })
                    CREATE (u)-[r:HAS_SESSION {created_at: $timestamp, updated_at: $timestamp}]->(s)
                    RETURN s.id as session_id
                """, 
                user_id=user_id, 
                session_id=session_id,
                title=session_data.get('title', ''),
                date=session_data.get('date', ''),
                description=session_data.get('description', ''),
                transcript=session_data.get('transcript', ''),
                status=session_data.get('status', 'pending'),
                analysis_status=session_data.get('analysis_status', 'pending'),
                created_at=session_data.get('created_at', ''),
                updated_at=session_data.get('updated_at', ''),
                timestamp=datetime.now().isoformat()
                )
                
                record = result.single()
                if record:
                    self.logger.info(f"Successfully created session node with ID: {record['session_id']}")
                    return record["session_id"]
                else:
                    self.logger.error(f"Failed to create session node for user {user_id}")
                    return None
        except Exception as e:
            self.logger.error(f"Error in create_session_node: {str(e)}")
            self._handle_error(e, "create_session_node")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its relationships"""
        try:
            with self.driver.session() as session:
                # Find the previous session to update its LastSession flag
                session.run("""
                    MATCH (s:Session {id: $session_id})
                    WITH s
                    MATCH (prev:Session)
                    WHERE prev.created_at < s.created_at
                    WITH prev
                    ORDER BY prev.created_at DESC
                    LIMIT 1
                    SET prev.isLastSession = true
                """, session_id=session_id)
                
                # Delete the session and all related nodes
                session.run("""
                    MATCH (s:Session {id: $session_id})
                    OPTIONAL MATCH (s)-[r]->(n)
                    DELETE r, n, s
                """, session_id=session_id)
                
                return True
        except Exception as e:
            self._handle_error(e, "delete_session")
            return False

    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data from Neo4j"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    RETURN s {
                        .id,
                        .title,
                        .date,
                        .description,
                        .duration,
                        .status,
                        .analysis_status,
                        .transcript,
                        .userId,
                        .created_at,
                        .updated_at
                    } as session
                """, session_id=session_id)
                
                record = result.single()
                if record:
                    return record['session']
                    return None
                
        except Exception as e:
            self.logger.error(f"Error getting session data: {str(e)}")
            return None

    def get_session_with_relationships(self, session_id: str) -> Dict[str, Any]:
        """Get a session with all its relationships and elements"""
        try:
            with self.driver.session() as session:
                # Enhanced query to get all session elements with their related topics
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    
                    // Get all emotions and their topics
                    OPTIONAL MATCH (s)-[re:HAS_EMOTION]->(e:Emotion)
                    OPTIONAL MATCH (e)-[ret:RELATED_TO]->(et:Topic)
                    
                    // Get all insights and their topics
                    OPTIONAL MATCH (s)-[ri:HAS_INSIGHT]->(i:Insight)
                    OPTIONAL MATCH (i)-[rit:RELATED_TO]->(it:Topic)
                    
                    // Get all beliefs and their topics
                    OPTIONAL MATCH (s)-[rb:HAS_BELIEF]->(b:Belief)
                    OPTIONAL MATCH (b)-[rbt:RELATED_TO]->(bt:Topic)
                    
                    // Get all challenges and their topics
                    OPTIONAL MATCH (s)-[rc:HAS_CHALLENGE]->(c:Challenge)
                    OPTIONAL MATCH (c)-[rct:RELATED_TO]->(ct:Topic)
                    
                    // Get all action items and their topics
                    OPTIONAL MATCH (s)-[ra:HAS_ACTION_ITEM]->(a:ActionItem)
                    OPTIONAL MATCH (a)-[rat:RELATED_TO]->(at:Topic)
                    
                    // Adjacent sessions in sequence
                    OPTIONAL MATCH (prev:Session)-[:NEXT_SESSION]->(s)
                    OPTIONAL MATCH (s)-[:NEXT_SESSION]->(next:Session)
                    
                    // Return everything
                    RETURN 
                        s,
                        collect(DISTINCT {
                            emotion: e, 
                            relationship: re,
                            topic: et, 
                            topic_relationship: ret
                        }) as emotions,
                        
                        collect(DISTINCT {
                            insight: i, 
                            relationship: ri,
                            topic: it, 
                            topic_relationship: rit
                        }) as insights,
                        
                        collect(DISTINCT {
                            belief: b, 
                            relationship: rb,
                            topic: bt, 
                            topic_relationship: rbt
                        }) as beliefs,
                        
                        collect(DISTINCT {
                            challenge: c, 
                            relationship: rc,
                            topic: ct, 
                            topic_relationship: rct
                        }) as challenges,
                        
                        collect(DISTINCT {
                            action_item: a, 
                            relationship: ra,
                            topic: at, 
                            topic_relationship: rat
                        }) as action_items,
                        
                        prev,
                        next
                """, session_id=session_id)
                
                record = result.single()
                if not record:
                    return None
                
                session_data = dict(record["s"])
                
                # Process adjacent sessions
                if record["prev"]:
                    session_data["previous_session"] = {
                        "id": record["prev"]["id"],
                        "title": record["prev"].get("title", ""),
                        "date": record["prev"].get("date", "")
                    }
                
                if record["next"]:
                    session_data["next_session"] = {
                        "id": record["next"]["id"],
                        "title": record["next"].get("title", ""),
                        "date": record["next"].get("date", "")
                    }
                
                # Process elements and their topics
                session_data["emotions"] = self._process_elements_with_topics(record["emotions"], "emotion")
                session_data["insights"] = self._process_elements_with_topics(record["insights"], "insight")
                session_data["beliefs"] = self._process_elements_with_topics(record["beliefs"], "belief")
                session_data["challenges"] = self._process_elements_with_topics(record["challenges"], "challenge")
                session_data["actionitems"] = self._process_elements_with_topics(record["action_items"], "action_item")
                
                # Collect all unique topics
                all_topics = set()
                
                for element_type in ["emotions", "insights", "beliefs", "challenges", "actionitems"]:
                    for item in session_data[element_type]:
                        if "topic" in item and item["topic"]:
                            topic_tuple = tuple(sorted(item["topic"].items()))
                            all_topics.add(topic_tuple)
                
                session_data["topics"] = [dict(t) for t in all_topics]
                
                return session_data
        except Exception as e:
            self._handle_error(e, "get_session_with_relationships")
    
    def _process_elements_with_topics(self, elements_data, element_type):
        """Process element data with topics from query results"""
        results = []
        
        for item in elements_data:
            element = item.get(element_type)
            if not element:
                continue
                
            # Create element dictionary with properties
            element_dict = dict(element)
            
            # Add relationship properties
            rel = item.get("relationship")
            if rel:
                for key, value in dict(rel).items():
                    if key not in ["created_at", "updated_at"] and key not in element_dict:
                        element_dict[key] = value
            
            # Add topic if present
            topic = item.get("topic")
            if topic:
                topic_dict = dict(topic)
                
                # Add topic relationship properties if useful
                topic_rel = item.get("topic_relationship")
                if topic_rel:
                    topic_rel_dict = dict(topic_rel)
                    if "relevance" in topic_rel_dict:
                        topic_dict["relevance"] = topic_rel_dict["relevance"]
                
                element_dict["topic"] = topic_dict
            
            results.append(element_dict)
        
        return results

    #######################
    # Element Management
    #######################

    def add_emotion_to_session(self, session_id: str, emotion_data: Dict[str, Any]) -> str:
        """Add an emotion to a session"""
        try:
            with self.driver.session() as session:
                # Extract topics and session-specific data from emotion data
                topics = emotion_data.pop('topics', []) if 'topics' in emotion_data else []
                intensity = emotion_data.pop('intensity', 0)
                context = emotion_data.pop('context', '')
                timestamp = emotion_data.pop('timestamp', None)
                
                # Prepare emotion data - keep only generic properties on the node
                emotion_id = self._generate_id("E")
                emotion_data = self._ensure_timestamps(emotion_data)
                emotion_data.update({
                    'id': emotion_id,
                    'name': emotion_data.get('name'),
                    'user_id': emotion_data.get('user_id')
                })
                
                # Create emotion node and relationship
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    MERGE (e:Emotion {name: $name, user_id: $user_id})
                    ON CREATE SET e.id = $id, e.created_at = $created_at, e.updated_at = $updated_at
                    ON MATCH SET e.updated_at = $updated_at
                    CREATE (s)-[r:HAS_EMOTION {
                        intensity: $intensity,
                        context: $context,
                        timestamp: $timestamp,
                        confidence: $confidence,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        modified_by: $modified_by
                    }]->(e)
                    RETURN e.id
                """,
                session_id=session_id,
                name=emotion_data['name'],
                user_id=emotion_data.get('user_id'),
                id=emotion_id,
                intensity=intensity,
                context=context,
                timestamp=timestamp,
                confidence=emotion_data.get('confidence', 0),
                created_at=emotion_data['created_at'],
                updated_at=emotion_data['updated_at'],
                modified_by=emotion_data.get('modified_by', 'system'))
                
                emotion_id = result.single()["e.id"]
                
                # Create topic relationships if topics provided
                for topic_name in topics:
                    self._create_topic_relationship(emotion_id, topic_name, 'emotion')
                
                return emotion_id
        except Exception as e:
            self._handle_error(e, "add_emotion_to_session")

    def add_insight_to_session(self, session_id: str, insight_data: Dict[str, Any]) -> str:
        """Add an insight to a session"""
        try:
            with self.driver.session() as session:
                # Extract topics and session-specific data from insight data
                topics = insight_data.pop('topics', []) if 'topics' in insight_data else []
                context = insight_data.pop('context', '')
                timestamp = insight_data.pop('timestamp', None)
                
                # Prepare insight data - keep only generic properties on the node
                insight_id = self._generate_id("I")
                insight_data = self._ensure_timestamps(insight_data)
                
                # Generate name from text if not provided
                text = insight_data.get('text', '')
                name = insight_data.get('name', text[:50] if text else '')
                
                insight_data.update({
                    'id': insight_id,
                    'text': text,
                    'name': name,
                    'user_id': insight_data.get('user_id')
                })
                
                # Create insight node and relationship
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    MERGE (i:Insight {name: $name, user_id: $user_id})
                    ON CREATE SET i.id = $id, i.text = $text, i.created_at = $created_at, i.updated_at = $updated_at
                    ON MATCH SET i.updated_at = $updated_at, i.text = $text
                    CREATE (s)-[r:HAS_INSIGHT {
                        context: $context,
                        timestamp: $timestamp,
                        confidence: $confidence,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        modified_by: $modified_by
                    }]->(i)
                    RETURN i.id
                """, 
                session_id=session_id,
                name=name,
                user_id=insight_data.get('user_id'),
                id=insight_id,
                text=text,
                context=context,
                timestamp=timestamp,
                confidence=insight_data.get('confidence', 0),
                created_at=insight_data['created_at'],
                updated_at=insight_data['updated_at'],
                modified_by=insight_data.get('modified_by', 'system'))
                
                insight_id = result.single()["i.id"]
                
                # Create topic relationships if topics provided
                for topic_name in topics:
                    self._create_topic_relationship(insight_id, topic_name, 'insight')
                
                return insight_id
        except Exception as e:
            self._handle_error(e, "add_insight_to_session")

    def add_belief_to_session(self, session_id: str, belief_data: Dict[str, Any]) -> str:
        """Add a belief to a session"""
        try:
            with self.driver.session() as session:
                # Extract topics and session-specific data from belief data
                topics = belief_data.pop('topics', []) if 'topics' in belief_data else []
                impact = belief_data.pop('impact', '')
                timestamp = belief_data.pop('timestamp', None)
                
                # Prepare belief data - keep only generic properties on the node
                belief_id = self._generate_id("B")
                belief_data = self._ensure_timestamps(belief_data)
                
                # Generate name from text if not provided
                text = belief_data.get('text', '')
                name = belief_data.get('name', text[:50] if text else '')
                
                belief_data.update({
                    'id': belief_id,
                    'text': text,
                    'name': name,
                    'user_id': belief_data.get('user_id')
                })
                
                # Create belief node and relationship
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    MERGE (b:Belief {text: $text, user_id: $user_id})
                    ON CREATE SET b.id = $id, b.name = $name, b.created_at = $created_at, b.updated_at = $updated_at
                    ON MATCH SET b.updated_at = $updated_at, b.name = $name
                    CREATE (s)-[r:HAS_BELIEF {
                        impact: $impact,
                        timestamp: $timestamp,
                        confidence: $confidence,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        modified_by: $modified_by
                    }]->(b)
                    RETURN b.id
                """,
                session_id=session_id,
                text=belief_data['text'],
                name=name,
                user_id=belief_data.get('user_id'),
                id=belief_id,
                impact=impact,
                timestamp=timestamp,
                confidence=belief_data.get('confidence', 0),
                created_at=belief_data['created_at'],
                updated_at=belief_data['updated_at'],
                modified_by=belief_data.get('modified_by', 'system'))
                
                belief_id = result.single()["b.id"]
                
                # Create topic relationships if topics provided
                for topic_name in topics:
                    self._create_topic_relationship(belief_id, topic_name, 'belief')
                
                return belief_id
        except Exception as e:
            self._handle_error(e, "add_belief_to_session")

    def add_challenge_to_session(self, session_id: str, challenge_data: Dict[str, Any]) -> str:
        """Add a challenge to a session"""
        try:
            with self.driver.session() as session:
                # Extract topics and session-specific data from challenge data
                topics = challenge_data.pop('topics', []) if 'topics' in challenge_data else []
                impact = challenge_data.pop('impact', '')
                severity = challenge_data.pop('severity', '')
                timestamp = challenge_data.pop('timestamp', None)
                
                # Prepare challenge data - keep only generic properties on the node
                challenge_id = self._generate_id("C")
                challenge_data = self._ensure_timestamps(challenge_data)
                
                # Generate name from text if not provided
                text = challenge_data.get('text', '')
                name = challenge_data.get('name', text[:50] if text else '')
                
                challenge_data.update({
                    'id': challenge_id,
                    'text': text,
                    'name': name,
                    'user_id': challenge_data.get('user_id')
                })
                
                # Create challenge node and relationship
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    MERGE (c:Challenge {name: $name, user_id: $user_id})
                    ON CREATE SET c.id = $id, c.text = $text, c.created_at = $created_at, c.updated_at = $updated_at
                    ON MATCH SET c.updated_at = $updated_at, c.text = $text
                    CREATE (s)-[r:HAS_CHALLENGE {
                        impact: $impact,
                        severity: $severity,
                        timestamp: $timestamp,
                        confidence: $confidence,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        modified_by: $modified_by
                    }]->(c)
                    RETURN c.id
                """,
                session_id=session_id,
                name=name,
                user_id=challenge_data.get('user_id'),
                id=challenge_id,
                text=text,
                impact=impact,
                severity=severity,
                timestamp=timestamp,
                confidence=challenge_data.get('confidence', 0),
                created_at=challenge_data['created_at'],
                updated_at=challenge_data['updated_at'],
                modified_by=challenge_data.get('modified_by', 'system'))
                
                challenge_id = result.single()["c.id"]
                
                # Create topic relationships if topics provided
                for topic_name in topics:
                    self._create_topic_relationship(challenge_id, topic_name, 'challenge')
                
                return challenge_id
        except Exception as e:
            self._handle_error(e, "add_challenge_to_session")

    def add_action_item_to_session(self, session_id: str, action_data: Dict[str, Any]) -> str:
        """Add an action item to a session"""
        try:
            with self.driver.session() as session:
                # Extract topics from action item data
                topics = action_data.pop('topics', []) if 'topics' in action_data else []
                
                # Prepare action item data
                action_id = self._generate_id("A")
                action_data = self._ensure_timestamps(action_data)
                
                # Handle both text and description fields
                text = action_data.get('text', '')
                description = action_data.get('description', '')
                action_name = action_data.get('actionName', text[:50] if text else description[:50])
                
                action_data.update({
                    'id': action_id,
                    'actionName': action_name,
                    'description': description or text,  # Use description if available, otherwise use text
                    'user_id': action_data.get('user_id')
                })
                
                # Create action item node and relationship
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    CREATE (a:ActionItem $action_data)
                    CREATE (s)-[r:HAS_ACTION_ITEM {
                        priority: $priority,
                        status: $status,
                        due_date: $due_date,
                        context: $context,
                        created_at: $created_at,
                        updated_at: $updated_at,
                        modified_by: $modified_by
                    }]->(a)
                    RETURN a.id
                """, 
                session_id=session_id,
                action_data=action_data,
                priority=action_data.get('priority', 'medium'),
                status=action_data.get('status', 'pending'),
                due_date=action_data.get('due_date'),
                context=action_data.get('context', ''),
                created_at=action_data['created_at'],
                updated_at=action_data['updated_at'],
                modified_by=action_data.get('modified_by', 'system'))
                
                action_id = result.single()["a.id"]
                
                # Create topic relationships if topics provided
                for topic_name in topics:
                    self._create_topic_relationship(action_id, topic_name, 'action_item')
                
                return action_id
        except Exception as e:
            self._handle_error(e, "add_action_item_to_session")

    #######################
    # Bulk Operations
    #######################


    def _create_topic_relationship(self, element_id: str, topic_name: str, element_type: str) -> bool:
        """Create relationship between an element and a topic"""
        try:
            with self.driver.session() as session:
                # First ensure the topic exists (merge it if not)
                session.run("""
                    MERGE (t:Topic {name: $topic_name})
                    ON CREATE SET t.id = $topic_id, t.created_at = $timestamp, t.updated_at = $timestamp
                    ON MATCH SET t.updated_at = $timestamp
                """, 
                topic_name=topic_name, 
                topic_id=self._generate_id("T"),
                timestamp=datetime.now().isoformat())
                
                # Create the relationship based on element type
                node_label = {
                    'emotion': 'Emotion',
                    'insight': 'Insight',
                    'belief': 'Belief',
                    'challenge': 'Challenge',
                    'action_item': 'ActionItem'
                }.get(element_type)
                
                if not node_label:
                    self.logger.error(f"Invalid element type: {element_type}")
                    return False
                
                result = session.run(f"""
                    MATCH (e:{node_label} {{id: $element_id}})
                    MATCH (t:Topic {{name: $topic_name}})
                    MERGE (e)-[r:RELATED_TO {{
                        relevance: $relevance,
                        created_at: $timestamp,
                        updated_at: $timestamp,
                        modified_by: $modified_by
                    }}]->(t)
                    RETURN r
                """, 
                element_id=element_id,
                topic_name=topic_name,
                relevance=0.8,  # Default relevance
                timestamp=datetime.now().isoformat(),
                modified_by='system')
                
                return bool(result.single())
        except Exception as e:
            self._handle_error(e, f"create_{element_type}_topic_relationship")
            return False

    def get_user_topics(self, user_email):
        """
        Get all topics associated with a user's sessions.
        
        Args:
            user_email (str): The email of the user
            
        Returns:
            list: A list of unique topic objects with name, count, and last_used properties
        """
        try:
            with self.driver.session() as session:
                # Find all topics from all element types connected to sessions owned by this user
                query = """
                MATCH (u:User {email: $email})-[:HAS_SESSION]->(s:Session)
                OPTIONAL MATCH (s)-[:HAS_EMOTION]->(e:Emotion)-[:RELATED_TO]->(t1:Topic)
                OPTIONAL MATCH (s)-[:HAS_INSIGHT]->(i:Insight)-[:RELATED_TO]->(t2:Topic)
                OPTIONAL MATCH (s)-[:HAS_BELIEF]->(b:Belief)-[:RELATED_TO]->(t3:Topic)
                OPTIONAL MATCH (s)-[:HAS_CHALLENGE]->(c:Challenge)-[:RELATED_TO]->(t4:Topic)
                OPTIONAL MATCH (s)-[:HAS_ACTION_ITEM]->(a:ActionItem)-[:RELATED_TO]->(t5:Topic)
                
                WITH s, COLLECT(DISTINCT t1) + COLLECT(DISTINCT t2) + 
                     COLLECT(DISTINCT t3) + COLLECT(DISTINCT t4) + 
                     COLLECT(DISTINCT t5) AS topics
                UNWIND topics AS topic
                WHERE topic IS NOT NULL
                
                WITH topic.name AS topic_name, COUNT(DISTINCT topic) AS topic_count, 
                     MAX(s.created_at) AS last_used
                RETURN topic_name, topic_count, last_used
                ORDER BY topic_count DESC
                """
                
                result = session.run(query, email=user_email)
                topics = []
                
                for record in result:
                    topics.append({
                        "name": record["topic_name"],
                        "count": record["topic_count"],
                        "last_used": record["last_used"]
                    })
                
                return topics
                
        except Exception as e:
            self._handle_error(e, "get_user_topics")
            return []
            
    def classify_topic_with_taxonomy(self, topic_name, taxonomy_name=None):
        """
        Connect a Topic node to a TopicTaxonomy node in the Neo4j database.
        If taxonomy_name is not provided, the function will attempt to find the best matching taxonomy.
        
        Args:
            topic_name (str): The name of the topic to classify
            taxonomy_name (str, optional): The specific taxonomy name to connect with
            
        Returns:
            bool: True if the classification was successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                # If taxonomy name is provided, connect directly
                if taxonomy_name:
                    result = session.run("""
                        MATCH (t:Topic {name: $topic_name})
                        MATCH (tt:TopicTaxonomy {name: $taxonomy_name})
                        MERGE (t)-[r:CLASSIFIED_AS {
                            created_at: $timestamp,
                            updated_at: $timestamp,
                            confidence: 1.0
                        }]->(tt)
                        RETURN r
                    """, 
                    topic_name=topic_name,
                    taxonomy_name=taxonomy_name,
                    timestamp=datetime.now().isoformat())
                    
                    return bool(result.single())
                
                # If no taxonomy name provided, find the best match
                # First get all taxonomies
                taxonomies_result = session.run("""
                    MATCH (tt:TopicTaxonomy)
                    RETURN tt.name AS name, tt.level AS level
                    ORDER BY tt.level, tt.name
                """)
                
                taxonomies = [(record["name"], record.get("level", "main")) for record in taxonomies_result]
                
                # Simple string matching for now - could be enhanced with NLP
                best_match = None
                best_score = 0
                
                topic_lower = topic_name.lower()
                for tax_name, tax_level in taxonomies:
                    tax_lower = tax_name.lower()
                    
                    # Exact match
                    if topic_lower == tax_lower:
                        best_match = tax_name
                        break
                    
                    # Contains match
                    if topic_lower in tax_lower or tax_lower in topic_lower:
                        # Higher score for main level taxonomies
                        score = 0.8 if tax_level == "main" else 0.6
                        if score > best_score:
                            best_score = score
                            best_match = tax_name
                
                # If no good match found, connect to a general category
                if not best_match and taxonomies:
                    best_match = "Personal Development"  # Default taxonomy
                
                # Create the relationship
                if best_match:
                    confidence = 1.0 if best_score == 0 else best_score
                    result = session.run("""
                        MATCH (t:Topic {name: $topic_name})
                        MATCH (tt:TopicTaxonomy {name: $taxonomy_name})
                        MERGE (t)-[r:CLASSIFIED_AS {
                            created_at: $timestamp,
                            updated_at: $timestamp,
                            confidence: $confidence
                        }]->(tt)
                        RETURN r
                    """, 
                    topic_name=topic_name,
                    taxonomy_name=best_match,
                    confidence=confidence,
                    timestamp=datetime.now().isoformat())
                    
                    return bool(result.single())
                    
                return False
                
        except Exception as e:
            self._handle_error(e, "classify_topic_with_taxonomy")
            return False

    def relate_taxonomy_nodes(self, parent_name, child_name, relationship_type="PARENT_OF"):
        """
        Create a relationship between two taxonomy nodes.
        
        Args:
            parent_name (str): The name of the parent taxonomy node
            child_name (str): The name of the child taxonomy node
            relationship_type (str): The type of relationship to create
            
        Returns:
            bool: True if the relationship was created successfully, False otherwise
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (parent:TopicTaxonomy {name: $parent_name})
                    MATCH (child:TopicTaxonomy {name: $child_name})
                    MERGE (parent)-[r:$relationship_type {
                created_at: $timestamp,
                        updated_at: $timestamp
                    }]->(child)
                    RETURN r
                """, 
                parent_name=parent_name,
                child_name=child_name,
                relationship_type=relationship_type,
                timestamp=datetime.now().isoformat())
                
                return bool(result.single())
                
        except Exception as e:
            self._handle_error(e, "relate_taxonomy_nodes")
            return False

    def create_session_relationship(self, source_session_id: str, target_session_id: str) -> bool:
        """Create a NEXT_SESSION relationship between two sessions"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s1:Session {id: $source_id})
                    MATCH (s2:Session {id: $target_id})
                    MERGE (s1)-[r:NEXT_SESSION]->(s2)
                    ON CREATE SET r.created_at = $timestamp
                    RETURN r
                """,
                source_id=source_session_id,
                target_id=target_session_id,
                timestamp=datetime.now().isoformat())
                
                return bool(result.single())
        except Exception as e:
            self._handle_error(e, "create_session_relationship")

    def get_next_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the next session in the sequence"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Session {id: $session_id})-[:NEXT_SESSION]->(next:Session)
                    RETURN next
                """, session_id=session_id)
                
                record = result.single()
                if record:
                    return dict(record["next"])
                return None
        except Exception as e:
            self._handle_error(e, "get_next_session")

    def get_previous_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the previous session in the sequence"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (prev:Session)-[:NEXT_SESSION]->(s:Session {id: $session_id})
                    RETURN prev
                """, session_id=session_id)
                
                record = result.single()
                if record:
                    return dict(record["prev"])
                return None
        except Exception as e:
            self._handle_error(e, "get_previous_session")

    def get_user_session_sequence(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all user sessions in sequence order"""
        try:
            with self.driver.session() as session:
                # Find the first session (has no incoming NEXT_SESSION relationship)
                result = session.run("""
                    MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)
                    WHERE NOT EXISTS { (:Session)-[:NEXT_SESSION]->(s) }
                    RETURN s as session
                """, user_id=user_id)
                
                record = result.single()
                if not record:
                    # If no first session is found, return all sessions ordered by date
                    result = session.run("""
                        MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)
                        RETURN s as session
                        ORDER BY s.created_at
                    """, user_id=user_id)
                    return [dict(record["session"]) for record in result]
                
                # Start with the first session and follow NEXT_SESSION relationships
                first_session = dict(record["session"])
                sessions = [first_session]
                current_id = first_session["id"]
                
                # Follow the chain of NEXT_SESSION relationships
                while True:
                    result = session.run("""
                        MATCH (s:Session {id: $current_id})-[:NEXT_SESSION]->(next:Session)
                        RETURN next as session
                    """, current_id=current_id)
                    
                    record = result.single()
                    if not record:
                        break
                        
                    next_session = dict(record["session"])
                    sessions.append(next_session)
                    current_id = next_session["id"]
                
                return sessions
        except Exception as e:
            self._handle_error(e, "get_user_session_sequence")

    def get_user_elements_by_type(self, user_id: str, element_type: str) -> List[Dict[str, Any]]:
        """
        Get all elements of a specific type for a user with their topics and sessions.
        
        Args:
            user_id (str): The user ID
            element_type (str): One of 'emotion', 'insight', 'belief', 'challenge', 'action_item'
            
        Returns:
            list: List of elements with their topics and session info
        """
        try:
            with self.driver.session() as session:
                # Map element type to node label and relationship type
                type_mapping = {
                    'emotion': {'node': 'Emotion', 'rel': 'HAS_EMOTION'},
                    'insight': {'node': 'Insight', 'rel': 'HAS_INSIGHT'},
                    'belief': {'node': 'Belief', 'rel': 'HAS_BELIEF'},
                    'challenge': {'node': 'Challenge', 'rel': 'HAS_CHALLENGE'},
                    'action_item': {'node': 'ActionItem', 'rel': 'HAS_ACTION_ITEM'}
                }
                
                if element_type not in type_mapping:
                    raise ValueError(f"Invalid element type: {element_type}")
                
                node_label = type_mapping[element_type]['node']
                rel_type = type_mapping[element_type]['rel']
                
                query = f"""
                MATCH (u:User {{userId: $user_id}})-[:HAS_SESSION]->(s:Session)-[rel:{rel_type}]->(e:{node_label})
                OPTIONAL MATCH (e)-[tr:RELATED_TO]->(t:Topic)
                RETURN e, rel, s, t, tr
                ORDER BY s.created_at DESC, e.created_at DESC
                """
                
                result = session.run(query, user_id=user_id)
                
                elements = []
                element_ids = set()  # Track processed elements to avoid duplicates
                
                for record in result:
                    element = dict(record["e"])
                    element_id = element["id"]
                    
                    # Skip if we've already processed this element
                    if element_id in element_ids:
                        continue
                        
                    element_ids.add(element_id)
                    
                    # Add relationship properties
                    rel = record["rel"]
                    if rel:
                        rel_dict = dict(rel)
                        for key, value in rel_dict.items():
                            if key not in ["created_at", "updated_at"] and key not in element:
                                element[key] = value
                    
                    # Add session information
                    session_node = record["s"]
                    if session_node:
                        element["session"] = {
                            "id": session_node["id"],
                            "title": session_node.get("title", ""),
                            "date": session_node.get("date", ""),
                            "created_at": session_node.get("created_at", "")
                        }
                    
                    # Add topic if present
                    topic = record["t"]
                    if topic:
                        topic_dict = dict(topic)
                        
                        # Add topic relationship properties
                        topic_rel = record["tr"]
                        if topic_rel:
                            topic_rel_dict = dict(topic_rel)
                            if "relevance" in topic_rel_dict:
                                topic_dict["relevance"] = topic_rel_dict["relevance"]
                        
                        element["topic"] = topic_dict
                    
                    elements.append(element)
                
                return elements
        except Exception as e:
            self._handle_error(e, f"get_user_{element_type}s")

    def get_user_elements_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all elements for a user, including counts by type and top topics.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            dict: Summary of user elements
        """
        try:
            with self.driver.session() as session:
                # Get counts by element type
                counts_query = """
                MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)
                
                OPTIONAL MATCH (s)-[:HAS_EMOTION]->(e:Emotion)
                WITH u, s, count(e) as emotion_count
                
                    OPTIONAL MATCH (s)-[:HAS_INSIGHT]->(i:Insight)
                WITH u, s, emotion_count, count(i) as insight_count
                
                    OPTIONAL MATCH (s)-[:HAS_BELIEF]->(b:Belief)
                WITH u, s, emotion_count, insight_count, count(b) as belief_count
                
                    OPTIONAL MATCH (s)-[:HAS_CHALLENGE]->(c:Challenge)
                WITH u, s, emotion_count, insight_count, belief_count, count(c) as challenge_count
                
                OPTIONAL MATCH (s)-[:HAS_ACTION_ITEM]->(a:ActionItem)
                WITH u, s, emotion_count, insight_count, belief_count, challenge_count, count(a) as action_item_count
                
                RETURN 
                    count(s) as session_count,
                    sum(emotion_count) as emotion_count,
                    sum(insight_count) as insight_count,
                    sum(belief_count) as belief_count,
                    sum(challenge_count) as challenge_count,
                    sum(action_item_count) as action_item_count
                """
                
                counts_result = session.run(counts_query, user_id=user_id)
                counts_record = counts_result.single()
                
                if not counts_record:
                    return {
                        "session_count": 0,
                        "emotion_count": 0,
                        "insight_count": 0,
                        "belief_count": 0, 
                        "challenge_count": 0,
                        "action_item_count": 0,
                        "top_topics": []
                    }
                
                # Get top topics
                topics_query = """
                MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)
                MATCH (s)-[r]->(e)-[:RELATED_TO]->(t:Topic)
                WHERE type(r) IN ['HAS_EMOTION', 'HAS_INSIGHT', 'HAS_BELIEF', 'HAS_CHALLENGE', 'HAS_ACTION_ITEM']
                WITH t, count(e) as element_count
                RETURN t.name as topic_name, element_count
                ORDER BY element_count DESC
                LIMIT 10
                """
                
                topics_result = session.run(topics_query, user_id=user_id)
                top_topics = [{"name": record["topic_name"], "count": record["element_count"]} 
                             for record in topics_result]
                
                return {
                    "session_count": counts_record["session_count"],
                    "emotion_count": counts_record["emotion_count"],
                    "insight_count": counts_record["insight_count"],
                    "belief_count": counts_record["belief_count"],
                    "challenge_count": counts_record["challenge_count"],
                    "action_item_count": counts_record["action_item_count"],
                    "top_topics": top_topics
                }
        except Exception as e:
            self._handle_error(e, "get_user_elements_summary")

    def save_session_analysis(self, session_id: str, analysis_data: Dict[str, Any], user_id: str) -> bool:
        """
        Save analysis results to Neo4j, creating nodes for emotions, insights, beliefs, challenges, and action items.
        
        Args:
            session_id (str): The ID of the session to save analysis for
            analysis_data (dict): The analysis data from the analysis service
            user_id (str): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Saving analysis for session {session_id}")
            
            # 1. Update session with analysis status
            with self.driver.session() as session:
                session.run("""
                    MATCH (s:Session {id: $session_id})
                    SET s.analysis_status = 'completed',
                        s.analysis_timestamp = $timestamp,
                        s.updated_at = $timestamp
                """, 
                session_id=session_id,
                timestamp=datetime.now().isoformat())
            
            # 2. Process emotions
            if "Emotions" in analysis_data:
                for emotion in analysis_data["Emotions"]:
                    # Format: [name, intensity, context, topics]
                    emotion_data = {
                        "name": emotion[0],  # name
                        "intensity": float(emotion[1]),  # intensity
                        "context": emotion[2],  # context
                        "topics": [emotion[3]] if isinstance(emotion[3], str) else emotion[3],  # topics
                        "user_id": user_id,
                        "isUserModified": False
                    }
                    self.add_emotion_to_session(session_id, emotion_data)
            
            # 3. Process beliefs
            if "Beliefs" in analysis_data:
                for belief in analysis_data["Beliefs"]:
                    # Format: [id, name, text, impact, topics]
                    belief_data = {
                        "name": belief[1],  # name
                        "text": belief[2],  # text
                        "impact": belief[3],  # impact
                        "topics": [belief[4]] if isinstance(belief[4], str) else belief[4],  # topics
                        "user_id": user_id,
                        "isUserModified": False
                    }
                    self.add_belief_to_session(session_id, belief_data)
            
            # 4. Process action items
            if "actionitems" in analysis_data:
                for actionitem in analysis_data["actionitems"]:
                    # Format: [id, name, description, topics, status]
                    action_data = {
                        "name": actionitem[1],  # name
                        "text": actionitem[2],  # description
                        "impact": "Action item identified from session analysis",
                        "topics": [actionitem[3]] if isinstance(actionitem[3], str) else actionitem[3],  # topics
                        "user_id": user_id,
                        "isUserModified": False,
                        "status": actionitem[4] if len(actionitem) > 4 else "hasn't started"  # status
                    }
                    self.add_action_item_to_session(session_id, action_data)
            
            # 5. Process insights
            if "Insights" in analysis_data:
                for insight in analysis_data["Insights"]:
                    # Format: [name, text, context, topics]
                    insight_data = {
                        "name": insight[0],  # name
                        "text": insight[1],  # text
                        "context": insight[2],  # context
                        "topics": insight[3] if isinstance(insight[3], list) else [insight[3]],  # topics - fixed order
                        "user_id": user_id,
                        "isUserModified": False
                    }
                    self.add_insight_to_session(session_id, insight_data)
            
            # 6. Process challenges
            if "Challenges" in analysis_data:
                for challenge in analysis_data["Challenges"]:
                    # Format: [name, text, impact, topics]
                    challenge_data = {
                        "name": challenge[0],  # name
                        "text": challenge[1],  # text
                        "impact": challenge[2],  # impact
                        "topics": challenge[3] if isinstance(challenge[3], list) else [challenge[3]],  # topics - fixed order
                        "user_id": user_id,
                        "isUserModified": False,
                        "severity": "",  # Default empty severity
                        "status": "active"
                    }
                    self.add_challenge_to_session(session_id, challenge_data)
            
            self.logger.info(f"Successfully saved analysis for session {session_id}")
            return True
            
        except Exception as e:
            self._handle_error(e, "save_session_analysis")
            return False

    def get_all_taxonomies(self):
        """
        Get all available taxonomy nodes.
            
        Returns:
            List of dictionaries containing taxonomy information.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:TopicTaxonomy)
                    OPTIONAL MATCH (t)-[r:PARENT_OF]->(child:TopicTaxonomy)
                    OPTIONAL MATCH (parent:TopicTaxonomy)-[r2:PARENT_OF]->(t)
                    RETURN t.name as name, 
                           COLLECT(DISTINCT child.name) as children, 
                           COLLECT(DISTINCT parent.name) as parents
                    """
                )
                
                taxonomies = []
                for record in result:
                    taxonomies.append({
                        "name": record["name"],
                        "children": record["children"],
                        "parents": record["parents"]
                    })
                    
                self.logger.info(f"Retrieved {len(taxonomies)} taxonomy nodes from database")
                return taxonomies
        except Exception as e:
            self.logger.error(f"Error retrieving taxonomies: {str(e)}")
            return []

    def create_default_user_settings(self, user_id: str) -> bool:
        """Create default settings for a new user"""
        try:
            default_settings = {
                'gpt_model': 'gpt-4',
                'max_tokens': 500,
                'temperature': 0.7,
                'available_topics': [],
                'system_prompt_template': '',
                'analysis_prompt_template': '',
                'analysis_elements': []
            }
            return self.save_user_settings(user_id, default_settings)
        except Exception as e:
            self._handle_error(e, "create_default_user_settings")
            return False

    def update_last_login(self, user_id: str) -> bool:
        """Update the user's last login timestamp"""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})
                    SET u.last_login = $timestamp
                    RETURN u
                    """,
                    {
                        'user_id': user_id,
                        'timestamp': self._get_timestamp()
                    }
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            self._handle_error(e, "update_last_login")
            return False
        
    def get_admin_users(self) -> List[Dict[str, Any]]:
        """Get all admin users"""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User)
                    WHERE u.is_admin = true
                    RETURN u.id AS userId, u.email AS email, u.name AS name, 
                           u.created_at AS created_at, u.last_login AS last_login
                    ORDER BY u.created_at DESC
                    """
                )
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error getting admin users: {str(e)}")
            self._handle_error(e, "get_admin_users")
            return []

    def get_user_settings_by_id(self, settings_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings by settings ID"""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (s:Settings {id: $settings_id})
                    OPTIONAL MATCH (s)-[:HAS_ELEMENT]->(e:AnalysisElement)
                    WITH s, collect(e) as elements
                    RETURN s {
                        .id, .gpt_model, .max_tokens, .temperature, 
                        .max_sessions, .max_duration, .allowed_file_types,
                        .created_at, .updated_at, 
                        elements: [el IN elements | el {
                            .id, .name, .description, .enabled, .categories,
                            .format_template, .system_instructions, 
                            .analysis_instructions, .requires_topic,
                            .requires_timestamp, .additional_fields
                        }]
                    } as settings
                    """,
                    {'settings_id': settings_id}
                )
                record = result.single()
                if record:
                    return record["settings"]
                return None
        except Exception as e:
            logger.error(f"Error getting user settings by ID: {str(e)}")
            self._handle_error(e, "get_user_settings_by_id")
            return None

    def get_user_sessions_with_stats(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user with added statistics"""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {userId: $user_id})-[:OWNS]->(s:Session)
                    OPTIONAL MATCH (s)-[:HAS_EMOTION]->(e:Emotion)
                    OPTIONAL MATCH (s)-[:HAS_TOPIC]->(t:Topic)
                    OPTIONAL MATCH (s)-[:HAS_BELIEF]->(b:Belief)
                    OPTIONAL MATCH (s)-[:HAS_ACTION_ITEM]->(a:ActionItem)
                    WITH s, count(DISTINCT e) as emotionCount, 
                         count(DISTINCT t) as topicCount,
                         count(DISTINCT b) as beliefCount,
                         count(DISTINCT a) as actionItemCount
                    RETURN s.id as id, s.title as title, s.description as description,
                           s.created_at as created_at, s.updated_at as updated_at,
                           s.duration as duration, emotionCount, topicCount, 
                           beliefCount, actionItemCount
                    ORDER BY s.created_at DESC
                    """,
                    {'user_id': user_id}
                )
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error getting user sessions with stats: {str(e)}")
            self._handle_error(e, "get_user_sessions_with_stats")
            return []

    def change_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Change a user's password"""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {userId: $user_id})
                    SET u.password_hash = $password_hash,
                        u.updated_at = $timestamp
                    RETURN u
                    """,
                    {
                        'user_id': user_id,
                        'password_hash': new_password_hash,
                        'timestamp': self._get_timestamp()
                    }
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error changing user password: {str(e)}")
            self._handle_error(e, "change_user_password")
            return False

    def update_admin_settings(self, settings_id: str, settings_data: Dict[str, Any]) -> bool:
        """Update admin settings"""
        try:
            # Prepare update parameters
            params = {
                'settings_id': settings_id,
                'timestamp': self._get_timestamp()
            }
            
            # Add allowed settings fields to parameters
            update_fields = []
            allowed_fields = [
                'gpt_model', 'max_tokens', 'temperature', 
                'max_sessions', 'max_duration', 'allowed_file_types'
            ]
            
            for field in allowed_fields:
                if field in settings_data:
                    params[field] = settings_data[field]
                    update_fields.append(f"s.{field} = ${field}")
            
            # Only update if there are fields to update
            if not update_fields:
                return False
            
            # Add updated_at field
            update_fields.append("s.updated_at = $timestamp")
            
            with self.driver.session() as session:
                # Update settings node
                query = f"""
                MATCH (s:Settings {{id: $settings_id}})
                SET {', '.join(update_fields)}
                RETURN s
                """
                
                result = session.run(query, params)
                
                # Update analysis elements if provided
                if 'analysis_elements' in settings_data and isinstance(settings_data['analysis_elements'], list):
                    for element in settings_data['analysis_elements']:
                        if 'id' in element and 'enabled' in element:
                            session.run(
                                """
                                MATCH (e:AnalysisElement {id: $id})
                                SET e.enabled = $enabled
                                """,
                                {
                                    'id': element['id'],
                                    'enabled': element['enabled']
                                }
                            )
            
            return result.single() is not None
        except Exception as e:
            logger.error(f"Error updating admin settings: {str(e)}")
            self._handle_error(e, "update_admin_settings")
            return False

    def save_analysis_to_session(self, user_id: str, session_id: str, analysis_results: Dict[str, Any]) -> bool:
        """
        Save analysis results to a session in a single transaction.
        
        Args:
            user_id (str): The user ID
            session_id (str): The session ID
            analysis_results (Dict[str, Any]): Analysis results from analyze_transcript_and_extract
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if analysis_results.get('status') != 'completed':
                logger.error(f"Analysis failed: {analysis_results.get('error', 'Unknown error')}")
                return False
                
            elements = analysis_results.get('elements', {})
            
            # Start transaction
            with self.driver.session() as session:
                # Save each element type
                for element_type, element_list in elements.items():
                    for element in element_list:
                        # Generate name from text if not provided
                        if 'name' not in element:
                            element['name'] = element.get('text', '')[:50] or element.get('description', '')[:50] or 'Unnamed'
                        
                        # Create element node
                        element_node = session.write_transaction(
                            lambda tx: tx.run(
                                f"""
                                MATCH (s:Session {{id: $session_id}})
                                MERGE (e:{element_type} {{name: $name, user_id: $user_id}})
                                ON CREATE SET e += $properties
                                ON MATCH SET e += $properties
                                MERGE (s)-[:CONTAINS]->(e)
                                RETURN e
                                """,
                                session_id=session_id,
                                user_id=user_id,
                                name=element['name'],
                                properties={
                                    'text': element.get('text', ''),
                                    'description': element.get('description', ''),
                                    'confidence': element.get('confidence', 1.0),
                                    'created_at': element.get('created_at', datetime.now().isoformat()),
                                    'updated_at': element.get('updated_at', datetime.now().isoformat()),
                                    'topics': element.get('topics', []),
                                    'impact': element.get('impact', 0),
                                    'intensity': element.get('intensity', 0),
                                    'context': element.get('context', ''),
                                    'status': element.get('status', 'pending')
                                }
                            ).single()
                        )
                        
                        if not element_node:
                            logger.error(f"Failed to create {element_type} node")
                            return False
                
                # Update session with analysis metadata
                session.write_transaction(
                    lambda tx: tx.run(
                        """
                        MATCH (s:Session {id: $session_id})
                        SET s.analysis_status = 'completed',
                            s.analysis_updated_at = $updated_at
                        """,
                        session_id=session_id,
                        updated_at=datetime.now().isoformat()
                    )
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving analysis to session: {str(e)}")
            return False

    def add_topic(self, session_id: str, topic_data: Dict[str, Any]) -> str:
        """Add a topic to the database"""
        try:
            with self.driver.session() as session:
                # Prepare topic data
                topic_id = self._generate_id("T")
                topic_data = self._ensure_timestamps(topic_data)
                
                # Create topic node and relationship
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    MERGE (t:Topic {name: $name, user_id: $user_id})
                    ON CREATE SET t.id = $id, t.description = $description, t.created_at = $created_at, t.updated_at = $updated_at
                    ON MATCH SET t.updated_at = $updated_at
                    CREATE (s)-[r:HAS_TOPIC {
                        created_at: $created_at,
                        updated_at: $updated_at,
                        modified_by: $modified_by
                    }]->(t)
                    RETURN t.id
                """,
                session_id=session_id,
                name=topic_data['name'],
                user_id=topic_data.get('user_id'),
                id=topic_id,
                description=topic_data.get('description', ''),
                created_at=topic_data['created_at'],
                updated_at=topic_data['updated_at'],
                modified_by=topic_data.get('modified_by', 'system'))
                
                record = result.single()
                if record:
                    return record["t.id"]
                else:
                    self.logger.error(f"Failed to create topic {topic_data['name']}")
                    return None
        except Exception as e:
            self.logger.error(f"Error in add_topic: {str(e)}")
            self._handle_error(e, "add_topic")
            return None

    def update_session_status(self, session_id: str, status: str, analysis_status: str = None) -> bool:
        """Update the status of a session."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (s:Session {session_id: $session_id})
                SET s.status = $status
                """
                params = {"session_id": session_id, "status": status}
                
                if analysis_status:
                    query += ", s.analysis_status = $analysis_status"
                    params["analysis_status"] = analysis_status
                    
                query += " RETURN s"
                
                result = session.run(query, params).single()
                return bool(result)
        except Exception as e:
            logging.error(f"Error updating session status: {str(e)}")
            return False

    def update_session_with_elements(self, session_id: str, elements: Dict[str, Any], user_id: str) -> bool:
        """
        Update a session with extracted elements and set analysis status to completed.
        
        Args:
            session_id: ID of the session to update
            elements: Dictionary containing extracted elements
            user_id: ID of the user who owns the session
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Verify session exists
            session = self.get_session_data(session_id)
            if not session:
                self.logger.error(f"Session {session_id} not found")
                return False

            # Format elements for Neo4j
            analysis_data = {}
            
            # Format emotions: [name, intensity, context, topic, timestamp]
            if "emotions" in elements:
                analysis_data["Emotions"] = [
                    [e["name"], e["intensity"], e["context"], e.get("topic", None), e.get("timestamp", "")]
                    for e in elements["emotions"]
                ]
            
            # Format beliefs: [id, name, description, impact, topic, timestamp]
            if "beliefs" in elements:
                analysis_data["Beliefs"] = [
                    [str(uuid.uuid4()), b["name"], b["description"], b["impact"], b.get("topic", None), b.get("timestamp", "")]
                    for b in elements["beliefs"]
                ]
            
            # Format action items: [id, name, description, topic, timestamp]
            if "action_items" in elements:
                analysis_data["actionitems"] = [
                    [str(uuid.uuid4()), a["name"], a["description"], a.get("topic", None), a.get("status", "hasn't started")]
                    for a in elements["action_items"]
                ]
            
            # Format challenges: [name, text, impact, topic]
            # Fix: Changed order to match expected format in save_session_analysis
            if "challenges" in elements:
                analysis_data["Challenges"] = [
                    [c["name"], c.get("description", ""), c.get("impact", ""), c.get("topic", None)]
                    for c in elements["challenges"]
                ]
            
            # Format insights: [name, text, context, topic]
            # Fix: Changed order to match expected format in save_session_analysis
            if "insights" in elements:
                analysis_data["Insights"] = [
                    [i["name"], i.get("description", ""), i.get("context", ""), i.get("topic", None)]
                    for i in elements["insights"]
                ]

            # Save analysis data and update session status
            success = self.save_session_analysis(session_id, analysis_data, user_id)
            if success:
                print(f"Successfully updated session {session_id} with elements")
                return True
            else:
                print(f"Failed to update session {session_id} with elements")
                return False
                
        except Exception as e:
            print(f"Error updating session with elements: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_query(self, query: str, params: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Run an arbitrary Cypher query against Neo4j.
        
        Args:
            query: The Cypher query to execute
            params: Parameters for the query (optional)
            
        Returns:
            List of results as dictionaries, or None if the query failed
        """
        try:
            self.logger.info(f"Executing Neo4j query: {query}")
            
            with self.driver.session() as session:
                result = session.run(query, parameters=params or {})
                
                # Convert results to a list of dictionaries
                records = []
                for record in result:
                    # Convert each record to a dictionary
                    record_dict = {}
                    for key, value in record.items():
                        # Handle Neo4j Node objects by converting to dict
                        if hasattr(value, 'items'):
                            record_dict[key] = dict(value)
                        # Handle Neo4j Relationship objects
                        elif hasattr(value, 'start_node'):
                            record_dict[key] = {
                                'start': dict(value.start_node),
                                'end': dict(value.end_node),
                                'type': value.type,
                                'properties': dict(value)
                            }
                        # Handle primitive types and lists
                        else:
                            record_dict[key] = value
                    
                    records.append(record_dict)
                
                return records
        except Exception as e:
            self.logger.error(f"Error executing Neo4j query: {str(e)}")
            return None

    def get_session_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results for a session."""
        try:
            with self.driver.session() as session:
                # Get the session node with its analysis data and elements
                result = session.run("""
                    MATCH (s:Session {id: $session_id})
                    OPTIONAL MATCH (s)-[:HAS_EMOTION]->(e:Emotion)
                    OPTIONAL MATCH (s)-[:HAS_INSIGHT]->(i:Insight)
                    OPTIONAL MATCH (s)-[:HAS_BELIEF]->(b:Belief)
                    OPTIONAL MATCH (s)-[:HAS_CHALLENGE]->(c:Challenge)
                    OPTIONAL MATCH (s)-[:HAS_ACTION_ITEM]->(a:ActionItem)
                    RETURN s,
                           collect(DISTINCT e) as emotions,
                           collect(DISTINCT i) as insights,
                           collect(DISTINCT b) as beliefs,
                           collect(DISTINCT c) as challenges,
                           collect(DISTINCT a) as action_items
                """, session_id=session_id).single()
                
                if not result:
                    return None
                    
                session_data = dict(result['s'])
                
                # Organize elements by type
                analysis_results = {
                    'emotions': [dict(e) for e in result['emotions'] if e is not None],
                    'insights': [dict(i) for i in result['insights'] if i is not None],
                    'beliefs': [dict(b) for b in result['beliefs'] if b is not None],
                    'challenges': [dict(c) for c in result['challenges'] if c is not None],
                    'action_items': [dict(a) for a in result['action_items'] if a is not None]
                }
                
                return {
                    'session_id': session_id,
                    'status': session_data.get('status'),
                    'analysis_status': session_data.get('analysis_status'),
                    'elements': analysis_results
                }
                
        except Exception as e:
            self.logger.error(f"Error getting session analysis: {str(e)}")
            return None