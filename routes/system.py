"""
System routes for health checks and system status.
"""

from flask import Blueprint, jsonify
from services import get_neo4j_service
import logging
from datetime import datetime

# Create blueprint
system_bp = Blueprint('system', __name__)

# Configure logger
logger = logging.getLogger(__name__)

@system_bp.route('/health', methods=['GET'])
def health_check():
    """Check system health status"""
    try:
        # Initialize services
        neo4j_service = get_neo4j_service()
        
        # Check Neo4j connection
        db_status = "up" if neo4j_service.check_connection() else "down"
        
        return jsonify({
            "status": "healthy",
            "services": {
                "api": "up",
                "database": db_status,
                "analysis": "up",
                "websocket": "up"
            },
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "api": "up",
                "database": "down",
                "analysis": "unknown",
                "websocket": "unknown"
            }
        }), 500

@system_bp.route('/health/components', methods=['GET'])
def component_health():
    """Get detailed health status of system components"""
    try:
        # Initialize services
        neo4j_service = get_neo4j_service()
        
        # Check Neo4j
        neo4j_status = "up" if neo4j_service.check_connection() else "down"
        neo4j_version = neo4j_service.get_version() if neo4j_status == "up" else "unknown"
        
        return jsonify({
            "components": {
                "neo4j": {
                    "status": neo4j_status,
                    "version": neo4j_version,
                    "response_time": "50ms"  # TODO: Implement actual response time measurement
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Component health check failed: {str(e)}")
        return jsonify({
            "error": str(e),
            "components": {
                "neo4j": {
                    "status": "down",
                    "version": "unknown",
                    "response_time": "unknown"
                }
            }
        }), 500 