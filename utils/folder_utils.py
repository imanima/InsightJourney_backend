import os

def create_folders(app):
    """Create necessary folders for the application."""
    folders = [
        app.config['UPLOAD_FOLDER'],
        app.config['TRANSCRIPTS_FOLDER'],
        app.config['ANALYSIS_FOLDER']
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder) 