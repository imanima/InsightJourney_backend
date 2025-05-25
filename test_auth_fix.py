#!/usr/bin/env python3

import requests
import json
import sys

def test_auth_fix():
    """Test that the authentication duplicate issue is fixed"""
    
    base_url = "http://localhost:8080/api/v1"
    
    print("🧪 Testing Authentication Fix")
    print("=" * 50)
    
    # Test data
    test_user = {
        "name": "Test User",
        "email": "testauth@example.com",
        "password": "TestPassword123!"
    }
    
    # 1. Register user
    print("\n1. Testing user registration...")
    register_response = requests.post(f"{base_url}/auth/register", json=test_user)
    print(f"Register Status: {register_response.status_code}")
    
    if register_response.status_code == 200:
        register_data = register_response.json()
        print(f"✅ Registration successful: {register_data.get('email')}")
        print(f"   User ID: {register_data.get('id')}")
        print(f"   Token provided: {'Yes' if register_data.get('access_token') else 'No'}")
    else:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    # 2. Test immediate login after registration
    print("\n2. Testing immediate login after registration...")
    login_data = {
        "username": test_user["email"],  # API expects 'username' not 'email'
        "password": test_user["password"]
    }
    
    login_response = requests.post(f"{base_url}/auth/login", data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"✅ Login successful!")
        print(f"   Access token provided: {'Yes' if login_data.get('access_token') else 'No'}")
        print(f"   User email: {login_data.get('user', {}).get('email')}")
        token = login_data.get('access_token')
    else:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    # 3. Test authenticated endpoint
    print("\n3. Testing authenticated endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    sessions_response = requests.get(f"{base_url}/sessions", headers=headers)
    print(f"Sessions Status: {sessions_response.status_code}")
    
    if sessions_response.status_code == 200:
        sessions_data = sessions_response.json()
        print(f"✅ Authenticated request successful!")
        print(f"   Sessions count: {len(sessions_data) if isinstance(sessions_data, list) else 'N/A'}")
    else:
        print(f"❌ Authenticated request failed: {sessions_response.text}")
        return False
    
    # 4. Test duplicate registration (should fail)
    print("\n4. Testing duplicate registration (should fail)...")
    duplicate_response = requests.post(f"{base_url}/auth/register", json=test_user)
    print(f"Duplicate Register Status: {duplicate_response.status_code}")
    
    if duplicate_response.status_code == 409:  # Conflict
        print("✅ Duplicate registration correctly rejected")
    else:
        print(f"⚠️  Expected 409 Conflict, got: {duplicate_response.status_code}")
        print(f"   Response: {duplicate_response.text}")
    
    # 5. Test login again (should still work)
    print("\n5. Testing login again (should still work)...")
    login2_response = requests.post(f"{base_url}/auth/login", data=login_data)
    print(f"Second Login Status: {login2_response.status_code}")
    
    if login2_response.status_code == 200:
        print("✅ Second login successful!")
    else:
        print(f"❌ Second login failed: {login2_response.text}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_auth_fix()
        if success:
            print("\n✅ Authentication fix verified successfully!")
        else:
            print("\n❌ Authentication issues still exist.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 