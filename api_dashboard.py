#!/usr/bin/env python3
"""
Insight Journey API Dashboard

A comprehensive dashboard script that provides a unified interface for:
1. Running API tests
2. Accessing API documentation
3. Testing specific API endpoints 

Usage:
    python api_dashboard.py
"""

import os
import sys
import subprocess
import webbrowser
import json
from datetime import datetime

# Update default API URL to point to Cloud Run
API_URL = "https://insight-journey-a47jf6g6sa-uc.a.run.app"

def print_header():
    """Print dashboard header"""
    os.system('clear' if os.name != 'nt' else 'cls')
    print("=" * 80)
    print(" " * 25 + "INSIGHT JOURNEY API DASHBOARD")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_URL}")
    print("-" * 80)

def check_server_status():
    """Check if the API server is running"""
    try:
        import requests
        response = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API Server Status: ONLINE")
            print(f"   API Version: {health_data.get('api_version', 'Unknown')}")
            print(f"   Status: {health_data.get('status', 'Unknown')}")
            
            # Display additional health information if available
            for key, value in health_data.items():
                if key not in ['status', 'api_version']:
                    print(f"   {key}: {value}")
            
            return True
        else:
            print(f"❌ API Server Status: ERROR (Responded with status code {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Server Status: OFFLINE (Error: {str(e)})")
        return False

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error: {e.stderr}")
        return None

