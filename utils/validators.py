from functools import wraps
from flask import request, jsonify
from pydantic import BaseModel, ValidationError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionUploadSchema(BaseModel):
    title: str
    date: str
    client_name: str | None = None
    notes: str | None = None

class AdminSettingsSchema(BaseModel):
    gpt_model: str
    max_tokens: int
    temperature: float
    system_prompt_template: str | None = None
    analysis_prompt_template: str | None = None

def validate_request(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
                validated_data = schema(**data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                logger.error(f"Validation Error: {str(e)}")
                return jsonify({'error': 'Validation Error', 'details': e.errors()}), 400
        return decorated_function
    return decorator 

def validate_session_data(data):
    """Validate session data
    
    Args:
        data (dict): Session data to validate
        
    Returns:
        str: Error message if validation fails, None if validation succeeds
    """
    if not data:
        return "Session data must be provided"
        
    # Required fields
    required_fields = ['title', 'date']
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
            
    # Validate title
    title = data.get('title', '').strip()
    if not title:
        return "Title cannot be empty"
    if len(title) > 200:
        return "Title cannot be longer than 200 characters"
        
    # Validate date
    try:
        date_str = data.get('date')
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD"
        
    # Optional fields length validation
    if 'client_name' in data and len(data['client_name']) > 100:
        return "Client name cannot be longer than 100 characters"
        
    if 'notes' in data and len(data['notes']) > 5000:
        return "Notes cannot be longer than 5000 characters"
        
    if 'transcript' in data and len(data['transcript']) > 50000:
        return "Transcript cannot be longer than 50000 characters"
        
    # Validate status if provided
    valid_statuses = ['pending', 'in_progress', 'completed', 'archived']
    if 'status' in data and data['status'] not in valid_statuses:
        return f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
    return None 