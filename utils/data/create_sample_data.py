#!/usr/bin/env python3

"""
Sample Data Generator for Insight Journey

This script creates:
1. A test user
2. Three therapy session entries with different transcripts
3. Analyzes each transcript using our analysis component
4. Stores all results in Neo4j
5. Creates relationships between sessions

Useful for generating demonstration data and testing the full pipeline.
"""

import os
import re
import json
import logging
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import openai
import httpx
import time
import uuid
import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample therapy transcripts - three different types of sessions
TRANSCRIPT_1 = """
During today's session, I explored my feelings about my recent promotion at work. 
I'm excited about the opportunity but feeling anxious about the increased responsibilities.
I've been struggling with impostor syndrome, wondering if I really deserve this role. 
My manager has been supportive, but I still worry I'll disappoint them.

We discussed strategies to address these feelings, including documenting my 
accomplishments, practicing positive self-talk, and seeking feedback proactively. 
I acknowledged that my tendency toward perfectionism is contributing to my anxiety.

By the end of our discussion, I felt more confident about my ability to handle the 
new role. I committed to creating boundaries around work hours to prevent burnout 
and to practice mindfulness when self-doubt arises.
"""

TRANSCRIPT_2 = """
I've been having difficulties in my relationship with my partner lately. We've been
arguing more frequently, especially about household responsibilities and financial decisions.
I feel frustrated and unheard when I bring up my concerns, and sometimes I shut down
rather than continuing the conversation.

During our session today, we explored my communication patterns. I realized that I tend
to avoid conflict until I'm already feeling resentful, which makes productive discussion
more difficult. I was able to connect this to my childhood experiences where expressing
needs often led to disappointment.

I feel hopeful that I can improve our communication by expressing my needs earlier and
more clearly. We developed a plan that includes scheduling regular check-ins with my
partner and using "I feel" statements rather than accusations. I'm committed to working
on staying engaged during difficult conversations rather than withdrawing.
"""

TRANSCRIPT_3 = """
Today we focused on my ongoing struggles with work-life balance. Since starting to
work from home, I've found it increasingly difficult to separate my professional and
personal life. I often work late into the evening and check emails first thing in
the morning. I've been experiencing fatigue, irritability, and some trouble sleeping.

I shared that I've been feeling guilty when I'm not working, as if I'm not being
productive enough. At the same time, I'm feeling resentful of how much my job has
taken over my life. We identified that this internal conflict is creating significant
stress.

Through our discussion, I connected this pattern to my core belief that my worth is
tied to my productivity. We explored how this belief developed and how it no longer
serves me. I feel motivated to establish clearer boundaries, including a dedicated
workspace that I can leave at the end of the day and specific work hours.

I'm going to try implementing a shutdown ritual to transition from work to personal
time, and scheduling activities in the evening that I look forward to. I'm also
committing to a technology-free morning routine for the first 30 minutes of my day.
"""

# Enhanced prompts with better topic connections for emotions
DEFAULT_SYSTEM_PROMPT = """
You are an AI assistant analyzing coaching session transcripts.
Identify the following elements in the text:

1. Emotions: Identify emotions with their intensity (1-10), context, and related topics.
   For each emotion, specify which topics from your topic list it relates to.
2. Topics: List main topics discussed in the session.
3. Beliefs: Identify core beliefs expressed, especially limiting ones.
4. Action Items: Suggest specific, actionable next steps.

Format your response in clear sections with each element clearly labeled.
Ensure emotions are connected to relevant topics from your topic list.
"""

DEFAULT_ANALYSIS_PROMPT = """
Please analyze the following coaching session transcript:

{text}

Extract the following elements, maintaining the exact format specified:

1. EMOTIONS:
   List emotions with intensity, context, and related topics. 
   Format: Emotion (intensity: X) - Context [Related to topics: Topic1, Topic2]

2. TOPICS:
   List main topics discussed, one per line with a dash.

3. BELIEFS:
   Identify beliefs expressed, especially those that may be limiting. Format: "Belief statement"

4. ACTION ITEMS:
   Suggest concrete actions the client could take. Format them as clear directives.

Be specific, practical, and focus on elements clearly present in the text.
"""

