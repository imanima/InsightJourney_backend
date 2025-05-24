# Analysis API

This document describes the Analysis API endpoints in the Insight Journey platform.

## Overview

The Analysis API provides endpoints for managing and retrieving analysis results, including emotions, topics, and insights. It integrates with Neo4j for graph-based analysis and storage.

## Neo4j Integration

### Graph Schema

```cypher
// Nodes
(User)-[:HAS_SESSION]->(Session)
(Session)-[:HAS_TRANSCRIPT]->(Transcript)
(Session)-[:HAS_EMOTION]->(Emotion)
(Session)-[:HAS_BELIEF]->(Belief)
(Session)-[:HAS_INSIGHT]->(Insight)
(Session)-[:HAS_CHALLENGE]->(Challenge)
(Session)-[:HAS_ACTION_ITEM]->(ActionItem)
(Session)-[:HAS_TOPIC]->(Topic)

// Relationships
(Emotion)-[:RELATED_TO]->(Topic)
(Belief)-[:RELATED_TO]->(Topic)
(Insight)-[:RELATED_TO]->(Topic)
(Challenge)-[:RELATED_TO]->(Topic)
(ActionItem)-[:RELATED_TO]->(Topic)
```

### Neo4j Endpoints

```http
POST /api/v1/analysis/neo4j/query
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "query": "MATCH (s:Session {id: $sessionId}) RETURN s",
    "parameters": {
        "sessionId": "string"
    }
}
```

**Response**
```json
{
    "status": "success",
    "data": {
        "results": [
            // Neo4j query results
        ]
    }
}
```

## Base URL

All API endpoints are relative to:
```
https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1
```

## Endpoints

### Start Analysis

```http
POST /sessions/{session_id}/analyze
```

Response:
```json
{
    "status": "processing",
    "message": "Analysis started for session {session_id}"
}
```

### Get Analysis Results

```http
GET /sessions/{session_id}/analysis
```

Response:
```json
{
    "status": "completed",
    "elements": {
        "emotions": [
            {
                "name": "Anxiety",
                "intensity": 7,
                "context": "Work presentation",
                "topic": "Career",
                "timestamp": "2024-03-20T14:30:00Z"
            }
        ],
        "insights": [
            {
                "name": "Need for preparation",
                "context": "Recognizing that preparation reduces anxiety",
                "topic": "Personal Growth",
                "timestamp": "2024-03-20T14:35:00Z"
            }
        ],
        "beliefs": [
            {
                "name": "Performance equals worth",
                "description": "Belief that work performance determines self-worth",
                "impact": "High",
                "topic": "Self-Esteem",
                "timestamp": "2024-03-20T14:40:00Z"
            }
        ],
        "challenges": [
            {
                "name": "Public speaking anxiety",
                "impact": "High",
                "topic": "Career",
                "timestamp": "2024-03-20T14:45:00Z"
            }
        ],
        "action_items": [
            {
                "name": "Practice presentation",
                "description": "Rehearse presentation multiple times",
                "topic": "Career",
                "timestamp": "2024-03-20T14:50:00Z"
            }
        ]
    }
}
```

### Update Elements

```http
PUT /sessions/{session_id}/elements
```

Request body: Same as analysis results format above.

Response:
```json
{
    "status": "success",
    "message": "Successfully updated elements for session {session_id}"
}
```

### Get Analysis Status

```http
GET /analysis/{analysis_id}/status
```

Response:
```json
{
  "status": "string",
  "progress": 0,
  "result": {
    "emotions": [],
    "topics": [],
    "insights": []
  }
}
```

### Get Graph Analysis

```http
GET /api/v1/analysis/{session_id}/graph
Authorization: Bearer <access_token>
```

**Response**
```json
{
    "status": "success",
    "data": {
        "nodes": [
            {
                "id": "string",
                "type": "emotion" | "belief" | "insight" | "challenge" | "action_item" | "topic",
                "properties": {
                    // Node properties
                }
            }
        ],
        "relationships": [
            {
                "source": "string",
                "target": "string",
                "type": "RELATED_TO" | "HAS" | "CONNECTED_TO",
                "properties": {
                    // Relationship properties
                }
            }
        ]
    }
}
```

### Export Analysis to Neo4j

```http
POST /api/v1/analysis/{session_id}/export
Authorization: Bearer <access_token>
```

**Response**
```json
{
    "status": "success",
    "data": {
        "export": {
            "id": "string",
            "session_id": "string",
            "status": "completed",
            "nodes_created": 100,
            "relationships_created": 150,
            "created_at": "string"
        }
    }
}
```

## Error Responses

- 400: Bad Request
  - Invalid session ID
  - Invalid transcript ID
  - Invalid settings
- 401: Unauthorized
- 403: Forbidden
- 404: Analysis not found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

- 5 analyses per minute per user
- 50 analyses per hour per user
- 100MB total data size per analysis

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

### Get Emotion Analysis

```http
GET /api/v1/analysis/{analysis_id}/emotions
Authorization: Bearer <access_token>
```

**Query Parameters**
- `category` (string)
- `start_time` (string, ISO datetime)
- `end_time` (string, ISO datetime)
- `threshold` (number, 0-1)

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
                "timestamp": "string",
                "context": {
                    "text": "string",
                    "start_time": "string",
                    "end_time": "string"
                }
            }
        ]
    }
}
```

### Get Topic Analysis

```http
GET /api/v1/analysis/{analysis_id}/topics
Authorization: Bearer <access_token>
```

**Query Parameters**
- `category` (string)
- `start_time` (string, ISO datetime)
- `end_time` (string, ISO datetime)
- `threshold` (number, 0-1)

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
                "timestamp": "string",
                "context": {
                    "text": "string",
                    "start_time": "string",
                    "end_time": "string"
                }
            }
        ]
    }
}
```

