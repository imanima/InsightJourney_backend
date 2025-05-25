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
from typing import Any, Dict, List
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
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

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
# Regex patterns for element extraction
# ---------------------------------------------------------------------------
EMO_RE = re.compile(r"""
    ===\s*EMOTIONS\s*===\n
    Name:\s*(?P<name>[^\n]+)\n
    Intensity:\s*(?P<intensity>\d+)\n
    Context:\s*(?P<context>[^\n]+)\n
    Topic:\s*(?P<topic>[^\n]+)\n
    Timestamp:\s*(?P<timestamp>[^\n]+)
""", re.VERBOSE | re.DOTALL)

BELIEF_RE = re.compile(r"""
    ===\s*BELIEFS\s*===\n
    Name:\s*(?P<name>[^\n]+)\n
    Description:\s*(?P<description>[^\n]+)\n
    Impact:\s*(?P<impact>[^\n]+)\n
    Topic:\s*(?P<topic>[^\n]+)\n
    Timestamp:\s*(?P<timestamp>[^\n]+)
""", re.VERBOSE | re.DOTALL)

ACTION_RE = re.compile(r"""
    ===\s*ACTION\s*ITEMS\s*===\n
    Name:\s*(?P<name>[^\n]+)\n
    Description:\s*(?P<description>[^\n]+)\n
    Topic:\s*(?P<topic>[^\n]+)\n
    Timestamp:\s*(?P<timestamp>[^\n]+)
""", re.VERBOSE | re.DOTALL)

CHAL_RE = re.compile(r"""
    ===\s*CHALLENGES\s*===\n
    Name:\s*(?P<name>[^\n]+)\n
    Impact:\s*(?P<impact>[^\n]+)\n
    Topic:\s*(?P<topic>[^\n]+)\n
    Timestamp:\s*(?P<timestamp>[^\n]+)
""", re.VERBOSE | re.DOTALL)

INSIGHT_RE = re.compile(r"""
    ===\s*INSIGHTS\s*===\n
    Name:\s*(?P<name>[^\n]+)\n
    Context:\s*(?P<context>[^\n]+)\n
    Topic:\s*(?P<topic>[^\n]+)\n
    Timestamp:\s*(?P<timestamp>[^\n]+)
""", re.VERBOSE | re.DOTALL)

# ---------------------------------------------------------------------------
# OpenAI call with retries
# ---------------------------------------------------------------------------
retry_openai = retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    wait=wait_exponential_jitter(initial=1, max=20),
    stop=stop_after_attempt(6),
)

@retry_openai
def _ask_llm(prompt: str) -> str:
    log.info("Creating OpenAI client...")
    try:
        # Initialize OpenAI client without proxy configuration to avoid issues
        log.info("Attempting to initialize OpenAI client...")
        client = OpenAI(api_key=OPENAI_KEY)
        log.info("OpenAI client created successfully")
        
        log.info("Sending request to OpenAI...")
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful therapy analysis assistant that extracts structured insights from therapy session transcripts."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
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
        
        # Verify OpenAI API key
        if not OPENAI_KEY:
            log.error("OpenAI API key not found in environment variables")
            raise RuntimeError("OpenAI API key not configured")
            
        # Validate OpenAI API key format
        if not (OPENAI_KEY.startswith('sk-') or OPENAI_KEY.startswith('sk-proj-')) or len(OPENAI_KEY) < 40:
            log.error("Invalid OpenAI API key format")
            raise RuntimeError("Invalid OpenAI API key format")
        
        # Use default prompt template
        prompt_template = PROMPT_TEMPLATE
        log.info("Using default prompt template")
        
        # Format the prompt with the transcript
        try:
            prompt = prompt_template.format(transcript=transcript)
            log.info("Formatted prompt with transcript")
        except Exception as e:
            log.error(f"Error formatting prompt: {str(e)}")
            raise
        
        # Get analysis from LLM
        log.info("Calling OpenAI API...")
        try:
            analysis_text = _ask_llm(prompt)
            log.info(f"Received response from OpenAI: {analysis_text[:200]}...")
        except Exception as e:
            log.error(f"Error calling OpenAI API: {str(e)}")
            raise
        
        # Extract elements from analysis
        log.info("Extracting elements from analysis...")
        try:
            elements = extract_elements(analysis_text)
            log.info(f"Extracted elements: {elements}")
        except Exception as e:
            log.error(f"Error extracting elements: {str(e)}")
            raise
        
        return elements
        
    except Exception as e:
        log.error(f"Error analyzing transcript: {str(e)}")
        raise

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
            # Extract emotions
            emotions = EMO_RE.finditer(text)
            for match in emotions:
                emotion_dict = match.groupdict()
                # Keep emotion even if topic is not valid
                elements['emotions'].append(emotion_dict)
        except Exception as e:
            logging.error(f"Error extracting emotions: {str(e)}")
            
        try:
            # Extract beliefs
            beliefs = BELIEF_RE.finditer(text)
            for match in beliefs:
                belief_dict = match.groupdict()
                # Keep belief even if topic is not valid
                elements['beliefs'].append(belief_dict)
        except Exception as e:
            logging.error(f"Error extracting beliefs: {str(e)}")
            
        try:
            # Extract action items
            action_items = ACTION_RE.finditer(text)
            for match in action_items:
                action_dict = match.groupdict()
                # Keep action item even if topic is not valid
                elements['action_items'].append(action_dict)
        except Exception as e:
            logging.error(f"Error extracting action items: {str(e)}")
            
        try:
            # Extract challenges
            challenges = CHAL_RE.finditer(text)
            for match in challenges:
                challenge_dict = match.groupdict()
                # Keep challenge even if topic is not valid
                elements['challenges'].append(challenge_dict)
        except Exception as e:
            logging.error(f"Error extracting challenges: {str(e)}")
            
        try:
            # Extract insights
            insights = INSIGHT_RE.finditer(text)
            for match in insights:
                insight_dict = match.groupdict()
                # Keep insight even if topic is not valid
                elements['insights'].append(insight_dict)
        except Exception as e:
            logging.error(f"Error extracting insights: {str(e)}")
            
        return elements
        
    except Exception as e:
        logging.error(f"Error in extract_elements: {str(e)}")
        return {
            'emotions': [],
            'beliefs': [],
            'action_items': [],
            'challenges': [],
            'insights': []
        }

def analyze_transcript_and_extract(transcript: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze transcript and extract elements in one step."""
    try:
        log.info("Starting combined analysis and extraction...")
        
        # Analyze transcript
        try:
            analysis = analyze_transcript(transcript)
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
