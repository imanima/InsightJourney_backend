"""
Taxonomy Service

This service loads and provides access to the taxonomy data 
(emotions, topics, beliefs) for use in analysis and classification.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TaxonomyService:
    """Service to manage and access taxonomy data"""
    
    def __init__(self):
        """Initialize the taxonomy service by loading taxonomy data"""
        self.resources_dir = Path(__file__).parent.parent / "resources"
        self.emotions = []
        self.topics = []
        self.beliefs = []
        self.emotion_names = []
        self.topic_names = []
        self.belief_names = []
        self.main_topics = []
        self.load_taxonomies()
        
    def load_taxonomies(self):
        """Load taxonomy data from JSON files"""
        try:
            # Load emotions
            emotion_path = self.resources_dir / "emotion_taxonomy.json"
            if emotion_path.exists():
                with open(emotion_path, 'r') as f:
                    self.emotions = json.load(f)
                    self.emotion_names = [e['name'] for e in self.emotions]
                    logger.info(f"Loaded {len(self.emotions)} emotions from taxonomy")
            else:
                logger.warning(f"Emotion taxonomy file not found at {emotion_path}")
                
            # Load topics
            topic_path = self.resources_dir / "topic_taxonomy.json"
            if topic_path.exists():
                with open(topic_path, 'r') as f:
                    self.topics = json.load(f)
                    self.topic_names = [t['name'] for t in self.topics]
                    self.main_topics = [t['name'] for t in self.topics if t.get('level') == 'main']
                    logger.info(f"Loaded {len(self.topics)} topics from taxonomy")
            else:
                logger.warning(f"Topic taxonomy file not found at {topic_path}")
                
            # Load beliefs
            belief_path = self.resources_dir / "belief_taxonomy.json"
            if belief_path.exists():
                with open(belief_path, 'r') as f:
                    self.beliefs = json.load(f)
                    self.belief_names = [b['name'] for b in self.beliefs]
                    logger.info(f"Loaded {len(self.beliefs)} beliefs from taxonomy")
            else:
                logger.warning(f"Belief taxonomy file not found at {belief_path}")
                
        except Exception as e:
            logger.error(f"Error loading taxonomies: {str(e)}")
    
    def get_emotions(self) -> List[Dict[str, Any]]:
        """Get all emotions from the taxonomy"""
        return self.emotions
    
    def get_topics(self) -> List[Dict[str, Any]]:
        """Get all topics from the taxonomy"""
        return self.topics
    
    def get_main_topics(self) -> List[Dict[str, Any]]:
        """Get only main topics (not subtopics)"""
        return [t for t in self.topics if t.get('level') == 'main']
    
    def get_subtopics(self, parent_topic: str) -> List[Dict[str, Any]]:
        """Get subtopics for a specific parent topic"""
        return [t for t in self.topics if t.get('parent') == parent_topic]
    
    def get_beliefs(self) -> List[Dict[str, Any]]:
        """Get all beliefs from the taxonomy"""
        return self.beliefs
    
    def get_emotion_names(self) -> List[str]:
        """Get a list of all emotion names"""
        return self.emotion_names
    
    def get_topic_names(self) -> List[str]:
        """Get a list of all topic names"""
        return self.topic_names
    
    def get_main_topic_names(self) -> List[str]:
        """Get a list of main topic names only"""
        return self.main_topics
    
    def get_belief_names(self) -> List[str]:
        """Get a list of all belief names"""
        return self.belief_names
    
    def find_closest_emotion(self, emotion_name: str) -> Optional[str]:
        """Find the closest matching emotion in our taxonomy"""
        if not emotion_name:
            return None
            
        # Direct match
        emotion_lower = emotion_name.lower()
        for e in self.emotion_names:
            if e.lower() == emotion_lower:
                return e
                
        # Partial match
        for e in self.emotion_names:
            if e.lower() in emotion_lower or emotion_lower in e.lower():
                return e
                
        return None
    
    def find_closest_topic(self, topic_name: str) -> Optional[str]:
        """Find the closest matching topic in our taxonomy"""
        if not topic_name:
            return None
            
        # Direct match
        topic_lower = topic_name.lower()
        for t in self.topic_names:
            if t.lower() == topic_lower:
                return t
        
        # Check for main topics first (higher priority)
        for t in self.main_topics:
            if t.lower() in topic_lower or topic_lower in t.lower():
                return t
        
        # Then check all topics including subtopics
        best_match = None
        best_score = 0
        
        for t in self.topic_names:
            t_lower = t.lower()
            
            # Contains match in either direction
            if t_lower in topic_lower:
                score = len(t_lower) / len(topic_lower)  # Longer matches get higher score
                if score > best_score:
                    best_score = score
                    best_match = t
            elif topic_lower in t_lower:
                score = len(topic_lower) / len(t_lower)  # Longer matches get higher score
                if score > best_score:
                    best_score = score
                    best_match = t
                
        # Only return if we have a reasonably good match (avoids very weak connections)
        if best_score > 0.3:
            return best_match
                
        return None
    
    def get_analysis_prompt_constraints(self) -> str:
        """
        Get a formatted string with taxonomy constraints for analysis prompts
        """
        emotions_list = ", ".join(self.emotion_names)
        main_topics_list = ", ".join(self.main_topics)
        
        constraints = f"""
IMPORTANT CONSTRAINTS - YOU MUST FOLLOW THESE EXACTLY:
1. When identifying emotions, you MUST ONLY use the following approved emotions:
   {emotions_list}
   Do not use any other emotion terms, even if they seem similar.

2. When identifying topics, you MUST ONLY use these main categories and their sub-topics:
   {main_topics_list}
   
3. For sub-topics, only use those that directly fall under these main categories.

4. For each identified emotion, provide an intensity rating (1-10) and relevant context.

5. For each belief, assess whether it appears to be limiting or empowering.

6. Format each emotion exactly as: "EmotionName (intensity: X) - Context"
   where EmotionName is one of the approved emotions listed above.

7. Format each topic exactly as: "- TopicName" 
   where TopicName is one of the approved topics or sub-topics.

Do NOT attempt to add new emotions or topics that aren't on these lists.
"""
        return constraints.strip()

# Create a singleton instance of the service
taxonomy_service = TaxonomyService() 