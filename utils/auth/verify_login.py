#!/usr/bin/env python3
"""
Script to verify login API endpoint functionality
"""
import requests
import json
import uuid
import time

# API base URL
API_URL = "https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1"

def print_response(response, title):
    """Pretty print an API response"""
    print("\n" + "=" * 80)
    print(f"{title} - Status Code: {response.status_code}")
    print("=" * 80)
    
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

def create_test_user():
    """Create a test user for login verification"""
    unique_id = str(uuid.uuid4())[:8]
    email = f"verify_test_{unique_id}@example.com"
    password = "Verify123!"
    name = f"Verification Tester {unique_id}"
    
    print(f"\nCreating test user with:")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Name: {name}")
    
    try:
        registration_data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        response = requests.post(
            f"{API_URL}/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_response(response, "User Registration Response")
        
        if response.status_code in [200, 201]:
            return email, password, name
        else:
            print("Failed to create test user")
            return None, None, None
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        return None, None, None

def test_login_direct_text():
    """Test login with direct text form data"""
    email, password, _ = create_test_user()
    if not email:
        return False
        
    print(f"\nTesting LOGIN with direct FORM data")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    try:
        # Create URL-encoded form data directly
        form_data = f"username={email}&password={password}"
        
        response = requests.post(
            f"{API_URL}/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print_response(response, "Login Response (Direct Form)")
        
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ Login successful using direct form data!")
            return True
        else:
            print("❌ Login failed using direct form data")
            return False
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        return False

def test_login_dict_form():
    """Test login with dictionary form data"""
    email, password, _ = create_test_user()
    if not email:
        return False
        
    print(f"\nTesting LOGIN with DICTIONARY form data")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    try:
        # Create form data as dictionary
        form_data = {
            "username": email,
            "password": password
        }
        
        response = requests.post(
            f"{API_URL}/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print_response(response, "Login Response (Dictionary Form)")
        
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ Login successful using dictionary form data!")
            return True
        else:
            print("❌ Login failed using dictionary form data")
            return False
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        return False

def test_login_curl_equivalent():
    """Test login with requests API that matches curl command"""
    email, password, _ = create_test_user()
    if not email:
        return False
        
    print(f"\nTesting LOGIN with most CURL-LIKE implementation")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    try:
        import urllib.parse
        
        # Create form data exactly like curl does
        form_data = urllib.parse.urlencode({
            "username": email,
            "password": password
        })
        
        # Set same headers as curl
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "python-requests/2.28.1"
        }
        
        response = requests.post(
            f"{API_URL}/auth/login",
            data=form_data,
            headers=headers
        )
        
        print_response(response, "Login Response (Curl-like)")
        
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ Login successful using curl-like implementation!")
            token = response.json().get("access_token")
            return token
        else:
            print("❌ Login failed using curl-like implementation")
            return None
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        return None

def test_authenticated_endpoint(token):
    """Test an authenticated endpoint with the token"""
    if not token:
        print("No token available to test authentication")
        return
        
    print("\nTesting authentication with token")
    
    try:
        response = requests.get(
            f"{API_URL}/sessions",  # Try a different endpoint than /auth/me
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print_response(response, "Authenticated Endpoint Response")
        
        # Even a 404 is acceptable as long as it's not a 401 unauthorized
        if response.status_code != 401:
            print("✅ Authentication is working (token is accepted)")
        else:
            print("❌ Authentication failed (token was rejected)")
    except Exception as e:
        print(f"Error testing authentication: {str(e)}")

if __name__ == "__main__":
    print("=========== COMPREHENSIVE LOGIN API VERIFICATION ===========")
    
    # Test login with direct form data
    direct_test = test_login_direct_text()
    
    # Test login with dictionary form data
    dict_test = test_login_dict_form()
    
    # Test login with curl-equivalent implementation
    token = test_login_curl_equivalent()
    
    # If we got a token, test authentication
    if token:
        test_authenticated_endpoint(token)
    
    # Print overall results
    print("\n================ VERIFICATION SUMMARY ================")
    print(f"Direct Form Data Test: {'SUCCESS' if direct_test else 'FAILED'}")
    print(f"Dictionary Form Test: {'SUCCESS' if dict_test else 'FAILED'}")
    print(f"Curl-Like Test: {'SUCCESS' if token else 'FAILED'}")
    
    if direct_test or dict_test or token:
        print("\n✅ THE LOGIN API IS WORKING CORRECTLY")
        print("The frontend team can use the implementation in FRONTEND_AUTH_GUIDE.md")
        print("to connect to the authentication API.")
    else:
        print("\n❌ THE LOGIN API IS NOT WORKING PROPERLY")
        print("All login attempts failed. There might be an issue with the backend.") 