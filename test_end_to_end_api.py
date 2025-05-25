#!/usr/bin/env python3
"""
End-to-End API Testing Script for Insight Journey Backend

This script tests the complete user workflow:
1. User Registration
2. User Login (get auth token)
3. Create Session with transcript
4. Analyze Session (triggers OpenAI analysis)
5. Retrieve Analysis Elements from Neo4j
6. Verify data persistence

All API calls hit the actual local backend (localhost:8080) and write to real Neo4j database.
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8080/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Test data
TEST_USER_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Test User"

# Sample therapy transcript for testing
SAMPLE_TRANSCRIPT = """
Session 1 - Anxiety and Work Stress
Date: May 24, 2025
Duration: 45 minutes
Client: Sarah

[00:00] Therapist: Hi Sarah, how are you feeling today?

[00:05] Sarah: Hi, I'm feeling quite anxious actually. Work has been really overwhelming lately.

[00:15] Therapist: I'm sorry to hear that. Can you tell me more about what's been happening at work?

[00:25] Sarah: Well, we have this big project deadline coming up, and I feel like I'm drowning in tasks. I keep worrying that I'm going to mess something up and disappoint my team.

[00:45] Therapist: That sounds like a lot of pressure. How is this anxiety affecting you physically?

[00:55] Sarah: I've been having trouble sleeping. My mind just races at night thinking about all the things I need to do. And I've been getting these tension headaches.

[01:15] Therapist: Those are common physical symptoms of anxiety. Have you noticed any patterns in when these feelings are strongest?

[01:30] Sarah: Definitely in the mornings when I'm getting ready for work, and then again in the evenings when I'm trying to wind down but my brain won't stop.

[01:50] Therapist: It sounds like your mind is having difficulty transitioning between work mode and rest mode. Let's explore some strategies that might help with that.

[02:05] Sarah: That would be really helpful. I feel like I need to learn how to turn off my work brain.

[02:20] Therapist: One technique we can try is called the "worry window." Instead of trying to suppress anxious thoughts, we designate a specific 15-minute period each day to acknowledge and process them.

[02:40] Sarah: That's interesting. So instead of fighting the thoughts, I give them a specific time?

[02:50] Therapist: Exactly. And outside of that window, when anxious thoughts arise, you acknowledge them but remind yourself that you'll address them during your designated worry time.

[03:10] Sarah: I think that could help. Sometimes I feel guilty for having these worries, like I should just be able to push them away.

[03:25] Therapist: It's completely normal to have these concerns, especially when you care deeply about your work. The goal isn't to eliminate worry entirely, but to manage it in a way that doesn't overwhelm your daily life.

[03:45] Sarah: That makes sense. I do care a lot about doing well, maybe too much sometimes.

[04:00] Therapist: What do you think drives that need to perform perfectly?

[04:10] Sarah: I guess I've always been a perfectionist. Growing up, I felt like I had to excel to get approval from my parents. Old habits, I suppose.

[04:30] Therapist: That's a really insightful connection. Those early patterns can definitely influence how we approach challenges as adults.

[04:45] Sarah: Yeah, I can see how that perfectionism is actually making my anxiety worse now.

[05:00] Therapist: For our next session, I'd like you to try the worry window technique and also practice some deep breathing exercises when you notice tension building up. How does that sound?

[05:15] Sarah: That sounds doable. I'm willing to try anything that might help me feel more balanced.

[05:25] Therapist: Great. Remember, progress takes time, and it's okay to have setbacks. You're taking important steps by being here and being open to trying new approaches.