# Define emotion categories for testing
EMOTION_CATEGORIES = {
    'positive': ['joy', 'happiness', 'excitement', 'gratitude', 'pride', 'love', 'hope', 'optimism'],
    'negative': ['sadness', 'anger', 'fear', 'anxiety', 'frustration', 'disappointment', 'guilt', 'shame'],
    'neutral': ['surprise', 'curiosity', 'confusion', 'interest', 'boredom', 'calmness', 'peace']
}

def get_openai_client():
    """Get OpenAI client"""
    try:
        # Remove httpx client initialization for container compatibility
        return openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        logger.error(f"Error creating OpenAI client: {str(e)}")
        return None

def analyze_transcript(text):
    """
    Analyze transcript using OpenAI
    """
    try:
        logger.info(f"Analyzing transcript: {len(text)} characters")
        client = get_openai_client()
        
        if not client:
            logger.error("Failed to create OpenAI client")
            return None
        
        # Configure model
        model = "gpt-4"
        temperature = 0.7
        max_tokens = 2000
        
        # Format the prompt
        analysis_prompt = DEFAULT_ANALYSIS_PROMPT.format(text=text)
        
        # Print the prompts for evaluation
        print("\n" + "="*80)
        print("SYSTEM PROMPT:")
        print(DEFAULT_SYSTEM_PROMPT)
        print("\n" + "="*80)
        print("USER PROMPT:")
        print(analysis_prompt)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract elements from result
        raw_analysis = response.choices[0].message.content
        
        # Print the raw analysis results for evaluation
        print("\n" + "="*80)
        print("RAW ANALYSIS RESULTS:")
        print(raw_analysis)
        print("="*80 + "\n")
        
        elements = extract_elements(raw_analysis)
        
        # Connect topics to each element explicitly
        elements = connect_topics_to_elements(elements)
        
        # Generate additional insights
        insights = generate_insights(elements)
        elements["insights"] = insights
        
        # Generate summary
        elements["summary"] = generate_summary(elements)
        
        # Print the structured elements for evaluation
        print("\n" + "="*80)
        print("STRUCTURED ANALYSIS RESULTS:")
        pprint.pprint(elements)
        print("="*80 + "\n")
        
        logger.info(f"Analysis complete: {len(str(elements))} bytes")
        return elements
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return None

