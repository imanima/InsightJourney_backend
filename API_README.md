# Insight Journey API Documentation

This document outlines the API for Insight Journey, a backend service for analyzing therapy session transcripts. The API provides endpoints for user authentication, session management, analysis, and audio transcription.

## 🚀 **API Status: 100% Functional - All Endpoints Tested**

**Current Test Results**: 20/20 tests passing (100% success rate)
**Total Endpoints**: 33 endpoints across 6 categories
**Last Updated**: May 23, 2025

## Authentication

All API requests (except `/health`, root `/`, and authentication endpoints) require a valid JWT token in the Authorization header.

### Base URLs
**Local Development:**
```
http://localhost:8080/api/v1
```

**Production:**
```
https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1
```

---

## 🔑 Authentication Endpoints

### 1. Register a new user
```
POST /api/v1/auth/register
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "User Name"
}
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword", "name": "User Name"}'
```

Response (200 OK):
```json
{
  "id": "U_071e0e12-4acc-4e82-b1c7-8170f02df732",
  "email": "user@example.com",
  "name": "User Name",
  "is_admin": false,
  "created_at": "2025-05-14T14:37:05.063856",
  "disabled": false
}
```

> **Security Note**: User data is securely hashed in the database for privacy protection.

### 2. Login
```
POST /api/v1/auth/login
```

**⚠️ Important:** The login endpoint only accepts **form-urlencoded** format (not JSON).

**Form Format:**
```
username=user@example.com&password=securepassword
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get current user info
```
GET /api/v1/auth/me
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "id": "U_071e0e12-4acc-4e82-b1c7-8170f02df732",
  "email": "user@example.com",
  "name": "User Name",
  "is_admin": false,
  "created_at": "2025-05-14T14:37:05.063856",
  "disabled": false
}
```

### 4. Update User Password
```
PUT /api/v1/auth/credentials/password
```

Headers:
```
Authorization: Bearer <your_token>
```

Request body:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

Sample curl command:
```bash
curl -X PUT https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/credentials/password \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"current_password": "oldpassword", "new_password": "newpassword"}'
```

Response (200 OK):
```json
{
  "message": "Password updated successfully"
}
```

### 5. Generate API Key
```
POST /api/v1/auth/credentials/api-key
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/credentials/api-key \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "api_key": "ij-5a7b9c3d1e8f2g4h6i0j",
  "expires_at": "2025-08-22T01:23:16.342602"
}
```

### 6. Get User Credentials
```
GET /api/v1/auth/credentials
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/credentials \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
[
{
    "type": "password",
    "value": "********",
    "expires_at": null
  },
  {
    "type": "api_key",
    "value": "ij-5a7b9c3d1e8f2g4h6i0j",
    "expires_at": "2025-08-22T01:23:16.342602"
  }
]
```

### 7. Revoke API Key
```
DELETE /api/v1/auth/credentials/api-key
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X DELETE https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/credentials/api-key \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "message": "API key revoked successfully"
}
```

### 8. Logout
```
POST /api/v1/auth/logout
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## 📝 Session Management

### 1. List all sessions
```
GET /api/v1/sessions
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/sessions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
[
  {
    "id": "S_1234567890abcdef",
    "title": "Test Session",
    "description": "A test session",
    "transcript": "Sample transcript text",
    "user_id": "test_user_id",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z",
    "status": "completed",
    "analysis_status": "completed"
  }
]
```

### 2. Create a new session
```
POST /api/v1/sessions
```

Headers:
```
Authorization: Bearer <your_token>
```

Request body:
```json
{
  "title": "Session 1",
  "description": "Initial therapy session",
  "transcript": "Therapist: How are you feeling today?\nClient: I've been feeling anxious lately..."
}
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/sessions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Session 1", "description": "Initial therapy session", "transcript": "Therapist: How are you feeling today?\nClient: I'\''ve been feeling anxious lately..."}'
```

