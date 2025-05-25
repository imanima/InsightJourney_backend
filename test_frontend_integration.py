#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests the API endpoints through the Next.js frontend proxy to verify the integration is working.
"""

import requests
import json
import uuid
import time

# Configuration
FRONTEND_URL = "http://localhost:4000"
PROXY_BASE = f"{FRONTEND_URL}/api/proxy"

class FrontendIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def log(self, message: str, success: bool = True):
        """Log test results"""
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    def test_registration(self):
        """Test user registration through frontend proxy"""
        print("\n🔧 Testing User Registration via Frontend Proxy")
        print("-" * 60)
        
        test_email = f"integration_test_{uuid.uuid4().hex[:8]}@example.com"
        
        try:
            response = self.session.post(
                f"{PROXY_BASE}/auth/register",
                json={
                    "email": test_email,
                    "password": "IntegrationTest123!",
                    "name": "Integration Test User"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Registration successful: {data.get('email')}")
                return test_email, "IntegrationTest123!"
            else:
                self.log(f"Registration failed: {response.status_code} - {response.text}", False)
                return None, None
                
        except Exception as e:
            self.log(f"Registration error: {str(e)}", False)
            return None, None
    
    def test_login(self, email: str, password: str):
        """Test user login through frontend proxy"""
        print("\n🔑 Testing User Login via Frontend Proxy")
        print("-" * 60)
        
        try:
            # Test login with form data (OAuth2 requirement)
            response = self.session.post(
                f"{PROXY_BASE}/auth/login",
                data={
                    "username": email,  # OAuth2 uses 'username' field
                    "password": password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.auth_token = token
                    
                    # Set the token as a cookie (like the frontend would do)
                    # This simulates what setAuthToken() does in the frontend
                    self.session.cookies.set('auth_token', token, path='/')
                    
                    # Also set Authorization header for API calls
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    
                    self.log(f"Login successful, got auth token and set cookie")
                    return True
                else:
                    self.log("Login successful but no token received", False)
                    return False
            else:
                self.log(f"Login failed: {response.status_code} - {response.text}", False)
                return False
                
        except Exception as e:
            self.log(f"Login error: {str(e)}", False)
            return False
    
    def test_session_creation(self):
        """Test session creation through frontend proxy"""
        print("\n📝 Testing Session Creation via Frontend Proxy")
        print("-" * 60)
        
        try:
            transcript = """
            [00:00] Therapist: How are you feeling today?
            [00:05] Client: I'm feeling anxious about upcoming work presentations.
            [00:15] Therapist: Can you tell me more about that anxiety?
            [00:25] Client: I worry that I'll forget what to say and embarrass myself.
            """
            
            # Debug: Print current session headers
            print(f"🔍 Current session headers: {dict(self.session.headers)}")
            print(f"🔍 Current session cookies: {dict(self.session.cookies)}")
            print(f"🔍 Auth token: {self.auth_token[:20] if self.auth_token else 'None'}...")
            
            response = self.session.post(
                f"{PROXY_BASE}/sessions",
                json={
                    "title": "Frontend Integration Test Session",
                    "description": "Testing session creation through frontend",
                    "transcript": transcript.strip()
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 Response status: {response.status_code}")
            print(f"🔍 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("id")
                self.log(f"Session created successfully: {session_id}")
                return session_id, transcript.strip()
            else:
                self.log(f"Session creation failed: {response.status_code} - {response.text}", False)
                return None, None
                
        except Exception as e:
            self.log(f"Session creation error: {str(e)}", False)
            return None, None
    
    def test_analysis(self, session_id: str, transcript: str):
        """Test analysis through frontend proxy"""
        print("\n🧠 Testing Analysis via Frontend Proxy")
        print("-" * 60)
        
        try:
            response = self.session.post(
                f"{PROXY_BASE}/analysis/analyze",
                json={
                    "session_id": session_id,
                    "transcript": transcript
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", {})
                self.log(f"Analysis completed successfully")
                
                # Show analysis results summary
                for element_type, elements in results.items():
                    count = len(elements) if isinstance(elements, list) else 0
                    print(f"  • {element_type}: {count} items")
                    
                return True
            else:
                self.log(f"Analysis failed: {response.status_code} - {response.text}", False)
                return False
                
        except Exception as e:
            self.log(f"Analysis error: {str(e)}", False)
            return False
    
    def test_elements_retrieval(self, session_id: str):
        """Test retrieving analysis elements through frontend proxy"""
        print("\n📊 Testing Elements Retrieval via Frontend Proxy")
        print("-" * 60)
        
        try:
            response = self.session.get(
                f"{PROXY_BASE}/analysis/{session_id}/elements"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Elements retrieved successfully")
                
                # Show elements summary
                for element_type, elements in data.items():
                    count = len(elements) if isinstance(elements, list) else 0
                    print(f"  • {element_type}: {count} items")
                    if count > 0 and isinstance(elements, list):
                        print(f"    Sample: {elements[0]}")
                        
                return True
            else:
                self.log(f"Elements retrieval failed: {response.status_code} - {response.text}", False)
                return False
                
        except Exception as e:
            self.log(f"Elements retrieval error: {str(e)}", False)
            return False
    
    def test_text_analysis_workflow(self):
        """Test the complete text analysis workflow through frontend"""
        print("\n📝 Testing Text Analysis Workflow via Frontend")
        print("-" * 60)
        
        try:
            # Test transcript for analysis
            test_transcript = """
            [00:00] Therapist: How are you feeling today?
            [00:05] Client: I'm feeling quite anxious about my upcoming presentation.
            [00:15] Therapist: Can you tell me more about that anxiety?
            [00:25] Client: I worry that I'll forget what to say and embarrass myself.
            [00:35] Therapist: That sounds like a challenging feeling to carry.
            [00:45] Client: Yes, it's been keeping me up at night.
            """
            
            # Step 1: Create session with transcript (simulating directAnalysis)
            session_data = {
                "title": "Text Analysis Test Session",
                "description": "Testing text analysis workflow",
                "transcript": test_transcript.strip()
            }
            
            print("🔍 Creating session with transcript...")
            response = self.session.post(
                f"{PROXY_BASE}/sessions",
                json=session_data
            )
            
            if response.status_code != 200:
                print(f"❌ Session creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            session_data = response.json()
            session_id = session_data.get("id")
            print(f"✅ Session created: {session_id}")
            
            # Step 2: Run analysis on the session
            print("🔍 Running analysis...")
            analysis_response = self.session.post(
                f"{PROXY_BASE}/analysis/analyze",
                json={
                    "session_id": session_id,
                    "transcript": test_transcript.strip()
                }
            )
            
            if analysis_response.status_code != 200:
                print(f"❌ Analysis failed: {analysis_response.status_code}")
                print(f"Response: {analysis_response.text}")
                return False
            
            analysis_data = analysis_response.json()
            print(f"✅ Analysis completed: {analysis_data.get('status')}")
            
            # Step 3: Retrieve analysis elements
            print("🔍 Retrieving analysis elements...")
            elements_response = self.session.get(
                f"{PROXY_BASE}/analysis/{session_id}/elements"
            )
            
            if elements_response.status_code != 200:
                print(f"❌ Elements retrieval failed: {elements_response.status_code}")
                print(f"Response: {elements_response.text}")
                return False
            
            elements_data = elements_response.json()
            print(f"✅ Elements retrieved successfully")
            print(f"  • emotions: {len(elements_data.get('emotions', []))} items")
            print(f"  • insights: {len(elements_data.get('insights', []))} items")
            print(f"  • beliefs: {len(elements_data.get('beliefs', []))} items")
            print(f"  • challenges: {len(elements_data.get('challenges', []))} items")
            
            return True
            
        except Exception as e:
            print(f"❌ Text analysis workflow failed: {str(e)}")
            return False
    
    def run_integration_test(self):
        """Run the complete frontend integration test"""
        print("🌐 FRONTEND-BACKEND INTEGRATION TEST")
        print("=" * 80)
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Proxy Base: {PROXY_BASE}")
        print("=" * 80)
        
        # Test registration
        email, password = self.test_registration()
        if not email:
            print("\n❌ Integration test failed at registration step")
            return False
        
        # Wait a moment for user creation to complete
        time.sleep(1)
        
        # Test login
        if not self.test_login(email, password):
            print("\n❌ Integration test failed at login step")
            return False
        
        # Test session creation
        session_id, transcript = self.test_session_creation()
        if not session_id:
            print("\n❌ Integration test failed at session creation step")
            return False
        
        # Test analysis
        if not self.test_analysis(session_id, transcript):
            print("\n❌ Integration test failed at analysis step")
            return False
        
        # Test elements retrieval
        if not self.test_elements_retrieval(session_id):
            print("\n❌ Integration test failed at elements retrieval step")
            return False
        
        # Test text analysis workflow
        if not self.test_text_analysis_workflow():
            print("\n❌ Integration test failed at text analysis workflow step")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 ALL FRONTEND INTEGRATION TESTS PASSED!")
        print("✅ Frontend proxy is correctly communicating with backend")
        print("✅ Authentication flow is working")
        print("✅ Session creation is working") 
        print("✅ OpenAI analysis is working")
        print("✅ Neo4j storage and retrieval is working")
        print("=" * 80)
        
        return True

def main():
    tester = FrontendIntegrationTester()
    success = tester.run_integration_test()
    
    if success:
        print("\n🌟 Frontend is ready for use!")
        print(f"🔗 Visit: {FRONTEND_URL}")
        print("📱 You can now test the full application in your browser")
    else:
        print("\n⚠️ Integration test failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 