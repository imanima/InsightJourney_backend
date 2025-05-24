from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import os
from dotenv import load_dotenv
import logging
# Use the directly importable JWT exceptions
from jwt import ExpiredSignatureError, InvalidTokenError

from services.neo4j_service import Neo4jService
from services.user_service import UserService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AuthService:
    def __init__(self, neo4j_service: Neo4jService, secret_key: str, token_expiry: int = 24):
        self.neo4j_service = neo4j_service
        self.user_service = UserService(neo4j_service)
        self.secret_key = secret_key
        self.token_expiry = token_expiry  # in hours
        logger.debug("AuthService initialized")

    def register_user(self, email: str, password: str, name: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Register a new user with the provided email, password, and name.
        Returns a tuple of (success, response_dict, error_message).
        """
        try:
            # Create user using user service
            user_id = self.user_service.create_user(email, password, name)
            
            # Get created user
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return False, {}, "Failed to create user"

            # Generate token
            token = self._generate_token(user_id)
            
            response = {
                "access_token": token,
                "user": {
                    "id": user_id,
                    "email": email,
                    "name": name
                }
            }
            logger.info(f"Successfully registered user: {email}")
            return True, response, None

        except ValueError as e:
            logger.warning(f"Validation error during user registration: {str(e)}")
            return False, {}, str(e)
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return False, {}, "An unexpected error occurred"

    def login_user(self, email: str, password: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """Login a user"""
        try:
            # Verify user credentials
            if not self.user_service.verify_password(email, password):
                logger.warning(f"Invalid login attempt for email: {email}")
                return False, {}, "Invalid credentials"
                
            # Get user data
            user = self.user_service.get_user_by_email(email)
            if not user:
                logger.warning(f"User not found during login: {email}")
                return False, {}, "User not found"
                
            # Check if user is disabled
            if user.get("disabled", False):
                logger.warning(f"Attempted login to disabled account: {email}")
                return False, {}, "User account is disabled"
                
            # Generate JWT token with user ID instead of email
            user_id = user.get("userId")
            if not user_id:
                logger.error(f"User data missing userId: {user}")
                return False, {}, "Invalid user data"
                
            # Generate token with proper subject field
            expires = datetime.utcnow() + timedelta(hours=self.token_expiry)
            token_data = {
                "sub": user_id,  # Use user ID as subject for better security
                "exp": int(expires.timestamp())
            }
            
            access_token = jwt.encode(token_data, self.secret_key, algorithm='HS256')
            logger.info(f"Login successful for user: {email}")
            
            return True, {
                "access_token": access_token,
                "user": user
            }, None
            
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}", exc_info=True)
            return False, {}, str(e)

    def _generate_token(self, user_id: str) -> str:
        """Generate a JWT token for the user"""
        try:
            payload = {
                'sub': user_id,
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry)
            }
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise

    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the user_id if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload.get('sub')
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get a user by their ID"""
        try:
            return self.user_service.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error retrieving user by ID: {str(e)}")
            return None

    def logout_user(self, token: str) -> bool:
        """
        Logout a user by invalidating their token.
        In a real implementation, you might want to add the token to a blacklist.
        """
        # For now, we just verify the token is valid
        user_id = self.verify_token(token)
        if user_id:
            logger.info(f"User {user_id} logged out")
            return True
        return False

    def change_password(self, user_id: str, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change a user's password after verifying the current password
        Returns a tuple of (success, error_message).
        """
        try:
            # Get user
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # For password verification, we need to find the original email
            # Let's get it from the EmailLookup table via neo4j service
            try:
                # Get all email lookups to find the one with this user_id
                with self.neo4j_service.driver.session() as session:
                    result = session.run("""
                        MATCH (e:EmailLookup {userId: $user_id})
                        RETURN e.email as email
                    """, user_id=user_id)
                    
                    record = result.single()
                    if not record:
                        return False, "Unable to verify current password"
                    
                    original_email = record["email"]
            except Exception as e:
                logger.error(f"Could not retrieve original email for user: {user_id}: {str(e)}")
                return False, "Unable to verify current password"
            
            # Verify current password using the original email
            if not self.user_service.verify_password(original_email, current_password):
                logger.warning(f"Failed password change attempt for user: {user_id}")
                return False, "Current password is incorrect"
            
            # Hash the new password
            new_password_hash = generate_password_hash(new_password)
            
            # Update password in database using neo4j service
            success = self.neo4j_service.change_user_password(user_id, new_password_hash)
            if not success:
                return False, "Failed to update password"
            
            logger.info(f"Password changed successfully for user: {user_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}", exc_info=True)
            return False, "An unexpected error occurred"

    def reset_password_request(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Request a password reset for the given email
        Returns a tuple of (success, error_message).
        
        Note: This method would typically generate a reset token and send an email.
        For now, it just checks if the user exists and returns success.
        """
        try:
            # Check if user exists
            user = self.user_service.get_user_by_email(email)
            if not user:
                # Don't reveal whether the user exists for security reasons
                logger.info(f"Password reset requested for non-existent user: {email}")
                return True, None
            
            # In a real application, generate a reset token and send an email
            # For now, just log the request
            logger.info(f"Password reset requested for user: {email}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error processing password reset request: {str(e)}")
            return False, "An unexpected error occurred"

    def is_admin(self, user_id: str) -> bool:
        """Check if a user has admin privileges"""
        try:
            user = self.user_service.get_user_by_id(user_id)
            return user is not None and user.get('is_admin', False)
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return False 

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token from the Authorization header
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Get the JWT secret key - use the same lookup logic as AuthService
        jwt_secret = (
            os.getenv("JWT_SECRET_KEY") or 
            os.getenv("FLASK_SECRET_KEY") or 
            os.getenv("SECRET_KEY") or
            "dev-secret-key-change-in-production"
        )
        
        # Decode the token
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get the user from the database
        from services import get_neo4j_service
        neo4j_service = get_neo4j_service()
        user = neo4j_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is disabled
        if user.get("disabled", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        ) 