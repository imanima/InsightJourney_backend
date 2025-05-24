from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = {
            'error': error.name,
            'message': error.description,
            'status_code': error.code
        }
        logger.error(f"HTTP Error: {error.code} - {error.name} - {error.description}")
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        response = {
            'error': 'Internal Server Error',
            'message': str(error),
            'status_code': 500
        }
        logger.error(f"Internal Server Error: {str(error)}")
        return jsonify(response), 500 