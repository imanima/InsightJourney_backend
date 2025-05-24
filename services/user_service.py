import logging
import hashlib
import hmac
import os
from typing import Optional, Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, neo4j_service):
        self.neo4j = neo4j_service
        # Use a secret key for HMAC hashing - ideally from environment variable
        self.hash_key = os.getenv("DATA_HASH_KEY", "insightjourney-hash-key-change-in-production").encode()

    def create_user(self, email: str, password: str, name: str = "", is_admin: bool = False) -> str:
        """Create a new user with hashed password and anonymized data"""
        try:
            # Check if user exists - we need a separate lookup mechanism
            existing_user = self.neo4j.get_user_by_email(email)
            if existing_user:
                logger.warning(f"User with email {email} already exists")
                raise ValueError(f"User with email {email} already exists")
            
            # Hash the password
            password_hash = generate_password_hash(password)
            
            # Hash the email and name for anonymization
            email_hash = self._hash_data(email)
            name_hash = self._hash_data(name) if name else ""
            
            # Create user with anonymized data
            user_id = self.neo4j.create_user(
                email=email_hash,  # Store only hashed email in User node
                password_hash=password_hash,
                name=name_hash,
                is_admin=is_admin,
                original_email=email  # Pass original email for lookup node creation
            )
            
            return user_id
        except ValueError:
            # Re-raise ValueError for duplicate users
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise ValueError(f"Failed to create user: {str(e)}")

    def verify_password(self, email: str, password: str) -> bool:
        """Verify a user's password"""
        try:
            # Get user by email (will use email lookup)
            user = self.neo4j.get_user_by_email(email)
            if not user or not user.get("password_hash"):
                return False
                
            # Verify password
            return check_password_hash(user["password_hash"], password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
            
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        try:
            user = self.neo4j.get_user_by_id(user_id)
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
            
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email"""
        try:
            user = self.neo4j.get_user_by_email(email)
            return user
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
            
    def _hash_data(self, data: str) -> str:
        """Hash sensitive data using HMAC-SHA256"""
        if not data:
            return ""
        return hmac.new(self.hash_key, data.encode(), hashlib.sha256).hexdigest()

    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user attributes with anonymization"""
        try:
            # Ensure password is hashed if being updated
            if 'password' in kwargs:
                kwargs['password_hash'] = generate_password_hash(kwargs.pop('password'))
            
            # Anonymize user data
            if 'email' in kwargs:
                kwargs['email_hash'] = self._hash_data(kwargs['email'])
            
            if 'name' in kwargs:
                kwargs['name'] = self._hash_data(kwargs['name'])
            
            return self.neo4j.update_user(user_id, **kwargs)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            return self.neo4j.delete_user(user_id)
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise

    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            return self.neo4j.get_user_sessions(user_id)
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            raise
    
    def deanonymize_for_display(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        For API responses only, replace anonymized data with original values
        while keeping the anonymized data in the database
        """
        # We keep original email so we can display it back to the user
        # But names are fully anonymized - we can't recover them
        result = user_data.copy()
        
        # If we need to display original names, we would need to store them separately 
        # and retrieve them here
        
        return result 