[05:40] Sarah: Thank you. I already feel a bit better just talking about it.
"""

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.session_id = None
        
    def log_step(self, step: str, success: bool = True, data: Any = None):
        """Log each step with status and data"""
        status = "✅" if success else "❌"
        print(f"\n{status} {step}")
        if data:
            if isinstance(data, dict) and len(str(data)) > 200:
                # Truncate long responses
                print(f"   Response: {str(data)[:200]}...")
            else:
                print(f"   Response: {data}")
        print("-" * 60)
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    files: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                if files:
                    # For file uploads, don't set Content-Type header
                    headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
                    response = requests.post(url, headers=headers, files=files, data=data)
                else:
                    response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "data": {"error": str(e)}
            }
    
    def step_1_user_registration(self) -> bool:
        """Step 1: Register a new user"""
        print("🚀 Starting End-to-End API Test")
        print(f"📧 Test User Email: {TEST_USER_EMAIL}")
        
        user_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME,
            "is_admin": False
        }
        
        result = self.make_request("POST", "/auth/register", user_data)
        
        if result["success"]:
            self.user_id = result["data"].get("user_id") or result["data"].get("id")
            self.log_step("User Registration", True, result["data"])
            return True
        else:
            self.log_step("User Registration", False, result["data"])
            return False
    
    def step_2_user_login(self) -> bool:
        """Step 2: Login user and get auth token"""
        login_data = {
            "username": TEST_USER_EMAIL,  # FastAPI OAuth2 uses 'username' field
            "password": TEST_USER_PASSWORD
        }
        
        # OAuth2 login uses form data, not JSON
        # Remove Content-Type header for form data
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        
        try:
            url = f"{self.base_url}/auth/login"
            response = requests.post(url, headers=headers, data=login_data)
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            result = {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response_data
            }
        except Exception as e:
            result = {
                "success": False,
                "status_code": 0,
                "data": {"error": str(e)}
            }
        
        if result["success"]:
            self.auth_token = result["data"].get("access_token")
            if self.auth_token:
                # Add auth token to headers for subsequent requests
                self.headers["Authorization"] = f"Bearer {self.auth_token}"
                self.log_step("User Login", True, {"token_received": True, "token_type": result["data"].get("token_type")})
                return True
            else:
                self.log_step("User Login", False, "No access token received")
                return False
        else:
            self.log_step("User Login", False, result["data"])
            return False
    
    def step_3_create_session(self) -> bool:
        """Step 3: Create a new session with transcript"""
        session_data = {
            "title": "End-to-End Test Session",
            "description": "Testing complete API workflow with real transcript analysis",
            "transcript": SAMPLE_TRANSCRIPT
        }
        
        result = self.make_request("POST", "/sessions", session_data)
        
        if result["success"]:
            self.session_id = result["data"].get("id")
            self.log_step("Session Creation", True, {
                "session_id": self.session_id,
                "title": result["data"].get("title"),
                "status": result["data"].get("status")
            })
            return True
        else:
            self.log_step("Session Creation", False, result["data"])
            return False
    
    def step_4_analyze_session(self) -> bool:
        """Step 4: Trigger session analysis (OpenAI analysis + write elements to Neo4j)"""
        if not self.session_id:
            self.log_step("Session Analysis & Neo4j Write", False, "No session ID available")
            return False
        
        analysis_data = {
            "session_id": self.session_id,
            "transcript": SAMPLE_TRANSCRIPT
        }
        
        result = self.make_request("POST", "/analysis/analyze", analysis_data)
        
        if result["success"]:
            self.log_step("Session Analysis & Neo4j Write", True, {
                "session_id": result["data"].get("session_id"),
                "status": result["data"].get("status"),
                "analysis_keys": list(result["data"].get("results", {}).keys()) if result["data"].get("results") else []
            })
            return True
        else:
            self.log_step("Session Analysis & Neo4j Write", False, result["data"])
            return False
    
    def step_5_retrieve_analysis_elements(self) -> bool:
        """Step 5: Retrieve analysis elements from Neo4j (verify they were written correctly)"""
        if not self.session_id:
            self.log_step("Retrieve Analysis Elements (Verification)", False, "No session ID available")
            return False
        
        result = self.make_request("GET", f"/analysis/{self.session_id}/elements")
        
        if result["success"]:
            elements = result["data"]
            summary = {
                "emotions_count": len(elements.get("emotions", [])),
                "insights_count": len(elements.get("insights", [])),
                "beliefs_count": len(elements.get("beliefs", [])),
                "action_items_count": len(elements.get("action_items", [])),
                "challenges_count": len(elements.get("challenges", []))
            }
            
            self.log_step("Retrieve Analysis Elements (Verification)", True, summary)
            
            # Show sample elements if they exist
            if elements.get("emotions"):
                print(f"   Sample Emotion: {elements['emotions'][0]}")
            if elements.get("insights"):
                print(f"   Sample Insight: {elements['insights'][0]}")
            
            return True
        else:
            self.log_step("Retrieve Analysis Elements (Verification)", False, result["data"])
            return False
    
    def step_6_verify_session_data(self) -> bool:
        """Step 6: Verify session data persistence in Neo4j"""
        if not self.session_id:
            self.log_step("Verify Session Data", False, "No session ID available")
            return False
        
        result = self.make_request("GET", f"/sessions/{self.session_id}")
        
        if result["success"]:
            session_data = result["data"]
            verification = {
                "session_exists": True,
                "has_transcript": bool(session_data.get("transcript")),
                "transcript_length": len(session_data.get("transcript", "")),
                "status": session_data.get("status"),
                "analysis_status": session_data.get("analysis_status")
            }
            
            self.log_step("Verify Session Data", True, verification)
            return True
        else:
            self.log_step("Verify Session Data", False, result["data"])
            return False
    
    def run_complete_test(self):
        """Run the complete end-to-end test"""
        print("=" * 80)
        print("🧠 INSIGHT JOURNEY - END-TO-END API TEST")
        print("=" * 80)
        
        steps = [
            ("User Registration", self.step_1_user_registration),
            ("User Login", self.step_2_user_login),
            ("Create Session", self.step_3_create_session),
            ("Analyze Session & Write to Neo4j", self.step_4_analyze_session),
            ("Retrieve Analysis Elements (Verification)", self.step_5_retrieve_analysis_elements),
            ("Verify Session Data", self.step_6_verify_session_data)
        ]
        
        results = []
        
        for step_name, step_func in steps:
            try:
                success = step_func()
                results.append((step_name, success))
                
                if not success:
                    print(f"\n❌ Test failed at step: {step_name}")
                    break
                    
                # Add small delay between steps
                time.sleep(1)
                
            except Exception as e:
                print(f"\n💥 Exception in {step_name}: {str(e)}")
                results.append((step_name, False))
                break
        
        # Print final summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for step_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {step_name}")
        
        print(f"\n🎯 Results: {passed}/{total} steps passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! End-to-end workflow is working correctly.")
            print(f"📝 Session ID: {self.session_id}")
            print(f"👤 User ID: {self.user_id}")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        print("=" * 80)

def main():
    """Main function to run the test"""
    tester = APITester()
    tester.run_complete_test()

if __name__ == "__main__":
    main() 