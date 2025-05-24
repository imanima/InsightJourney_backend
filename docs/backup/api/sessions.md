# Sessions

## Create Session
```http
POST /sessions
```
```json
{
    "title": "Therapy Session 1",
    "inputMethod": "text",
    "text": "Session transcript"
}
```
Response:
```json
{
    "sessionId": "session_id",
    "graphId": "graph_id",
    "status": "created"
}
```

## Get Session
```http
GET /sessions/{session_id}
```
Response:
```json
{
    "id": "session_id",
    "title": "Session Title",
    "date": "2024-03-20T14:30:00Z",
    "status": "completed",
    "analysis_status": "success",
    "emotions": [...],
    "insights": [...],
    "beliefs": [...],
    "challenges": [...],
    "action_items": [...]
}
```

## List Sessions
```http
GET /sessions
```
Response:
```json
{
    "sessions": [
        {
            "id": "session_id",
            "title": "Session Title",
            "date": "2024-03-20T14:30:00Z",
            "status": "completed"
        }
    ]
}
```

## Overview

The Sessions API allows you to manage user sessions, including creation, retrieval, and analysis of session data.

## Endpoints

### Create Session

```http
POST /sessions
```

Request body:
```json
{
  "title": "string",
  "description": "string",
  "duration": 0,
  "status": "string",
  "analysis_status": "string"
}
```

Response:
```json
{
  "session_id": "string",
  "status": "string"
}
```

### List Sessions

```http
GET /sessions
Authorization: Bearer <access_token>
```

**Query Parameters**
- `page` (integer, default: 1)
- `per_page` (integer, default: 10)
- `sort` (string, options: created_at, updated_at)
- `order` (string, options: asc, desc)

**Response**
```json
{
    "status": "success",
    "data": {
        "sessions": [
            {
                "id": "string",
                "title": "string",
                "description": "string",
                "settings": {},
                "created_at": "string",
                "updated_at": "string"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 100,
            "pages": 10
        }
    }
}
```

### Get Session

```http
GET /sessions/{session_id}
```

Response:
```json
{
  "session_id": "string",
  "title": "string",
  "description": "string",
  "duration": 0,
  "status": "string",
  "analysis_status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

### Update Session

```http
PUT /sessions/{session_id}
```

Request body:
```json
{
  "title": "string",
  "description": "string",
  "status": "string",
  "analysis_status": "string"
}
```

Response:
```json
{
  "status": "string",
  "message": "string"
}
```

### Delete Session

```http
DELETE /sessions/{session_id}
```

Response:
```json
{
  "status": "string",
  "message": "string"
}
```

### Upload Content

```http
POST /sessions/{session_id}/content
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <file>
type: "audio" | "video" | "text"
```

**Response**
```json
{
    "status": "success",
    "data": {
        "upload": {
            "id": "string",
            "filename": "string",
            "type": "string",
            "size": 1024,
            "created_at": "string"
        }
    }
}
```

### Get Analysis Status

```http
GET /sessions/{session_id}/analysis/status
Authorization: Bearer <access_token>
```

**Response**
```json
{
    "status": "success",
    "data": {
        "analysis": {
            "status": "processing" | "completed" | "failed",
            "progress": 0.75,
            "error": "string",
            "updated_at": "string"
        }
    }
}
```

### Get Emotions

```http
GET /sessions/{session_id}/emotions
Authorization: Bearer <access_token>
```

**Query Parameters**
- `start_time` (string, ISO datetime)
- `end_time` (string, ISO datetime)
- `category` (string)

**Response**
```json
{
    "status": "success",
    "data": {
        "emotions": [
            {
                "id": "string",
                "name": "string",
                "intensity": 0.8,
                "category": "string",
                "timestamp": "string"
            }
        ]
    }
}
```

### Get Topics

```http
GET /sessions/{session_id}/topics
Authorization: Bearer <access_token>
```

**Query Parameters**
- `start_time` (string, ISO datetime)
- `end_time` (string, ISO datetime)
- `category` (string)

**Response**
```json
{
    "status": "success",
    "data": {
        "topics": [
            {
                "id": "string",
                "name": "string",
                "confidence": 0.9,
                "category": "string",
                "timestamp": "string"
            }
        ]
    }
}
```

### Get Insights

```http
GET /sessions/{session_id}/insights
Authorization: Bearer <access_token>
```

**Query Parameters**
- `type` (string)
- `start_time` (string, ISO datetime)
- `end_time` (string, ISO datetime)

**Response**
```json
{
    "status": "success",
    "data": {
        "insights": [
            {
                "id": "string",
                "content": "string",
                "type": "string",
                "confidence": 0.95,
                "timestamp": "string"
            }
        ]
    }
}
```

### WebSocket Events

Connect to:
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/sessions/{session_id}/events
```

