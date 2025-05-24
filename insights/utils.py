"""
Utility functions for the Insights module.

These functions help with data manipulation, statistical analysis,
and Cypher query generation for the various insight features.
"""

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

def generate_insight_id(prefix: str = "INS") -> str:
    """Generate a unique ID for an insight"""
    return f"{prefix}_{str(uuid.uuid4())}"

def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage with error handling"""
    if total == 0:
        return 0
    return round((part / total) * 100, 1)

def detect_significant_change(values: List[float], threshold: float = 1.0) -> List[int]:
    """
    Detect indices where values change significantly (more than threshold)
    Returns list of indices where significant changes occur
    """
    if not values or len(values) < 2:
        return []
    
    changes = []
    for i in range(1, len(values)):
        if abs(values[i] - values[i-1]) > threshold:
            changes.append(i)
    
    return changes

def markov_chain_prediction(
    transitions: Dict[str, Dict[str, int]], 
    current_state: str,
    steps: int = 1
) -> Dict[str, float]:
    """
    Predict next state using a Markov chain model
    
    Args:
        transitions: Transition count matrix as nested dict
        current_state: Current state to predict from
        steps: Number of steps to predict ahead
        
    Returns:
        Dictionary of predicted states and their probabilities
    """
    if current_state not in transitions:
        return {}
    
    # For single step prediction
    if steps == 1:
        total = sum(transitions[current_state].values())
        return {
            state: count / total 
            for state, count in transitions[current_state].items()
        }
    
    # For multi-step prediction (simplified implementation)
    current_probs = {current_state: 1.0}
    for _ in range(steps):
        new_probs = {}
        for state, prob in current_probs.items():
            if state in transitions:
                total = sum(transitions[state].values())
                for next_state, count in transitions[state].items():
                    next_prob = count / total
                    new_probs[next_state] = new_probs.get(next_state, 0) + (prob * next_prob)
        current_probs = new_probs
    
    return current_probs

def calculate_correlation(
    occurrences_together: int,
    total_emotion_occurrences: int,
    total_topic_occurrences: int,
    session_count: int
) -> Tuple[float, float]:
    """
    Calculate correlation percentage and confidence score
    
    Args:
        occurrences_together: How many times emotion and topic appear together
        total_emotion_occurrences: Total occurrences of the emotion
        total_topic_occurrences: Total occurrences of the topic
        session_count: Total number of sessions
        
    Returns:
        Tuple of (correlation_percentage, confidence_score)
    """
    # Correlation percentage: how often topic appears when emotion is present
    if total_emotion_occurrences == 0:
        correlation = 0
    else:
        correlation = (occurrences_together / total_emotion_occurrences) * 100
    
    # Confidence score based on sample size relative to total sessions
    # More occurrences = higher confidence
    confidence = min(1.0, (occurrences_together / max(1, session_count)) * 2)
    
    return round(correlation, 1), round(confidence, 2)

def format_turning_point_description(
    emotion: str,
    date: str,
    previous_intensity: float,
    current_intensity: float,
    insight_name: Optional[str] = None
) -> str:
    """Format a human-readable description of a turning point"""
    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
    formatted_date = date_obj.strftime("%b %d")
    
    change = round(previous_intensity - current_intensity, 1)
    change_text = f"decreased by {change}" if change > 0 else f"increased by {abs(change)}"
    
    if insight_name:
        return f"⚡ On {formatted_date} your {emotion.lower()} {change_text} points after Insight '{insight_name}'."
    else:
        return f"⚡ On {formatted_date} your {emotion.lower()} {change_text} points."

def format_correlation_description(
    emotion: str,
    topic: str,
    percentage: float
) -> str:
    """Format a human-readable description of a correlation"""
    emotion_emoji = get_emotion_emoji(emotion)
    return f"{emotion_emoji} {emotion} spikes {percentage}% of the time when '{topic}' appears."

def get_emotion_emoji(emotion: str) -> str:
    """Get an appropriate emoji for an emotion"""
    emotion_map = {
        "Anxiety": "🌧️",
        "Sadness": "😢",
        "Anger": "😠",
        "Fear": "😨",
        "Joy": "😊",
        "Hope": "✨",
        "Pride": "🏆",
        "Guilt": "😓",
        "Shame": "🙈",
        "Disappointment": "😔"
    }
    return emotion_map.get(emotion, "🔍")

def generate_cypher_query_turning_point(emotion_name: str = "Anxiety", threshold: float = 1.0) -> str:
    """Generate Cypher query for finding turning points in emotion intensity"""
    return f"""
    MATCH (s:Session)-[r:HAS_EMOTION]->(e:Emotion)
    WHERE e.name = '{emotion_name}'
    WITH s, r.intensity AS intensity
    ORDER BY s.date
    WITH collect({{date: s.date, id: s.id, intensity: intensity}}) AS points
    UNWIND range(1, size(points)-1) AS i
    WITH points[i-1] AS prev, points[i] AS curr
    WHERE curr.intensity < prev.intensity - {threshold}
    RETURN curr.date AS turning_date, 
           curr.id AS session_id,
           prev.intensity AS previous_intensity, 
           curr.intensity AS current_intensity
    ORDER BY turning_date DESC
    LIMIT 1
    """

def generate_cypher_query_correlation() -> str:
    """Generate Cypher query for finding emotion and topic correlations"""
    return """
    MATCH (s:Session)-[:HAS_EMOTION]->(e:Emotion), 
          (s:Session)-[:HAS_TOPIC]->(t:Topic)
    WITH e.name AS emotion, t.name AS topic, count(s) AS together_count
    MATCH (s:Session)-[:HAS_EMOTION]->(e:Emotion)
    WHERE e.name = emotion
    WITH emotion, topic, together_count, count(s) AS emotion_count
    MATCH (s:Session)-[:HAS_TOPIC]->(t:Topic)
    WHERE t.name = topic
    WITH emotion, topic, together_count, emotion_count, count(s) AS topic_count
    MATCH (s:Session)
    WITH emotion, topic, together_count, emotion_count, topic_count, count(s) AS total_sessions
    RETURN emotion, 
           topic, 
           together_count,
           emotion_count,
           topic_count,
           total_sessions,
           (1.0 * together_count / emotion_count) * 100 AS correlation_percentage
    ORDER BY correlation_percentage DESC
    LIMIT 10
    """

def generate_cypher_query_insight_cascade() -> str:
    """Generate Cypher query for finding insight cascades"""
    return """
    MATCH path=(i1:Insight)<-[:RELATES_TO_INSIGHT*1..3]-(i2:Insight)
    WHERE i1 <> i2
    WITH i1, i2, length(path) AS distance
    RETURN i1.id AS source_id, 
           i1.name AS source_name,
           i1.created_at AS source_date,
           i2.id AS target_id, 
           i2.name AS target_name,
           i2.created_at AS target_date,
           distance
    ORDER BY source_date
    """

def generate_cypher_query_challenge_persistence() -> str:
    """Generate Cypher query for tracking challenge persistence"""
    return """
    MATCH (c:Challenge)<-[:HAS_CHALLENGE]-(s:Session)
    WITH c, collect(s) AS sessions
    WITH c, sessions, sessions[0].date AS first_date, sessions[size(sessions)-1].date AS last_date
    WITH c, sessions, first_date, last_date, 
         duration.between(datetime(first_date), datetime(last_date)).days AS days
    WHERE size(sessions) > 1
    RETURN c.id AS challenge_id,
           c.name AS challenge_name,
           first_date,
           last_date,
           days AS persistence_days,
           size(sessions) AS session_count
    ORDER BY session_count DESC
    LIMIT 10
    """ 