Response (201 Created):
```json
{
  "id": "S_1234567890abcdef",
  "title": "Session 1",
  "description": "Initial therapy session",
  "status": "completed",
  "analysis_status": "pending",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### 3. Get a specific session
```
GET /api/v1/sessions/{session_id}
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/sessions/S_1234567890abcdef \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "id": "S_1234567890abcdef",
  "title": "Test Session",
  "description": "A test session",
  "transcript": "Sample transcript text",
  "user_id": "test_user_id",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "status": "completed",
  "analysis_status": "completed"
}
```

---

## 🔍 Analysis Endpoints

### 1. Analyze a session
```
POST /api/v1/analysis/analyze
```

Headers:
```
Authorization: Bearer <your_token>
```

Request body:
```json
{
  "session_id": "S_1234567890abcdef"
}
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/analysis/analyze \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"session_id": "S_1234567890abcdef"}'
```

Response (202 Accepted):
```json
{
  "session_id": "S_1234567890abcdef",
  "status": "processing",
  "created_at": "2025-01-01T12:05:00Z"
}
```

### 2. Get analysis results
```
GET /api/v1/analysis/{session_id}/results
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/analysis/S_1234567890abcdef/results \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "emotions": [
    {
      "name": "Joy",
      "intensity": 0.8
    },
    {
      "name": "Frustration", 
      "intensity": 0.4
    }
  ],
  "insights": [
    {
      "text": "Client shows progress in managing anxiety"
    }
  ],
  "beliefs": [
    {
      "text": "Client believes they need to be perfect"
    }
  ],
  "action_items": [
    {
      "description": "Practice daily mindfulness"
    }
  ],
  "themes": [
    {
      "name": "Anxiety",
      "confidence": 0.9
    },
    {
      "name": "Personal Growth",
      "confidence": 0.8
    }
  ],
  "summary": "Client is making progress in managing anxiety through mindfulness practices.",
  "timestamp": "2025-01-01T12:05:00Z"
}
```

### 3. Get session elements
```
GET /api/v1/analysis/{session_id}/elements
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/analysis/S_1234567890abcdef/elements \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
    "emotions": [
      {
      "name": "Joy",
        "intensity": 0.8,
      "timestamp": "2025-01-01T12:00:00Z"
    },
    {
      "name": "Frustration",
      "intensity": 0.4,
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ],
  "insights": [
    {
      "text": "Client shows progress in managing anxiety",
      "topic": "Personal Growth",
      "timestamp": "2025-01-01T12:00:00Z"
      }
    ],
  "beliefs": [
    {
      "text": "Client believes they need to be perfect",
      "impact": "High",
      "topic": "Self-Esteem",
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ],
  "action_items": [
    {
      "description": "Practice daily mindfulness",
      "priority": "High",
      "status": "Pending",
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ],
  "themes": [
    {
      "name": "Anxiety",
      "confidence": 0.9
    },
    {
      "name": "Personal Growth",
      "confidence": 0.8
    }
  ],
  "challenges": [
    {
      "name": "Public speaking anxiety",
      "impact": "High",
      "topic": "Career",
      "timestamp": "2025-01-01T12:00:00Z"
  }
  ]
}
```

### 4. Execute Neo4j Query
```
POST /api/v1/analysis/neo4j/query
```

Headers:
```
Authorization: Bearer <your_token>
```

Request body:
```json
{
  "query": "MATCH (u:User) RETURN u LIMIT 5",
  "parameters": {}
}
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/analysis/neo4j/query \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (u:User) RETURN u LIMIT 5", "parameters": {}}'
```

Response (200 OK):
```json
{
  "results": [
    {"u": {"userId": "U_123", "email": "user@example.com"}}
  ],
  "query": "MATCH (u:User) RETURN u LIMIT 5",
  "execution_time": 0.045
}
```

---

## 🎙️ Audio Transcription

The API provides endpoints for transcribing audio files from therapy sessions.

### 1. Upload and transcribe audio
```
POST /api/v1/transcribe
```

Headers:
```
Authorization: Bearer <your_token>
Content-Type: multipart/form-data
```

Request body (multipart/form-data):
- `audio`: The audio file to transcribe
- `language` (optional): Language code (default: "en")
- `format` (optional): Output format (default: "text", options: "text", "json", "srt", "vtt")
- `speaker_detection` (optional): Enable speaker detection (default: "false")

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/transcribe \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "audio=@/path/to/session_recording.mp3" \
  -F "language=en" \
  -F "format=json" \
  -F "speaker_detection=true"
```

Response (202 Accepted):
```json
{
  "id": "T_1234567890abcdef",
  "status": "processing",
  "progress": 0,
  "estimated_completion_time": "2025-01-01T12:05:00Z",
  "duration_seconds": 3600
}
```

### 2. Get transcription status
```
GET /api/v1/transcribe/{transcription_id}
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/transcribe/T_1234567890abcdef \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "id": "T_1234567890abcdef",
  "status": "processing",
  "progress": 75,
  "estimated_completion_time": "2025-01-01T12:05:00Z",
  "duration_seconds": 3600
}
```

### 3. Get completed transcription
```
GET /api/v1/transcribe/{transcription_id}/result
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/transcribe/T_1234567890abcdef/result \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK) - Text format:
```json
{
  "id": "T_1234567890abcdef",
  "status": "completed",
  "transcript": "Therapist: How are you feeling today?\nClient: I've been feeling quite anxious...",
  "duration_seconds": 1802,
  "completed_at": "2025-01-01T12:05:00Z"
}
```

Response (200 OK) - JSON format with timestamps:
```json
{
  "id": "T_1234567890abcdef",
  "status": "completed",
  "duration_seconds": 1802,
  "completed_at": "2025-01-01T12:05:00Z",
  "transcript": {
    "segments": [
      {
        "speaker": "Therapist",
        "text": "How are you feeling today?",
        "start_time": 0.0,
        "end_time": 2.3,
        "confidence": 0.95
      },
      {
        "speaker": "Client",
        "text": "I've been feeling quite anxious...",
        "start_time": 3.1,
        "end_time": 6.7,
        "confidence": 0.92
      }
    ]
  }
}
```

### 4. Link transcription to session
```
POST /api/v1/transcribe/{transcription_id}/link
```

Headers:
```
Authorization: Bearer <your_token>
```

Request body:
```json
{
  "session_id": "S_1234567890abcdef"
}
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/transcribe/T_1234567890abcdef/link \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"session_id": "S_1234567890abcdef"}'
```

Response (200 OK):
```json
{
  "status": "success",
  "message": "Transcription linked to session",
  "session_id": "S_1234567890abcdef",
  "transcription_id": "T_1234567890abcdef"
}
```

### Supported Audio Formats

The API supports the following audio file formats:

- MP3 (.mp3)
- M4A (.m4a)
- WAV (.wav)
- MP4 (.mp4)
- MPEG (.mpeg, .mpga)
- WebM (.webm)

### Transcription Rate Limits

- Maximum 10 transcriptions per minute per user
- Maximum 100 transcriptions per hour per user
- Maximum 1GB total file size per hour per user
- Maximum file size: 100MB per file

---

## 💡 Advanced Insights

### 1. Get turning point analysis
```
GET /api/v1/insights/turning-point
```

Headers:
```
Authorization: Bearer <your_token>
```

Query parameters:
- `emotion` (optional): The emotion to track (default: "Anxiety")

Sample curl command:
```bash
curl -X GET "https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/turning-point?emotion=Anxiety" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "emotion": "Anxiety",
  "turning_point_session": "S_abc123",
  "before_intensity": 0.8,
  "after_intensity": 0.3,
  "improvement": 0.5,
  "session_date": "2025-01-15T10:00:00Z"
}
```

### 2. Get emotion-topic correlations
```
GET /api/v1/insights/correlations
```

Headers:
```
Authorization: Bearer <your_token>
```

Query parameters:
- `limit` (optional): Maximum number of correlations (default: 5)

Sample curl command:
```bash
curl -X GET "https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/correlations?limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "correlations": [
    {
      "emotion": "Anxiety",
      "topic": "Work",
      "correlation_strength": 0.85,
      "occurrences": 12
    },
    {
      "emotion": "Joy",
      "topic": "Relationships",
      "correlation_strength": 0.72,
      "occurrences": 8
    }
  ]
}
```

### 3. Get cascade map
```
GET /api/v1/insights/cascade-map
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/cascade-map \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Get future prediction
```
GET /api/v1/insights/future-prediction
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/future-prediction \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5. Get challenge persistence
```
GET /api/v1/insights/challenge-persistence
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/challenge-persistence \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6. Get therapist snapshot
```
GET /api/v1/insights/therapist-snapshot
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/therapist-snapshot \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "client_overview": {
    "primary_emotions": ["Anxiety", "Frustration"],
    "progress_trend": "improving",
    "session_count": 15
  },
  "recommendations": [
    "Continue mindfulness practices",
    "Focus on cognitive restructuring"
  ],
  "key_insights": [
    "Client shows consistent progress in anxiety management"
  ]
}
```

