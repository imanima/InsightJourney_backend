# Backend Integration Guide

This document describes how to integrate other backend services with the Insight Journey platform.

## Overview

The Insight Journey platform provides multiple integration points:
1. RESTful API endpoints
2. WebSocket events
3. Message queue integration
4. Database access

## Base URL
```
https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1
```

## API Integration

### Authentication

```python
import requests

class InsightJourneyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None

    def login(self, email: str, password: str) -> dict:
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        if data['status'] == 'success':
            self.access_token = data['data']['access_token']
            self.refresh_token = data['data']['refresh_token']
        return data

    def refresh_token(self) -> dict:
        response = requests.post(
            f'{self.base_url}/auth/refresh',
            headers={'Authorization': f'Bearer {self.refresh_token}'}
        )
        data = response.json()
        if data['status'] == 'success':
            self.access_token = data['data']['access_token']
            self.refresh_token = data['data']['refresh_token']
        return data

    def request(self, method: str, endpoint: str, **kwargs) -> dict:
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'

        response = requests.request(
            method,
            f'{self.base_url}{endpoint}',
            headers=headers,
            **kwargs
        )

        if response.status_code == 401:
            self.refresh_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.request(
                method,
                f'{self.base_url}{endpoint}',
                headers=headers,
                **kwargs
            )

        return response.json()
```

### Session Management

```python
class SessionClient(InsightJourneyClient):
    def create_session(self, title: str, description: str) -> dict:
        return self.request(
            'POST',
            '/sessions',
            json={'title': title, 'description': description}
        )

    def upload_content(self, session_id: str, file_path: str) -> dict:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.request(
                'POST',
                f'/sessions/{session_id}/content',
                files=files
            )

    def get_analysis_status(self, session_id: str) -> dict:
        return self.request(
            'GET',
            f'/sessions/{session_id}/analysis/status'
        )

    def get_emotions(self, session_id: str, **params) -> dict:
        return self.request(
            'GET',
            f'/sessions/{session_id}/emotions',
            params=params
        )

    def get_topics(self, session_id: str, **params) -> dict:
        return self.request(
            'GET',
            f'/sessions/{session_id}/topics',
            params=params
        )

    def get_insights(self, session_id: str, **params) -> dict:
        return self.request(
            'GET',
            f'/sessions/{session_id}/insights',
            params=params
        )
```

## WebSocket Integration

### Event Subscription

```python
import websockets
import asyncio
import json

class WebSocketClient:
    def __init__(self, session_id: str, access_token: str):
        self.session_id = session_id
        self.access_token = access_token
        self.uri = f'wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/sessions/{session_id}/events'
        self.handlers = {}

    async def connect(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        async with websockets.connect(self.uri, extra_headers=headers) as ws:
            while True:
                try:
                    message = await ws.recv()
                    event = json.loads(message)
                    await self.handle_event(event)
                except websockets.exceptions.ConnectionClosed:
                    break

    async def handle_event(self, event: dict):
        event_type = event['type']
        if event_type in self.handlers:
            await self.handlers[event_type](event['data'])

    def on(self, event_type: str, handler):
        self.handlers[event_type] = handler

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.connect())
```

## Message Queue Integration

### Celery Tasks

```python
from celery import Celery
from typing import Dict, Any

celery = Celery(
    'insight_journey',
    broker='redis://insight-journey-redis:6379/1',
    backend='redis://insight-journey-redis:6379/2'
)

@celery.task
def process_content(session_id: str) -> Dict[str, Any]:
    # Process uploaded content
    pass

@celery.task
def analyze_emotions(content: str) -> Dict[str, Any]:
    # Analyze emotions in content
    pass

@celery.task
def analyze_topics(content: str) -> Dict[str, Any]:
    # Analyze topics in content
    pass

@celery.task
def generate_insights(
    emotions: Dict[str, Any],
    topics: Dict[str, Any]
) -> Dict[str, Any]:
    # Generate insights from analysis
    pass

def start_analysis_pipeline(session_id: str):
    workflow = (
        process_content.s(session_id) |
        analyze_emotions.s() |
        analyze_topics.s() |
        generate_insights.s()
    )
    return workflow.apply_async()
```

## Database Integration

### SQLAlchemy Models

```python
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    sessions = relationship('Session', back_populates='user')

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String)
    user = relationship('User', back_populates='sessions')
```

