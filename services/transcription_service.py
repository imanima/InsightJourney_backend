"""Transcription service for handling both audio and text transcripts."""
import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import tempfile
import json
import uuid
import time
from datetime import datetime, timedelta

from openai import OpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter
from openai import RateLimitError, APIError

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s • %(levelname)s • %(message)s")
log = logging.getLogger("transcription-service")

# OpenAI configuration
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
AUDIO_MODEL = os.getenv("OPENAI_AUDIO_MODEL", "whisper-1")

class TranscriptionService:
    def __init__(self, chunk_size_seconds: int = 300, max_concurrent: int = 5, max_retries: int = 3):
        """Initialize the transcription service.
        
        Args:
            chunk_size_seconds (int): Size of each audio chunk in seconds (default: 300 = 5 minutes)
            max_concurrent (int): Maximum number of concurrent transcription tasks
            max_retries (int): Maximum number of retries for failed transcriptions
        """
        self.chunk_size_seconds = chunk_size_seconds
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        
        # Initialize OpenAI client (with compatibility with different OpenAI versions)
        if OPENAI_KEY:
            try:
                # Initialize OpenAI client without proxy configuration to avoid issues
                self.client = OpenAI(api_key=OPENAI_KEY)
                log.info("OpenAI client initialized successfully")
            except Exception as e:
                log.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
        else:
            log.warning("No OpenAI API key found, transcription service will not work")
            self.client = None
            
        self.temp_dir = tempfile.gettempdir()
        self.active_jobs = {}  # Store active transcription jobs

    async def transcribe_audio(self, audio_path: Path) -> Optional[str]:
        """Transcribe an audio file using OpenAI's Whisper API."""
        try:
            # Get audio duration
            duration = self._get_audio_duration(audio_path)
            log.info(f"Audio duration: {duration} seconds")
            
            # Process in chunks
            full_transcript = []
            for start_time in range(0, int(duration), self.chunk_size_seconds):
                # Extract chunk
                chunk_path = self._extract_audio_chunk(audio_path, start_time, self.chunk_size_seconds)
                if not chunk_path:
                    continue
                    
                # Transcribe chunk
                chunk_transcript = await self._transcribe_chunk(chunk_path)
                if chunk_transcript:
                    full_transcript.append(chunk_transcript)
                    
                # Clean up chunk file
                os.remove(chunk_path)
                
            return " ".join(full_transcript) if full_transcript else None
            
        except Exception as e:
            log.error(f"Error transcribing audio file: {str(e)}")
            return None

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get the duration of an audio file using ffprobe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception as e:
            log.error(f"Error getting audio duration: {str(e)}")
            return 0

    def _extract_audio_chunk(self, audio_path: Path, start_time: int, duration: int) -> Optional[Path]:
        """Extract a chunk of audio using ffmpeg."""
        try:
            chunk_path = Path(self.temp_dir) / f"chunk_{start_time}.mp3"
            
            # Use -y flag to automatically overwrite existing files
            cmd = [
                'ffmpeg',
                '-y',  # Automatically overwrite output files
                '-i', str(audio_path),
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'libmp3lame',
                '-loglevel', 'error',
                str(chunk_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return chunk_path
        except Exception as e:
            log.error(f"Error extracting audio chunk: {str(e)}")
            return None

    @retry(
        retry=retry_if_exception_type((RateLimitError, APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=60)
    )
    async def _transcribe_chunk(self, chunk_path: Path) -> Optional[str]:
        """Transcribe a single chunk using OpenAI's Whisper API."""
        try:
            with open(chunk_path, 'rb') as audio_file:
                response = await asyncio.to_thread(
                    self.client.audio.transcriptions.create,
                    file=audio_file,
                    model=AUDIO_MODEL,
                    language="en"
                )
                
            return response.text

        except Exception as e:
            log.error(f"Error transcribing chunk: {str(e)}")
            return None
            
    async def api_transcribe(self, 
                        audio_file_path: str, 
                        user_id: str,
                        options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle API transcription requests with status tracking and options.
        
        Args:
            audio_file_path: Path to the uploaded audio file
            user_id: ID of the user requesting transcription
            options: Dictionary of transcription options including:
                - language: Language code (default: "en")
                - format: Output format (default: "text", options: "text", "json", "srt", "vtt")
                - speaker_detection: Enable speaker detection (default: False)
                
        Returns:
            Dictionary with transcription job details including:
                - id: Unique transcription ID
                - status: Current status (processing, completed, failed)
                - progress: Progress percentage (0-100)
                - estimated_completion_time: Estimated completion time
        """
        # Set default options
        if options is None:
            options = {}
            
        language = options.get("language", "en")
        output_format = options.get("format", "text")
        speaker_detection = options.get("speaker_detection", "false").lower() == "true"
        
        # Generate unique transcription ID
        transcription_id = f"T_{uuid.uuid4()}"
        
        # Validate file exists
        if not os.path.exists(audio_file_path):
            return {
                "id": transcription_id,
                "status": "failed",
                "error": "Audio file not found"
            }
            
        # Get file info
        try:
            audio_duration = self._get_audio_duration(Path(audio_file_path))
            file_size = os.path.getsize(audio_file_path)
            
            # Estimate completion time (rough estimate based on file duration)
            # Typically transcription takes 0.3-0.5x real-time duration
            processing_factor = 0.4  # Estimated processing speed relative to audio duration
            estimated_seconds = audio_duration * processing_factor
            estimated_completion_time = datetime.now() + timedelta(seconds=estimated_seconds)
            
            # Store job info
            self.active_jobs[transcription_id] = {
                "id": transcription_id,
                "user_id": user_id,
                "file_path": audio_file_path,
                "status": "processing",
                "progress": 0,
                "start_time": datetime.now().isoformat(),
                "estimated_completion_time": estimated_completion_time.isoformat(),
                "duration_seconds": audio_duration,
                "file_size_bytes": file_size,
                "options": {
                    "language": language,
                    "format": output_format,
                    "speaker_detection": speaker_detection
                }
            }
            
            # Start async transcription process
            asyncio.create_task(self._process_transcription_job(transcription_id))
            
            # Return initial status
            return {
                "id": transcription_id,
                "status": "processing",
                "progress": 0,
                "estimated_completion_time": estimated_completion_time.isoformat(),
                "duration_seconds": audio_duration
            }
            
        except Exception as e:
            log.error(f"Error starting transcription job: {str(e)}")
            return {
                "id": transcription_id,
                "status": "failed",
                "error": f"Error starting transcription: {str(e)}"
            }
            
    async def _process_transcription_job(self, transcription_id: str) -> None:
        """Process a transcription job asynchronously and update its status."""
        if transcription_id not in self.active_jobs:
            log.error(f"Transcription job {transcription_id} not found")
            return
            
        job = self.active_jobs[transcription_id]
        audio_path = Path(job["file_path"])
        options = job["options"]
        
        try:
            # Update status to processing
            self.active_jobs[transcription_id]["status"] = "processing"
            self.active_jobs[transcription_id]["progress"] = 10
            
            # Get audio duration
            duration = self._get_audio_duration(audio_path)
            
            # Process in chunks
            full_transcript = []
            chunks_total = max(1, int(duration) // self.chunk_size_seconds)
            chunks_processed = 0
            
            for start_time in range(0, int(duration), self.chunk_size_seconds):
                # Extract chunk
                chunk_path = self._extract_audio_chunk(audio_path, start_time, self.chunk_size_seconds)
                if not chunk_path:
                    continue
                    
                # Transcribe chunk
                chunk_transcript = await self._transcribe_chunk(chunk_path)
                if chunk_transcript:
                    full_transcript.append(chunk_transcript)
                    
                # Clean up chunk file
                os.remove(chunk_path)
                
                # Update progress
                chunks_processed += 1
                progress = min(95, int((chunks_processed / chunks_total) * 100))
                self.active_jobs[transcription_id]["progress"] = progress
                
            # Format the transcript according to requested format
            final_transcript = " ".join(full_transcript) if full_transcript else ""
            
            if options["format"] == "json" and options["speaker_detection"]:
                # Format with speaker detection (simplified example)
                formatted_transcript = self._format_transcript_with_speakers(final_transcript)
            else:
                # Plain text format
                formatted_transcript = final_transcript
                
            # Update job with completed status and results
            self.active_jobs[transcription_id].update({
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.now().isoformat(),
                "transcript": formatted_transcript
            })
            
        except Exception as e:
            log.error(f"Error processing transcription job {transcription_id}: {str(e)}")
            self.active_jobs[transcription_id].update({
                "status": "failed",
                "error": str(e)
            })
            
    def _format_transcript_with_speakers(self, transcript: str) -> Dict[str, Any]:
        """Format a transcript with speaker detection (simplified example)."""
        # This is a simplified implementation - in reality, you would use
        # a more sophisticated speaker diarization system
        
        segments = []
        current_time = 0.0
        
        lines = transcript.split('\n')
        for line in lines:
            if not line.strip():
                continue
                
            # Simple parsing for "Speaker: Text" format
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip()
                text = parts[1].strip()
            else:
                speaker = "Unknown"
                text = line.strip()
                
            # Estimate timing (very rough approximation)
            # In reality, this would come from the speech recognition system
            words = len(text.split())
            duration = words * 0.5  # rough estimate: 0.5 seconds per word
            
            segments.append({
                "speaker": speaker,
                "text": text,
                "start_time": round(current_time, 1),
                "end_time": round(current_time + duration, 1),
                "confidence": 0.9  # placeholder confidence score
            })
            
            current_time += duration
            
        return {"segments": segments}
            
    def get_transcription_status(self, transcription_id: str) -> Dict[str, Any]:
        """Get the status of a transcription job."""
        if transcription_id not in self.active_jobs:
            return {
                "status": "not_found",
                "error": "Transcription job not found"
            }
            
        # Return a copy of the job status to avoid modification
        job = self.active_jobs[transcription_id].copy()
        
        # Filter out internal fields
        if "file_path" in job:
            del job["file_path"]
            
        return job
        
    def get_completed_transcription(self, transcription_id: str) -> Dict[str, Any]:
        """Get a completed transcription result."""
        status = self.get_transcription_status(transcription_id)
        
        if status.get("status") != "completed":
            return {
                "id": transcription_id,
                "status": status.get("status", "unknown"),
                "message": "Transcription is not completed yet" if status.get("status") == "processing" else "Transcription failed or not found"
            }
            
        return status
        
    def link_transcription_to_session(self, transcription_id: str, session_id: str) -> Dict[str, Any]:
        """Link a completed transcription to a therapy session."""
        if transcription_id not in self.active_jobs:
            return {
                "status": "failed",
                "error": "Transcription job not found"
            }
            
        job = self.active_jobs[transcription_id]
        
        if job.get("status") != "completed":
            return {
                "status": "failed",
                "error": "Cannot link incomplete transcription"
            }
            
        if "linked_session_id" in job and job["linked_session_id"] != session_id:
            return {
                "status": "failed",
                "error": "Transcription already linked to a different session"
            }
            
        # Link the transcription
        self.active_jobs[transcription_id]["linked_session_id"] = session_id
        
        return {
            "status": "success",
            "message": "Transcription linked to session",
            "transcription_id": transcription_id,
            "session_id": session_id
        }
        
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up old transcription jobs that exceed the maximum age."""
        now = datetime.now()
        max_age = timedelta(hours=max_age_hours)
        jobs_to_remove = []
        
        for job_id, job in self.active_jobs.items():
            # Check completed jobs
            if job.get("completed_at"):
                completed_time = datetime.fromisoformat(job["completed_at"])
                if now - completed_time > max_age:
                    jobs_to_remove.append(job_id)
            # Check failed or stuck jobs
            elif job.get("start_time"):
                start_time = datetime.fromisoformat(job["start_time"])
                if now - start_time > max_age:
                    jobs_to_remove.append(job_id)
                    
        # Remove the old jobs
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
            
        return len(jobs_to_remove) 