def extract_elements(text):
    """Extract structured elements from analyzed text"""
    elements = {
        'emotions': [],
        'topics': [],
        'beliefs': [],
        'action_items': [],
        'challenges': []
    }
    
    # Extract emotions with topics
    # Format: "Joy (intensity: 8) - When discussing achievements [Related to topics: Career, Self-confidence]"
    emotion_pattern = r'(\w+)\s*\(intensity:\s*(\d+)\)\s*-\s*([^\[]+)(?:\[Related to topics:\s*([^\]]+)\])?'
    for match in re.finditer(emotion_pattern, text):
        emotion_name = match.group(1).strip()
        intensity = int(match.group(2)) / 10.0  # Scale to 0-1 for Neo4j
        context = match.group(3).strip()
        
        # Extract topics if they're included in the format
        topics_list = []
        if match.group(4):  # Topics were specified
            topics_text = match.group(4).strip()
            topics_list = [t.strip() for t in topics_text.split(',')]
        
        elements['emotions'].append({
            'name': emotion_name,
            'intensity': intensity,
            'context': context,
            'confidence': 0.8,  # Default confidence
            'isUserModified': False,
            'topics': topics_list  # Pre-populate with topics from the analysis
        })
    
    # Extract topics - Format: "- Work-life balance"
    topics_section = re.search(r'TOPICS:(.+?)(?=\n\s*\n\s*(?:BELIEFS|ACTION|INSIGHTS|EMOTION)|\Z)', text, re.DOTALL | re.IGNORECASE)
    if topics_section:
        topics = re.findall(r'-\s*([^\n]+)', topics_section.group(1))
        elements['topics'] = [
            {
                'name': topic.strip(),
                'relevance': 1.0,
                'isUserModified': False
            } for topic in topics
        ]
    
    # Extract beliefs - Format: "- "I'll never be good enough""
    beliefs_section = re.search(r'BELIEFS:(.+?)(?=\n\s*\n\s*(?:ACTION|INSIGHTS|EMOTION)|\Z)', text, re.DOTALL | re.IGNORECASE)
    if beliefs_section:
        beliefs = re.findall(r'"([^"]+)"', beliefs_section.group(1))
        if not beliefs:  # Try alternate format: - Belief text
            beliefs = re.findall(r'-\s*([^\n]+)', beliefs_section.group(1))
            
        elements['beliefs'] = [
            {
                "text": belief.strip(),
                "category": "Uncategorized",
                "confidence": 0.8,
                "isUserModified": False,
                "topics": []  # Initialize empty topics list
            } for belief in beliefs
        ]
    
    # Extract action items - Format: "- Schedule time for self-care"
    action_items_section = re.search(r'ACTION ITEMS:(.+?)(?=\n\s*\n|\Z)', text, re.DOTALL | re.IGNORECASE)
    if action_items_section:
        action_items = re.findall(r'-\s*([^\n]+)', action_items_section.group(1))
        elements['action_items'] = [
            {
                "description": item.strip(),
                "priority": determine_priority(item),
                "dueDate": estimate_due_date(item),
                "status": "pending",
                "isUserModified": False,
                "topics": []  # Initialize empty topics list
            } for item in action_items
        ]
    
    return elements

def connect_topics_to_elements(elements):
    """Connect topics to each element based on context and content"""
    # Get all topic names for reference
    all_topic_names = [topic['name'].lower() for topic in elements.get('topics', [])]
    
    # For emotions, we may already have topics from the analysis
    # But we'll also look for additional matches in context
    for emotion in elements.get('emotions', []):
        context = emotion.get('context', '').lower()
        topics_already_assigned = [t.lower() for t in emotion.get('topics', [])]
        
        # Look for additional topic matches in context
        for topic_name in all_topic_names:
            if topic_name.lower() in context and topic_name.lower() not in topics_already_assigned:
                emotion['topics'].append(topic_name)
    
    # Connect topics to beliefs
    for belief in elements.get('beliefs', []):
        text = belief.get('text', '').lower()
        matched_topics = []
        
        # Look for topic matches in belief text
        for topic_name in all_topic_names:
            if topic_name.lower() in text:
                matched_topics.append(topic_name)
        
        belief['topics'] = matched_topics
    
    # Connect topics to action items
    for action in elements.get('action_items', []):
        description = action.get('description', '').lower()
        matched_topics = []
        
        # Look for topic matches in action description
        for topic_name in all_topic_names:
            if topic_name.lower() in description:
                matched_topics.append(topic_name)
        
        action['topics'] = matched_topics
    
    return elements

