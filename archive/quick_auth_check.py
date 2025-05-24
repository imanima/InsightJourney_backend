#!/usr/bin/env python3
"""
Quick authentication check script with detailed error diagnostics
"""
import requests
import json
import uuid
import traceback
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL (use local)
API_URL = "http://localhost:8000/api/v1"

def print_response(response, title):
    """Print response with detailed error information"""
    divider = "=" * 80
    print(f"\n{divider}")
    print(f"{title} - Status Code: {response.status_code}")
    print(f"{divider}")
    
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        # Try to parse as JSON
        data = response.json()
        print("\nResponse Body (JSON):")
        print(json.dumps(data, indent=2))
    except Exception as e:
        # Otherwise print as text
        print("\nResponse Body (Text):")
        print(response.text)
        print(f"\nError parsing JSON: {str(e)}")
    
    print("-" * 80)

def test_auth():
    """Test all authentication endpoints with detailed error handling"""
    
    # Generate unique credentials
    unique_id = str(uuid.uuid4())[:8]
    email = f"debug_{unique_id}@example.com"
    password = "Debug123!"
    name = f"Debug User {unique_id}"
    
    # 1. Test registration
    try:
        print(f"\nTesting registration with email: {email}")
        register_data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        register_response = requests.post(
            f"{API_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_response(register_response, "Registration Response")
        
        if register_response.status_code >= 500:
            print("⚠️ Registration endpoint returned server error")
            print("Debugging error...")
        
    except Exception as e:
        print(f"❌ Registration request failed with exception: {str(e)}")
        traceback.print_exc()
    
    # 2. Test login
    token = None
    try:
        print(f"\nTesting login with email: {email}")
        login_data = {
            "username": email,
            "password": password
        }
        
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print_response(login_response, "Login Response")
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ Login successful, got token: {token[:20]}...")
        elif login_response.status_code >= 500:
            print("⚠️ Login endpoint returned server error")
            print("Debugging error...")
        
    except Exception as e:
        print(f"❌ Login request failed with exception: {str(e)}")
        traceback.print_exc()
    
    # 3. Test /auth/me endpoint
    if token:
        try:
            print(f"\nTesting /auth/me endpoint with token")
            me_response = requests.get(
                f"{API_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print_response(me_response, "Me Endpoint Response")
            
            if me_response.status_code >= 500:
                print("⚠️ /auth/me endpoint returned server error")
                print("Debugging error...")
            
        except Exception as e:
            print(f"❌ /auth/me request failed with exception: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 30 + "AUTH DIAGNOSIS")
    print("=" * 80)
    
    # Print environment variables (masked for security)
    neo4j_uri = os.environ.get("NEO4J_URI", "Not set")
    neo4j_username = os.environ.get("NEO4J_USERNAME", "Not set")
    neo4j_password = "***MASKED***" if os.environ.get("NEO4J_PASSWORD") else "Not set"
    flask_secret = "***MASKED***" if os.environ.get("FLASK_SECRET_KEY") else "Not set"
    
    print(f"NEO4J_URI: {neo4j_uri}")
    print(f"NEO4J_USERNAME: {neo4j_username}")
    print(f"NEO4J_PASSWORD: {neo4j_password}")
    print(f"FLASK_SECRET_KEY: {flask_secret}")
    
    try:
        test_auth()
    except Exception as e:
        print(f"Test failed with unexpected exception: {str(e)}")
        traceback.print_exc() 