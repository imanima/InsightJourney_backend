#!/usr/bin/env python3
"""
Script to debug local server errors
"""
import requests
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Local API base URL
LOCAL_API_URL = "http://localhost:8000/api/v1"

def test_registration_with_error_details():
    """Test registration and capture error details"""
    unique_id = str(uuid.uuid4())[:8]
    email = f"debug_test_{unique_id}@example.com"
    password = "DebugTest123!"
    name = f"Debug Test {unique_id}"
    
    logger.info(f"Testing registration with email: {email}")
    
    try:
        registration_data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        # Set up session with full debugging
        session = requests.Session()
        session.hooks = {'response': lambda r, *args, **kwargs: r.raise_for_status()}
        
        # Make the request
        response = session.post(
            f"{LOCAL_API_URL}/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"Registration successful: {response.status_code}")
        logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        if e.response is not None:
            logger.error(f"Status Code: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                logger.error(f"Error Detail: {json.dumps(error_detail, indent=2)}")
            except:
                logger.error(f"Error Response: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")

def check_server_logs():
    """Suggest checking server logs"""
    print("\n" + "=" * 80)
    print("ERROR DIAGNOSIS")
    print("=" * 80)
    print("Both the local server and deployed server are returning 500 errors.")
    print("This suggests an issue in the backend code that's causing internal server errors.")
    print("\nTo fix this issue:")
    print("1. Check the server logs in the terminal where uvicorn is running")
    print("2. Look for Python tracebacks or error messages")
    print("3. The error is likely in the auth-related code (routes/auth.py or services/auth_service.py)")
    print("\nCommon issues that could cause this:")
    print("- Database connection issues with Neo4j")
    print("- Missing environment variables")
    print("- Code changes that introduced bugs")
    print("- Issues with the JWT token generation or validation")
    print("\nAfter you fix the issues in the code, you'll need to:")
    print("1. Restart the local server")
    print("2. Test again with python test_local_auth.py")
    print("3. Deploy the fixed version with ./quickdeploy.sh")

if __name__ == "__main__":
    test_registration_with_error_details()
    check_server_logs() 