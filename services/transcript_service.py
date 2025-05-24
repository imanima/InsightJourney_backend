from typing import Dict, List, Any
import re

def process_transcript(transcript: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Process a transcript and extract emotions, beliefs, and topics.
    
    Args:
        transcript (Dict[str, Any]): A dictionary containing the transcript text and segments
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing extracted emotions, beliefs, and topics
    """
    # Initialize result dictionary
    result = {
        "emotions": [],
        "beliefs": [],
        "topics": []
    }
    
    # Process each segment
    for segment in transcript.get("segments", []):
        text = segment.get("text", "").lower()
        
        # Extract emotions
        emotion_patterns = {
            "Joy": r"(?:feeling|am|feel)\s+(?:really\s+)?(?:happy|joyful|excited|elated)",
            "Gratitude": r"(?:grateful|thankful|appreciate)",
            "Pride": r"(?:proud|accomplished|achieved)",
            "Confidence": r"(?:confident|capable|strong)",
            "Determination": r"(?:determined|committed|dedicated)",
            "Growth": r"(?:grow|learn|develop|improve)"
        }
        
        for emotion, pattern in emotion_patterns.items():
            if re.search(pattern, text):
                # Calculate intensity based on modifiers
                intensity = 5  # default
                if "really" in text:
                    intensity = 8
                elif "very" in text:
                    intensity = 7
                
                result["emotions"].append({
                    "name": emotion,
                    "intensity": intensity,
                    "context": text
                })
        
        # Extract beliefs
        belief_patterns = [
            r"i believe (?:that )?(.+?)(?:\.|$)",
            r"i think (?:that )?(.+?)(?:\.|$)",
            r"i feel (?:that )?(.+?)(?:\.|$)",
            r"i know (?:that )?(.+?)(?:\.|$)"
        ]
        
        for pattern in belief_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                belief = match.group(1).strip()
                if belief and len(belief) > 5:  # Avoid very short beliefs
                    result["beliefs"].append(belief)
        
        # Extract topics
        topic_patterns = [
            r"(?:about|regarding|concerning)\s+(\w+(?:\s+\w+){0,3})",
            r"(?:in|at|on)\s+(\w+(?:\s+\w+){0,3})",
            r"(?:the|a|an)\s+(\w+(?:\s+\w+){0,3})"
        ]
        
        for pattern in topic_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                topic = match.group(1).strip()
                if topic and len(topic) > 3:  # Avoid very short topics
                    result["topics"].append(topic)
    
    # Remove duplicates while preserving order
    # For emotions, use name as key
    seen_emotions = {}
    unique_emotions = []
    for emotion in result["emotions"]:
        if emotion["name"] not in seen_emotions:
            seen_emotions[emotion["name"]] = True
            unique_emotions.append(emotion)
    result["emotions"] = unique_emotions
    
    # For beliefs and topics, they are strings so we can use set
    result["beliefs"] = list(dict.fromkeys(result["beliefs"]))
    result["topics"] = list(dict.fromkeys(result["topics"]))
    
    return result 