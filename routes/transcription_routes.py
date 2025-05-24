"""
API routes for handling audio file transcription requests and retrieving results.
"""

import os
import uuid
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.transcription_service import TranscriptionService
from routes.auth import User, oauth2_scheme

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create API router - update to use just /transcribe
router = APIRouter(prefix="/transcribe", tags=["transcription"])

# Initialize transcription service
transcription_service = TranscriptionService(
    chunk_size_seconds=300,  # 5 minutes
    max_concurrent=5,
    max_retries=3
)

# Available output formats
ALLOWED_FORMATS = ["text", "json", "srt", "vtt"]

# Maximum file size (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes

# Supported file types
SUPPORTED_FILE_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "video/mp4": ".mp4",
    "audio/mpeg3": ".mp3",
    "audio/webm": ".webm",
    "video/webm": ".webm"
}

class TranscriptionLinkRequest(BaseModel):
    """Request model for linking a transcription to a session."""
    session_id: str

# Define a function to get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user."""
    # For now, we'll use a mock implementation
    return User(
        id="test_user_id",
        email="test@example.com",
        name="Test User",
        is_admin=False,
        created_at=datetime.now(),
        disabled=False
    )

# Helper function to get file storage path (uses temp directory in production)
def get_file_storage_path() -> Path:
    """
    Get a path for storing uploaded files.
    In production, uses a temporary directory that's container-friendly.
    In development, uses a local 'uploads' directory.
    
    Returns:
        Path: Path to the storage directory
    """
    # Check for production environment
    if os.environ.get('ENVIRONMENT') == 'production':
        # Use the system's temp directory
        temp_dir = Path(tempfile.gettempdir()) / "insight_journey_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    else:
        # Development mode - use local directory
        base_dir = Path(__file__).parent.parent
        uploads_dir = base_dir / "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        return uploads_dir

@router.post("", status_code=202)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    language: str = Form("en"),
    format: str = Form("text"),
    speaker_detection: str = Form("false")
):
    """
    Upload and transcribe an audio file.
    
    Args:
        audio: The audio file to transcribe
        language: Language code (default: "en")
        format: Output format (default: "text", options: "text", "json", "srt", "vtt")
        speaker_detection: Enable speaker detection (default: "false")
        
    Returns:
        Transcription job details with ID and status
    """
    # For testing, use a fixed user ID
    current_user_id = "test_user_id"
    
    # Validate file size
    if audio.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large, maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )
    
    # Validate content type
    content_type = audio.content_type
    if content_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. " +
                  f"Supported types: {', '.join(SUPPORTED_FILE_TYPES.keys())}"
        )
    
    # Validate format
    if format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. " +
                  f"Supported formats: {', '.join(ALLOWED_FORMATS)}"
        )
    
    try:
        # Generate a unique filename
        file_extension = SUPPORTED_FILE_TYPES[content_type]
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Get storage path and ensure directory exists
        storage_dir = get_file_storage_path() / "audio"
        os.makedirs(storage_dir, exist_ok=True)
        file_path = storage_dir / filename
        
        # Read file content - use more memory-efficient approach for large files
        contents = await audio.read()
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Saved audio file to {file_path}")
        
        # Initialize transcription options
        options = {
            "language": language,
            "format": format,
            "speaker_detection": speaker_detection
        }
        
        # Start transcription in the background
        result = await transcription_service.api_transcribe(
            str(file_path),
            current_user_id,
            options=options
        )
        
        # Schedule cleanup of old transcription jobs
        background_tasks.add_task(transcription_service.cleanup_old_jobs)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {str(e)}")


@router.get("/{transcription_id}")
async def get_transcription_status(
    transcription_id: str
):
    """
    Get the status of a transcription job.
    
    Args:
        transcription_id: ID of the transcription job
        
    Returns:
        Status of the transcription job
    """
    status = transcription_service.get_transcription_status(transcription_id)
    
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    # For testing, don't check user access
    # if status.get("user_id") and status.get("user_id") != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this transcription")
    
    return status


@router.get("/{transcription_id}/result")
async def get_transcription_result(
    transcription_id: str
):
    """
    Get the result of a completed transcription job.
    
    Args:
        transcription_id: ID of the transcription job
        
    Returns:
        Transcription result
    """
    result = transcription_service.get_completed_transcription(transcription_id)
    
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    if result.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Transcription is not completed (status: {result.get('status')})"
        )
    
    # For testing, don't check user access
    # if result.get("user_id") and result.get("user_id") != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this transcription")
    
    return result


@router.post("/{transcription_id}/link")
async def link_transcription_to_session(
    transcription_id: str,
    request: TranscriptionLinkRequest
):
    """
    Link a completed transcription to a therapy session.
    
    Args:
        transcription_id: ID of the transcription job
        request: Request containing session ID
        
    Returns:
        Status of the linking operation
    """
    # Check status first
    status = transcription_service.get_transcription_status(transcription_id)
    
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    # For testing, don't check user access
    # if status.get("user_id") and status.get("user_id") != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this transcription")
    
    # Link the transcription to the session
    result = transcription_service.link_transcription_to_session(
        transcription_id,
        request.session_id
    )
    
    if result.get("status") == "failed":
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to link transcription"))
    
    return result 