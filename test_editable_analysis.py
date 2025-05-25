#!/usr/bin/env python3
"""
Test script for the editable session analysis functionality
This tests the complete workflow of creating, analyzing, and editing session elements
"""

import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8080/api/v1"

def test_editable_analysis_workflow():
    """Test the complete editable analysis workflow"""
    
    print("🧪 Testing Editable Session Analysis Workflow")
    print("=" * 60)
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "email": "test_edit@example.com", 
        "password": "password123",
        "name": "Test Edit User"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if register_response.status_code not in [200, 201]:
        print(f"   ⚠️  Registration failed or user exists: {register_response.text}")
    else:
        print("   ✅ User registered successfully")
    
    # Step 2: Login to get token (using form data)
    print("\n2. Logging in...")
    login_data = {
        "username": "test_edit@example.com",  # API expects 'username' not 'email'
        "password": "password123"
    }
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)  # Use data= for form encoding
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json().get("access_token")
    if not token:
        print("   ❌ No access token received")
        return False
    
    print("   ✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Create a session first
    print("\n3. Creating a session...")
    session_data = {
        "title": "Test Editable Analysis Session",
        "description": "Testing the editable analysis workflow",
        "transcript": """
    Today I'm feeling quite overwhelmed with work. The deadlines are approaching fast and I'm struggling to manage my time effectively. I've been having trouble sleeping because my mind keeps racing about all the tasks I need to complete. 

    I think part of the problem is that I tend to be a perfectionist. I spend too much time on small details instead of focusing on the big picture. This belief that everything must be perfect is really holding me back and causing a lot of stress.

    I want to work on developing better time management skills and learning to let go of perfectionism. Maybe I should try breaking down large tasks into smaller, manageable pieces and setting more realistic expectations for myself.

    The challenge is that I've been this way for so long, it feels hard to change. But I know that if I don't address this pattern, it's going to continue affecting my mental health and work performance.
    """
    }
    
    session_response = requests.post(f"{BASE_URL}/sessions", json=session_data, headers=headers)
    
    if session_response.status_code != 200:
        print(f"   ❌ Session creation failed: {session_response.text}")
        return False
    
    session_id = session_response.json().get("id")
    if not session_id:
        print("   ❌ No session ID received")
        return False
    
    print(f"   ✅ Session created with ID: {session_id}")
    
    # Step 4: Run analysis on the created session
    print("\n4. Running analysis on the session...")
    
    transcript = session_data["transcript"]
    analysis_data = {"session_id": session_id, "transcript": transcript}
    analysis_response = requests.post(f"{BASE_URL}/analysis/analyze", json=analysis_data, headers=headers)
    
    if analysis_response.status_code != 200:
        print(f"   ❌ Analysis failed: {analysis_response.text}")
        return False
    
    print(f"   ✅ Analysis completed for session: {session_id}")
    
    # Step 5: Get analysis elements
    print("\n5. Retrieving analysis elements...")
    elements_response = requests.get(f"{BASE_URL}/analysis/{session_id}/elements", headers=headers)
    
    if elements_response.status_code != 200:
        print(f"   ❌ Failed to get elements: {elements_response.text}")
        return False
    
    original_elements = elements_response.json()
    print(f"   ✅ Retrieved elements:")
    print(f"      - Emotions: {len(original_elements.get('emotions', []))}")
    print(f"      - Beliefs: {len(original_elements.get('beliefs', []))}")
    print(f"      - Action Items: {len(original_elements.get('action_items', []))}")
    print(f"      - Challenges: {len(original_elements.get('challenges', []))}")
    print(f"      - Insights: {len(original_elements.get('insights', []))}")
    
    # Step 6: Test editing elements
    print("\n6. Testing element modification...")
    
    # Modify existing elements
    modified_elements = json.loads(json.dumps(original_elements))  # Deep copy
    
    # Add a new emotion
    if 'emotions' not in modified_elements:
        modified_elements['emotions'] = []
    
    modified_elements['emotions'].append({
        "name": "Determination",
        "intensity": 4,
        "context": "Feeling determined to overcome perfectionism",
        "topic": "Personal Growth",
        "timestamp": "2024-05-25T00:00:00Z"
    })
    
    # Add a new action item
    if 'action_items' not in modified_elements:
        modified_elements['action_items'] = []
    
    modified_elements['action_items'].append({
        "name": "Practice Time Boxing",
        "description": "Set specific time limits for tasks to avoid perfectionism",
        "topic": "Productivity",
        "status": "Not Started",
        "timestamp": "2024-05-25T00:00:00Z"
    })
    
    # Modify an existing belief (if any exist)
    if modified_elements.get('beliefs') and len(modified_elements['beliefs']) > 0:
        modified_elements['beliefs'][0]['impact'] = "High"
        modified_elements['beliefs'][0]['description'] = "Modified: Everything must be perfect before I can move forward"
    
    print("   📝 Modified elements:")
    print(f"      - Added new emotion: Determination")
    print(f"      - Added new action item: Practice Time Boxing")
    if original_elements.get('beliefs'):
        print(f"      - Modified first belief impact and description")
    
    # Step 7: Update elements via the new analysis endpoint
    print("\n7. Saving modified elements...")
    update_data = {"elements": modified_elements}
    
    # Use the new analysis endpoint for updating elements
    update_response = requests.put(f"{BASE_URL}/analysis/{session_id}/elements", json=update_data, headers=headers)
    
    if update_response.status_code != 200:
        print(f"   ❌ Failed to update elements: {update_response.text}")
        return False
    
    print("   ✅ Elements updated successfully")
    
    # Step 8: Verify changes were saved
    print("\n8. Verifying changes were saved...")
    verification_response = requests.get(f"{BASE_URL}/analysis/{session_id}/elements", headers=headers)
    
    if verification_response.status_code != 200:
        print(f"   ❌ Failed to verify changes: {verification_response.text}")
        return False
    
    updated_elements = verification_response.json()
    
    # Check if our new elements exist
    new_emotion_found = any(e.get('name') == 'Determination' for e in updated_elements.get('emotions', []))
    new_action_found = any(a.get('name') == 'Practice Time Boxing' for a in updated_elements.get('action_items', []))
    
    print(f"   📊 Verification results:")
    print(f"      - Original emotions: {len(original_elements.get('emotions', []))}")
    print(f"      - Updated emotions: {len(updated_elements.get('emotions', []))}")
    print(f"      - New emotion found: {'✅' if new_emotion_found else '❌'}")
    print(f"      - Original action items: {len(original_elements.get('action_items', []))}")
    print(f"      - Updated action items: {len(updated_elements.get('action_items', []))}")
    print(f"      - New action item found: {'✅' if new_action_found else '❌'}")
    
    if new_emotion_found and new_action_found:
        print("\n🎉 SUCCESS: Editable analysis workflow is working correctly!")
        print("   - Elements can be retrieved from the database")
        print("   - Elements can be modified and saved")
        print("   - Changes persist in the database")
        return True
    else:
        print("\n❌ FAILURE: Some elements were not saved correctly")
        return False

if __name__ == "__main__":
    try:
        success = test_editable_analysis_workflow()
        if success:
            print("\n✅ All tests passed! The editable analysis feature is ready to use.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 