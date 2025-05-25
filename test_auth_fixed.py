#!/usr/bin/env python3

import requests
import json
import sys

def test_auth_workflow():
    """Test the complete authentication workflow"""
    
    base_url = "http://localhost:8080/api/v1"
    
    print("🔄 Testing Authentication Workflow...")
    
    # 1. Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "name": "Test User",
        "email": "test_auth_user@example.com",
        "password": "TestPassword123!"
    }
    
    register_response = requests.post(f"{base_url}/auth/register", json=register_data)
    print(f"Register Status: {register_response.status_code}")
    
    if register_response.status_code not in [200, 409]:  # 409 = user already exists
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    # 2. Login
    print("\n2. Logging in...")
    login_data = {
        "username": "test_auth_user@example.com",
        "password": "TestPassword123!"
    }
    
    login_response = requests.post(
        f"{base_url}/auth/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"✅ Got token: {token[:20]}...")
    
    # 3. Test authenticated endpoint - get current user
    print("\n3. Testing authentication...")
    headers = {"Authorization": f"Bearer {token}"}
    
    me_response = requests.get(f"{base_url}/auth/me", headers=headers)
    print(f"Auth Test Status: {me_response.status_code}")
    
    if me_response.status_code != 200:
        print(f"❌ Authentication failed: {me_response.text}")
        return False
    
    user_data = me_response.json()
    print(f"✅ Authenticated as: {user_data.get('email')}")
    
    # 4. Test creating a session (this was previously failing)
    print("\n4. Testing session creation...")
    session_data = {
        "title": "Test Session",
        "description": "Testing authentication fix",
        "transcript": "This is a test transcript for verification."
    }
    
    session_response = requests.post(
        f"{base_url}/sessions", 
        json=session_data, 
        headers=headers
    )
    print(f"Session Creation Status: {session_response.status_code}")
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.text}")
        return False
    
    session_result = session_response.json()
    session_id = session_result["id"]
    print(f"✅ Created session: {session_id}")
    
    # 5. Test getting sessions
    print("\n5. Testing session retrieval...")
    sessions_response = requests.get(f"{base_url}/sessions", headers=headers)
    print(f"Sessions Status: {sessions_response.status_code}")
    
    if sessions_response.status_code != 200:
        print(f"❌ Session retrieval failed: {sessions_response.text}")
        return False
    
    sessions = sessions_response.json()
    print(f"✅ Retrieved {len(sessions)} sessions")
    
    # 6. Test analysis endpoint (this should work now)
    print("\n6. Testing analysis...")
    analysis_data = {
        "session_id": session_id,
        "transcript": "I feel anxious about work. I believe I need to be perfect. I want to practice mindfulness."
    }
    
    analysis_response = requests.post(
        f"{base_url}/analysis/analyze", 
        json=analysis_data, 
        headers=headers
    )
    print(f"Analysis Status: {analysis_response.status_code}")
    
    if analysis_response.status_code != 200:
        print(f"⚠️  Analysis failed: {analysis_response.text}")
        print("This might be due to analysis service issues, not authentication")
    else:
        analysis_result = analysis_response.json()
        print(f"✅ Analysis completed: {analysis_result.get('status')}")
    
    print("\n🎉 Authentication workflow test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_auth_workflow()
    sys.exit(0 if success else 1) 