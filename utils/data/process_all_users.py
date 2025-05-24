import os
import json
from datetime import datetime
import traceback
import logging
from services.neo4j_service import Neo4jService
from services.analysis_service import analyze_transcript, extract_elements
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("transcript_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path to user directories
USER_DIRS_PATH = "test_data_generator/output"

# Constants for validation
VALID_EMOTIONS = [
    "Anxiety", "Sadness", "Anger", "Fear", "Hope",
    "Joy", "Frustration", "Confusion", "Relief", "Gratitude"
]

VALID_TOPICS = [
    "Relationships", "Career", "Health", "Self-Esteem", "Stress Management",
    "Time Management", "Boundaries", "Personal Growth", "Trauma", "Life Transitions",
    "Purpose"
]

def save_analysis_to_directory(analysis, elements, filename, output_dir="analysis_results"):
    """Save analysis results to a directory"""
    try:
        # Create timestamp for the batch
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = os.path.join(output_dir, f"batch_{timestamp}")
        json_dir = os.path.join(batch_dir, "json")
        
        # Create directories if they don't exist
        os.makedirs(json_dir, exist_ok=True)
        
        # Create unique filename
        base_name = os.path.splitext(os.path.basename(filename))[0]
        safe_name = ''.join(c if c.isalnum() else '_' for c in base_name)
        result_filename = f"{safe_name}.json"
        result_path = os.path.join(json_dir, result_filename)
        
        # Prepare results data
        results = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "elements": elements
        }
        
        # Save to file
        with open(result_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Saved analysis results to {result_path}")
        return result_path
    except Exception as e:
        logger.error(f"Error saving analysis to directory: {str(e)}")
        return None

def process_transcript(neo4j_service, file_path, user_id):
    """Process a single transcript file and save results to Neo4j"""
    try:
        logger.info(f"Processing {file_path}...")
        
        # Read transcript file
        with open(file_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        logger.info(f"Successfully read {len(transcript)} characters")
        
        # Analyze transcript using OpenAI
        logger.info("Analyzing transcript with OpenAI...")
        analysis = analyze_transcript(transcript)
        
        # Extract elements from analysis
        logger.info("Extracting elements from analysis...")
        elements = extract_elements(analysis)
        
        # Print summary of extracted elements
        logger.info("Summary of extracted elements:")
        for element_type, items in elements.items():
            logger.info(f"{element_type}: {len(items)} items")
        
        # Save analysis results to directory
        save_analysis_to_directory(analysis, elements, os.path.basename(file_path))
        
        # Create session in Neo4j
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Extract session number and date if available (session_XX_YYYYMMDD.txt)
        session_info = base_name.split('_')
        if len(session_info) >= 3:
            session_num = session_info[1]
            session_date = session_info[2]
            # Format date if it's in the format YYYYMMDD
            if len(session_date) == 8 and session_date.isdigit():
                try:
                    session_date = f"{session_date[:4]}-{session_date[4:6]}-{session_date[6:8]}"
                except:
                    session_date = datetime.now().strftime("%Y-%m-%d")
            session_title = f"Session {session_num}"
        else:
            session_title = f"Session {base_name}"
            session_date = datetime.now().strftime("%Y-%m-%d")
        
        # Prepare session data for Neo4j
        session_data = {
            "userId": user_id,
            "title": session_title,
            "date": session_date,
            "description": "Therapy session transcript analysis",
            "transcript": transcript,
            "status": "completed",
            "analysis_status": "pending"
        }
        
        # Create session using the Neo4j service method
        logger.info(f"Creating Neo4j session for {session_title}...")
        session_id = neo4j_service.create_session(session_data)
        if not session_id:
            logger.error("Failed to create session in Neo4j")
            return False
            
        logger.info(f"Created session {session_id} for user {user_id}")
        
        # Now update the session with all the extracted elements
        logger.info("Adding extracted elements to the session...")
        update_success = neo4j_service.update_session_with_elements(session_id, elements, user_id)
        
        if update_success:
            logger.info(f"Successfully added elements to session {session_id}")
        else:
            logger.error(f"Failed to add elements to session {session_id}")
            return False
            
        logger.info(f"Successfully processed {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing transcript {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def create_user_for_directory(neo4j_service, dir_name):
    """Create a user for a directory"""
    try:
        # Parse user name and therapist from directory name
        parts = dir_name.split('_')
        if len(parts) >= 2:
            user_name = parts[0]
            therapist = '_'.join(parts[1:]) if len(parts) > 2 else parts[1]
        else:
            user_name = dir_name
            therapist = "Unknown Therapist"
        
        # Check if user already exists
        user_email = f"{user_name.lower()}@example.com"
        user = neo4j_service.get_user_by_email(user_email)
        
        if user:
            logger.info(f"User {user_name} already exists with ID: {user['userId']}")
            return user['userId']
        
        # Create user with email based on name
        logger.info(f"Creating new user for {user_name}...")
        password_hash = generate_password_hash("password123")
        created_user_id = neo4j_service.create_user(user_email, password_hash, user_name)
        
        if created_user_id:
            logger.info(f"Created user with name: {user_name}, email: {user_email}, ID: {created_user_id}")
            return created_user_id
        else:
            logger.error(f"Failed to create user for {user_name}")
            return None
    except Exception as e:
        logger.error(f"Error creating user for directory {dir_name}: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def process_user_directory(neo4j_service, user_dir, max_sessions=None):
    """Process all transcripts in a user directory"""
    try:
        user_dir_path = os.path.join(USER_DIRS_PATH, user_dir)
        
        # Create user for this directory
        user_id = create_user_for_directory(neo4j_service, user_dir)
        if not user_id:
            logger.error(f"Skipping directory {user_dir} due to user creation failure")
            return False
        
        # Process all transcripts in the directory
        session_count = 0
        transcripts_processed = 0
        
        # Look for session files - they should be in the format "session_XX_YYYYMMDD.txt" 
        transcript_files = [f for f in os.listdir(user_dir_path) if f.startswith("session_") and f.endswith(".txt")]
        transcript_files.sort()  # Sort by name to process in order
        
        logger.info(f"Found {len(transcript_files)} transcript files in {user_dir}")
        
        for filename in transcript_files:
            file_path = os.path.join(user_dir_path, filename)
            success = process_transcript(neo4j_service, file_path, user_id)
            
            if success:
                transcripts_processed += 1
            
            session_count += 1
            
            # Limit to max_sessions transcripts per user if specified
            if max_sessions is not None and transcripts_processed >= max_sessions:
                logger.info(f"Processed {max_sessions} transcripts for user {user_dir}, stopping as requested")
                break
        
        logger.info(f"Completed processing for user {user_dir}")
        logger.info(f"Total sessions: {session_count}")
        logger.info(f"Successfully processed: {transcripts_processed}")
        
        return transcripts_processed > 0  # Success if at least one transcript was processed
    except Exception as e:
        logger.error(f"Error processing user directory {user_dir}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Process all user directories"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Process transcript files for multiple users')
    parser.add_argument('--max-sessions', type=int, help='Maximum number of sessions to process per user (omit for all sessions)')
    parser.add_argument('--user', type=str, help='Process only a specific user directory (optional)')
    parser.add_argument('--batch-size', type=int, default=0, help='Number of users to process (0 for all users)')
    parser.add_argument('--batch-start', type=int, default=0, help='Starting index for batch processing')
    parser.add_argument('--all-sessions', action='store_true', help='Process all sessions for each user')
    args = parser.parse_args()
    
    # Set max_sessions to None if all_sessions flag is set
    max_sessions = None if args.all_sessions else args.max_sessions or 3  # Default to 3 if not specified
    
    # Log the start of processing
    logger.info("=" * 60)
    logger.info("Starting transcript processing")
    if max_sessions is None:
        logger.info("Processing ALL sessions for each user")
    else:
        logger.info(f"Max sessions per user: {max_sessions}")
    if args.batch_size > 0:
        logger.info(f"Batch processing: size={args.batch_size}, start={args.batch_start}")
    logger.info("=" * 60)
    
    # Initialize Neo4j service
    neo4j_uri = os.getenv("NEO4J_URI", "neo4j+s://8769633e.databases.neo4j.io")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "Uz4JHnnePdo17I6q2g9WAlseO5EQu_2o2CERt1UkDQo")
    
    # Create Neo4j service
    neo4j_service = Neo4jService(
        uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password
    )
    
    # Get user directories
    user_directories = []
    try:
        # Check if we should process a specific user
        if args.user:
            user_dir = args.user
            if os.path.isdir(os.path.join(USER_DIRS_PATH, user_dir)):
                user_directories = [user_dir]
                logger.info(f"Processing only user: {user_dir}")
            else:
                logger.error(f"User directory not found: {user_dir}")
                return
        else:
            # Process all users or a batch
            all_directories = [d for d in os.listdir(USER_DIRS_PATH) if os.path.isdir(os.path.join(USER_DIRS_PATH, d))]
            
            # Sort directories for consistent batch processing
            all_directories.sort()
            
            # Apply batch parameters if specified
            if args.batch_size > 0:
                batch_end = min(args.batch_start + args.batch_size, len(all_directories))
                user_directories = all_directories[args.batch_start:batch_end]
                logger.info(f"Batch processing users {args.batch_start} to {batch_end-1}")
                logger.info(f"Selected users: {', '.join(user_directories)}")
            else:
                user_directories = all_directories
                logger.info(f"Found {len(user_directories)} user directories: {', '.join(user_directories)}")
    except Exception as e:
        logger.error(f"Error listing user directories: {str(e)}")
        logger.error(traceback.format_exc())
        return
    
    # Process each user directory
    successful_dirs = 0
    
    for user_dir in user_directories:
        logger.info("=" * 60)
        logger.info(f"Processing user directory: {user_dir}")
        logger.info("=" * 60)
        
        success = process_user_directory(
            neo4j_service, 
            user_dir,
            max_sessions=max_sessions
        )
        
        if success:
            successful_dirs += 1
    
    logger.info("=" * 60)
    logger.info("Processing complete.")
    logger.info(f"Total user directories: {len(user_directories)}")
    logger.info(f"Successfully processed: {successful_dirs}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 