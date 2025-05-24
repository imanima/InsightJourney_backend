"""
Configuration service for the application.
Loads configuration from environment variables and provides
access to application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfigService:
    """Service for accessing application configuration"""
    
    def __init__(self):
        # Neo4j configuration
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "insight_password")
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Analysis configuration
        self.max_sessions = int(os.getenv("MAX_SESSIONS", "50"))
        self.max_duration = int(os.getenv("MAX_DURATION", "3600"))  # seconds
        self.allowed_file_types = os.getenv("ALLOWED_FILE_TYPES", "mp3,wav,m4a").split(",")
        
        # Default analysis elements
        self.default_analysis_elements = [
            "emotions", "topics", "insights", "action_items", "beliefs", "challenges"
        ]
    
    def get_neo4j_config(self):
        """Get Neo4j configuration as a dictionary"""
        return {
            "uri": self.neo4j_uri,
            "username": self.neo4j_username,
            "password": self.neo4j_password
        }
    
    def get_openai_client(self):
        """Get OpenAI client configuration"""
        from openai import OpenAI
        # Initialize minimal OpenAI client for container compatibility
        return OpenAI(api_key=self.openai_api_key)

# Create a singleton instance
config_service = ConfigService()