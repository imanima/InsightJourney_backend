"""
Conversation generator for creating realistic coaching session transcripts.
Uses OpenAI's API to generate conversations based on personas and session progression.
"""

import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from typing import Dict, List, Any
import logging
from pathlib import Path
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configurations
from config.personas import CLIENT_PERSONA, COACH_PERSONA
from config.session_progression import SESSION_PROGRESSION

class ConversationGenerator:
    def __init__(self, openai_api_key: str):
        """Initialize the conversation generator with OpenAI API key."""
        self.openai_api_key = openai_api_key
        # Initialize client in a container-friendly way without optional parameters
        self.client = OpenAI(api_key=openai_api_key)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def _create_session_prompt(self, session_data: Dict[str, Any], session_number: int) -> str:
        """Create a detailed prompt for the conversation generation."""
        return f"""
        Generate a natural, flowing coaching conversation between {COACH_PERSONA['name']} (coach) and {CLIENT_PERSONA['name']} (client).
        
        Session Information:
        - Session Number: {session_number}
        - Theme: {session_data['theme']}
        - Topics to cover: {', '.join(session_data['topics'])}
        - Expected outcomes: {', '.join(session_data['expected_outcomes'])}

        Coach Profile:
        - Name: {COACH_PERSONA['name']}
        - Style: {COACH_PERSONA['coaching_style']['approach']}
        - Techniques: {', '.join(COACH_PERSONA['coaching_style']['techniques'])}

        Client Profile:
        - Name: {CLIENT_PERSONA['name']}
        - Background: {CLIENT_PERSONA['background']['current_role']}
        - Current Situation: {CLIENT_PERSONA['personal_context']['family']}
        - Challenges: {', '.join(CLIENT_PERSONA['challenges'])}

        Requirements:
        1. Create a natural, flowing conversation that feels authentic and unscripted
        2. Include emotional moments and reactions that feel genuine
        3. Show the coach's professional style while maintaining warmth and empathy
        4. Demonstrate the client's personality through their language and examples
        5. Include timestamps for each exchange (approximately 45-60 minute session)
        6. Format as a natural transcript with clear speaker labels
        7. Ensure the conversation leads to meaningful outcomes
        8. Keep the focus on the client's journey and growth
        9. Include specific examples and concrete next steps
        10. Show progression from previous sessions
        11. Include moments of reflection and insight
        12. Add natural pauses and transitions between topics
        13. Include follow-up questions and clarifications
        14. End with clear action items and next steps

        Key Elements to Naturally Include:
        - Emotions: Show through dialogue and reactions
        - Beliefs: Reveal through client's language and examples
        - Action Items: Develop through collaborative discussion
        - Challenges: Explore through specific situations
        - Insights: Emerge through reflection and discussion

        Conversation Flow:
        1. Opening and check-in (5-7 minutes)
           - How client is feeling
           - Updates since last session
           - What they want to focus on

        2. Main discussion (30-40 minutes)
           - Deep exploration of topics
           - Natural progression of ideas
           - Moments of discovery
           - Practical solutions

        3. Reflection (5-7 minutes)
           - Key learnings
           - New perspectives
           - Aha moments

        4. Closing (5-7 minutes)
           - Specific next steps
           - Support needed
           - Follow-up plan

        Format the output as:
        [TIMESTAMP] Speaker: Text

        The conversation should feel like a real coaching session, with natural flow and authentic interaction.
        """

    def generate_conversation(self, session_data: Dict[str, Any], session_number: int) -> str:
        """Generate a conversation for a specific session."""
        try:
            prompt = self._create_session_prompt(session_data, session_number)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional conversation generator for coaching sessions. Create natural, authentic conversations that flow like real coaching sessions while capturing key elements organically."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000  # Increased token limit for longer conversations
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating conversation for session {session_number}: {str(e)}")
            raise

    def generate_all_sessions(self) -> None:
        """Generate conversations for all sessions and save them to files."""
        start_date = datetime.now()
        
        for month, sessions in SESSION_PROGRESSION.items():
            for session_name, session_data in sessions.items():
                session_number = int(session_name.split('_')[1])
                session_date = start_date + timedelta(weeks=(session_number-1))
                
                logger.info(f"Generating conversation for {session_name}")
                
                try:
                    conversation = self.generate_conversation(session_data, session_number)
                    
                    # Create filename with date and session number
                    filename = f"session_{session_number:02d}_{session_date.strftime('%Y%m%d')}.txt"
                    filepath = self.output_dir / filename
                    
                    # Save conversation to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"Session {session_number}: {session_data['theme']}\n")
                        f.write(f"Date: {session_date.strftime('%Y-%m-%d')}\n")
                        f.write(f"Topics: {', '.join(session_data['topics'])}\n\n")
                        f.write(conversation)
                    
                    logger.info(f"Saved conversation to {filepath}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate session {session_name}: {str(e)}")
                    continue

def main():
    """Main function to run the conversation generator."""
    # Get OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize and run the generator
    generator = ConversationGenerator(openai_api_key)
    generator.generate_all_sessions()

if __name__ == "__main__":
    main() 