### Neo4j Integration

```python
from neo4j import GraphDatabase
from typing import Dict, Any

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def close(self):
        self.driver.close()

    def create_session_node(self, session_data: Dict[str, Any]):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_session_node,
                session_data
            )

    @staticmethod
    def _create_session_node(tx, session_data: Dict[str, Any]):
        query = """
        CREATE (s:Session {
            id: $id,
            title: $title,
            description: $description
        })
        """
        tx.run(query, **session_data)

    def create_emotion_node(
        self,
        session_id: str,
        emotion_data: Dict[str, Any]
    ):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_emotion_node,
                session_id,
                emotion_data
            )

    @staticmethod
    def _create_emotion_node(tx, session_id: str, emotion_data: Dict[str, Any]):
        query = """
        MATCH (s:Session {id: $session_id})
        CREATE (e:Emotion {
            id: $id,
            name: $name,
            intensity: $intensity,
            timestamp: $timestamp
        })
        CREATE (s)-[:CONTAINS]->(e)
        """
        tx.run(query, session_id=session_id, **emotion_data)
```

## Example Usage

### Complete Integration Example

```python
import asyncio
from typing import Dict, Any

class InsightJourneyIntegration:
    def __init__(
        self,
        api_url: str,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str
    ):
        self.api_client = InsightJourneyClient(api_url)
        self.neo4j_client = Neo4jClient(
            neo4j_uri,
            neo4j_user,
            neo4j_password
        )

    async def process_session(
        self,
        title: str,
        description: str,
        content_path: str
    ):
        # Create session
        session_data = self.api_client.create_session(
            title,
            description
        )
        session_id = session_data['data']['session']['id']

        # Store in Neo4j
        self.neo4j_client.create_session_node(session_data['data']['session'])

        # Upload content
        upload_data = self.api_client.upload_content(
            session_id,
            content_path
        )

        # Start WebSocket client
        ws_client = WebSocketClient(session_id, self.api_client.access_token)

        # Define event handlers
        async def handle_emotion(data: Dict[str, Any]):
            self.neo4j_client.create_emotion_node(session_id, data)

        async def handle_topic(data: Dict[str, Any]):
            self.neo4j_client.create_topic_node(session_id, data)

        async def handle_insight(data: Dict[str, Any]):
            self.neo4j_client.create_insight_node(session_id, data)

        # Register handlers
        ws_client.on('new_emotion', handle_emotion)
        ws_client.on('new_topic', handle_topic)
        ws_client.on('new_insight', handle_insight)

        # Start WebSocket connection
        await ws_client.connect()

        # Start analysis pipeline
        task = start_analysis_pipeline(session_id)
        result = task.get()

        return result

if __name__ == '__main__':
    integration = InsightJourneyIntegration(
        api_url='https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1',
        neo4j_uri='bolt://8769633e.databases.neo4j.io:7687',
        neo4j_user='neo4j',
        neo4j_password='password'
    )

    asyncio.run(integration.process_session(
        title='Test Session',
        description='Integration test',
        content_path='test.txt'
    )) 
```

## Error Handling
All endpoints return appropriate HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

Error responses include:
```json
{
    "error": "Error message",
    "details": "Additional error details"
}
```

## Rate Limiting
- 100 requests per minute per user
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time until limit resets

## Webhooks
Available webhook events:
1. `analysis.complete`: Sent when analysis is completed
2. `action_item.created`: Sent when new action item is created
3. `action_item.updated`: Sent when action item is updated
4. `action_item.deleted`: Sent when action item is deleted

Webhook payload format:
```json
{
    "event": "event_name",
    "data": {
        // Event-specific data
    },
    "timestamp": "ISO-8601 timestamp"
}
```

## Best Practices
1. Always include the Authorization header for authenticated requests
2. Handle rate limiting by implementing exponential backoff
3. Implement proper error handling for all API calls
4. Cache responses when appropriate to reduce API calls
5. Use webhooks for real-time updates instead of polling
6. Implement retry logic for failed requests
7. Validate all user input before sending to the API
8. Use proper content types for file uploads
9. Implement proper loading states for async operations
10. Handle token expiration and refresh logic

## Monitoring
- API health status: `GET /health`
- Response times are typically under 500ms
- Error rates are monitored and logged
- System status is available through the health endpoint

## Support
For API-related issues or questions, contact the backend team or refer to the API documentation. 