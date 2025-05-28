"""analysis_service.py – minimal element extractor
================================================
• Focuses only on the *detailed* prompt that returns all seven sections, each with an optional
  **Topic** field.
• Drops JSON‑schema mode, legacy prompt, CLI wrapper, and tiktoken chunker – leaving just the
  essentials: prompt, regex extraction.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter
from services.transcription_service import TranscriptionService

# ---------------------------------------------------------------------------
# Env & logging
# ---------------------------------------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s • %(levelname)s • %(message)s")
log = logging.getLogger("analysis-core")

# Predefined lists of valid emotions and topics
VALID_EMOTIONS = [
    "Anxiety", "Sadness", "Anger", "Fear", "Hope",
    "Joy", "Frustration", "Confusion", "Relief", "Gratitude"
]

VALID_TOPICS = [
    "Relationships", "Career", "Health", "Self-Esteem", "Stress Management",
    "Time Management", "Boundaries", "Personal Growth", "Trauma", "Life Transitions",
    "Purpose"
]

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

# ---------------------------------------------------------------------------
# Settings integration
# ---------------------------------------------------------------------------
def get_user_analysis_settings(user_id: str = None) -> Dict[str, Any]:
    """Get user's analysis settings from Neo4j, with fallbacks to defaults"""
    try:
        if user_id:
            # Import here to avoid circular imports
            from services import get_neo4j_service
            
            neo4j_service = get_neo4j_service()
            settings = neo4j_service.get_user_settings(user_id)
            
            if settings:
                log.info(f"Loaded user settings for {user_id}: model={settings.get('gpt_model', DEFAULT_MODEL)}")
                return {
                    'gpt_model': settings.get('gpt_model', DEFAULT_MODEL),
                    'max_tokens': settings.get('max_tokens', 1500),
                    'temperature': settings.get('temperature', 0.7),
                    'system_prompt_template': settings.get('system_prompt_template'),
                    'analysis_prompt_template': settings.get('analysis_prompt_template'),
                }
            else:
                log.info(f"No settings found for user {user_id}, using defaults")
        else:
            log.info("No user_id provided, using default settings")
            
    except Exception as e:
        log.warning(f"Error loading user settings: {str(e)}, using defaults")
    
    # Return default settings
    return {
        'gpt_model': DEFAULT_MODEL,
        'max_tokens': 1500,
        'temperature': 0.7,
        'system_prompt_template': None,
        'analysis_prompt_template': None,
    }

