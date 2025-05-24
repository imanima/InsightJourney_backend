# Insight Journey API Documentation

## Base URL
```
https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1
```

## Authentication

### Register User
```http
POST /auth/register
```

Request body:
```json
{
  "email": "string",
  "password": "string",
  "name": "string"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "string",
      "email": "string",
      "name": "string"
    },
    "access_token": "string",
    "refresh_token": "string"
  }
}
```

### Login
```http
POST /auth/login
```

Request body:
```json
{
  "email": "string",
  "password": "string"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "access_token": "string",
    "refresh_token": "string"
  }
}
```

### Logout
```http
POST /auth/logout
```

Response:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

## Sessions

### Create Session
```http
POST /sessions
```

Request body:
```json
{
  "title": "string",
  "description": "string",
  "duration": number,
  "status": "string",
  "analysis_status": "string"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "session": {
      "id": "string",
      "title": "string",
      "description": "string",
      "duration": number,
      "status": "string",
      "analysis_status": "string",
      "created_at": "string",
      "updated_at": "string"
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
  "status": "success",
  "data": {
    "session": {
      "id": "string",
      "title": "string",
      "description": "string",
      "duration": number,
      "status": "string",
      "analysis_status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  }
}
```

### List Sessions
```http
GET /sessions
```

Query Parameters:
- `page` (integer, default: 1)
- `per_page` (integer, default: 10)
- `sort` (string, options: created_at, updated_at)
- `order` (string, options: asc, desc)

Response:
```json
{
  "status": "success",
  "data": {
    "sessions": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "duration": number,
        "status": "string",
        "analysis_status": "string",
        "created_at": "string",
        "updated_at": "string"
      }
    ],
    "pagination": {
      "page": number,
      "per_page": number,
      "total": number,
      "pages": number
    }
  }
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
  "status": "success",
  "message": "Session updated successfully"
}
```

### Delete Session
```http
DELETE /sessions/{session_id}
```

Response:
```json
{
  "status": "success",
  "message": "Session deleted successfully"
}
```

## Analysis

### Start Analysis
```http
POST /analysis/start
```

Request body:
```json
{
  "session_id": "string",
  "transcript": "string"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "analysis_id": "string",
    "status": "string",
    "progress": number
  }
}
```

### Get Analysis Status
```http
GET /analysis/{analysis_id}/status
```

Response:
```json
{
  "status": "success",
  "data": {
    "status": "string",
    "progress": number,
    "result": {
      "emotions": [],
      "topics": [],
      "insights": []
    }
  }
}
```

### Get Analysis Results
```http
GET /analysis/{analysis_id}/results
```

