"""
Analysis helpers for direct API calls to language models
Used as a replacement for the removed test_api_direct.py file
"""

import logging
import json
import os
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Sample transcript for testing
SAMPLE_TRANSCRIPT = """
Coach: How have you been feeling since our last session?
Client: I've been quite stressed about work. The deadlines keep piling up.
Coach: I hear that work pressure has been building. How has that affected your wellbeing?
Client: I've been sleeping poorly, and I notice I get anxious when I think about my tasks.
Coach: It sounds like this stress is impacting both your mental and physical health.
Client: Yes, and I feel like I'm not doing enough, even though I'm working long hours.
Coach: That's interesting. Do you often feel like your efforts aren't sufficient?
Client: I guess I do. I always think I should be doing more or doing better.
"""

def analyze_session(transcript, session_id=None, save_results=False):
    """
    Simplified analysis function that returns mock data
    This replaces the implementation from the deleted test_api_direct.py
    
    In a production environment, this would connect to OpenAI or another LLM
    """
    logger.info(f"Analyzing session {session_id if session_id else 'unknown'}")
    
    # Check if we have an API key (for future real implementation)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No OpenAI API key found, using mock data")
    
    # Generate mock analysis results
    results = {
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "results": {
            "emotions": [
                {
                    "name": "Anxiety",
                    "intensity": 8,
                    "context": "When discussing work deadlines",
                    "topics": ["Work Stress", "Performance"]
                },
                {
                    "name": "Frustration",
                    "intensity": 6,
                    "context": "Feeling inadequate despite long hours",
                    "topics": ["Self-Criticism", "Work-Life Balance"]
                }
            ],
            "topics": [
                {
                    "name": "Work Stress",
                    "relevance": 0.9
                },
                {
                    "name": "Self-Criticism",
                    "relevance": 0.8
                },
                {
                    "name": "Work-Life Balance",
                    "relevance": 0.7
                }
            ],
            "insights": [
                {
                    "text": "Client exhibits perfectionist tendencies",
                    "category": "Self-awareness",
                    "confidence": 0.85,
                    "topics": ["Self-Criticism", "Work Stress"]
                },
                {
                    "text": "Stress is manifesting in physical symptoms",
                    "category": "Well-being",
                    "confidence": 0.9,
                    "topics": ["Work Stress", "Health"]
                }
            ],
            "action_items": [
                {
                    "description": "Practice setting boundaries at work",
                    "priority": "High",
                    "due_date": "Within a week",
                    "status": "pending",
                    "topics": ["Work-Life Balance", "Self-Care"]
                },
                {
                    "description": "Implement a bedtime routine to improve sleep",
                    "priority": "Medium",
                    "due_date": "Starting tonight",
                    "status": "pending",
                    "topics": ["Health", "Self-Care"]
                }
            ]
        }
    }
    
    # If save_results is True, we would save to database in a real implementation
    if save_results:
        logger.info(f"Saving analysis results for session {session_id}")
        # This would interact with database in a real implementation
    
    return results 