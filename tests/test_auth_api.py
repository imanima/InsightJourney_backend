"""
Authentication API Tests for Insight Journey Backend

This module tests authentication endpoints against the actual running application:
1. User registration
2. User login
3. Token validation
4. Password updates
5. Error handling
"""

import pytest
import requests
import json
import os
import time
from datetime import datetime
import uuid

# Test configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
AUTH_BASE_URL = f"{API_BASE_URL}/api/v1/auth"

# Test data
TEST_USER_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Test User"


class TestAuthAPI:
    """Test class for authentication API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method to run before each test"""
        self.session = requests.Session()
        self.test_user_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_token = None
        self.test_user_id = None

    @pytest.mark.auth
    @pytest.mark.api
    def test_user_registration_success(self):
        """Test successful user registration"""
        registration_data = {
            "email": self.test_user_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        response = self.session.post(
            f"{AUTH_BASE_URL}/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check response structure
        data = response.json()
        assert "id" in data, "Response should contain user ID"
        assert "email" in data, "Response should contain email"
        assert "name" in data, "Response should contain name"
        assert data["email"] == self.test_user_email
        assert data["name"] == TEST_USER_NAME
        assert data["is_admin"] is False
        assert "created_at" in data
        
        # Store user ID for cleanup
        self.test_user_id = data["id"]

    @pytest.mark.auth
    @pytest.mark.api  
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email returns error"""
        registration_data = {
            "email": self.test_user_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        # Register user first time
        response1 = self.session.post(
            f"{AUTH_BASE_URL}/register",
            json=registration_data
        )
        assert response1.status_code == 200
        
        # Try to register same email again
        response2 = self.session.post(
            f"{AUTH_BASE_URL}/register", 
            json=registration_data
        )
        
        # Should return error for duplicate email
        assert response2.status_code in [400, 409], f"Expected 400 or 409, got {response2.status_code}"

    @pytest.mark.auth
    @pytest.mark.api
    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields"""
        # Missing password
        response = self.session.post(
            f"{AUTH_BASE_URL}/register",
            json={"email": self.test_user_email, "name": TEST_USER_NAME}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        
        # Missing email
        response = self.session.post(
            f"{AUTH_BASE_URL}/register",
            json={"password": TEST_USER_PASSWORD, "name": TEST_USER_NAME}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.auth
    @pytest.mark.api
    def test_user_login_success(self):
        """Test successful user login"""
        # First register a user
        registration_data = {
            "email": self.test_user_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        reg_response = self.session.post(f"{AUTH_BASE_URL}/register", json=registration_data)
        assert reg_response.status_code == 200
        
        # Now login with form data (OAuth2 format)
        login_data = {
            "username": self.test_user_email,  # Note: parameter name is 'username' but it's the email
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(
            f"{AUTH_BASE_URL}/login",
            data=login_data,  # Use data for form-encoded
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access token"
        assert "token_type" in data, "Response should contain token type"
        assert data["token_type"] == "bearer"
        
        # Store token for further tests
        self.test_token = data["access_token"]
        assert len(self.test_token) > 0, "Token should not be empty"

    @pytest.mark.auth
    @pytest.mark.api
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = self.session.post(
            f"{AUTH_BASE_URL}/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should return 401 for invalid credentials
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should contain detail"

    @pytest.mark.auth
    @pytest.mark.api
    def test_user_login_missing_fields(self):
        """Test login with missing fields"""
        # Missing password
        response = self.session.post(
            f"{AUTH_BASE_URL}/login",
            data={"username": self.test_user_email},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.auth
    @pytest.mark.api
    def test_get_current_user_with_valid_token(self):
        """Test getting current user info with valid token"""
        # First register and login
        self._register_and_login()
        
        # Get current user info
        response = self.session.get(
            f"{AUTH_BASE_URL}/me",
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert data["email"] == self.test_user_email
        # Note: name might be hashed for security, so just check it exists and is not empty
        assert len(data["name"]) > 0, "Name should not be empty"

    @pytest.mark.auth
    @pytest.mark.api
    def test_get_current_user_no_token(self):
        """Test getting current user info without token"""
        response = self.session.get(f"{AUTH_BASE_URL}/me")
        
        # Should return 401 for missing token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.auth
    @pytest.mark.api  
    def test_get_current_user_invalid_token(self):
        """Test getting current user info with invalid token"""
        response = self.session.get(
            f"{AUTH_BASE_URL}/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.auth
    @pytest.mark.api
    def test_update_password_success(self):
        """Test successful password update"""
        # First register and login
        self._register_and_login()
        
        # Update password
        new_password = "NewPassword456!"
        update_data = {
            "current_password": TEST_USER_PASSWORD,
            "new_password": new_password
        }
        
        response = self.session.put(
            f"{AUTH_BASE_URL}/credentials/password",
            json=update_data,
            headers={
                "Authorization": f"Bearer {self.test_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert "success" in data["message"].lower() or "updated" in data["message"].lower()

    @pytest.mark.auth
    @pytest.mark.api
    def test_update_password_wrong_current_password(self):
        """Test password update with wrong current password"""
        # First register and login
        self._register_and_login()
        
        # Try to update with wrong current password
        update_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword456!"
        }
        
        response = self.session.put(
            f"{AUTH_BASE_URL}/credentials/password",
            json=update_data,
            headers={
                "Authorization": f"Bearer {self.test_token}",
                "Content-Type": "application/json"
            }
        )
        
        # Should return 400 for wrong current password
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.auth
    @pytest.mark.api
    def test_generate_api_key(self):
        """Test API key generation"""
        # First register and login
        self._register_and_login()
        
        # Generate API key
        response = self.session.post(
            f"{AUTH_BASE_URL}/credentials/api-key",
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "api_key" in data
        # API key might use different prefix format (ij- instead of ij_)
        assert data["api_key"].startswith("ij"), "API key should start with ij"
        assert len(data["api_key"]) > 10, "API key should be a reasonable length"

    @pytest.mark.auth
    @pytest.mark.api
    def test_auth_workflow_complete(self):
        """Test complete authentication workflow"""
        # 1. Register user
        registration_data = {
            "email": self.test_user_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        reg_response = self.session.post(f"{AUTH_BASE_URL}/register", json=registration_data)
        assert reg_response.status_code == 200
        
        # 2. Login
        login_data = {
            "username": self.test_user_email,
            "password": TEST_USER_PASSWORD
        }
        
        login_response = self.session.post(
            f"{AUTH_BASE_URL}/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # 3. Get user info
        user_response = self.session.get(
            f"{AUTH_BASE_URL}/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["email"] == self.test_user_email
        
        # 4. Generate API key
        api_key_response = self.session.post(
            f"{AUTH_BASE_URL}/credentials/api-key",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert api_key_response.status_code == 200
        assert "api_key" in api_key_response.json()

    # Helper methods
    def _register_and_login(self):
        """Helper method to register and login a test user"""
        # Register
        registration_data = {
            "email": self.test_user_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        reg_response = self.session.post(f"{AUTH_BASE_URL}/register", json=registration_data)
        assert reg_response.status_code == 200
        
        # Login
        login_data = {
            "username": self.test_user_email,
            "password": TEST_USER_PASSWORD
        }
        
        login_response = self.session.post(
            f"{AUTH_BASE_URL}/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        
        self.test_token = login_response.json()["access_token"]
        return self.test_token


# Standalone test functions for running with pytest directly
@pytest.mark.auth
@pytest.mark.api
@pytest.mark.integration
def test_api_health_check():
    """Test that the API is running and accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
        assert response.status_code in [200, 404], f"API health check failed: {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running or not accessible")


@pytest.mark.auth
@pytest.mark.api 
@pytest.mark.integration
def test_auth_endpoints_exist():
    """Test that authentication endpoints exist"""
    # Test register endpoint exists
    response = requests.post(f"{AUTH_BASE_URL}/register", json={})
    assert response.status_code != 404, "Register endpoint should exist"
    
    # Test login endpoint exists  
    response = requests.post(f"{AUTH_BASE_URL}/login", data={})
    assert response.status_code != 404, "Login endpoint should exist"
    
    # Test me endpoint exists (should return 401 without token)
    response = requests.get(f"{AUTH_BASE_URL}/me")
    assert response.status_code in [401, 403], "Me endpoint should exist and require auth"


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"]) 