### Get Insights

```http
GET /api/v1/analysis/{analysis_id}/insights
Authorization: Bearer <access_token>
```

**Query Parameters**
- `type` (string)
- `start_time` (string, ISO datetime)
- `end_time` (string, ISO datetime)
- `threshold` (number, 0-1)

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
                "timestamp": "string",
                "related_emotions": [
                    {
                        "id": "string",
                        "name": "string"
                    }
                ],
                "related_topics": [
                    {
                        "id": "string",
                        "name": "string"
                    }
                ]
            }
        ]
    }
}
```

### Get Analysis Summary

```http
GET /api/v1/analysis/{analysis_id}/summary
Authorization: Bearer <access_token>
```

**Response**
```json
{
    "status": "success",
    "data": {
        "summary": {
            "duration": "string",
            "emotion_stats": {
                "total": 100,
                "by_category": {
                    "basic": 60,
                    "complex": 40
                },
                "top_emotions": [
                    {
                        "name": "string",
                        "count": 10,
                        "average_intensity": 0.8
                    }
                ]
            },
            "topic_stats": {
                "total": 50,
                "by_category": {
                    "personal": 30,
                    "professional": 20
                },
                "top_topics": [
                    {
                        "name": "string",
                        "count": 5,
                        "average_confidence": 0.9
                    }
                ]
            },
            "insight_stats": {
                "total": 25,
                "by_type": {
                    "pattern": 10,
                    "recommendation": 8,
                    "observation": 7
                }
            }
        }
    }
}
```

### Upload and Analyze Transcript

```http
POST /api/v1/analysis/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <transcript_file>
```

**Response**
```json
{
    "message": "Transcript analyzed successfully",
    "session_id": "string",
    "analysis_results": {
        "emotions": [
            {
                "name": "string",
                "text": "string",
                "intensity": number,
                "context": "string",
                "timestamp": "string",
                "confidence": number,
                "topics": ["string"]
            }
        ],
        "beliefs": [
            {
                "name": "string",
                "text": "string",
                "impact": number,
                "timestamp": "string",
                "confidence": number,
                "topics": ["string"]
            }
        ],
        "insights": [
            {
                "name": "string",
                "text": "string",
                "context": "string",
                "timestamp": "string",
                "confidence": number,
                "topics": ["string"]
            }
        ],
        "challenges": [
            {
                "name": "string",
                "text": "string",
                "impact": number,
                "severity": "string",
                "timestamp": "string",
                "confidence": number,
                "topics": ["string"]
            }
        ],
        "action_items": [
            {
                "name": "string",
                "text": "string",
                "priority": "string",
                "status": "string",
                "due_date": "string",
                "context": "string",
                "topics": ["string"]
            }
        ]
    }
}
```

**Error Responses**
- 400: No file provided or empty filename
- 500: Failed to process transcript or internal server error

### Save Analysis Results

```http
POST /api/v1/analysis/save/{session_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "analysis_results": {
        "emotions": [
            {
                "name": "string",
                "intensity": 0.8,
                "context": "string",
                "topics": ["string"],
                "timestamp": "string"
            }
        ],
        "beliefs": [
            {
                "name": "string",
                "text": "string",
                "impact": 0.7,
                "topics": ["string"],
                "timestamp": "string"
            }
        ],
        "insights": [
            {
                "name": "string",
                "text": "string",
                "context": "string",
                "topics": ["string"],
                "timestamp": "string"
            }
        ],
        "challenges": [
            {
                "name": "string",
                "text": "string",
                "impact": 0.6,
                "severity": "string",
                "topics": ["string"],
                "timestamp": "string"
            }
        ],
        "action_items": [
            {
                "name": "string",
                "text": "string",
                "priority": "string",
                "status": "string",
                "due_date": "string",
                "context": "string",
                "topics": ["string"]
            }
        ]
    }
}
```

**Response**
```json
{
    "message": "Analysis results saved successfully",
    "session_id": "string"
}
```

**Error Responses**
- 400: No analysis results provided
- 500: Failed to save analysis results or internal server error

### WebSocket Events

Connect to:
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/analysis/{analysis_id}/events
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
class AnalysisService {
    constructor(private authService: AuthService) {}

    async startAnalysis(sessionId: string, settings = {}) {
        return this.authService.makeAuthenticatedRequest('/analysis/start', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId, settings })
        });
    }

    async getResults(analysisId: string) {
        return this.authService.makeAuthenticatedRequest(
            `/analysis/${analysisId}/results`
        );
    }

    connectToEvents(analysisId: string, handlers: {
        onProgress: (progress: number) => void,
        onEmotion: (emotion: any) => void,
        onTopic: (topic: any) => void,
        onInsight: (insight: any) => void
    }) {
        const ws = new WebSocket(
            `ws://localhost:5000/api/v1/analysis/${analysisId}/events`
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

class AnalysisService:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def start_analysis(self, session_id: str, settings: dict = None) -> dict:
        return self.auth_service.make_authenticated_request(
            '/analysis/start',
            method='POST',
            json={
                'session_id': session_id,
                'settings': settings or {}
            }
        )

    def get_results(self, analysis_id: str) -> dict:
        return self.auth_service.make_authenticated_request(
            f'/analysis/{analysis_id}/results'
        )

    async def connect_to_events(
        self,
        analysis_id: str,
        on_progress=None,
        on_emotion=None,
        on_topic=None,
        on_insight=None
    ):
        uri = f'ws://localhost:5000/api/v1/analysis/{analysis_id}/events'
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