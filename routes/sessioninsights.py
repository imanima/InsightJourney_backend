from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import logging
from werkzeug.utils import secure_filename
from services.session_service import SessionService
from services.analysis_service import AnalysisService
from utils.validators import validate_request, SessionUploadSchema
from models import db, Session
from datetime import datetime

logger = logging.getLogger(__name__)

session_bp = Blueprint('session_bp', __name__)

@session_bp.route('/', methods=['GET'])
@login_required
def get_sessions():
    """Get all sessions for the current user"""
    try:
        sessions = SessionService.get_user_sessions(current_user.id)
        return jsonify(sessions)
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@session_bp.route('/<int:session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """Get a specific session"""
    try:
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(session)
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@session_bp.route('/', methods=['POST'])
@login_required
def create_session():
    """Create a new session with audio file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        session_data = request.form.to_dict()
        
        # Validate session data
        if not session_data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
            
        if not session_data.get('date'):
            return jsonify({'error': 'Date is required'}), 400
        
        # Create session
        result = SessionService.create_session(file, session_data, current_user.id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@session_bp.route('/<int:session_id>/analysis', methods=['GET'])
@login_required
def get_analysis(session_id):
    """Get analysis results for a session"""
    try:
        analysis = AnalysisService.get_analysis(session_id, current_user.id)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error getting analysis for session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@session_bp.route('/<int:session_id>/transcript', methods=['GET'])
@login_required
def get_transcript(session_id):
    """Get transcript for a session"""
    try:
        transcript = SessionService.get_transcript(session_id, current_user.id)
        if not transcript:
            return jsonify({'error': 'Transcript not found'}), 404
        return jsonify(transcript)
    except Exception as e:
        logger.error(f"Error getting transcript for session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@session_bp.route('/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Delete a session and its associated files"""
    try:
        result = SessionService.delete_session(session_id, current_user.id)
        if not result:
            return jsonify({'error': 'Failed to delete session'}), 500
        return jsonify({'message': 'Session deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/sessions/<int:session_id>/analysis', methods=['GET'])
@login_required
def get_session_analysis(session_id):
    try:
        # Verify session ownership
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get analysis
        analysis = AnalysisService.get_session_analysis(session_id, current_user.id)
        if not analysis:
            return jsonify({"error": "Analysis not found"}), 404

        return jsonify({
            "analysis": {
                "session_id": session_id,
                "timestamp": analysis.get("timestamp"),
                "emotions": analysis.get("emotions", []),
                "themes": analysis.get("themes", []),
                "insights": analysis.get("insights", []),
                "action_items": analysis.get("action_items", []),
                "summary": analysis.get("summary", "")
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting session analysis: {str(e)}")
        return jsonify({"error": "Failed to get session analysis"}), 500

@insights_bp.route('/sessions/<int:session_id>/analyze', methods=['POST'])
@login_required
def analyze_session(session_id):
    try:
        # Verify session ownership
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Check if session has a transcript
        if not session.transcript:
            return jsonify({"error": "Session has no transcript to analyze"}), 400

        # Perform analysis
        result = AnalysisService.analyze_session(session_id, current_user.id)
        if not result:
            return jsonify({"error": "Analysis failed"}), 500

        return jsonify({
            "message": "Analysis completed successfully",
            "analysis": {
                "session_id": session_id,
                "timestamp": result.get("timestamp"),
                "emotions": result.get("emotions", []),
                "themes": result.get("themes", []),
                "insights": result.get("insights", []),
                "action_items": result.get("action_items", []),
                "summary": result.get("summary", "")
            }
        }), 200
    except Exception as e:
        logger.error(f"Error analyzing session: {str(e)}")
        return jsonify({"error": "Failed to analyze session"}), 500

@insights_bp.route('/sessions/<int:session_id>/analysis', methods=['PUT'])
@login_required
def update_session_analysis(session_id):
    try:
        # Verify session ownership
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate analysis data
        required_fields = ["insights", "action_items", "sentiment", "topics"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Update analysis
        success = AnalysisService.save_analysis(session_id, current_user.id, data)
        if not success:
            return jsonify({"error": "Failed to update analysis"}), 500

        return jsonify({"message": "Analysis updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating session analysis: {str(e)}")
        return jsonify({"error": "Failed to update analysis"}), 500

@insights_bp.route('/sessions/<int:session_id>/transcript', methods=['GET'])
@login_required
def get_session_transcript(session_id):
    try:
        # Verify session ownership
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get transcript
        transcript = SessionService.retrieve_transcript(current_user.id, session_id)
        if not transcript:
            return jsonify({"error": "Transcript not found"}), 404

        return jsonify({
            "transcript": {
                "session_id": session_id,
                "content": transcript,
                "timestamp": datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting session transcript: {str(e)}")
        return jsonify({"error": "Failed to get session transcript"}), 500

@insights_bp.route('/sessions/<int:session_id>/insights', methods=['GET'])
@login_required
def get_session_insights(session_id):
    try:
        # Verify session ownership
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get analysis
        analysis = AnalysisService.get_session_analysis(session_id, current_user.id)
        if not analysis:
            return jsonify({"error": "Analysis not found"}), 404

        return jsonify({
            "insights": {
                "session_id": session_id,
                "timestamp": analysis.get("timestamp"),
                "key_insights": analysis.get("insights", []),
                "action_items": analysis.get("action_items", []),
                "themes": analysis.get("themes", []),
                "emotions": analysis.get("emotions", [])
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting session insights: {str(e)}")
        return jsonify({"error": "Failed to get session insights"}), 500

@insights_bp.route('/sessions/<int:session_id>/summary', methods=['GET'])
@login_required
def get_session_summary(session_id):
    try:
        # Verify session ownership
        session = SessionService.get_session(session_id, current_user.id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get analysis
        analysis = AnalysisService.get_session_analysis(session_id, current_user.id)
        if not analysis:
            return jsonify({"error": "Analysis not found"}), 404

        return jsonify({
            "summary": {
                "session_id": session_id,
                "timestamp": analysis.get("timestamp"),
                "content": analysis.get("summary", ""),
                "key_points": analysis.get("insights", [])[:3],  # Top 3 insights
                "action_items": analysis.get("action_items", [])
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting session summary: {str(e)}")
        return jsonify({"error": "Failed to get session summary"}), 500 