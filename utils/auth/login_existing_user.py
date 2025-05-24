#!/usr/bin/env python3
"""
Script to verify login API with existing user
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

def test_login_existing_user(email, password):
    """Test login with an existing user"""
    print(f"\nTesting LOGIN with existing user")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    # Try with dictionary approach
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
            print("✅ Login successful with dictionary form!")
            token = response.json().get("access_token")
            return token
        else:
            print("❌ Login failed with dictionary form")
            return None
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        return None

def test_with_curl_command(email, password):
    """Print a curl command that can be run directly"""
    curl_cmd = f"""
    curl -v -X POST {API_URL}/auth/login \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "username={email}&password={password}"
    """
    
    print("\nFor manual testing, you can run this curl command:")
    print(curl_cmd)

if __name__ == "__main__":
    # Previously created test users - try both
    test_users = [
        ("fix_test_a88fbdb7@example.com", "FixedTest123!"),  # From previous test
        ("frontend_test_a52a9b71@example.com", "SecurePass123!")  # From earlier test
    ]
    
    success = False
    
    for email, password in test_users:
        token = test_login_existing_user(email, password)
        if token:
            success = True
            print(f"\n✅ Successfully logged in with {email}")
            break
    
    if not success:
        print("\n❌ Could not log in with any existing test user")
        
    # Print a curl command for manual testing
    if not success:
        test_with_curl_command(test_users[0][0], test_users[0][1]) 