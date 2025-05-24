import os
from werkzeug.utils import secure_filename
from typing import Optional

class LocalStorage:
    """Simple local storage implementation"""
    def upload(self, file_path: str) -> str:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path

    def delete(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False

# Use local storage implementation
storage = LocalStorage()

class FileService:
    def __init__(self):
        self.upload_folder = 'uploads'
        self.allowed_extensions = {'mp3', 'wav', 'm4a'}
        self.max_content_length = 50 * 1024 * 1024  # 50MB

    def allowed_file(self, filename: str) -> bool:
        """Check if the file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_file(self, file, user_id: str) -> Optional[str]:
        """Save a file and return its path."""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, str(user_id), filename)
            return storage.upload(file_path)
        return None

    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        return storage.delete(file_path) 