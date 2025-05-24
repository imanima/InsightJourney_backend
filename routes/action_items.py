from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import get_action_item_service
import logging

logger = logging.getLogger(__name__)

# Initialize service
action_item_service = get_action_item_service()

action_items_bp = Blueprint('action_items', __name__)

@action_items_bp.route('/sessions/<session_id>/action-items', methods=['POST'])
@jwt_required()
def create_action_item(session_id):
    """Create a new action item for a session"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('title', 'description', 'due_date')):
            return jsonify({'error': 'Missing required fields'}), 400

        action_item = action_item_service.create_action_item(session_id, data)
        return jsonify(action_item), 201
    except Exception as e:
        logger.error(f"Error creating action item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@action_items_bp.route('/sessions/<session_id>/action-items', methods=['GET'])
@jwt_required()
def get_action_items(session_id):
    """Get all action items for a session"""
    try:
        action_items = action_item_service.get_action_items(session_id)
        return jsonify(action_items), 200
    except Exception as e:
        logger.error(f"Error getting action items: {str(e)}")
        return jsonify({'error': str(e)}), 500

@action_items_bp.route('/sessions/<session_id>/action-items/<action_item_id>', methods=['PUT'])
@jwt_required()
def update_action_item(session_id, action_item_id):
    """Update an action item"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        action_item = action_item_service.update_action_item(session_id, action_item_id, data)
        if not action_item:
            return jsonify({'error': 'Action item not found'}), 404
        return jsonify(action_item), 200
    except Exception as e:
        logger.error(f"Error updating action item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@action_items_bp.route('/sessions/<session_id>/action-items/<action_item_id>', methods=['DELETE'])
@jwt_required()
def delete_action_item(session_id, action_item_id):
    """Delete an action item"""
    try:
        success = action_item_service.delete_action_item(session_id, action_item_id)
        if not success:
            return jsonify({'error': 'Action item not found'}), 404
        return jsonify({'message': 'Action item deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting action item: {str(e)}")
        return jsonify({'error': str(e)}), 500 