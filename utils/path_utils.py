"""
Utility functions for handling file paths in the application.
"""

import os
from pathlib import Path

def get_uploads_path() -> Path:
    """
    Get the path to the uploads directory.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path: Path to the uploads directory
    """
    # Get the base directory (project root)
    base_dir = Path(__file__).parent.parent
    
    # Define uploads directory
    uploads_dir = base_dir / "uploads"
    
    # Ensure the directory exists
    os.makedirs(uploads_dir, exist_ok=True)
    
    return uploads_dir

def get_test_data_path() -> Path:
    """
    Get the path to the test data directory.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path: Path to the test data directory
    """
    # Get the base directory (project root)
    base_dir = Path(__file__).parent.parent
    
    # Define test data directory
    test_data_dir = base_dir / "test_data"
    
    # Ensure the directory exists
    os.makedirs(test_data_dir, exist_ok=True)
    
    return test_data_dir 