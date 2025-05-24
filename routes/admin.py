from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from services import get_neo4j_service, get_admin_service
from datetime import datetime, timedelta
from functools import wraps

# Create the blueprint with a prefix that matches our app structure
admin_bp = Blueprint('admin_bp', __name__)
logger = logging.getLogger(__name__)

# Initialize services
neo4j_service = get_neo4j_service()

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = neo4j_service.get_user_by_id(user_id)
        if not user or not user.get('is_admin', False):
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Get admin settings"""
    try:
        logger.info("Getting admin settings")
        user_id = get_jwt_identity()
        settings = neo4j_service.get_user_settings(user_id)
        if not settings:
            logger.error("Admin settings not found")
            return jsonify({'error': 'Admin settings not found'}), 404
            
        return jsonify({
            "settings": settings
        }), 200
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        return jsonify({"error": "Failed to get settings"}), 500

@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
@admin_required
def update_settings():
    """Update admin settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate settings data
        if "max_sessions" in data and not isinstance(data["max_sessions"], int):
            return jsonify({"error": "max_sessions must be an integer"}), 400
        if "max_duration" in data and not isinstance(data["max_duration"], int):
            return jsonify({"error": "max_duration must be an integer"}), 400
        if "allowed_file_types" in data and not isinstance(data["allowed_file_types"], list):
            return jsonify({"error": "allowed_file_types must be a list"}), 400
        if "analysis_elements" in data and not isinstance(data["analysis_elements"], list):
            return jsonify({"error": "analysis_elements must be a list"}), 400

        user_id = get_jwt_identity()
        success = neo4j_service.save_user_settings(user_id, data)
        if not success:
            logger.error("Error updating settings")
            return jsonify({"error": "Failed to update settings"}), 500

        logger.info("Settings updated successfully")
        return jsonify({"message": "Settings updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({"error": "Failed to update settings"}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        # Get all users from Neo4j
        with neo4j_service.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                RETURN u.id AS id, u.email AS email, u.name AS name, u.is_admin AS is_admin
                """
            )
            users = [dict(record) for record in result]
        
        return jsonify({'users': users})
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user details (admin only)"""
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Get user from Neo4j
        user = neo4j_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Update properties
        properties = {}
        if 'name' in user_data:
            properties['name'] = user_data['name']
        if 'email' in user_data:
            properties['email'] = user_data['email']
        if 'is_admin' in user_data:
            properties['is_admin'] = user_data['is_admin']
            
        # Update user in Neo4j
        updated_user = neo4j_service.update_user(user_id, **properties)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': updated_user['id'],
                'name': updated_user['name'],
                'email': updated_user['email'],
                'is_admin': updated_user.get('is_admin', False)
            }
        })
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_stats():
    """Get admin statistics"""
    try:
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
                RETURN u.id AS id, u.email AS email, u.name AS name, 
                       u.created_at AS created_at, u.last_login AS last_login
                ORDER BY u.created_at DESC LIMIT 5
                """
            )
            recent_users = [dict(record) for record in result]
            
            # Get recent sessions
            result = session.run(
                """
                MATCH (s:Session)
                RETURN s.id AS id, s.title AS title, s.user_id AS user_id,
                       s.created_at AS created_at
                ORDER BY s.created_at DESC LIMIT 5
                """
            )
            recent_sessions = [dict(record) for record in result]
            
            # Get most active users
            result = session.run(
                """
                MATCH (u:User)-[:OWNS]->(s:Session)
                WITH u, count(s) AS session_count
                RETURN u.id AS id, u.email AS email, u.name AS name,
                       session_count
                ORDER BY session_count DESC LIMIT 5
                """
            )
            active_users = [dict(record) for record in result]
            
            # Get most common topics
            result = session.run(
                """
                MATCH (t:Topic)<-[:HAS_TOPIC]-(s:Session)
                WITH t.name AS topic, count(s) AS count
                WHERE count > 0
                RETURN topic, count
                ORDER BY count DESC LIMIT 10
                """
            )
            common_topics = [dict(record) for record in result]
        
        logger.info("Admin statistics retrieved successfully")
        return jsonify({
            "stats": {
                "total_users": total_users,
                "total_sessions": total_sessions,
                "admin_users": admin_users,
                "recent_users": recent_users,
                "recent_sessions": recent_sessions,
                "active_users": active_users,
                "common_topics": common_topics
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({"error": "Failed to get admin statistics"}), 500

@admin_bp.route('/user-activities', methods=['GET'])
@jwt_required()
@admin_required
def get_user_activities():
    """Get user activity statistics"""
    try:
        # Get parameters
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        current_time = datetime.now()
        start_date = (current_time - timedelta(days=days)).timestamp() * 1000  # Convert to milliseconds
        
        # Get user activities from Neo4j
        with neo4j_service.driver.session() as session:
            # Get login activities
            result = session.run(
                """
                MATCH (u:User)
                WHERE u.last_login >= $start_date
                RETURN u.email AS email, u.last_login AS last_login
                ORDER BY u.last_login DESC
                """, 
                { 'start_date': start_date }
            )
            login_activities = [dict(record) for record in result]
            
            # Get session creation activities
            result = session.run(
                """
                MATCH (u:User)-[:OWNS]->(s:Session)
                WHERE s.created_at >= $start_date
                RETURN u.email AS email, s.id AS session_id, 
                       s.title AS session_title, s.created_at AS created_at
                ORDER BY s.created_at DESC
                """,
                { 'start_date': start_date }
            )
            session_activities = [dict(record) for record in result]
        
        logger.info(f"User activities retrieved for the last {days} days")
        return jsonify({
            "activities": {
                "login_activities": login_activities,
                "session_activities": session_activities
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting user activities: {str(e)}")
        return jsonify({"error": "Failed to get user activities"}), 500 