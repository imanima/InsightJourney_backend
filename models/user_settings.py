"""
User Settings Model for Neo4j Database

This module defines the structure and operations for user settings in the Neo4j database.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Determine if we're in test mode
IS_TEST = os.getenv('TESTING', 'false').lower() == 'true'

# Neo4j connection settings
if IS_TEST:
    NEO4J_URI = os.getenv("NEO4J_TEST_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_TEST_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_TEST_PASSWORD", "testpassword123")
else:
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

@dataclass
class AnalysisElement:
    name: str
    description: str
    enabled: bool = True
    categories: Optional[List[str]] = None
    format_template: str = ""
    system_instructions: str = ""
    analysis_instructions: str = ""
    requires_topic: bool = False
    requires_timestamp: bool = False
    additional_fields: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'categories': self.categories or [],
            'format_template': self.format_template,
            'system_instructions': self.system_instructions,
            'analysis_instructions': self.analysis_instructions,
            'requires_topic': self.requires_topic,
            'requires_timestamp': self.requires_timestamp,
            'additional_fields': self.additional_fields or []
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisElement':
        return cls(
            name=data['name'],
            description=data['description'],
            enabled=data.get('enabled', True),
            categories=data.get('categories'),
            format_template=data.get('format_template', ''),
            system_instructions=data.get('system_instructions', ''),
            analysis_instructions=data.get('analysis_instructions', ''),
            requires_topic=data.get('requires_topic', False),
            requires_timestamp=data.get('requires_timestamp', False),
            additional_fields=data.get('additional_fields')
        )

class UserSettings:
    """User settings management using Neo4j"""
    
    def __init__(self):
        """Initialize connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, 
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            logger.info(f"Connected to Neo4j database at {NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()

    def create_settings(self, user_id: str, max_sessions: int = 10, max_duration: int = 3600,
                       allowed_file_types: List[str] = None, analysis_elements: List[Dict] = None,
                       system_prompt_template: str = None, analysis_prompt_template: str = None,
                       gpt_model: str = 'gpt-3.5-turbo', temperature: float = 0.7,
                       max_tokens: int = 2000) -> Dict[str, Any]:
        """Create new user settings in Neo4j"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_settings,
                user_id,
                max_sessions,
                max_duration,
                allowed_file_types or ['mp3', 'wav', 'm4a'],
                analysis_elements,
                system_prompt_template,
                analysis_prompt_template,
                gpt_model,
                temperature,
                max_tokens
            )
            return result

    def _create_settings(self, tx, user_id: str, max_sessions: int, max_duration: int,
                        allowed_file_types: List[str], analysis_elements: List[Dict],
                        system_prompt_template: str, analysis_prompt_template: str,
                        gpt_model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Create user settings node in Neo4j"""
        query = """
        MATCH (u:User {id: $user_id})
        MERGE (s:Settings {user_id: $user_id})
        SET s.max_sessions = $max_sessions,
            s.max_duration = $max_duration,
            s.allowed_file_types = $allowed_file_types,
            s.analysis_elements = $analysis_elements,
            s.system_prompt_template = $system_prompt_template,
            s.analysis_prompt_template = $analysis_prompt_template,
            s.gpt_model = $gpt_model,
            s.temperature = $temperature,
            s.max_tokens = $max_tokens,
            s.created_at = datetime(),
            s.updated_at = datetime()
        MERGE (u)-[:HAS_SETTINGS]->(s)
        RETURN s
        """
        result = tx.run(query,
                       user_id=user_id,
                       max_sessions=max_sessions,
                       max_duration=max_duration,
                       allowed_file_types=allowed_file_types,
                       analysis_elements=analysis_elements,
                       system_prompt_template=system_prompt_template,
                       analysis_prompt_template=analysis_prompt_template,
                       gpt_model=gpt_model,
                       temperature=temperature,
                       max_tokens=max_tokens)
        return result.single()['s']

    def get_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings from Neo4j"""
        with self.driver.session() as session:
            result = session.read_transaction(self._get_settings, user_id)
            return result

    def _get_settings(self, tx, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings node from Neo4j"""
        query = """
        MATCH (s:Settings {user_id: $user_id})
        RETURN s
        """
        result = tx.run(query, user_id=user_id)
        record = result.single()
        return record['s'] if record else None

    def update_settings(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user settings in Neo4j"""
        with self.driver.session() as session:
            result = session.write_transaction(self._update_settings, user_id, **kwargs)
            return result

    def _update_settings(self, tx, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user settings node in Neo4j"""
        set_clauses = []
        for key, value in kwargs.items():
            if value is not None:
                set_clauses.append(f"s.{key} = ${key}")
        
        if not set_clauses:
            return None

        query = f"""
        MATCH (s:Settings {{user_id: $user_id}})
        SET {', '.join(set_clauses)}, s.updated_at = datetime()
        RETURN s
        """
        result = tx.run(query, user_id=user_id, **kwargs)
        record = result.single()
        return record['s'] if record else None

    def delete_settings(self, user_id: str) -> bool:
        """Delete user settings from Neo4j"""
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_settings, user_id)
            return result

    def _delete_settings(self, tx, user_id: str) -> bool:
        """Delete user settings node from Neo4j"""
        query = """
        MATCH (s:Settings {user_id: $user_id})
        DETACH DELETE s
        RETURN count(s) as deleted
        """
        result = tx.run(query, user_id=user_id)
        return result.single()['deleted'] > 0 