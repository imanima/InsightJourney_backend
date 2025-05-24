import os
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = None

    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            logger.info("Connected to Neo4j database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            return False

    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def get_session(self):
        """Get a Neo4j session"""
        if not self.driver:
            self.connect()
        return self.driver.session()

# Create a singleton instance
neo4j_connection = Neo4jConnection()

def get_neo4j_driver():
    """Get or create Neo4j driver instance with proper error handling"""
    try:
        # Get environment variables
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')

        # Validate environment variables
        if not uri or uri == 'your_neo4j_uri':
            raise ValueError("NEO4J_URI not properly configured in .env file")
        if not username or username == 'your_neo4j_username':
            raise ValueError("NEO4J_USERNAME not properly configured in .env file")
        if not password or password == 'your_neo4j_password':
            raise ValueError("NEO4J_PASSWORD not properly configured in .env file")

        logger.info(f"Connecting to Neo4j at {uri}")
        
        # Validate URI scheme
        valid_schemes = ['bolt', 'bolt+ssc', 'bolt+s', 'neo4j', 'neo4j+ssc', 'neo4j+s']
        uri_scheme = uri.split('://')[0] if '://' in uri else ''
        if uri_scheme not in valid_schemes:
            raise ValueError(f"Invalid URI scheme '{uri_scheme}'. Must be one of: {', '.join(valid_schemes)}")

        # Create driver with validated credentials
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Verify connection
        with driver.session() as session:
            session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {str(e)}")
        raise
