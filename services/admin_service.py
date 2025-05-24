import logging
import os
from models.user_settings import UserSettings, AnalysisElement
from services.constants import DEFAULT_ANALYSIS_ELEMENTS, GPT_MODEL_CONFIGS, DEFAULT_SETTINGS
from typing import Optional, List, Dict, Any
from models import db
from flask_login import current_user
from flask import current_app
from services.neo4j_utils import get_neo4j_driver, neo4j_connection
from services.neo4j_service import save_user_settings, get_user_settings, delete_user_settings
from models.user import User

logger = logging.getLogger(__name__)

def create_folders(app):
    """Create necessary folders if they don't exist"""
    folders = [
        app.config['UPLOAD_FOLDER'],
        app.config['TRANSCRIPT_FOLDER'],
        app.config['ANALYSIS_FOLDER']
    ]
    
    for folder in folders:
        try:
            if not os.path.exists(folder):
                os.makedirs(folder, mode=0o755, exist_ok=True)
                logger.info(f"Created directory: {folder}")
            else:
                # Ensure proper permissions on existing folders
                os.chmod(folder, 0o755)
                logger.info(f"Updated permissions for existing directory: {folder}")
        except Exception as e:
            logger.error(f"Error creating/updating directory {folder}: {e}")
            # Log error but don't raise - these folders are not critical for database operation
            continue

class AdminService:
    def __init__(self):
        self.model_configs = GPT_MODEL_CONFIGS
        self._initialize_default_elements()

    def _initialize_default_elements(self):
        """Initialize default analysis elements"""
        self.default_elements = DEFAULT_ANALYSIS_ELEMENTS

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available GPT models with their configurations"""
        return [
            {
                'id': model_id,
                'description': config['description'],
                'max_tokens': config['max_tokens'],
                'default_temp': config['default_temp']
            }
            for model_id, config in self.model_configs.items()
        ]

    def validate_model_settings(self, settings: Dict[str, Any]) -> None:
        """Validate GPT model settings"""
        model = settings.get('gpt_model')
        if model not in self.model_configs:
            raise ValueError(f"Invalid GPT model. Must be one of: {', '.join(self.model_configs.keys())}")
        
        max_tokens = settings.get('max_tokens', 0)
        model_config = self.model_configs[model]
        if max_tokens > model_config['max_tokens']:
            raise ValueError(f"Max tokens ({max_tokens}) exceeds model limit ({model_config['max_tokens']})")
        
        temperature = settings.get('temperature', 0)
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")

    @staticmethod
    def get_settings(user_id: str) -> Optional[UserSettings]:
        """Get user settings"""
        try:
            # Get settings from database
            settings = UserSettings.query.filter_by(user_id=user_id).first()
            if not settings:
                # Create default settings
                settings = UserSettings(
                    user_id=user_id,
                    max_sessions=DEFAULT_SETTINGS['max_sessions'],
                    max_duration=DEFAULT_SETTINGS['max_duration'],
                    allowed_file_types=DEFAULT_SETTINGS['allowed_file_types'],
                    gpt_model=DEFAULT_SETTINGS['gpt_model'],
                    max_tokens=DEFAULT_SETTINGS['max_tokens'],
                    temperature=DEFAULT_SETTINGS['temperature'],
                    system_prompt_template=DEFAULT_SETTINGS['system_prompt_template'],
                    analysis_prompt_template=DEFAULT_SETTINGS['analysis_prompt_template'],
                    analysis_elements=DEFAULT_ANALYSIS_ELEMENTS
                )
                db.session.add(settings)
                db.session.commit()
            return settings
        except Exception as e:
            logger.error(f"Error getting settings for user {user_id}: {str(e)}")
            return None

    @staticmethod
    def update_settings(settings_data: Dict[str, Any], user_id: str) -> bool:
        """Update user settings"""
        try:
            settings = AdminService.get_settings(user_id)
            if not settings:
                return False

            # Update settings
            for key, value in settings_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)

            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating settings for user {user_id}: {str(e)}")
            return False

    @staticmethod
    def get_enabled_elements(user_id: str) -> List[Dict[str, Any]]:
        """Get enabled analysis elements for a user"""
        try:
            settings = AdminService.get_settings(user_id)
            if not settings:
                return []
            return [element for element in settings.analysis_elements if element.get('enabled', True)]
        except Exception as e:
            logger.error(f"Error getting enabled elements for user {user_id}: {str(e)}")
            return []

    @staticmethod
    def get_element_by_name(element_name: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific analysis element by name"""
        try:
            settings = AdminService.get_settings(user_id)
            if not settings:
                return None
            for element in settings.analysis_elements:
                if element.get('name') == element_name:
                    return element
            return None
        except Exception as e:
            logger.error(f"Error getting element {element_name} for user {user_id}: {str(e)}")
            return None

    @staticmethod
    def toggle_element(element_name: str, enabled_state: bool, user_id: str) -> bool:
        """Toggle an analysis element's enabled state"""
        try:
            settings = AdminService.get_settings(user_id)
            if not settings:
                return False

            for element in settings.analysis_elements:
                if element.get('name') == element_name:
                    element['enabled'] = enabled_state
                    db.session.commit()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error toggling element {element_name} for user {user_id}: {str(e)}")
            return False

    @staticmethod
    def list_users(admin_user: User) -> List[Dict[str, Any]]:
        """List all users (admin only)"""
        if not admin_user.is_admin:
            logger.warning(f"Non-admin user {admin_user.id} attempted to list users")
            return []

        try:
            users = User.query.all()
            return [
                {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'is_admin': user.is_admin,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return []

    @staticmethod
    def update_user_role(admin_user: User, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user role (admin only)"""
        if not admin_user.is_admin:
            logger.warning(f"Non-admin user {admin_user.id} attempted to update user role")
            return False

        try:
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return False

            if 'role' in user_data:
                user.is_admin = user_data['role'].lower() == 'admin'
                db.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user {user_id} role: {str(e)}")
            return False

# Create a singleton instance
admin_service = AdminService() 