### Event Types

1. **Analysis Progress**
```json
{
    "type": "analysis_progress",
    "data": {
        "status": "processing",
        "progress": 0.75
    }
}
```

2. **New Emotion**
```json
{
    "type": "new_emotion",
    "data": {
        "emotion": {
            "id": "string",
            "name": "string",
            "intensity": 0.8,
            "timestamp": "string"
        }
    }
}
```

3. **New Topic**
```json
{
    "type": "new_topic",
    "data": {
        "topic": {
            "id": "string",
            "name": "string",
            "confidence": 0.9,
            "timestamp": "string"
        }
    }
}
```

4. **New Insight**
```json
{
    "type": "new_insight",
    "data": {
        "insight": {
            "id": "string",
            "content": "string",
            "type": "string",
            "timestamp": "string"
        }
    }
}
```

## Example Usage

### JavaScript/TypeScript
```typescript
class SessionService {
    constructor(private authService: AuthService) {}

    async createSession(title: string, description: string) {
        return this.authService.makeAuthenticatedRequest('/sessions', {
            method: 'POST',
            body: JSON.stringify({ title, description })
        });
    }

    async uploadContent(sessionId: string, file: File) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', file.type.split('/')[0]);

        return this.authService.makeAuthenticatedRequest(
            `/sessions/${sessionId}/content`,
            {
                method: 'POST',
                body: formData
            }
        );
    }

    connectToEvents(sessionId: string, handlers: {
        onProgress: (progress: number) => void,
        onEmotion: (emotion: any) => void,
        onTopic: (topic: any) => void,
        onInsight: (insight: any) => void
    }) {
        const ws = new WebSocket(
            `ws://localhost:5000/api/v1/sessions/${sessionId}/events`
        );

        ws.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);
            switch (type) {
                case 'analysis_progress':
                    handlers.onProgress(data.progress);
                    break;
                case 'new_emotion':
                    handlers.onEmotion(data.emotion);
                    break;
                case 'new_topic':
                    handlers.onTopic(data.topic);
                    break;
                case 'new_insight':
                    handlers.onInsight(data.insight);
                    break;
            }
        };

        return ws;
    }
}
```

### Python
```python
import websockets
import json
import asyncio

class SessionService:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def create_session(self, title: str, description: str) -> dict:
        return self.auth_service.make_authenticated_request(
            '/sessions',
            method='POST',
            json={'title': title, 'description': description}
        )

    def upload_content(self, session_id: str, file_path: str) -> dict:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.auth_service.make_authenticated_request(
                f'/sessions/{session_id}/content',
                method='POST',
                files=files
            )

    async def connect_to_events(
        self,
        session_id: str,
        on_progress=None,
        on_emotion=None,
        on_topic=None,
        on_insight=None
    ):
        uri = f'ws://localhost:5000/api/v1/sessions/{session_id}/events'
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                event = json.loads(message)
                
                if event['type'] == 'analysis_progress' and on_progress:
                    on_progress(event['data']['progress'])
                elif event['type'] == 'new_emotion' and on_emotion:
                    on_emotion(event['data']['emotion'])
                elif event['type'] == 'new_topic' and on_topic:
                    on_topic(event['data']['topic'])
                elif event['type'] == 'new_insight' and on_insight:
                    on_insight(event['data']['insight'])
``` 