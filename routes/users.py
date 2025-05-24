from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import get_neo4j_service
import logging

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')
neo4j_service = get_neo4j_service()

@users_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_user():
    """Delete the current user's account"""
    try:
        user_id = get_jwt_identity()
        success = neo4j_service.delete_user(user_id)
        
        if not success:
            return jsonify({'error': 'Failed to delete user'}), 500
            
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the current user's profile"""
    try:
        user_id = get_jwt_identity()
        user = neo4j_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'is_admin': user.get('is_admin', False)
        }), 200
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({'error': str(e)}), 500

@users_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update the current user's settings"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Get current settings
        settings = neo4j_service.get_user_settings(user_id) or {}
        
        # Update with new values
        if 'max_sessions' in data:
            settings['max_sessions'] = data['max_sessions']
        if 'max_duration' in data:
            settings['max_duration'] = data['max_duration']
        if 'allowed_file_types' in data:
            settings['allowed_file_types'] = data['allowed_file_types']
            
        # Save settings
        success = neo4j_service.save_user_settings(user_id, settings)
        
        if not success:
            return jsonify({'error': 'Failed to save settings'}), 500
            
        return jsonify(settings), 200
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        return jsonify({'error': str(e)}), 500 