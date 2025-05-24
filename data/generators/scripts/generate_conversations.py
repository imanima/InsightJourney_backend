"""
Script to generate realistic coaching/therapy conversations based on client and professional personas.
Uses OpenAI's API to generate natural, contextually appropriate conversations.
"""

import os
import json
import datetime
import sys
from pathlib import Path
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import configurations
from config.clients import CLIENTS
from config.professionals import PROFESSIONALS
from config.session_themes import SESSION_THEMES, SESSION_PROGRESSION

# Load environment variables
load_dotenv()

class ConversationGenerator:
    def __init__(self):
        """Initialize the conversation generator with OpenAI API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    def _create_session_prompt(
        self,
        client: Dict,
        professional: Dict,
        session_number: int,
        theme: Dict,
        session_date: datetime.datetime
    ) -> str:
        """Create a detailed prompt for the conversation generation."""
        return f"""Generate a realistic therapy session transcript between {professional['name']} ({professional['role']}) and {client['name']} ({client['role']}).

Session Information:
- Session Number: {session_number}/24 (Weekly sessions over 6 months)
- Date: {session_date.strftime('%B %d, %Y')}
- Duration: 50 minutes
- Start Time: {session_date.strftime('%I:%M %p')}

Professional Profile:
- Name: {professional['name']}
- Role: {professional['role']}
- Background: {professional['background']['education']}, {professional['background']['experience']}, {professional['background']['specialization']}
- Style: {professional['style']['approach']}
- Strengths: {', '.join(professional['style']['strengths'])}
- Techniques: {', '.join(professional['style']['techniques'])}
- Tech Usage: {', '.join(professional['tech_usage'])}

Client Profile:
- Name: {client['name']}
- Age: {client['age']}
- Role: {client['role']}
- Background: {client['background']}
- Tech Habits: {', '.join(client['tech_habits'])}
- Challenges: {', '.join(client['challenges'])}
- Goals: {', '.join(client['goals'])}
- Personality: {', '.join(client['personality_traits'])}

Session Theme:
- Topics: {', '.join(theme['topics'])}
- Techniques: {', '.join(theme['techniques'])}
- Expected Outcomes: {', '.join(theme['expected_outcomes'])}

Requirements:
1. Generate a natural, flowing conversation with EXACT timestamps every 5-10 minutes
2. Use format [HH:MM] for timestamps (e.g., [02:15] for 2 hours 15 minutes)
3. Include specific examples and details relevant to the client's situation
4. Show progress and development throughout the session
5. Include emotional expressions and non-verbal cues in parentheses
6. End with clear action items and next steps
7. Reference previous sessions' work and progress (if not first session)
8. Show progression in addressing the client's challenges over the 6-month period