def generate_insights(elements):
    """Generate insights based on extracted elements"""
    insights = []
    
    # Get elements
    emotions = elements.get('emotions', [])
    topics = elements.get('topics', [])
    beliefs = elements.get('beliefs', [])
    
    # Generate emotion-based insights
    for emotion in emotions:
        name = emotion.get('name', '')
        intensity = emotion.get('intensity', 0.5)
        context = emotion.get('context', '')
        
        if name.lower() in EMOTION_CATEGORIES.get('positive', []):
            insights.append({
                "text": f"Positive emotion ({name}) around '{context}' indicates strength area",
                "category": "Emotional",
                "confidence": 0.8,
                "isUserModified": False,
                "topics": emotion.get('topics', [])  # Connect to the emotion's topics
            })
        elif name.lower() in EMOTION_CATEGORIES.get('negative', []) and intensity > 0.6:
            insights.append({
                "text": f"Strong {name} around '{context}' suggests growth opportunity",
                "category": "Emotional",
                "confidence": 0.7,
                "isUserModified": False,
                "topics": emotion.get('topics', [])  # Connect to the emotion's topics
            })
    
    # Generate belief-based insights
    for belief in beliefs:
        text = belief.get('text', '')
        
        if any(word in text.lower() for word in ["never", "always", "can't", "impossible"]):
            insights.append({
                "text": f"Potential limiting belief: '{text}'",
                "category": "Mindset",
                "confidence": 0.8,
                "isUserModified": False,
                "topics": belief.get('topics', [])
            })
        elif any(word in text.lower() for word in ["grow", "learn", "improve", "can", "possible"]):
            insights.append({
                "text": f"Growth mindset indicator: '{text}'",
                "category": "Mindset",
                "confidence": 0.8,
                "isUserModified": False,
                "topics": belief.get('topics', [])
            })
    
    # Generate topic-focused insight
    if topics:
        topic_names = [t.get('name', '') for t in topics[:3]]
        insights.append({
            "text": f"Main focus areas: {', '.join(topic_names)}",
            "category": "Focus",
            "confidence": 0.9,
            "isUserModified": False,
            "topics": topic_names
        })
    
    return insights

def generate_summary(elements):
    """Generate a concise summary from analysis elements"""
    emotions = elements.get('emotions', [])
    topics = elements.get('topics', [])
    beliefs = elements.get('beliefs', [])
    
    # Determine emotional tone
    positive_emotions = sum(1 for e in emotions if e.get('name', '').lower() in EMOTION_CATEGORIES.get('positive', []))
    negative_emotions = sum(1 for e in emotions if e.get('name', '').lower() in EMOTION_CATEGORIES.get('negative', []))
    emotional_tone = "positive" if positive_emotions > negative_emotions else "negative" if negative_emotions > positive_emotions else "mixed"
    
    # Get main topics
    main_topics = [t.get('name', '') for t in topics[:2]] if topics else ['personal development']
    
    # Get potential limiting beliefs
    limiting_beliefs = [b.get('text', '') for b in beliefs if any(word in b.get('text', '').lower() for word in ["never", "always", "can't", "impossible"])]
    
    # Create summary
    summary = f"Session focused on {', '.join(main_topics)} with a {emotional_tone} emotional tone."
    
    if limiting_beliefs:
        summary += f" Potential limiting belief identified: '{limiting_beliefs[0]}'."
        
    return summary

def determine_priority(action_item):
    """Determine priority of an action item based on content"""
    text_lower = action_item.lower()
    
    if any(word in text_lower for word in ["urgent", "immediately", "asap", "critical", "today"]):
        return "High"
    elif any(word in text_lower for word in ["important", "significant", "priority", "key"]):
        return "Medium"
        
    return "Normal"

def estimate_due_date(action_item):
    """Estimate due date of an action item based on content"""
    text_lower = action_item.lower()
    
    if any(term in text_lower for term in ["today", "now", "immediately", "asap"]):
        return "Today"
    elif any(term in text_lower for term in ["tomorrow", "next day"]):
        return "Tomorrow"
    elif any(term in text_lower for term in ["this week", "few days"]):
        return "Within a week"
    elif any(term in text_lower for term in ["next week"]):
        return "Next week"
    elif any(term in text_lower for term in ["month", "30 days"]):
        return "Within a month"
        
    return "No deadline"

def import_neo4j_service():
    """Import Neo4j service with error handling"""
    try:
        # Add the current directory to the path to ensure imports work
        sys.path.append('.')
        
        # Try importing the Neo4j service
        from services.neo4j_service import Neo4jService
        logger.info("Successfully imported Neo4jService")
        return Neo4jService()
    except ImportError as e:
        logger.error(f"Error importing Neo4jService: {str(e)}")
        return None

