import os
import asyncio
from pathlib import Path
from typing import Optional
from services.transcription_service import TranscriptionService

async def transcribe_audio_file(audio_path: str, output_dir: str = "transcriptions") -> Optional[str]:
    """Transcribe a single audio file and save the result"""
    try:
        # Initialize transcription service
        transcription_service = TranscriptionService()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get filename and create output path
        filename = os.path.basename(audio_path)
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_transcribed.txt")
        
        # Transcribe audio
        print(f"\nTranscribing {filename}...")
        transcript = await transcription_service.transcribe_audio(Path(audio_path))
        
        # Save transcription
        with open(output_path, "w") as f:
            f.write(transcript)
        
        print(f"Successfully transcribed {filename}:")
        print(f"- Saved transcription to: {output_path}")
        
        return transcript
    except Exception as e:
        print(f"Error transcribing {filename}: {str(e)}")
        return None

async def transcribe_directory(directory: str, output_dir: str = "transcriptions") -> None:
    """Transcribe all audio files in a directory"""
    try:
        # Get all audio files in directory
        audio_extensions = ['.mp3', '.m4a', '.wav', '.mp4', '.mpeg', '.mpga', '.webm']
        files = [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
            and any(f.lower().endswith(ext) for ext in audio_extensions)
        ]
        
        if not files:
            print(f"No audio files found in {directory}")
            return
        
        # Process all files concurrently
        tasks = []
        for filename in files:
            file_path = os.path.join(directory, filename)
            task = transcribe_audio_file(file_path, output_dir)
            tasks.append(task)
        
        # Wait for all tasks to complete
        transcripts = await asyncio.gather(*tasks)
        successful = [t for t in transcripts if t is not None]
        
        # Print summary
        print("\nTranscription Summary:")
        print(f"Processed {len(files)} audio files")
        print(f"Successfully transcribed {len(successful)} files")
        
    except Exception as e:
        print(f"Error processing directory: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <audio_file_or_directory> [output_directory]")
        sys.exit(1)
    
    path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "transcriptions"
    
    if os.path.isfile(path):
        asyncio.run(transcribe_audio_file(path, output_dir))
    elif os.path.isdir(path):
        asyncio.run(transcribe_directory(path, output_dir))
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1) 