def start_server():
    """Start the API server"""
    print("\nStarting API server...")
    subprocess.Popen(["python", "main.py"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
    
    # Wait a few seconds for the server to start
    import time
    time.sleep(3)
    
    if check_server_status():
        print("Server started successfully")
    else:
        print("Server may have failed to start. Check logs for details.")

def run_all_tests():
    """Run all API tests"""
    print("\nRunning all API tests...")
    run_command("./run_api_tests.sh -v")
    input("\nPress Enter to continue...")

def run_transcription_tests():
    """Run transcription API tests"""
    print("\nRunning transcription API tests...")
    run_command("./run_api_tests.sh -v -T -a ./test_data/test_audio.mp3")
    input("\nPress Enter to continue...")

def run_auth_tests():
    """Run authentication API tests"""
    print("\nRunning authentication API tests...")
    run_command("./run_api_tests.sh -v -e auth")
    input("\nPress Enter to continue...")

def run_session_tests():
    """Run session API tests"""
    print("\nRunning session API tests...")
    run_command("./run_api_tests.sh -v -e sessions")
    input("\nPress Enter to continue...")

def run_analysis_tests():
    """Run analysis API tests"""
    print("\nRunning analysis API tests...")
    run_command("./run_api_tests.sh -v -e analysis")
    input("\nPress Enter to continue...")

def open_api_docs():
    """Open API documentation in the default browser"""
    if os.path.exists("API_README.md"):
        # For systems that can display markdown
        print("\nOpening API documentation...")
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", "API_README.md"])
        else:
            try:
                with open("API_README.md", "r") as f:
                    content = f.read()
                print("\n" + "=" * 80)
                print(" " * 30 + "API DOCUMENTATION")
                print("=" * 80)
                print(content)
                print("=" * 80)
            except Exception as e:
                print(f"Error displaying documentation: {e}")
    else:
        print("\nAPI documentation file (API_README.md) not found.")
    
    input("\nPress Enter to continue...")

def display_openapi_endpoints():
    """Display all available API endpoints from OpenAPI schema"""
    print("\nFetching API endpoints...")
    
    try:
        import requests
        response = requests.get(f"{API_URL}/api/v1/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            print("\n" + "=" * 80)
            print(" " * 30 + "API ENDPOINTS")
            print("=" * 80)
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    print(f"\n{method.upper()} {path}")
                    print(f"Description: {details.get('description', 'No description')}")
                    print("-" * 80)
        else:
            print(f"Failed to fetch OpenAPI schema: Status code {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to continue...")

def manual_api_test():
    """Allow manual testing of API endpoints"""
    print("\n" + "=" * 80)
    print(" " * 30 + "MANUAL API TEST")
    print("=" * 80)
    
    # Create a test session with requests
    import requests
    session = requests.Session()
    
    # Store token for authenticated requests
    auth_token = None
    
    while True:
        print("\nAvailable endpoints to test:")
        print("1. Health Check (GET /api/v1/health)")
        print("2. Register User (POST /api/v1/auth/register)")
        print("3. Login (POST /api/v1/auth/login)")
        print("4. Get Current User (GET /api/v1/auth/me) [Requires Auth]")
        print("5. List Sessions (GET /api/v1/sessions) [Requires Auth]")
        print("6. Direct Analysis (POST /api/v1/analysis/direct) [Requires Auth]")
        print("0. Return to main menu")
        
        choice = input("\nSelect endpoint to test (0-6): ")
        
        # Health check
        if choice == "1":
            try:
                response = session.get(f"{API_URL}/api/v1/health")
                print_response(response)
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Register user
        elif choice == "2":
            try:
                email = input("Enter email: ")
                password = input("Enter password: ")
                name = input("Enter name: ")
                
                data = {
                    "email": email,
                    "password": password,
                    "name": name
                }
                
                response = session.post(
                    f"{API_URL}/api/v1/auth/register",
                    json=data
                )
                print_response(response)
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Login
        elif choice == "3":
            try:
                username = input("Enter email: ")
                password = input("Enter password: ")
                
                data = {
                    "username": username,
                    "password": password
                }
                
                response = session.post(
                    f"{API_URL}/api/v1/auth/login",
                    data=data
                )
                print_response(response)
                
                if response.status_code == 200:
                    auth_token = response.json().get("access_token")
                    if auth_token:
                        session.headers.update({"Authorization": f"Bearer {auth_token}"})
                        print("✅ Authentication token saved for subsequent requests")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Get current user
        elif choice == "4":
            if not auth_token:
                print("❌ Authentication required. Please login first (option 3)")
                continue
                
            try:
                response = session.get(f"{API_URL}/api/v1/auth/me")
                print_response(response)
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # List sessions
        elif choice == "5":
            if not auth_token:
                print("❌ Authentication required. Please login first (option 3)")
                continue
                
            try:
                response = session.get(f"{API_URL}/api/v1/sessions")
                print_response(response)
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Direct analysis
        elif choice == "6":
            if not auth_token:
                print("❌ Authentication required. Please login first (option 3)")
                continue
                
            try:
                transcript = input("Enter transcript text: ")
                
                data = {
                    "transcript": transcript
                }
                
                response = session.post(
                    f"{API_URL}/api/v1/analysis/direct",
                    json=data
                )
                print_response(response)
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Return to main menu
        elif choice == "0":
            break
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def print_response(response):
    """Pretty print an API response"""
    print("\n" + "-" * 80)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    try:
        # Try to parse as JSON
        data = response.json()
        print("\nResponse Body (JSON):")
        import json
        print(json.dumps(data, indent=2))
    except:
        # Otherwise print as text
        print("\nResponse Body (Text):")
        print(response.text)
    
    print("-" * 80)

def main():
    """Main dashboard function"""
    while True:
        print_header()
        server_status = check_server_status()
        
        print("\nOptions:")
        if not server_status:
            print("1. Start API Server")
        print(f"{'2' if not server_status else '1'}. Run All API Tests")
        print(f"{'3' if not server_status else '2'}. Run Transcription API Tests")
        print(f"{'4' if not server_status else '3'}. Run Authentication API Tests")
        print(f"{'5' if not server_status else '4'}. Run Session API Tests")
        print(f"{'6' if not server_status else '5'}. Run Analysis API Tests")
        print(f"{'7' if not server_status else '6'}. Open API Documentation")
        if server_status:
            print("7. Display API Endpoints")
        print("8. Manual API Test")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if not server_status:
            # Server is not running
            if choice == "1":
                start_server()
            elif choice == "2":
                run_all_tests()
            elif choice == "3":
                run_transcription_tests()
            elif choice == "4":
                run_auth_tests()
            elif choice == "5":
                run_session_tests()
            elif choice == "6":
                run_analysis_tests()
            elif choice == "7":
                open_api_docs()
            elif choice == "8":
                manual_api_test()
            elif choice == "0":
                print("\nExiting dashboard. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
        else:
            # Server is running
            if choice == "1":
                run_all_tests()
            elif choice == "2":
                run_transcription_tests()
            elif choice == "3":
                run_auth_tests()
            elif choice == "4":
                run_session_tests()
            elif choice == "5":
                run_analysis_tests()
            elif choice == "6":
                open_api_docs()
            elif choice == "7":
                display_openapi_endpoints()
            elif choice == "8":
                manual_api_test()
            elif choice == "0":
                print("\nExiting dashboard. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
        
        # Add a small delay before clearing the screen
        import time
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDashboard closed by user. Goodbye!")
        sys.exit(0) 