def create_demo_user(neo4j_service):
    """Create a demo user in Neo4j"""
    user_id = f"demo_user_{str(uuid.uuid4())[:8]}"
    user_email = f"demo_{str(uuid.uuid4())[:8]}@example.com"
    user_name = "Demo User"
    
    logger.info(f"Creating demo user with ID: {user_id} and email: {user_email}")
    
    with neo4j_service.driver.session() as session:
        # Create user node
        session.run(
            "CREATE (u:User {userId: $user_id, email: $email, name: $name, created_at: $timestamp})",
            user_id=user_id,
            email=user_email,
            name=user_name,
            timestamp=datetime.now().isoformat()
        )
        logger.info(f"Created demo user with ID: {user_id}")
    
    return user_id, user_email

def create_session_data(user_id, transcript, title, date_offset=0):
    """Create session data dictionary"""
    session_date = (datetime.now() - timedelta(days=date_offset)).strftime("%Y-%m-%d")
    
    return {
        "title": title,
        "date": session_date,
        "userId": user_id,
        "transcript": transcript,
        "client_name": "Sample Client",
        "status": "completed"
    }

def create_and_analyze_sessions(neo4j_service, user_id):
    """Create sessions, analyze them, and store in Neo4j"""
    # Create session data for each transcript
    session_data_1 = create_session_data(
        user_id, 
        TRANSCRIPT_1, 
        "Career Advancement and Impostor Syndrome", 
        date_offset=14
    )
    
    session_data_2 = create_session_data(
        user_id, 
        TRANSCRIPT_2, 
        "Relationship Communication Patterns", 
        date_offset=7
    )
    
    session_data_3 = create_session_data(
        user_id, 
        TRANSCRIPT_3, 
        "Work-Life Balance in Remote Work", 
        date_offset=0
    )
    
    # Create sessions and analyze each one
    session_info = []
    
    # Process first session
    logger.info("="*80)
    logger.info("Processing Session 1: Career Advancement and Impostor Syndrome")
    session_id_1 = neo4j_service.create_session(session_data_1)
    logger.info(f"Created session with ID: {session_id_1}")
    
    analysis_1 = analyze_transcript(TRANSCRIPT_1)
    if analysis_1:
        success_1 = neo4j_service.save_session_analysis(session_id_1, analysis_1, user_id)
        logger.info(f"Analysis saved to Neo4j: {success_1}")
        session_info.append((session_id_1, "Career Advancement"))
    
    # Small delay between sessions
    time.sleep(1)
    
    # Process second session
    logger.info("="*80)
    logger.info("Processing Session 2: Relationship Communication Patterns")
    session_id_2 = neo4j_service.create_session(session_data_2)
    logger.info(f"Created session with ID: {session_id_2}")
    
    analysis_2 = analyze_transcript(TRANSCRIPT_2)
    if analysis_2:
        success_2 = neo4j_service.save_session_analysis(session_id_2, analysis_2, user_id)
        logger.info(f"Analysis saved to Neo4j: {success_2}")
        session_info.append((session_id_2, "Relationship Communication"))
    
    # Small delay between sessions
    time.sleep(1)
    
    # Process third session
    logger.info("="*80)
    logger.info("Processing Session 3: Work-Life Balance in Remote Work")
    session_id_3 = neo4j_service.create_session(session_data_3)
    logger.info(f"Created session with ID: {session_id_3}")
    
    analysis_3 = analyze_transcript(TRANSCRIPT_3)
    if analysis_3:
        success_3 = neo4j_service.save_session_analysis(session_id_3, analysis_3, user_id)
        logger.info(f"Analysis saved to Neo4j: {success_3}")
        session_info.append((session_id_3, "Work-Life Balance"))
    
    return session_info

def create_session_relationships(neo4j_service, session_info):
    """Create relationships between sequential sessions"""
    # Link sessions in sequence
    for i in range(len(session_info) - 1):
        source_id = session_info[i][0]
        target_id = session_info[i + 1][0]
        
        success = neo4j_service.create_session_relationship(source_id, target_id)
        logger.info(f"Created relationship between {session_info[i][1]} -> {session_info[i+1][1]}: {success}")