Generate the conversation now, starting at {session_date.strftime('%I:%M %p')}:"""

    def generate_conversation(
        self,
        client: Dict,
        professional: Dict,
        session_number: int,
        theme: Dict,
        session_date: datetime.datetime
    ) -> str:
        """Generate a conversation using OpenAI's API."""
        prompt = self._create_session_prompt(
            client, professional, session_number, theme, session_date
        )
        
        try:
            client = openai.Client(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "You are a skilled conversation generator that creates realistic therapy session transcripts with precise timestamps and natural progression."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating conversation: {e}")
            return None

    def save_conversation(
        self,
        conversation: str,
        client: Dict,
        professional: Dict,
        session_number: int,
        session_date: datetime.datetime,
        output_dir: Path
    ) -> None:
        """Save the generated conversation to a file."""
        filename = f"session_{session_number:02d}_{session_date.strftime('%Y%m%d')}.txt"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            f.write(f"Session {session_number}/24\n")
            f.write(f"Date: {session_date.strftime('%B %d, %Y')}\n")
            f.write(f"Time: {session_date.strftime('%I:%M %p')}\n")
            f.write(f"Client: {client['name']} ({client['role']})\n")
            f.write(f"Professional: {professional['name']} ({professional['role']})\n")
            f.write("\n" + conversation)

    def generate_all_sessions(
        self,
        client_key: str,
        professional_key: str,
        client_type: str,
        theme_key: str,
        start_date: datetime.datetime = None
    ) -> None:
        """Generate conversations for all sessions in the progression."""
        # Get client and professional info
        client = CLIENTS[client_type][client_key]
        prof_type, prof_name = professional_key.split("/")
        professional = PROFESSIONALS[prof_type][prof_name]
        theme = SESSION_THEMES[client_type][theme_key]
        
        # Create directory for this client-professional pair
        pair_dir = self.output_dir / f"{client['name']}_{professional['name'].replace(' ', '_')}"
        pair_dir.mkdir(exist_ok=True)
        
        # Set start date if not provided
        if start_date is None:
            start_date = datetime.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Generate 24 weekly sessions (6 months)
        for session_number in range(1, 25):
            print(f"Generating session {session_number}/24...")
            
            # Calculate session date (weekly sessions)
            session_date = start_date + datetime.timedelta(weeks=session_number-1)
            
            conversation = self.generate_conversation(
                client,
                professional,
                session_number,
                theme,
                session_date
            )
            
            if conversation:
                self.save_conversation(
                    conversation,
                    client,
                    professional,
                    session_number,
                    session_date,
                    pair_dir
                )
                print(f"Saved session {session_number}/24")
            else:
                print(f"Failed to generate session {session_number}/24")

def main():
    """Main function to run the conversation generator."""
    generator = ConversationGenerator()
    
    # Define client-therapist pairs with their themes based on recommended matches
    pairs = [
        # Alex (27) - Imposter-syndrome designer with Dr. Harper
        {
            "client_key": "alex_designer",
            "professional_key": "therapists/dr_harper_torres",
            "client_type": "tech_professionals",
            "theme_key": "imposter_syndrome",
            "start_date": datetime.datetime(2025, 5, 1, 10, 0)  # May 1, 2025 at 10:00 AM
        },
        
        # Jasmine (30) - New-mom engineer with Riley
        {
            "client_key": "jasmine_engineer",
            "professional_key": "coaches/riley_chen",
            "client_type": "tech_professionals",
            "theme_key": "work_life_balance",
            "start_date": datetime.datetime(2025, 5, 2, 14, 0)  # May 2, 2025 at 2:00 PM
        },
        
        # Diego (24) - Social-anxious grad student with Dr. Harper
        {
            "client_key": "diego_student",
            "professional_key": "therapists/dr_harper_torres",
            "client_type": "students",
            "theme_key": "academic_pressure",
            "start_date": datetime.datetime(2025, 5, 3, 11, 0)  # May 3, 2025 at 11:00 AM
        },
        
        # Mei (29) - Ops lead with chronic pain with Mara
        {
            "client_key": "mei_ops",
            "professional_key": "therapists/mara_ortiz",
            "client_type": "tech_professionals",
            "theme_key": "chronic_pain",
            "start_date": datetime.datetime(2025, 5, 4, 15, 0)  # May 4, 2025 at 3:00 PM
        },
        
        # Sam (32) - Lonely indie game dev with Malik
        {
            "client_key": "sam_developer",
            "professional_key": "coaches/malik_johnson",
            "client_type": "entrepreneurs",
            "theme_key": "creative_block",
            "start_date": datetime.datetime(2025, 5, 5, 9, 0)  # May 5, 2025 at 9:00 AM
        },
        
        # Priya (26) - Insomniac VC analyst with Dr. Harper
        {
            "client_key": "priya_analyst",
            "professional_key": "therapists/dr_harper_torres",
            "client_type": "tech_professionals",
            "theme_key": "sleep_issues",
            "start_date": datetime.datetime(2025, 5, 6, 13, 0)  # May 6, 2025 at 1:00 PM
        },
        
        # Evan (34) - DevOps caregiver with Dr. Serena
        {
            "client_key": "evan_engineer",
            "professional_key": "therapists/dr_serena_bianchi",
            "client_type": "healthcare_professionals",
            "theme_key": "caregiver_stress",
            "start_date": datetime.datetime(2025, 5, 7, 10, 0)  # May 7, 2025 at 10:00 AM
        },
        
        # Lina (28) - ADHD freelancer with Riley
        {
            "client_key": "lina_freelancer",
            "professional_key": "coaches/riley_chen",
            "client_type": "tech_professionals",
            "theme_key": "adhd_management",
            "start_date": datetime.datetime(2025, 5, 8, 14, 0)  # May 8, 2025 at 2:00 PM
        },
        
        # Omar (25) - Burned-out PhD candidate with Malik
        {
            "client_key": "omar_phd",
            "professional_key": "coaches/malik_johnson",
            "client_type": "students",
            "theme_key": "career_transition",
            "start_date": datetime.datetime(2025, 5, 9, 9, 0)  # May 9, 2025 at 9:00 AM
        },
        
        # Zoë (31) - UX researcher on fertility journey with Dr. Serena
        {
            "client_key": "zoe_researcher",
            "professional_key": "therapists/dr_serena_bianchi",
            "client_type": "tech_professionals",
            "theme_key": "fertility_journey",
            "start_date": datetime.datetime(2025, 5, 10, 11, 0)  # May 10, 2025 at 11:00 AM
        }
    ]
    
    # Generate sessions for each pair
    for pair in pairs:
        print(f"\nGenerating sessions for {pair['client_key']} with {pair['professional_key']}...")
        generator.generate_all_sessions(
            client_key=pair["client_key"],
            professional_key=pair["professional_key"],
            client_type=pair["client_type"],
            theme_key=pair["theme_key"],
            start_date=pair["start_date"]
        )

if __name__ == "__main__":
    main() 
    main() 