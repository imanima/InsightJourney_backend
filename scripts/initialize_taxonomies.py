#!/usr/bin/env python
"""
Initialize Neo4j taxonomy nodes for emotions, topics, and beliefs.
This script should be run once to set up the taxonomy structure.
"""

import os
import logging
import json
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "insight_password")

# Save taxonomies to JSON files for easy reference in other services
TAXONOMY_DIR = Path(__file__).parent.parent / "resources"
TAXONOMY_DIR.mkdir(exist_ok=True)

def initialize_taxonomies():
    """Initialize taxonomy nodes for emotions, topics, and beliefs"""
    
    try:
        # Connect to Neo4j
        logger.info(f"Connecting to Neo4j at {NEO4J_URI}")
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        with driver.session() as session:
            # Create emotion taxonomy
            logger.info("Creating emotion taxonomy nodes")
            emotions = [
                {"name": "Anger", "description": "Strong feeling of displeasure or hostility"},
                {"name": "Frustration", "description": "Feeling of being upset or annoyed"},
                {"name": "Anxiety", "description": "Feeling of worry, nervousness, or unease"},
                {"name": "Fear", "description": "An unpleasant emotion caused by threat"},
                {"name": "Sadness", "description": "Feeling of sorrow or unhappiness"},
                {"name": "Grief", "description": "Deep sorrow, especially caused by loss"},
                {"name": "Guilt", "description": "Feeling of having done wrong or failed"},
                {"name": "Shame", "description": "Painful feeling of humiliation or distress"},
                {"name": "Joy", "description": "Feeling of great pleasure and happiness"},
                {"name": "Happiness", "description": "Feeling of joy, pleasure, or contentment"},
                {"name": "Excitement", "description": "Feeling of enthusiasm and eagerness"},
                {"name": "Hope", "description": "Feeling of expectation and desire"},
                {"name": "Love", "description": "Deep affection and attachment"},
                {"name": "Gratitude", "description": "Feeling of thankfulness and appreciation"},
                {"name": "Surprise", "description": "Feeling caused by something unexpected"},
                {"name": "Confusion", "description": "Feeling of being bewildered or unclear"},
                {"name": "Relief", "description": "Feeling of reassurance and relaxation"},
                {"name": "Pride", "description": "Feeling of deep pleasure from achievements"},
                {"name": "Confidence", "description": "Feeling of self-assurance and certainty"},
                {"name": "Overwhelm", "description": "Feeling of being overcome by intensity"}
            ]
            
            # Save emotions to JSON file
            with open(TAXONOMY_DIR / "emotion_taxonomy.json", "w") as f:
                json.dump(emotions, f, indent=2)
            
            for emotion in emotions:
                session.run("""
                MERGE (et:EmotionTaxonomy {name: $name})
                ON CREATE SET et.description = $description, et.created_at = datetime()
                ON MATCH SET et.description = $description, et.updated_at = datetime()
                """, name=emotion["name"], description=emotion["description"])
                logger.info(f"Created/Updated EmotionTaxonomy: {emotion['name']}")
            
            # Create emotion hierarchical relationships
            logger.info("Creating emotion hierarchical relationships")
            relationships = [
                {"parent": "Anger", "child": "Frustration"},
                {"parent": "Anxiety", "child": "Fear"},
                {"parent": "Sadness", "child": "Grief"},
                {"parent": "Joy", "child": "Happiness"},
                {"parent": "Joy", "child": "Excitement"}
            ]
            
            for rel in relationships:
                session.run("""
                MATCH (parent:EmotionTaxonomy {name: $parent})
                MATCH (child:EmotionTaxonomy {name: $child})
                MERGE (parent)-[:PARENT_OF]->(child)
                """, parent=rel["parent"], child=rel["child"])
                logger.info(f"Created relationship: {rel['parent']} -> {rel['child']}")
            
            # Create topic taxonomy
            logger.info("Creating topic taxonomy nodes")
            topics = [
                {"name": "Work", "description": "Professional life and career", "subtopics": [
                    "Career Growth", "Job Satisfaction", "Work-Life Balance", 
                    "Workplace Relationships", "Manager Relationship", "Team Dynamics",
                    "Workload Management", "Professional Development", "Job Security"
                ]},
                {"name": "Family", "description": "Relationships with family members", "subtopics": [
                    "Parent-Child Relationship", "Sibling Relationships", "Extended Family",
                    "Family Dynamics", "Family Responsibilities", "Family Conflict"
                ]},
                {"name": "Relationships", "description": "Personal relationships", "subtopics": [
                    "Romantic Relationships", "Friendships", "Social Connections",
                    "Communication", "Trust", "Boundaries", "Conflict Resolution"
                ]},
                {"name": "Self-Esteem", "description": "Confidence in one's worth or abilities", "subtopics": [
                    "Self-Image", "Self-Confidence", "Self-Worth", "Body Image"
                ]},
                {"name": "Health", "description": "Physical and mental wellbeing", "subtopics": [
                    "Physical Health", "Mental Health", "Sleep", "Exercise", 
                    "Nutrition", "Chronic Conditions", "Healthcare"
                ]},
                {"name": "Personal Development", "description": "Growth and learning", "subtopics": [
                    "Self-Improvement", "Goal Setting", "Time Management", 
                    "Stress Management", "Mindfulness", "Self-Care"
                ]},
                {"name": "Finances", "description": "Money and financial concerns", "subtopics": [
                    "Saving", "Investing", "Debt", "Financial Planning", "Income"
                ]},
                {"name": "Education", "description": "Learning and academic development", "subtopics": [
                    "Formal Education", "Skills Development", "Continuous Learning"
                ]},
                {"name": "Recreation", "description": "Leisure activities and hobbies", "subtopics": [
                    "Hobbies", "Travel", "Entertainment", "Sports", "Arts"
                ]}
            ]
            
            # Process topics and create in database
            all_topics = []
            topic_relationships = []
            
            for main_topic in topics:
                # Add main topic to all_topics list
                all_topics.append({
                    "name": main_topic["name"],
                    "description": main_topic["description"],
                    "level": "main"
                })
                
                # Create main topic in database
                session.run("""
                MERGE (tt:TopicTaxonomy {name: $name})
                ON CREATE SET tt.description = $description, tt.level = 'main', tt.created_at = datetime()
                ON MATCH SET tt.description = $description, tt.updated_at = datetime()
                """, name=main_topic["name"], description=main_topic["description"])
                logger.info(f"Created/Updated TopicTaxonomy: {main_topic['name']}")
                
                # Process subtopics
                for subtopic in main_topic.get("subtopics", []):
                    # Add subtopic to all_topics list
                    all_topics.append({
                        "name": subtopic,
                        "description": f"Subtopic of {main_topic['name']}",
                        "level": "sub",
                        "parent": main_topic["name"]
                    })
                    
                    # Create subtopic in database
                    session.run("""
                    MERGE (tt:TopicTaxonomy {name: $name})
                    ON CREATE SET tt.description = $description, tt.level = 'sub', tt.created_at = datetime()
                    ON MATCH SET tt.description = $description, tt.updated_at = datetime()
                    """, name=subtopic, description=f"Subtopic of {main_topic['name']}")
                    logger.info(f"Created/Updated TopicTaxonomy subtopic: {subtopic}")
                    
                    # Add relationship to list
                    topic_relationships.append({
                        "parent": main_topic["name"],
                        "child": subtopic
                    })
            
            # Save all topics to JSON file
            with open(TAXONOMY_DIR / "topic_taxonomy.json", "w") as f:
                json.dump(all_topics, f, indent=2)
            
            # Create topic hierarchical relationships
            logger.info("Creating topic hierarchical relationships")
            for rel in topic_relationships:
                session.run("""
                MATCH (parent:TopicTaxonomy {name: $parent})
                MATCH (child:TopicTaxonomy {name: $child})
                MERGE (parent)-[:PARENT_OF]->(child)
                """, parent=rel["parent"], child=rel["child"])
                logger.info(f"Created relationship: {rel['parent']} -> {rel['child']}")
            
            # Create belief taxonomy
            logger.info("Creating belief taxonomy nodes")
            beliefs = [
                {"name": "Self-Worth", "description": "Beliefs about one's value"},
                {"name": "World View", "description": "Beliefs about how the world works"},
                {"name": "Capability", "description": "Beliefs about one's abilities"},
                {"name": "Future", "description": "Beliefs about what will happen"},
                {"name": "Others", "description": "Beliefs about other people"},
                {"name": "Deservingness", "description": "Beliefs about what one deserves"},
                {"name": "Belonging", "description": "Beliefs about fitting in with others"},
                {"name": "Safety", "description": "Beliefs about security and safety"},
                {"name": "Control", "description": "Beliefs about control over life events"},
                {"name": "Purpose", "description": "Beliefs about one's purpose in life"}
            ]
            
            # Save beliefs to JSON file
            with open(TAXONOMY_DIR / "belief_taxonomy.json", "w") as f:
                json.dump(beliefs, f, indent=2)
            
            for belief in beliefs:
                session.run("""
                MERGE (bt:BeliefTaxonomy {name: $name})
                ON CREATE SET bt.description = $description, bt.created_at = datetime()
                ON MATCH SET bt.description = $description, bt.updated_at = datetime()
                """, name=belief["name"], description=belief["description"])
                logger.info(f"Created/Updated BeliefTaxonomy: {belief['name']}")
            
            logger.info("Taxonomy initialization complete")
    
    except Exception as e:
        logger.error(f"Error initializing taxonomies: {e}")
        raise
    finally:
        if 'driver' in locals():
            driver.close()
            logger.info("Neo4j connection closed")

if __name__ == "__main__":
    initialize_taxonomies() 