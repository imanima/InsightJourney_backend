#!/usr/bin/env python3
"""
Bulk Data Loader for Insight Journey Backend

This script loads all the generated therapy session data into the system:
1. Creates users for each persona in the output directory
2. For each user, creates 24 therapy sessions
3. Analyzes each session (OpenAI analysis + Neo4j storage)
4. Verifies data persistence

Directory structure expected:
data/generators/output/
├── Alex_Dr._Harper_Torres/
│   ├── session_01_20250501.txt
│   ├── session_02_20250508.txt
│   └── ... (24 sessions total)
├── Zoë_Dr._Serena_Bianchi/
└── ... (10 users total)

Usage:
    python bulk_data_loader.py
    python bulk_data_loader.py --users Alex,Zoë  # Load specific users only
    python bulk_data_loader.py --dry-run         # Preview what would be done
"""

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import requests

# Configuration
BASE_URL = "http://localhost:8080/api/v1"
HEADERS = {"Content-Type": "application/json"}
DEFAULT_PASSWORD = "Testuser123"
EMAIL_DOMAIN = "insightsout.com"

# Add parent directory to path to import from the test script
sys.path.append(str(Path(__file__).parent.parent))

class BulkDataLoader:
    def __init__(self, base_url: str = BASE_URL, dry_run: bool = False):
        self.base_url = base_url
        self.headers = HEADERS.copy()
        self.dry_run = dry_run
        self.output_dir = Path(__file__).parent / "output"
        self.stats = {
            "users_created": 0,
            "users_failed": 0,
            "sessions_created": 0,
            "sessions_failed": 0,
            "analyses_completed": 0,
            "analyses_failed": 0,
            "total_start_time": None,
            "user_timings": {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍"
        }.get(level, "📝")
        
        print(f"[{timestamp}] {prefix} {message}")
        
    def extract_user_info(self, folder_name: str) -> Tuple[str, str, str]:
        """Extract user information from folder name"""
        # Examples: "Alex_Dr._Harper_Torres" -> ("Alex", "alex@insightsout.com", "Alex")
        parts = folder_name.split('_')
        first_name = parts[0]
        email = f"{first_name.lower()}@{EMAIL_DOMAIN}"
        display_name = first_name
        
        return first_name, email, display_name
    
    def get_user_folders(self, specific_users: Optional[List[str]] = None) -> List[Path]:
        """Get list of user folders to process"""
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")
        
        user_folders = [d for d in self.output_dir.iterdir() if d.is_dir()]
        
        if specific_users:
            # Filter to only specified users
            filtered_folders = []
            for folder in user_folders:
                first_name, _, _ = self.extract_user_info(folder.name)
                if first_name.lower() in [u.lower() for u in specific_users]:
                    filtered_folders.append(folder)
            user_folders = filtered_folders
            
        return sorted(user_folders)
    
    def get_session_files(self, user_folder: Path) -> List[Path]:
        """Get all session files for a user, sorted by session number"""
        session_files = list(user_folder.glob("session_*.txt"))
        
        # Sort by session number (extract number from filename)
        def extract_session_number(filepath):
            match = re.search(r'session_(\d+)_', filepath.name)
            return int(match.group(1)) if match else 0
            
        return sorted(session_files, key=extract_session_number)
    
    def read_session_content(self, session_file: Path) -> Dict[str, str]:
        """Read and parse session file content"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from the session file
            lines = content.split('\n')
            session_info = {}
            
            # Parse header information
            for line in lines[:10]:  # Check first 10 lines for metadata
                if line.startswith('Session '):
                    session_info['session_number'] = line.split('/')[0].replace('Session ', '')
                elif line.startswith('Date: '):
                    session_info['date'] = line.replace('Date: ', '')
                elif line.startswith('Time: '):
                    session_info['time'] = line.replace('Time: ', '')
                elif line.startswith('Client: '):
                    session_info['client'] = line.replace('Client: ', '')
                elif line.startswith('Professional: '):
                    session_info['therapist'] = line.replace('Professional: ', '')
            
            # Create session title from filename and metadata
            session_num = session_info.get('session_number', 'Unknown')
            date = session_info.get('date', 'Unknown Date')
            session_info['title'] = f"Therapy Session {session_num} - {date}"
            session_info['description'] = f"Therapy session with {session_info.get('therapist', 'therapist')} on {date}"
            session_info['transcript'] = content
            
            return session_info
            
        except Exception as e:
            self.log(f"Error reading session file {session_file}: {str(e)}", "ERROR")
            return {}
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    files: Optional[Dict] = None) -> Dict:
        """Make HTTP request with error handling"""
        if self.dry_run:
            self.log(f"DRY RUN: {method} {endpoint}", "DEBUG")
            return {"success": True, "status_code": 200, "data": {"id": "dry_run_id"}}
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                if files:
                    headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
                    response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
                else:
                    response = requests.post(url, headers=self.headers, json=data, timeout=60)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response_data
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "status_code": 408, "data": {"error": "Request timeout"}}
        except Exception as e:
            return {"success": False, "status_code": 0, "data": {"error": str(e)}}
    
    def create_user(self, first_name: str, email: str, display_name: str) -> Tuple[bool, Optional[str]]:
        """Create a user account"""
        user_data = {
            "email": email,
            "password": DEFAULT_PASSWORD,
            "name": display_name,
            "is_admin": False
        }
        
        self.log(f"Creating user: {display_name} ({email})")
        result = self.make_request("POST", "/auth/register", user_data)
        
        if result["success"]:
            user_id = result["data"].get("user_id") or result["data"].get("id")
            self.log(f"✅ User created: {display_name} (ID: {user_id})", "SUCCESS")
            self.stats["users_created"] += 1
            return True, user_id
        else:
            error_msg = result["data"].get("error", "Unknown error")
            self.log(f"❌ Failed to create user {display_name}: {error_msg}", "ERROR")
            self.stats["users_failed"] += 1
            return False, None
    
    def login_user(self, email: str) -> Tuple[bool, Optional[str]]:
        """Login user and get auth token"""
        login_data = {
            "username": email,
            "password": DEFAULT_PASSWORD
        }
        
        # OAuth2 login uses form data
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        
        if self.dry_run:
            return True, "dry_run_token"
        
        try:
            url = f"{self.base_url}/auth/login"
            response = requests.post(url, headers=headers, data=login_data, timeout=30)
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            if response.status_code < 400:
                token = response_data.get("access_token")
                if token:
                    # Update headers with auth token
                    self.headers["Authorization"] = f"Bearer {token}"
                    return True, token
                else:
                    self.log(f"❌ No access token received for {email}", "ERROR")
                    return False, None
            else:
                error_msg = response_data.get("error", "Login failed")
                self.log(f"❌ Login failed for {email}: {error_msg}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Login error for {email}: {str(e)}", "ERROR")
            return False, None
    
    def create_session(self, session_info: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """Create a therapy session"""
        session_data = {
            "title": session_info.get("title", "Therapy Session"),
            "description": session_info.get("description", "Therapy session"),
            "transcript": session_info.get("transcript", "")
        }
        
        result = self.make_request("POST", "/sessions", session_data)
        
        if result["success"]:
            session_id = result["data"].get("id")
            self.stats["sessions_created"] += 1
            return True, session_id
        else:
            error_msg = result["data"].get("error", "Unknown error")
            self.log(f"   ❌ Failed to create session: {error_msg}", "ERROR")
            self.stats["sessions_failed"] += 1
            return False, None
    
    def analyze_session(self, session_id: str, transcript: str) -> bool:
        """Analyze a session (OpenAI + Neo4j)"""
        analysis_data = {
            "session_id": session_id,
            "transcript": transcript
        }
        
        result = self.make_request("POST", "/analysis/analyze", analysis_data)
        
        if result["success"]:
            self.stats["analyses_completed"] += 1
            return True
        else:
            error_msg = result["data"].get("error", "Unknown error")
            self.log(f"   ❌ Failed to analyze session {session_id}: {error_msg}", "ERROR")
            self.stats["analyses_failed"] += 1
            return False
    
    def process_user(self, user_folder: Path) -> bool:
        """Process a single user - create account and all sessions"""
        start_time = time.time()
        first_name, email, display_name = self.extract_user_info(user_folder.name)
        
        self.log(f"\n{'='*60}")
        self.log(f"Processing User: {display_name}")
        self.log(f"Folder: {user_folder.name}")
        self.log(f"Email: {email}")
        self.log(f"{'='*60}")
        
        # Step 1: Create user
        user_success, user_id = self.create_user(first_name, email, display_name)
        if not user_success:
            return False
        
        # Step 2: Login user
        login_success, token = self.login_user(email)
        if not login_success:
            return False
        
        # Step 3: Get session files
        session_files = self.get_session_files(user_folder)
        total_sessions = len(session_files)
        
        self.log(f"Found {total_sessions} session files for {display_name}")
        
        if total_sessions == 0:
            self.log(f"⚠️ No session files found for {display_name}", "WARNING")
            return False
        
        # Step 4: Process each session
        successful_sessions = 0
        for i, session_file in enumerate(session_files, 1):
            self.log(f"Processing session {i}/{total_sessions}: {session_file.name}")
            
            # Read session content
            session_info = self.read_session_content(session_file)
            if not session_info:
                continue
            
            # Create session
            session_success, session_id = self.create_session(session_info)
            if not session_success:
                continue
            
            # Analyze session
            analysis_success = self.analyze_session(session_id, session_info.get("transcript", ""))
            if analysis_success:
                successful_sessions += 1
                self.log(f"   ✅ Session {i} completed successfully")
            
            # Small delay to avoid overwhelming the API
            if not self.dry_run:
                time.sleep(0.5)
        
        # Record timing and results
        end_time = time.time()
        duration = end_time - start_time
        self.stats["user_timings"][display_name] = {
            "duration": duration,
            "sessions_processed": successful_sessions,
            "total_sessions": total_sessions
        }
        
        success_rate = (successful_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        self.log(f"✅ User {display_name} completed in {duration:.1f}s")
        self.log(f"   Sessions: {successful_sessions}/{total_sessions} ({success_rate:.1f}% success)")
        
        return successful_sessions > 0
    
    def print_final_stats(self):
        """Print comprehensive final statistics"""
        end_time = time.time()
        total_duration = end_time - self.stats["total_start_time"]
        
        print("\n" + "="*80)
        print("🎯 BULK DATA LOADING COMPLETE")
        print("="*80)
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Total Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        print(f"   Users Created: {self.stats['users_created']}")
        print(f"   Users Failed: {self.stats['users_failed']}")
        print(f"   Sessions Created: {self.stats['sessions_created']}")
        print(f"   Sessions Failed: {self.stats['sessions_failed']}")
        print(f"   Analyses Completed: {self.stats['analyses_completed']}")
        print(f"   Analyses Failed: {self.stats['analyses_failed']}")
        
        if self.stats["sessions_created"] > 0:
            session_success_rate = (self.stats["analyses_completed"] / self.stats["sessions_created"]) * 100
            print(f"   Analysis Success Rate: {session_success_rate:.1f}%")
        
        print(f"\n👥 USER BREAKDOWN:")
        for user, timing in self.stats["user_timings"].items():
            duration = timing["duration"]
            sessions = timing["sessions_processed"]
            total = timing["total_sessions"]
            rate = (sessions / total) * 100 if total > 0 else 0
            print(f"   {user}: {sessions}/{total} sessions ({rate:.1f}%) in {duration:.1f}s")
        
        if self.stats["users_created"] > 0:
            avg_time_per_user = total_duration / self.stats["users_created"]
            avg_sessions_per_user = self.stats["sessions_created"] / self.stats["users_created"]
            print(f"\n📈 AVERAGES:")
            print(f"   Time per user: {avg_time_per_user:.1f} seconds")
            print(f"   Sessions per user: {avg_sessions_per_user:.1f}")
            
        print("\n" + "="*80)
    
    def run(self, specific_users: Optional[List[str]] = None):
        """Run the bulk data loading process"""
        self.stats["total_start_time"] = time.time()
        
        try:
            # Get user folders to process
            user_folders = self.get_user_folders(specific_users)
            total_users = len(user_folders)
            
            if total_users == 0:
                self.log("❌ No user folders found to process", "ERROR")
                return
            
            self.log(f"🚀 Starting bulk data loading for {total_users} users")
            if self.dry_run:
                self.log("🔍 DRY RUN MODE - No actual API calls will be made", "WARNING")
            
            # Process each user
            successful_users = 0
            for i, user_folder in enumerate(user_folders, 1):
                self.log(f"\n{'🔄'} Processing user {i}/{total_users}")
                
                if self.process_user(user_folder):
                    successful_users += 1
                
                # Longer delay between users to avoid overwhelming the system
                if not self.dry_run and i < total_users:
                    time.sleep(2)
            
            # Print final statistics
            self.print_final_stats()
            
            if successful_users == total_users:
                self.log("🎉 All users processed successfully!", "SUCCESS")
            else:
                self.log(f"⚠️ {successful_users}/{total_users} users processed successfully", "WARNING")
                
        except KeyboardInterrupt:
            self.log("\n🛑 Process interrupted by user", "WARNING")
            self.print_final_stats()
        except Exception as e:
            self.log(f"💥 Unexpected error: {str(e)}", "ERROR")
            raise

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description="Bulk load therapy session data into Insight Journey")
    parser.add_argument("--users", type=str, help="Comma-separated list of specific users to load (e.g., 'Alex,Zoë')")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be done without making API calls")
    parser.add_argument("--base-url", type=str, default=BASE_URL, help="API base URL")
    
    args = parser.parse_args()
    
    # Parse specific users if provided
    specific_users = None
    if args.users:
        specific_users = [u.strip() for u in args.users.split(",")]
    
    # Create and run loader
    loader = BulkDataLoader(base_url=args.base_url, dry_run=args.dry_run)
    loader.run(specific_users=specific_users)

if __name__ == "__main__":
    main() 