from services.neo4j_service import Neo4jService
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User"
}

def reset_test_user():
    try:
        # Initialize Neo4j service
        neo4j_service = Neo4jService()
        
        # Get user by email
        with neo4j_service.driver.session() as session:
            # Delete all existing test users
            session.run("""
                MATCH (u:User {email: $email})
                DETACH DELETE u
            """, email=TEST_USER["email"])
            
            # Create a new test user
            session.run("""
                CREATE (u:User {
                    userId: 'test_user',
                    email: $email,
                    name: $name,
                    password_hash: $password_hash,
                    is_admin: false,
                    created_at: datetime(),
                    last_login: datetime(),
                    status: 'active'
                })
            """, 
                email=TEST_USER["email"],
                name=TEST_USER["name"],
                password_hash=generate_password_hash(TEST_USER["password"])
            )
            
            logger.info("Successfully reset test user")
            
    except Exception as e:
        logger.error(f"Error resetting test user: {str(e)}")

if __name__ == "__main__":
    reset_test_user() 