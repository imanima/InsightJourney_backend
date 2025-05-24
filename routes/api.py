from flask import Blueprint, jsonify, request
from datetime import datetime
from ..services.auth_service import AuthService
from ..services.session_service import SessionService
from ..services.neo4j_service import Neo4jService
from ..services.user_service import UserService
from ..extensions import db
from services import get_neo4j_service

# Create blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize services
neo4j_service = get_neo4j_service()
user_service = UserService(neo4j_service)
auth_service = AuthService(user_service)
session_service = SessionService(db_session=db.session)

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password', 'name')):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        success, user, error = auth_service.register_user(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )
        if not success:
            return jsonify({'error': error}), 400
            
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        success, result, error = auth_service.login_user(
            email=data['email'],
            password=data['password']
        )
        if not success:
            return jsonify({'error': error}), 401
            
        user, token = result
        return jsonify({
            'token': token,
            'id': user.id,
            'email': user.email,
            'name': user.name
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401

@api_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all sessions."""
    try:
        sessions = session_service.get_all_sessions()
        return jsonify({
            'sessions': [{
                'id': session.id,
                'title': session.title,
                'date': session.created_at.isoformat(),
                'status': session.status
            } for session in sessions]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in list_sessions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new session."""
    try:
        data = request.form
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract data from form
        title = data.get('title')
        input_method = data.get('inputMethod')
        content = data.get('text') if input_method == 'text' else request.files.get('audio')

        if not all([title, input_method]):
            return jsonify({'error': 'Missing required fields'}), 400

        # TODO: Get from authenticated user
        user_id = 1
        user_email = "test@example.com"  # TODO: Get from authenticated user
        user_name = "Test User"  # TODO: Get from authenticated user

        # Create session in SQL database
        sql_session = session_service.create_session(
            user_id=user_id,
            title=title,
            content=content,
            input_method=input_method
        )

        # Create session node in Neo4j
        graph_session_id = neo4j_service.create_session_node(
            user_id=user_id,
            title=title,
            date=datetime.now(),
            transcript=content if input_method == 'text' else None
        )

        # Store graph ID in SQL session
        sql_session.graph_id = graph_session_id
        db.session.commit()

        return jsonify({
            'sessionId': sql_session.id,
            'graphId': graph_session_id,
            'status': 'created'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in create_session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data from Neo4j."""
    try:
        # First get the session from SQL to get the graph ID
        sql_session = session_service.get_session(session_id, 1)  # TODO: Get from authenticated user
        if not sql_session:
            return jsonify({'error': 'Session not found'}), 404

        # Get session data from Neo4j
        session_data = neo4j_service.get_session_data(sql_session.graph_id)
        if not session_data:
            return jsonify({'error': 'Session not found in graph database'}), 404
        return jsonify(session_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting session data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sessions/<session_id>/analyze', methods=['POST', 'OPTIONS'])
def analyze_session(session_id):
    """Analyze a session."""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Get session from database
        session = session_service.get_session(session_id, 1)  # TODO: Get from authenticated user
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Start analysis process
        success = session_service.start_analysis(session)
        if not success:
            return jsonify({'error': 'Failed to start analysis'}), 500

        return jsonify({
            'status': 'processing',
            'message': f'Analysis started for session {session_id}'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in analyze_session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
@api_bp.route('/sessions/<session_id>/analysis', methods=['GET', 'OPTIONS'])
def get_session_analysis(session_id):
    """Get session analysis results."""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Get analysis results
        analysis = session_service.get_analysis(session_id, 1)  # TODO: Get from authenticated user
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        return jsonify(analysis), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_session_analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/sessions/<session_id>/elements', methods=['PUT', 'OPTIONS'])
def update_session_elements(session_id):
    """Update session elements."""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        if 'elements' not in data:
            return jsonify({'error': 'Missing elements data'}), 400

        # TODO: Get from authenticated user
        user_id = 1  # This should come from authentication

        # Get session from database to verify it exists
        session = session_service.get_session(session_id, user_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Update elements using Neo4j service
        success = neo4j_service.update_session_with_elements(
            session_id=session.graph_id,  # Use the graph ID from the SQL session
            elements=data['elements'],
            user_id=str(user_id)
        )

        if not success:
            return jsonify({'error': 'Failed to update session elements'}), 500

        return jsonify({
            'status': 'success',
            'message': f'Successfully updated elements for session {session_id}'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in update_session_elements: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 