def check_neo4j_relationship_types(neo4j_service, session_id):
    """Check and print relationship types in Neo4j for a session"""
    try:
        with neo4j_service.driver.session() as session:
            # Check for HAS_TOPIC relationships (which should not exist)
            result = session.run("""
                MATCH (s:Session {id: $session_id})-[r:HAS_TOPIC]->(t:Topic)
                RETURN count(r) as has_topic_count
            """, session_id=session_id)
            
            record = result.single()
            has_topic_count = record["has_topic_count"] if record else 0
            
            if has_topic_count > 0:
                logger.warning(f"Found {has_topic_count} HAS_TOPIC relationships which should not exist")
            else:
                logger.info("No HAS_TOPIC relationships found (correct)")
            
            # Check for correct relationship structures
            result = session.run("""
                MATCH (s:Session {id: $session_id})
                OPTIONAL MATCH (s)-[:HAS_EMOTION]->(e:Emotion)-[r:RELATED_TO]->(t:Topic)
                RETURN count(r) as emotion_topic_count
            """, session_id=session_id)
            
            record = result.single()
            emotion_topic_count = record["emotion_topic_count"] if record else 0
            logger.info(f"Found {emotion_topic_count} Emotion-to-Topic relationships")
            
            # Count all topic nodes for this session
            result = session.run("""
                MATCH (s:Session {id: $session_id})
                WITH s
                MATCH (t:Topic)
                WHERE EXISTS {
                    MATCH (s)-[:HAS_EMOTION|HAS_INSIGHT|HAS_BELIEF|HAS_CHALLENGE|HAS_ACTION_ITEM]->()-[:RELATED_TO]->(t)
                }
                RETURN count(DISTINCT t) as topic_count
            """, session_id=session_id)
            
            record = result.single()
            topic_count = record["topic_count"] if record else 0
            logger.info(f"Found {topic_count} distinct Topic nodes connected to session elements")
            
    except Exception as e:
        logger.error(f"Error checking Neo4j relationships: {str(e)}")

def main():
    """Run the sample data generator"""
    # Check OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        return
    
    logger.info(f"Using OPENAI_API_KEY: {openai_api_key[:5]}...{openai_api_key[-5:]}")
    
    # Import Neo4j service
    neo4j_service = import_neo4j_service()
    if not neo4j_service:
        logger.error("Failed to import Neo4jService, exiting")
        return
    
    # Create a demo user
    user_id, user_email = create_demo_user(neo4j_service)
    logger.info(f"Demo user created with ID: {user_id} and email: {user_email}")
    
    # Create and analyze sessions
    session_info = create_and_analyze_sessions(neo4j_service, user_id)
    
    # Create relationships between sessions
    create_session_relationships(neo4j_service, session_info)
    
    # Check relationships to ensure HAS_TOPIC doesn't exist
    logger.info("="*80)
    logger.info("VERIFYING RELATIONSHIP STRUCTURES IN NEO4J:")
    for session_id, topic in session_info:
        logger.info(f"Checking relationships for {topic} session (ID: {session_id})")
        check_neo4j_relationship_types(neo4j_service, session_id)
    
    # Save user information for future reference
    user_info = {
        "user_id": user_id,
        "email": user_email,
        "sessions": [{"id": s[0], "topic": s[1]} for s in session_info]
    }
    
    with open('demo_user_info.json', 'w') as f:
        json.dump(user_info, f, indent=2)
    logger.info(f"Saved user info to demo_user_info.json")
    
    logger.info("="*80)
    logger.info("SAMPLE DATA GENERATION COMPLETE!")
    logger.info("="*80)
    logger.info(f"Created user: {user_email}")
    logger.info(f"Created {len(session_info)} sessions with full analysis")
    logger.info(f"Created sequential relationships between sessions")
    logger.info(f"Verified absence of HAS_TOPIC relationships (using RELATED_TO instead)")
    logger.info(f"Details saved to demo_user_info.json")

if __name__ == "__main__":
    main() 