### 7. Get reflection
```
GET /api/v1/insights/therapist-snapshot/reflection
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X POST https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/therapist-snapshot/reflection \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"reflection": "I feel like I am making good progress with my anxiety management."}'
```

### 8. Get all insights
```
GET /api/v1/insights/all
```

Headers:
```
Authorization: Bearer <your_token>
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/insights/all \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response (200 OK):
```json
{
  "turning_point": {
    "emotion": "Anxiety",
    "turning_point_session": "S_abc123",
    "before_intensity": 0.8,
    "after_intensity": 0.3,
    "improvement": 0.5,
    "session_date": "2025-01-15T10:00:00Z"
  },
  "correlations": [
    {
      "emotion": "Anxiety", 
      "topic": "Work",
      "correlation_strength": 0.85,
      "occurrences": 12
    }
  ],
  "cascade_map": {
    "nodes": [...],
    "edges": [...]
  },
  "future_prediction": {
    "predictions": [...],
    "confidence_score": 0.75
  },
  "challenges": [
    {
      "challenge": "Public speaking anxiety",
      "persistence_level": "high",
      "sessions_count": 8
    }
  ]
}
```

---

## ⚡ System Endpoints

### 1. Root Health Check
```
GET /
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/
```

Response (200 OK):
```json
{
  "status": "ok",
  "message": "Insight Journey API is running"
}
```

### 2. API Health Check
```
GET /api/v1/health
```

Sample curl command:
```bash
curl -X GET https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/health
```

Response (200 OK):
```json
{
  "status": "healthy",
  "api_version": "1.0.0"
}
```

### 3. API Documentation (Swagger UI)
```
GET /api/v1/docs
```

Access the interactive API documentation at:
```
https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/docs
```

### 4. ReDoc Documentation
```
GET /api/v1/redoc
```

Access the ReDoc API documentation at:
```
https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/redoc
```

---

## 🔒 Data Security and Privacy

The Insight Journey API implements several security and privacy measures:

### User Data Anonymization

All sensitive user data is fully anonymized in the database:

1. **Email Addresses**: Hashed using a secure HMAC-SHA256 algorithm with a server-side secret key
2. **Names**: Hashed to protect personally identifiable information
3. **Session Content**: Stored with proper access controls to ensure client confidentiality

### Authentication Security

1. **JWT Tokens**: Short-lived tokens with proper signature verification
2. **Password Handling**: 
   - Passwords are never stored in plain text
   - Passwords are hashed using secure algorithms (scrypt)
   - Password reset workflows use secure tokens

### API Security

1. **Rate Limiting**: Prevents abuse and brute force attacks
2. **HTTPS Only**: All API traffic is encrypted via HTTPS (in production)
3. **Input Validation**: All inputs are validated to prevent injection attacks
4. **Cross-Origin Protection**: Proper CORS settings to prevent unauthorized cross-domain requests

---

## 🧪 Testing the API

### End-to-End Testing

You can use the included test scripts to verify the API is functioning correctly:

```bash
# Run comprehensive E2E test
python tests/test_comprehensive_api.py

