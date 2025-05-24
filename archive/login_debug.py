#!/usr/bin/env python3
"""
Debug script for login API endpoint
"""
import requests
import json

# API base URL
API_URL = "https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1"

def print_response(response, title):
    """Pretty print an API response"""
    print("\n" + "=" * 80)
    print(f"{title} - Status Code: {response.status_code}")
    print("=" * 80)
    
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

def test_login_form_encoded(email, password):
    """Test login with form-urlencoded format"""
    print(f"\nTesting LOGIN with form-urlencoded (email: {email})")
    
    try:
        # Create login data as form-urlencoded
        login_data = {
            "username": email,
            "password": password
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make the request
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data,
            headers=headers
        )
        
        print_response(response, "Login Form-Urlencoded Response")
        return response
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_login_json(email, password):
    """Test login with JSON format"""
    print(f"\nTesting LOGIN with JSON (email: {email})")
    
    try:
        # Create login data as JSON
        login_data = {
            "username": email,
            "password": password
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the request
        response = requests.post(
            f"{API_URL}/auth/login",
            json=login_data,
            headers=headers
        )
        
        print_response(response, "Login JSON Response")
        return response
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_login_raw_form(email, password):
    """Test login with raw form data"""
    print(f"\nTesting LOGIN with raw form data (email: {email})")
    
    try:
        # Create raw form data
        form_data = f"username={email}&password={password}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make the request
        response = requests.post(
            f"{API_URL}/auth/login",
            data=form_data,
            headers=headers
        )
        
        print_response(response, "Login Raw Form Response")
        return response
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_token_auth(token, email):
    """Test authenticating with a token"""
    print(f"\nTesting authentication with token for {email}")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(
            f"{API_URL}/auth/me",
            headers=headers
        )
        
        print_response(response, "Authentication Response")
    except Exception as e:
        print(f"Error during authentication: {str(e)}")

if __name__ == "__main__":
    # Use the previously created test user
    email = "frontend_test_a52a9b71@example.com"
    password = "SecurePass123!"
    
    # Try different login approaches
    form_response = test_login_form_encoded(email, password)
    json_response = test_login_json(email, password)
    raw_response = test_login_raw_form(email, password)
    
    # Check if any login was successful
    token = None
    
    if form_response and form_response.status_code == 200:
        try:
            token = form_response.json().get("access_token")
            print(f"\n✅ Form-urlencoded login successful, got token: {token[:20]}...")
        except:
            pass
            
    if json_response and json_response.status_code == 200:
        try:
            token = json_response.json().get("access_token")
            print(f"\n✅ JSON login successful, got token: {token[:20]}...")
        except:
            pass
            
    if raw_response and raw_response.status_code == 200:
        try:
            token = raw_response.json().get("access_token")
            print(f"\n✅ Raw form login successful, got token: {token[:20]}...")
        except:
            pass
    
    # Test authentication if we got a token
    if token:
        test_token_auth(token, email)
    else:
        print("\n❌ All login attempts failed, couldn't get a token.") 