# ---------------------------------------------------------------------------
# Prompt template (all sections include Topic)
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = f"""
Transcript Analysis for Coaching Session
Instructions: Carefully analyze the transcript and extract key elements that represent significant moments, patterns, or shifts in the session.
IMPORTANT: You MUST use the EXACT format specified below for each element. Do not deviate from this format.

Valid Emotions: {', '.join(VALID_EMOTIONS)}
Valid Topics: {', '.join(VALID_TOPICS)}

Guidelines for extraction:
- Emotions: Look for explicit emotional states and their intensity. Include context that triggered them.
- Beliefs: Capture both limiting and empowering beliefs. Focus on their impact on client's life.
- Action Items: Include specific, actionable commitments or changes the client plans to make.
- Challenges: Identify current struggles or obstacles the client is facing.
- Insights: Note moments of realization, understanding, or perspective shifts.

For each element, include the timestamp (in minutes:seconds format) when it occurred in the session.

REQUIRED FORMAT FOR EACH ELEMENT TYPE:

=== EMOTIONS ===
Name: <emotion from valid list>
Intensity: <number 1-5>
Context: <specific situation>
Topic: <topic from valid list>
Timestamp: <MM:SS>

=== BELIEFS ===
Name: <short name>
Description: <belief statement>
Impact: <effect on client>
Topic: <topic from valid list>
Timestamp: <MM:SS>

=== ACTION ITEMS ===
Name: <short name>
Description: <specific action>
Topic: <topic from valid list>
Timestamp: <MM:SS>

=== CHALLENGES ===
Name: <short name>
Impact: <effect on client>
Topic: <topic from valid list>
Timestamp: <MM:SS>

=== INSIGHTS ===
Name: <short name>
Context: <what led to insight>
Topic: <topic from valid list>
Timestamp: <MM:SS>

IMPORTANT FORMATTING RULES:
1. Use EXACTLY the field names shown above (Name:, Description:, etc.)
2. Each field MUST be on its own line
3. Include ALL fields for each element
4. Use ONLY emotions and topics from the valid lists
5. Separate elements with a blank line
6. Use MM:SS format for timestamps (e.g., 05:30)

Example of correct format:

=== EMOTIONS ===
Name: Anxiety
Intensity: 4
Context: Client feels anxious when thinking about upcoming work presentation
Topic: Career
Timestamp: 12:45

=== BELIEFS ===
Name: Perfectionism
Description: "I must be perfect to be worthy"
Impact: Causes excessive preparation and stress about performance
Topic: Self-Esteem
Timestamp: 15:30

=== ACTION ITEMS ===
Name: Boundary Setting
Description: Practice setting boundaries by declining non-urgent late-night work requests
Topic: Stress Management
Timestamp: 25:15

=== CHALLENGES ===
Name: Meeting Participation Challenge
Impact: Missing opportunities to contribute and feeling undervalued
Topic: Career
Timestamp: 08:20

=== INSIGHTS ===
Name: External Validation Pattern
Context: Reflected on tendency to overwork to gain approval
Topic: Self-Esteem
Timestamp: 32:10

Transcript:
{{transcript}}
"""

# ---------------------------------------------------------------------------
# Regex patterns for element extraction (now done inline in extract_elements)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# OpenAI call with retries
# ---------------------------------------------------------------------------
retry_openai = retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    wait=wait_exponential_jitter(initial=1, max=20),
    stop=stop_after_attempt(6),
)

@retry_openai
def _ask_llm(prompt: str, user_settings: Dict[str, Any] = None) -> str:
    """Call OpenAI API with user-configured settings"""
    log.info("Creating OpenAI client...")
    try:
        # Get settings with defaults
        if user_settings is None:
            user_settings = get_user_analysis_settings()
        
        model = user_settings.get('gpt_model', DEFAULT_MODEL)
        max_tokens = user_settings.get('max_tokens', 1500)
        temperature = user_settings.get('temperature', 0.7)
        
        log.info(f"Using OpenAI settings: model={model}, max_tokens={max_tokens}, temperature={temperature}")
        
        # Initialize OpenAI client with modern v1.82.0 compatible parameters
        log.info("Attempting to initialize OpenAI client...")
        client = OpenAI(
            api_key=OPENAI_KEY,
            timeout=60.0,  # Use timeout instead of deprecated parameters
            max_retries=3
        )
        log.info("OpenAI client created successfully")
        
        log.info("Sending request to OpenAI...")
        try:
            # Use custom system prompt if provided in settings
            system_prompt = user_settings.get('system_prompt_template')
            if not system_prompt:
                system_prompt = "You are a helpful therapy analysis assistant that extracts structured insights from therapy session transcripts."
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            log.info("Received response from OpenAI")
            return response.choices[0].message.content
        except Exception as e:
            log.error(f"Error in OpenAI API call: {str(e)}")
            raise
    except Exception as e:
        log.error(f"Error initializing or calling OpenAI client: {str(e)}")
        log.error(f"Exception type: {type(e)}")
        log.error(f"Exception args: {e.args}")
        # Instead of returning an error string, raise the exception so the system can handle it properly
        raise

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_transcript(transcript: str, user_id: str = None) -> Dict[str, Any]:
    """Return dict with five element arrays, each item contains a Topic field."""
    try:
        log.info("Starting transcript analysis...")
        
        # Verify OpenAI API key is provided
        if not OPENAI_KEY:
            log.error("No OpenAI API key found in environment variables")
            raise ValueError("OpenAI API key is required for analysis")
            
        # Check for placeholder values
        if OPENAI_KEY == "placeholder":
            log.error("OpenAI API key is set to placeholder value")
            raise ValueError("Please provide a valid OpenAI API key")
        
        # Load user settings for analysis configuration
        user_settings = get_user_analysis_settings(user_id)
        log.info(f"Loaded analysis settings: {user_settings}")
        
        # Use custom prompt template if provided, otherwise use default
        prompt_template = user_settings.get('analysis_prompt_template')
        if not prompt_template:
            prompt_template = PROMPT_TEMPLATE
            log.info("Using default prompt template")
        else:
            log.info("Using custom prompt template from user settings")
        
        # Format the prompt with the transcript
        try:
            prompt = prompt_template.format(transcript=transcript)
            log.info("Formatted prompt with transcript")
        except Exception as e:
            log.error(f"Error formatting prompt: {str(e)}")
            raise
        
        # Get analysis from LLM with user settings
        log.info("Calling OpenAI API with user settings...")
        try:
            analysis_text = _ask_llm(prompt, user_settings)
            log.info(f"Received response from OpenAI: {analysis_text[:200]}...")
        except Exception as e:
            log.error(f"Error calling OpenAI API: {str(e)}")
            raise
        
        # Extract elements from analysis
        log.info("Extracting elements from analysis...")
        try:
            elements = extract_elements(analysis_text)
            log.info(f"Successfully extracted {len(elements.get('emotions', []))} emotions, {len(elements.get('beliefs', []))} beliefs, {len(elements.get('action_items', []))} action items, {len(elements.get('challenges', []))} challenges, {len(elements.get('insights', []))} insights")
        except Exception as e:
            log.error(f"Error extracting elements: {str(e)}")
            raise
        
        return elements
        
    except Exception as e:
        log.error(f"Error analyzing transcript: {str(e)}")
        raise  # Re-raise the exception instead of returning mock data