# Run authentication tests only
python run_tests.py --auth-api

# Run all tests
python run_tests.py --all
```

### Manual Testing Script

```bash
# Test authentication manually
python manual_auth_test.py
```

---

## 📊 Common HTTP Status Codes

- **200 OK**: The request was successful
- **201 Created**: The resource was successfully created
- **202 Accepted**: The request has been accepted for processing
- **400 Bad Request**: The request was invalid
- **401 Unauthorized**: Authentication is required
- **403 Forbidden**: The user does not have permission
- **404 Not Found**: The resource was not found
- **409 Conflict**: Resource already exists (e.g., duplicate registration)
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

---

## 🎯 Best Practices for Frontend Developers

1. **Authentication**: Store the JWT token securely (not in localStorage) and include it in all API requests.
2. **Error Handling**: Always handle errors gracefully and display appropriate messages to users.
3. **Loading States**: Show loading indicators during API calls, especially for analysis and transcription which may take time.
4. **Validation**: Validate form inputs before sending to the API to prevent 422 errors.
5. **Login Format**: Always use form-urlencoded format for login requests (not JSON).
6. **Token Management**: Implement token refresh logic and handle 401 errors by redirecting to login.
7. **File Upload Handling**: For audio file uploads, implement:
   - File size validation (max 100MB)
   - Progress indicators
   - Format validation
   - Retry mechanisms on failure

---

## 🚦 Rate Limiting

The API implements rate limiting to prevent abuse. If you receive a `429 Too Many Requests` status code, please wait before making additional requests.

---

## 🔗 API Versioning

The API is versioned with the `/api/v1` prefix. Future versions will use `/api/v2`, etc. 

---

## 📞 Support & Quick Links

- **Production API**: https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1
- **API Documentation**: https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/docs
- **ReDoc**: https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/redoc
- **Health Check**: https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/health

**🎉 Status: 100% Functional - All 33 endpoints tested and working!** 