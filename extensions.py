"""Flask extensions module."""
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
jwt = JWTManager()
cors = CORS()

def init_app(app):
    """Initialize Flask extensions."""
    jwt.init_app(app)
    cors.init_app(app) 