Response:
```json
{
  "status": "success",
  "data": {
    "emotions": [
      {
        "id": "string",
        "name": "string",
        "intensity": number,
        "context": "string",
        "topics": ["string"],
        "timestamp": "string"
      }
    ],
    "beliefs": [
      {
        "id": "string",
        "name": "string",
        "text": "string",
        "impact": number,
        "topics": ["string"],
        "timestamp": "string"
      }
    ],
    "insights": [
      {
        "id": "string",
        "name": "string",
        "text": "string",
        "context": "string",
        "topics": ["string"],
        "timestamp": "string"
      }
    ],
    "challenges": [
      {
        "id": "string",
        "name": "string",
        "text": "string",
        "impact": number,
        "severity": "string",
        "topics": ["string"],
        "timestamp": "string"
      }
    ],
    "action_items": [
      {
        "id": "string",
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

## Action Items

### Create Action Item
```http
POST /action-items
```

Request body:
```json
{
  "session_id": "string",
  "title": "string",
  "description": "string",
  "status": "string",
  "priority": "string",
  "due_date": "string"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "action_item": {
      "id": "string",
      "session_id": "string",
      "title": "string",
      "description": "string",
      "status": "string",
      "priority": "string",
      "due_date": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  }
}
```

### Get Action Item
```http
GET /action-items/{action_item_id}
```

Response:
```json
{
  "status": "success",
  "data": {
    "action_item": {
      "id": "string",
      "session_id": "string",
      "title": "string",
      "description": "string",
      "status": "string",
      "priority": "string",
      "due_date": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  }
}
```

### Update Action Item
```http
PUT /action-items/{action_item_id}
```

Request body:
```json
{
  "title": "string",
  "description": "string",
  "status": "string",
  "priority": "string",
  "due_date": "string"
}
```

Response:
```json
{
  "status": "success",
  "message": "Action item updated successfully"
}
```

### Delete Action Item
```http
DELETE /action-items/{action_item_id}
```

Response:
```json
{
  "status": "success",
  "message": "Action item deleted successfully"
}
```

## Health Checks

### System Health
```http
GET /health
```

Response:
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "services": {
      "api": "up",
      "database": "up",
      "analysis": "up",
      "websocket": "up"
    },
    "version": "string",
    "timestamp": "string"
  }
}
```

### Component Health
```http
GET /health/components
```

Response:
```json
{
  "status": "success",
  "data": {
    "components": {
      "neo4j": {
        "status": "up",
        "version": "string",
        "response_time": "string"
      },
      "redis": {
        "status": "up",
        "version": "string",
        "memory_usage": "string"
      },
      "celery": {
        "status": "up",
        "workers": number,
        "tasks_queued": number
      }
    }
  }
}
```

## WebSocket Events

### Connection URL
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/sessions/{session_id}/events
```

### Event Types

1. **Analysis Progress**
```json
{
  "type": "analysis_progress",
  "data": {
    "status": "string",
    "progress": number
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
      "intensity": number,
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
      "confidence": number,
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

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "status": "error",
  "error": "validation_error",
  "message": "Invalid input",
  "details": {
    "field": ["error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "error": "authentication_error",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "error": "authorization_error",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "error": "not_found",
  "message": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "status": "error",
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "details": {
    "limit": number,
    "remaining": number,
    "reset": "string"
  }
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "error": "internal_error",
  "message": "Internal server error"
}
```

## Rate Limiting

- Authentication endpoints: 10 requests per minute
- Session endpoints: 100 requests per minute
- Analysis endpoints: 5 requests per minute
- Action item endpoints: 50 requests per minute

Rate limit headers included in responses:
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time until limit resets

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

## Taxonomy

### Get Taxonomy
```http
GET /taxonomy/{type}
```

Query Parameters:
- `type` (string, options: emotions, topics)

Response:
```json
{
  "status": "success",
  "data": {
    "taxonomy": {
      "type": "string",
      "elements": [
        {
          "id": "string",
          "name": "string",
          "level": number,
          "parent_id": "string",
          "description": "string",
          "created_at": "string",
          "updated_at": "string"
        }
      ]
    }
  }
}
```

## Pattern Analysis

### Get Session Patterns
```http
GET /sessions/{session_id}/patterns
```

Response:
```json
{
  "status": "success",
  "data": {
    "patterns": [
      {
        "type": "string",
        "description": "string",
        "confidence": number,
        "elements": [
          {
            "id": "string",
            "type": "string",
            "properties": {}
          }
        ],
        "created_at": "string"
      }
    ]
  }
}
```

## Progress Tracking

### Get User Progress
```http
GET /users/{user_id}/progress
```

Response:
```json
{
  "status": "success",
  "data": {
    "total_sessions": number,
    "completed_actions": number,
    "growth_score": number,
    "patterns": [
      {
        "type": "string",
        "description": "string",
        "trend": "string"
      }
    ],
    "created_at": "string",
    "updated_at": "string"
  }
}
```

## Neo4j Integration

### Get Graph Analysis
```http
GET /analysis/{session_id}/graph
```

Response:
```json
{
  "status": "success",
  "data": {
    "nodes": [
      {
        "id": "string",
        "type": "string",
        "properties": {}
      }
    ],
    "relationships": [
      {
        "source": "string",
        "target": "string",
        "type": "string",
        "properties": {
          "context": "string",
          "confidence": number,
          "modified_by": "string",
          "created_at": "string",
          "updated_at": "string"
        }
      }
    ]
  }
}
```

### Export to Neo4j
```http
POST /analysis/{session_id}/export
```

Response:
```json
{
  "status": "success",
  "data": {
    "export": {
      "id": "string",
      "session_id": "string",
      "status": "string",
      "nodes_created": number,
      "relationships_created": number,
      "created_at": "string"
    }
  }
}
```

### Run Neo4j Query
```http
POST /analysis/neo4j/query
```

Request body:
```json
{
  "query": "string",
  "parameters": {}
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "results": []
  }
}
```

## WebSocket Events

### Analysis Status
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/analysis/{analysis_id}/events
```

Events:
```json
{
  "type": "status_update",
  "data": {
    "status": "string",
    "progress": number
  }
}
```

### Pattern Detection
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/sessions/{session_id}/patterns/events
```

Events:
```json
{
  "type": "pattern_detected",
  "data": {
    "pattern": {
      "type": "string",
      "description": "string",
      "confidence": number
    }
  }
}
```

### Action Item Updates
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/action-items/{action_item_id}/events
```

Events:
```json
{
  "type": "status_change",
  "data": {
    "status": "string",
    "completed_at": "string"
  }
} 