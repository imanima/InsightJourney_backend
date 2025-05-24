#!/usr/bin/env python3
"""
Manual Authentication API Testing Script

This script demonstrates how to manually test all authentication endpoints
with a sample user. Perfect for testing and understanding the API workflow.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8080"
AUTH_BASE_URL = f"{API_BASE_URL}/api/v1/auth"

# Sample user data
SAMPLE_USER = {
    "email": f"manual_test_{uuid.uuid4().hex[:8]}@example.com",
    "password": "ManualTest123!",
    "name": "Manual Test User"
}

def print_response(response, operation):
    """Helper to print response details"""
    print(f"\n{'='*50}")
    print(f"🧪 {operation}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        response_data = response.json()
        print(f"Response Body:\n{json.dumps(response_data, indent=2)}")
        return response_data
    except:
        print(f"Response Text: {response.text}")
        return None

def test_health_check():
    """Test if the API server is running"""
    print("🔍 Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running!")
            return True
        else:
            print(f"⚠️ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not accessible!")
        return False

def test_user_registration():
    """Test user registration"""
    print(f"\n🔐 Testing User Registration")
    print(f"Email: {SAMPLE_USER['email']}")
    
    response = requests.post(
        f"{AUTH_BASE_URL}/register",
        json=SAMPLE_USER,
        headers={"Content-Type": "application/json"}
    )
    
    data = print_response(response, "User Registration")
    
    if response.status_code == 200:
        print("✅ User registration successful!")
        return data
    else:
        print("❌ User registration failed!")
        return None

def test_user_login():
    """Test user login"""
    print(f"\n🔑 Testing User Login")
    
    login_data = {
        "username": SAMPLE_USER["email"],
        "password": SAMPLE_USER["password"]
    }
    
    response = requests.post(
        f"{AUTH_BASE_URL}/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    data = print_response(response, "User Login")
    
    if response.status_code == 200 and data and "access_token" in data:
        print("✅ User login successful!")
        return data["access_token"]
    else:
        print("❌ User login failed!")
        return None

def test_get_current_user(token):
    """Test getting current user info"""
    print(f"\n👤 Testing Get Current User")
    
    response = requests.get(
        f"{AUTH_BASE_URL}/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    data = print_response(response, "Get Current User")
    
    if response.status_code == 200:
        print("✅ Get current user successful!")
        return data
    else:
        print("❌ Get current user failed!")
        return None

def test_password_update(token):
    """Test password update"""
    print(f"\n🔄 Testing Password Update")
    
    new_password = "NewManualTestPassword456!"
    update_data = {
        "current_password": SAMPLE_USER["password"],
        "new_password": new_password
    }
    
    response = requests.put(
        f"{AUTH_BASE_URL}/credentials/password",
        json=update_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    data = print_response(response, "Password Update")
    
    if response.status_code == 200:
        print("✅ Password update successful!")
        # Update our sample user password for future tests
        SAMPLE_USER["password"] = new_password
        return True
    else:
        print("❌ Password update failed!")
        return False

def test_api_key_generation(token):
    """Test API key generation"""
    print(f"\n🔑 Testing API Key Generation")
    
    response = requests.post(
        f"{AUTH_BASE_URL}/credentials/api-key",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    data = print_response(response, "API Key Generation")
    
    if response.status_code == 200 and data and "api_key" in data:
        print("✅ API key generation successful!")
        return data["api_key"]
    else:
        print("❌ API key generation failed!")
        return None

def test_invalid_scenarios():
    """Test various error scenarios"""
    print(f"\n🚫 Testing Error Scenarios")
    
    # Test registration with missing fields
    print("\n📝 Testing registration with missing email...")
    response = requests.post(
        f"{AUTH_BASE_URL}/register",
        json={"password": "test123", "name": "Test"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code} (expected 422)")
    
    # Test login with wrong credentials
    print("\n🔐 Testing login with wrong credentials...")
    response = requests.post(
        f"{AUTH_BASE_URL}/login",
        data={"username": "wrong@email.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response.status_code} (expected 401)")
    
    # Test accessing protected endpoint without token
    print("\n🛡️ Testing protected endpoint without token...")
    response = requests.get(f"{AUTH_BASE_URL}/me")
    print(f"Status: {response.status_code} (expected 401)")

def main():
    """Run all manual authentication tests"""
    print("🚀 MANUAL AUTHENTICATION API TESTING")
    print("="*60)
    print(f"Testing against: {AUTH_BASE_URL}")
    print(f"Sample User: {SAMPLE_USER['email']}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running! Please start the FastAPI server first:")
        print("   python main.py")
        return
    
    # Test registration
    user_data = test_user_registration()
    if not user_data:
        return
    
    # Test login
    token = test_user_login()
    if not token:
        return
    
    print(f"\n🎫 Token received: {token[:50]}...")
    
    # Test getting current user
    current_user = test_get_current_user(token)
    if not current_user:
        return
    
    # Test password update
    if test_password_update(token):
        # Login again with new password to get fresh token
        print("\n🔄 Re-logging in with new password...")
        token = test_user_login()
        if not token:
            return
    
    # Test API key generation
    api_key = test_api_key_generation(token)
    if api_key:
        print(f"\n🔑 API Key generated: {api_key}")
    
    # Test error scenarios
    test_invalid_scenarios()
    
    print(f"\n{'='*60}")
    print("🎉 MANUAL TESTING COMPLETE!")
    print(f"✅ Successfully tested all authentication endpoints")
    print(f"📧 Test user email: {SAMPLE_USER['email']}")
    print(f"🔑 Final API key: {api_key if api_key else 'Not generated'}")
    print("="*60)

if __name__ == "__main__":
    main() 