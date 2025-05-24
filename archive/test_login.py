#!/usr/bin/env python3
from services import get_neo4j_service, get_auth_service

def test_login(email, password):
    # Get the auth service
    auth_service = get_auth_service()
    
    # Try to login
    print(f"Attempting to login with email: {email}")
    success, response, error_message = auth_service.login_user(email, password)
    
    if success:
        print("Login successful!")
        print(f"Token: {response.get('access_token')[:30]}...")  # Show first 30 chars of token
        
        # Show user info
        user = response.get('user', {})
        print("\nUser details:")
        print(f"User ID: {user.get('userId')}")
        print(f"Email: {user.get('email')}")
        print(f"Name: {user.get('name')}")
    else:
        print(f"Login failed: {error_message}")
    
    return success

if __name__ == "__main__":
    # Test with the user we created
    test_login("fullyhashed@example.com", "SecurePass123!") 