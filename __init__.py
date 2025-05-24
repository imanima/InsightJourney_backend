"""
Backend application package for Insight Journey.
"""

from flask import Flask
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import routes for registration (disabled for pytest compatibility)
# try:
#     from .routes import auth_bp, sessions_bp, admin_bp
#     from .routes.analysis import analysis_bp
# except ImportError as e:
#     logger.warning(f"Could not import all blueprints: {str(e)}")

# Import services (disabled for pytest compatibility)  
# try:
#     from .services import get_neo4j_service, get_auth_service, get_admin_service
# except ImportError as e:
#     logger.warning(f"Could not import all services: {str(e)}")

# Create application instance (disabled for pytest compatibility)
# from .app import create_app 