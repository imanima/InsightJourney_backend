# Insight Journey API

## Overview
RESTful API for therapy session analysis and management.

## Base URL
```
http://localhost:8080/api/v1
```

## Quick Start
1. Register: `POST /auth/register`
2. Login: `POST /auth/login`
3. Create Session: `POST /sessions`
4. Analyze: `POST /sessions/{id}/analyze`
5. Get Results: `GET /sessions/{id}/analysis`

## Authentication
```http
Authorization: Bearer <token>
```

## Response Format
```json
{
    "status": "success",
    "data": { ... },
    "message": "Optional message"
}
```

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error

## Documentation
- [Authentication](authentication.md)
- [Sessions](sessions.md)
- [Analysis](analysis.md)
- [Action Items](action_items.md)
- [Transcription](transcription.md)

## Table of Contents

1. [Authentication](authentication.md)
2. [Users](users.md)
3. [Sessions](sessions.md)
4. [Analysis](analysis.md)
5. [Emotions](emotions.md)
6. [Topics](topics.md)
7. [Insights](insights.md)

## Response Format

All responses follow this format:
```json
{
    "status": "success",
    "data": {
        // Response data
    },
    "message": "Optional message"
}
```

Error responses:
```json
{
    "status": "error",
    "message": "Error message",
    "errors": [
        // Detailed error information
    ]
}
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per user

## Versioning

The API is versioned in the URL path. Current version: v1

## Pagination

Endpoints that return lists support pagination:
```
?page=1&per_page=10
```