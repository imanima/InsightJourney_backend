# Action Items

## Create Action Item
```http
POST /sessions/{session_id}/action_items
```
```json
{
    "name": "Practice presentation",
    "description": "Rehearse presentation multiple times",
    "topic": "Career",
    "priority": "high",
    "due_date": "2024-04-01T00:00:00Z",
    "context": "Work presentation preparation",
    "confidence": 0.85,
    "timestamp": "2024-03-20T14:50:00Z"
}
```

## Update Action Item
```http
PUT /sessions/{session_id}/action_items/{action_item_id}
```
```json
{
    "status": "completed",
    "priority": "high",
    "completed_at": "2024-03-25T15:30:00Z",
    "context": "Updated after successful presentation",
    "modified_by": "user_id"
}
```

## List Action Items
```http
GET /sessions/{session_id}/action_items
```
Response:
```json
{
    "action_items": [
        {
            "id": "action_item_id",
            "name": "Practice presentation",
            "description": "Rehearse presentation multiple times",
            "status": "pending",
            "priority": "high",
            "topic": "Career",
            "context": "Work presentation preparation",
            "confidence": 0.85,
            "due_date": "2024-04-01T00:00:00Z",
            "completed_at": null,
            "created_at": "2024-03-20T14:50:00Z",
            "updated_at": "2024-03-20T14:50:00Z",
            "modified_by": "user_id"
        }
    ]
}
```

## Base URL

All API endpoints are relative to:
```
https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1
```

## Endpoints

### Get Action Item

```http
GET /action-items/{action_item_id}
```

Response:
```json
{
  "action_item_id": "string",
  "session_id": "string",
  "title": "string",
  "description": "string",
  "status": "string",
  "priority": "string",
  "topic": "string",
  "context": "string",
  "confidence": number,
  "due_date": "string",
  "completed_at": "string",
  "created_at": "string",
  "updated_at": "string",
  "modified_by": "string"
}
```

### Delete Action Item

```http
DELETE /action-items/{action_item_id}
```

Response:
```json
{
  "status": "string",
  "message": "string"
}
```

### WebSocket Events

Connect to:
```
wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/action-items/{action_item_id}/events
```

Events:
```json
{
  "type": "status_change",
  "data": {
    "status": "string",
    "completed_at": "string",
    "modified_by": "string"
  }
}
```

### Error Responses

- 400: Bad Request
  - Invalid action item data
  - Missing required fields
- 401: Unauthorized
- 403: Forbidden
- 404: Action item not found
- 429: Too Many Requests
- 500: Internal Server Error

### Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user 