from datetime import datetime
from typing import List, Dict, Any, Optional
from services.neo4j_service import Neo4jService

class ActionItemService:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def create_action_item(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new action item in Neo4j."""
        query = """
        MATCH (s:Session {id: $session_id})
        CREATE (a:ActionItem {
            id: randomUUID(),
            title: $title,
            description: $description,
            status: $status,
            due_date: datetime($due_date),
            priority: $priority,
            topic: $topic,
            created_at: datetime(),
            updated_at: datetime()
        })-[:BELONGS_TO]->(s)
        RETURN a
        """
        params = {
            'session_id': session_id,
            'title': data['title'],
            'description': data.get('description', ''),
            'status': data.get('status', 'not_started'),
            'due_date': data['due_date'],
            'priority': data.get('priority', 'medium'),
            'topic': data.get('topic', '')
        }
        result = self.neo4j.execute_write(query, params)
        return self._format_action_item(result[0]['a'])

    def get_action_items(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all action items for a session."""
        query = """
        MATCH (a:ActionItem)-[:BELONGS_TO]->(s:Session {id: $session_id})
        RETURN a
        ORDER BY a.created_at DESC
        """
        params = {'session_id': session_id}
        results = self.neo4j.execute_read(query, params)
        return [self._format_action_item(record['a']) for record in results]

    def update_action_item(self, session_id: str, action_item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an action item."""
        query = """
        MATCH (a:ActionItem {id: $action_item_id})-[:BELONGS_TO]->(s:Session {id: $session_id})
        SET a += $updates,
            a.updated_at = datetime()
        RETURN a
        """
        updates = {k: v for k, v in data.items() if k in ['title', 'description', 'status', 'due_date', 'priority', 'topic']}
        if 'due_date' in updates:
            updates['due_date'] = datetime.fromisoformat(updates['due_date'])
        
        params = {
            'session_id': session_id,
            'action_item_id': action_item_id,
            'updates': updates
        }
        results = self.neo4j.execute_write(query, params)
        return self._format_action_item(results[0]['a']) if results else None

    def delete_action_item(self, session_id: str, action_item_id: str) -> bool:
        """Delete an action item."""
        query = """
        MATCH (a:ActionItem {id: $action_item_id})-[:BELONGS_TO]->(s:Session {id: $session_id})
        DELETE a
        """
        params = {
            'session_id': session_id,
            'action_item_id': action_item_id
        }
        self.neo4j.execute_write(query, params)
        return True

    def _format_action_item(self, node: Any) -> Dict[str, Any]:
        """Format a Neo4j node into a dictionary."""
        return {
            'id': node['id'],
            'title': node['title'],
            'description': node.get('description', ''),
            'status': node.get('status', 'not_started'),
            'due_date': node['due_date'].isoformat() if node.get('due_date') else None,
            'priority': node.get('priority', 'medium'),
            'topic': node.get('topic', ''),
            'created_at': node['created_at'].isoformat(),
            'updated_at': node['updated_at'].isoformat()
        } 