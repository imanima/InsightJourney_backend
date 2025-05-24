from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import get_neo4j_service

taxonomy_bp = Blueprint('taxonomy', __name__)
neo4j_service = get_neo4j_service()
logger = logging.getLogger(__name__)

@taxonomy_bp.route('/classify-topic', methods=['POST'])
@jwt_required()
def classify_topic():
    """
    Classify a topic with a taxonomy node. If taxonomy_name is not provided,
    the system will attempt to find the best matching taxonomy.
    
    Request body:
    {
        "topic_name": "string", // required
        "taxonomy_name": "string" // optional
    }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        logger.warning(f"No data provided in request to classify topic by user {current_user}")
        return jsonify({"error": "No data provided"}), 400
    
    topic_name = data.get('topic_name')
    taxonomy_name = data.get('taxonomy_name')  # Optional
    
    if not topic_name:
        logger.warning(f"Missing topic_name in request by user {current_user}")
        return jsonify({"error": "Missing topic_name"}), 400
    
    try:
        logger.info(f"User {current_user} is classifying topic '{topic_name}' with taxonomy '{taxonomy_name or 'auto'}'")
        success = neo4j_service.classify_topic_with_taxonomy(topic_name, taxonomy_name)
        
        if success:
            logger.info(f"Successfully classified topic '{topic_name}' for user {current_user}")
            return jsonify({"message": "Topic classified successfully"}), 200
        else:
            logger.warning(f"Failed to classify topic '{topic_name}' for user {current_user}")
            return jsonify({"error": "Topic classification failed"}), 500
            
    except Exception as e:
        logger.error(f"Error classifying topic for user {current_user}: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@taxonomy_bp.route('/relate-taxonomies', methods=['POST'])
@jwt_required()
def relate_taxonomies():
    """
    Create a relationship between two taxonomy nodes.
    
    Request body:
    {
        "parent_name": "string", // required
        "child_name": "string", // required
        "relationship_type": "string" // optional, defaults to "PARENT_OF"
    }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        logger.warning(f"No data provided in request to relate taxonomies by user {current_user}")
        return jsonify({"error": "No data provided"}), 400
    
    parent_name = data.get('parent_name')
    child_name = data.get('child_name')
    relationship_type = data.get('relationship_type', 'PARENT_OF')
    
    if not parent_name or not child_name:
        logger.warning(f"Missing parent_name or child_name in request by user {current_user}")
        return jsonify({"error": "Missing parent_name or child_name"}), 400
    
    try:
        logger.info(f"User {current_user} is creating relationship '{relationship_type}' from '{parent_name}' to '{child_name}'")
        success = neo4j_service.relate_taxonomy_nodes(parent_name, child_name, relationship_type)
        
        if success:
            logger.info(f"Successfully created taxonomy relationship for user {current_user}")
            return jsonify({"message": "Taxonomy relationship created successfully"}), 200
        else:
            logger.warning(f"Failed to create taxonomy relationship for user {current_user}")
            return jsonify({"error": "Taxonomy relationship creation failed"}), 500
            
    except Exception as e:
        logger.error(f"Error creating taxonomy relationship for user {current_user}: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@taxonomy_bp.route('/taxonomies', methods=['GET'])
@jwt_required()
def get_taxonomies():
    """
    Get all available taxonomy nodes.
    """
    current_user = get_jwt_identity()
    logger.info(f"User {current_user} requesting all taxonomy nodes")
    
    try:
        taxonomies = neo4j_service.get_all_taxonomies()
        return jsonify({"taxonomies": taxonomies}), 200
    except Exception as e:
        logger.error(f"Error retrieving taxonomies: {str(e)}")
        return jsonify({"error": "Failed to retrieve taxonomies"}), 500 