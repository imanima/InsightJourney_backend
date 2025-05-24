"""
Provides service initialization to ensure consistent configuration across the application.
"""

import os
from .neo4j_service import Neo4jService
from .session_service import SessionService
from .file_service import FileService
from .user_service import UserService
import logging
from typing import Any, Dict, Optional
from flask import current_app
from dotenv import load_dotenv

# Singleton service instances
_neo4j_service = None
_session_service = None
_file_service = None
_user_service = None
_admin_service = None
_auth_service = None

def get_neo4j_service():
    """Get or create a Neo4j service singleton instance"""
    global _neo4j_service
    if _neo4j_service is None:
        load_dotenv()
        
        # Get Neo4j configuration from environment
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        # Check for both NEO4J_USER and NEO4J_USERNAME for compatibility
        user = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        _neo4j_service = Neo4jService(uri=uri, user=user, password=password)
    return _neo4j_service

def get_session_service():
    """Get or create a session service singleton instance"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService(get_neo4j_service())
    return _session_service

def get_file_service():
    """Get or create a file service singleton instance"""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service

def get_user_service():
    """Get or create a user service singleton instance"""
    global _user_service
    if _user_service is None:
        _user_service = UserService(get_neo4j_service())
    return _user_service

def get_admin_service():
    """Get or create an admin service singleton instance"""
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service

# Import auth service and create factory function
try:
    from .auth_service import AuthService
    
    def get_auth_service():
        """Get or create an auth service singleton instance"""
        global _auth_service
        if _auth_service is None:
            # Load environment variables
            load_dotenv()
            
            # Look for secret key in multiple possible environment variables
            secret_key = (
                os.getenv("JWT_SECRET_KEY") or 
                os.getenv("FLASK_SECRET_KEY") or 
                os.getenv("SECRET_KEY") or
                "dev-secret-key-change-in-production"
            )
            
            # Get token expiry time (in hours)
            try:
                token_expiry = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "24"))
            except ValueError:
                token_expiry = 24
                logging.getLogger(__name__).warning(
                    "Invalid JWT_ACCESS_TOKEN_EXPIRES_HOURS value, using default: 24 hours"
                )
            
            # Create service with neo4j connection
            try:
                neo4j_service = get_neo4j_service()
                _auth_service = AuthService(neo4j_service, secret_key, token_expiry)
                logging.getLogger(__name__).info("Auth service initialized successfully")
            except Exception as e:
                logging.getLogger(__name__).error(f"Error initializing auth service: {str(e)}")
                raise
        
        return _auth_service
        
except ImportError:
    logging.getLogger(__name__).warning("AuthService import failed, creating stub")
    
    def get_auth_service():
        """Get auth service stub instance"""
        raise RuntimeError("AuthService is not available")

# ---------------------------------------------------------------------------
# Service stubs for optional dependencies
# ---------------------------------------------------------------------------

def _admin_service_stub(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    logging.getLogger(__name__).warning("AdminService import failed, creating stub")
    return {}

def _analysis_service_stub(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    logging.getLogger(__name__).warning("AnalysisService import failed, function not available")
    return {}

# ---------------------------------------------------------------------------
# Service imports with fallbacks
# ---------------------------------------------------------------------------

try:
    from .admin_service import AdminService
except ImportError:
    _admin_service = _admin_service_stub

try:
    from .analysis_service import analyze_transcript, extract_elements
except ImportError:
    analyze_transcript = _analysis_service_stub
    extract_elements = _analysis_service_stub

try:
    from .action_item_service import ActionItemService
    _action_item_service = None
    
    def get_action_item_service():
        """Get or create an action item service singleton instance"""
        global _action_item_service
        if _action_item_service is None:
            _action_item_service = ActionItemService(get_neo4j_service())
        return _action_item_service
        
except ImportError:
    logging.getLogger(__name__).warning("ActionItemService import failed, creating stub")
    
    # Create a stub service for compatibility
    class ActionItemServiceStub:
        def create_action_item(self, session_id, data):
            return {"id": "stub-id", "title": data.get("title", ""), "created": True}
        
        def get_action_items(self, session_id):
            return []
        
        def update_action_item(self, session_id, action_item_id, data):
            return {"id": action_item_id, "updated": True}
        
        def delete_action_item(self, session_id, action_item_id):
            return True
    
    _action_item_service = ActionItemServiceStub()
    
    def get_action_item_service():
        """Get action item service stub instance"""
        global _action_item_service
        return _action_item_service 

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "analyze_transcript",
    "extract_elements",
    "get_neo4j_service",
    "get_session_service",
    "get_file_service",
    "get_user_service",
    "get_auth_service",
    "get_admin_service"
] 