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
        
        try:
            with self.neo4j.driver.session() as session:
                result = session.run(query, params)
                record = result.single()
                return self._format_action_item(record['a']) if record else None
        except Exception as e:
            self.neo4j.logger.error(f"Error creating action item: {str(e)}")
            return None

    def get_action_items(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all action items for a session."""
        query = """
        MATCH (a:ActionItem)-[:BELONGS_TO]->(s:Session {id: $session_id})
        RETURN a
        ORDER BY a.created_at DESC
        """
        params = {'session_id': session_id}
        
        try:
            with self.neo4j.driver.session() as session:
                result = session.run(query, params)
                return [self._format_action_item(record['a']) for record in result]
        except Exception as e:
            self.neo4j.logger.error(f"Error getting action items: {str(e)}")
            return []

    def get_all_user_action_items(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all action items for a user across all sessions."""
        query = """
        MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)-[:HAS_ACTION_ITEM]->(a:ActionItem)
        OPTIONAL MATCH (a)-[:RELATED_TO]->(t:Topic)
        RETURN a, s.title as session_title, s.id as session_id, s.created_at as session_date,
               COLLECT(DISTINCT {name: t.name, id: t.id}) as topics
        ORDER BY a.created_at DESC
        """
        params = {'user_id': user_id}
        
        try:
            with self.neo4j.driver.session() as session:
                result = session.run(query, params)
                action_items = []
                
                for record in result:
                    item = self._format_action_item(record['a'])
                    item['sessionId'] = record['session_id']
                    item['sessionTitle'] = record['session_title']
                    
                    # Handle session_date safely
                    session_date = record['session_date']
                    if session_date:
                        try:
                            if hasattr(session_date, 'isoformat'):
                                item['sessionDate'] = session_date.isoformat()
                            else:
                                item['sessionDate'] = str(session_date)
                        except Exception:
                            item['sessionDate'] = str(session_date)
                    else:
                        item['sessionDate'] = None
                    
                    # Add topics if available
                    topics = record.get('topics', [])
                    if topics and topics[0].get('name'):  # Check if topics exist and are not empty
                        item['topics'] = [topic for topic in topics if topic.get('name')]
                    else:
                        item['topics'] = []
                    
                    action_items.append(item)
                
                self.neo4j.logger.info(f"Found {len(action_items)} action items for user {user_id}")
                return action_items
                
        except Exception as e:
            self.neo4j.logger.error(f"Error getting user action items: {str(e)}")
            return []

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
        
        try:
            with self.neo4j.driver.session() as session:
                result = session.run(query, params)
                record = result.single()
                return self._format_action_item(record['a']) if record else None
        except Exception as e:
            self.neo4j.logger.error(f"Error updating action item: {str(e)}")
            return None

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
        
        try:
            with self.neo4j.driver.session() as session:
                session.run(query, params)
                return True
        except Exception as e:
            self.neo4j.logger.error(f"Error deleting action item: {str(e)}")
            return False

    def _format_action_item(self, node: Any) -> Dict[str, Any]:
        """Format a Neo4j node into a dictionary."""
        if not node:
            return {}
            
        try:
            formatted = {
                'id': node.get('id'),
                'title': node.get('title', '') or node.get('name', ''),
                'description': node.get('description', ''),
                'status': node.get('status', 'not_started'),
                'priority': node.get('priority', 'medium'),
                'topic': node.get('topic', ''),
            }
            
            # Handle created_at safely
            if node.get('created_at'):
                try:
                    if hasattr(node['created_at'], 'isoformat'):
                        formatted['created_at'] = node['created_at'].isoformat()
                    else:
                        formatted['created_at'] = str(node['created_at'])
                except Exception:
                    formatted['created_at'] = str(node['created_at'])
            else:
                formatted['created_at'] = None
            
            # Handle updated_at safely
            if node.get('updated_at'):
                try:
                    if hasattr(node['updated_at'], 'isoformat'):
                        formatted['updated_at'] = node['updated_at'].isoformat()
                    else:
                        formatted['updated_at'] = str(node['updated_at'])
                except Exception:
                    formatted['updated_at'] = str(node['updated_at'])
            else:
                formatted['updated_at'] = None
            
            # Handle due_date safely
            if node.get('due_date'):
                try:
                    if hasattr(node['due_date'], 'isoformat'):
                        formatted['due_date'] = node['due_date'].isoformat()
                    else:
                        formatted['due_date'] = str(node['due_date'])
                except Exception:
                    formatted['due_date'] = str(node['due_date'])
            else:
                formatted['due_date'] = None
                
            return formatted
        except Exception as e:
            self.neo4j.logger.error(f"Error formatting action item: {str(e)}")
            return {} 