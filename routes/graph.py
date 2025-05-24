from flask import Blueprint, jsonify, request
from services import get_neo4j_service
from flask_jwt_extended import jwt_required

graph_bp = Blueprint('graph', __name__)
neo4j_service = get_neo4j_service()

@graph_bp.route('/export', methods=['POST'])
@jwt_required()
def export_to_neo4j():
    """Export session data to Neo4j"""
    try:
        session_id = request.json.get('session_id')
        if not session_id:
            return jsonify({
                'error': 'Session ID is required'
            }), 400
            
        # Export session data to Neo4j
        success = neo4j_service.export_session(session_id)
        if not success:
            return jsonify({
                'error': 'Failed to export session data to Neo4j'
            }), 500

        return jsonify({
            'message': 'Session data exported to Neo4j successfully',
            'data': {'session_id': session_id}
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Error exporting to Neo4j: {str(e)}'
        }), 500

@graph_bp.route('/query', methods=['POST'])
@jwt_required()
def run_query():
    """Run a Cypher query against Neo4j"""
    try:
        query = request.json.get('query')
        params = request.json.get('params', {})
        
        if not query:
            return jsonify({
                'error': 'Query is required'
            }), 400
            
        # Run the query
        results = neo4j_service.run_query(query, params)
        if results is None:
            return jsonify({
                'error': 'Failed to execute Neo4j query'
            }), 500

        return jsonify({
            'message': 'Query executed successfully',
            'data': {'results': results}
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Error executing Neo4j query: {str(e)}'
        }), 500 