def extract_elements(text):
    """Extract structured elements from the analysis text."""
    try:
        # If text is already a dictionary, return it
        if isinstance(text, dict):
            return text
            
        # Otherwise, try to extract elements using regex
        elements = {
            'emotions': [],
            'beliefs': [],
            'action_items': [],
            'challenges': [],
            'insights': []
        }
        
        try:
            # Extract emotions - find all emotions anywhere in text (handles duplicate headers)
            emotion_pattern = re.compile(r"""
                Name:\s*(?P<name>[^\n]+)\s*\n
                Intensity:\s*(?P<intensity>\d+)\s*\n
                Context:\s*(?P<context>[^\n]+)\s*\n
                Topic:\s*(?P<topic>[^\n]+)\s*\n
                Timestamp:\s*(?P<timestamp>[^\n]+)
            """, re.VERBOSE)
            
            for match in emotion_pattern.finditer(text):
                emotion_data = match.groupdict()
                # Clean up whitespace
                for key, value in emotion_data.items():
                    emotion_data[key] = value.strip() if isinstance(value, str) else value
                elements['emotions'].append(emotion_data)
            
            # Extract beliefs section and then individual beliefs
            belief_section_match = re.search(r'===\s*BELIEFS\s*===\s*\n(.*?)(?=\n\s*===|$)', text, re.DOTALL)
            if belief_section_match:
                belief_section = belief_section_match.group(1)
                belief_pattern = re.compile(r"""
                    Name:\s*(?P<name>[^\n]+)\s*\n
                    Description:\s*(?P<description>[^\n]+)\s*\n
                    Impact:\s*(?P<impact>[^\n]+)\s*\n
                    Topic:\s*(?P<topic>[^\n]+)\s*\n
                    Timestamp:\s*(?P<timestamp>[^\n]+)
                """, re.VERBOSE)
                
                for match in belief_pattern.finditer(belief_section):
                    belief_data = match.groupdict()
                    # Clean up whitespace
                    for key, value in belief_data.items():
                        belief_data[key] = value.strip() if isinstance(value, str) else value
                    elements['beliefs'].append(belief_data)
            
            # Extract action items section and then individual action items  
            action_section_match = re.search(r'===\s*ACTION ITEMS\s*===\s*\n(.*?)(?=\n\s*===|$)', text, re.DOTALL)
            if action_section_match:
                action_section = action_section_match.group(1)
                action_pattern = re.compile(r"""
                    Name:\s*(?P<name>[^\n]+)\s*\n
                    Description:\s*(?P<description>[^\n]+)\s*\n
                    Topic:\s*(?P<topic>[^\n]+)\s*\n
                    Timestamp:\s*(?P<timestamp>[^\n]+)
                """, re.VERBOSE)
                
                for match in action_pattern.finditer(action_section):
                    action_data = match.groupdict()
                    # Clean up whitespace
                    for key, value in action_data.items():
                        action_data[key] = value.strip() if isinstance(value, str) else value
                    elements['action_items'].append(action_data)
            
            # Extract challenges section and then individual challenges
            challenge_section_match = re.search(r'===\s*CHALLENGES\s*===\s*\n(.*?)(?=\n\s*===|$)', text, re.DOTALL)
            if challenge_section_match:
                challenge_section = challenge_section_match.group(1)
                challenge_pattern = re.compile(r"""
                    Name:\s*(?P<name>[^\n]+)\s*\n
                    Impact:\s*(?P<impact>[^\n]+)\s*\n
                    Topic:\s*(?P<topic>[^\n]+)\s*\n
                    Timestamp:\s*(?P<timestamp>[^\n]+)
                """, re.VERBOSE)
                
                for match in challenge_pattern.finditer(challenge_section):
                    challenge_data = match.groupdict()
                    # Clean up whitespace
                    for key, value in challenge_data.items():
                        challenge_data[key] = value.strip() if isinstance(value, str) else value
                    elements['challenges'].append(challenge_data)
            
            # Extract insights section and then individual insights
            insight_section_match = re.search(r'===\s*INSIGHTS\s*===\s*\n(.*?)(?=\n\s*===|$)', text, re.DOTALL)
            if insight_section_match:
                insight_section = insight_section_match.group(1)
                insight_pattern = re.compile(r"""
                    Name:\s*(?P<name>[^\n]+)\s*\n
                    Context:\s*(?P<context>[^\n]+)\s*\n
                    Topic:\s*(?P<topic>[^\n]+)\s*\n
                    Timestamp:\s*(?P<timestamp>[^\n]+)
                """, re.VERBOSE)
                
                for match in insight_pattern.finditer(insight_section):
                    insight_data = match.groupdict()
                    # Clean up whitespace
                    for key, value in insight_data.items():
                        insight_data[key] = value.strip() if isinstance(value, str) else value
                    elements['insights'].append(insight_data)
        
        except Exception as e:
            logging.error(f"Error extracting elements: {e}")
        
        return elements
        
    except Exception as e:
        logging.error(f"Error in extract_elements: {e}")
        return {
            'emotions': [],
            'beliefs': [],
            'action_items': [],
            'challenges': [],
            'insights': []
        }

def analyze_transcript_and_extract(transcript: str, user_id: str = None) -> Dict[str, Any]:
    """Analyze transcript and extract elements in one step."""
    try:
        log.info("Starting combined analysis and extraction...")
        
        # Analyze transcript with user settings
        try:
            analysis = analyze_transcript(transcript, user_id=user_id)
            log.info("Successfully analyzed transcript")
        except Exception as e:
            log.error(f"Error analyzing transcript: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "elements": {}
            }
        
        # Extract elements
        try:
            elements = extract_elements(analysis)
            log.info("Successfully extracted elements")
        except Exception as e:
            log.error(f"Error extracting elements: {str(e)}")
            return {
                "status": "failed", 
                "error": str(e),
                "elements": {}
            }
        
        return {
            "status": "completed",
            "elements": elements
        }
        
    except Exception as e:
        log.error(f"Error in analyze_transcript_and_extract: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "elements": {}
        }
