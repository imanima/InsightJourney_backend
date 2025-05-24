# Frontend Integration Guide

This document describes how to integrate a frontend application with the Insight Journey API.

## Overview

The Insight Journey API provides a RESTful interface for frontend applications to:
1. Manage user authentication
2. Create and manage sessions
3. Upload and analyze content
4. Retrieve analysis results in real-time

## Base URL
```
https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1
```

## API Test Results

### Authentication Endpoints
✅ Registration: Successfully tested
- Endpoint: `POST /auth/register`
- Request body: `{ email, password, name }`
- Response: 201 Created with user details

✅ Login: Successfully tested
- Endpoint: `POST /auth/login`
- Request body: `{ email, password }`
- Response: 200 OK with access token

### Session Management
✅ Create Session: Successfully tested
- Endpoint: `POST /sessions`
- Request body: `{ title, date, description, duration, status, analysis_status }`
- Response: 201 Created with session ID

✅ Get Session: Successfully tested
- Endpoint: `GET /sessions/{session_id}`
- Response: 200 OK with session details

✅ List Sessions: Successfully tested
- Endpoint: `GET /sessions`
- Response: 200 OK with array of sessions

### Analysis Endpoints
✅ Direct Analysis: Successfully tested
- Endpoint: `POST /analysis/direct`
- Request body: `{ transcript }`
- Response: 200 OK with analysis results

✅ File Upload Analysis: Successfully tested
- Endpoint: `POST /analysis/upload`
- Request: multipart/form-data with file
- Response: 200 OK with analysis results

### Action Items
✅ Create Action Item: Successfully tested
- Endpoint: `POST /sessions/{session_id}/action-items`
- Request body: `{ title, description, due_date, priority, status }`
- Response: 201 Created with action item ID

✅ Get Action Items: Successfully tested
- Endpoint: `GET /sessions/{session_id}/action-items`
- Response: 200 OK with array of action items

✅ Update Action Item: Successfully tested
- Endpoint: `PUT /sessions/{session_id}/action-items/{action_item_id}`
- Request body: `{ status, notes }`
- Response: 200 OK with updated action item

✅ Delete Action Item: Successfully tested
- Endpoint: `DELETE /sessions/{session_id}/action-items/{action_item_id}`
- Response: 200 OK

### User Management
✅ Get User Profile: Successfully tested
- Endpoint: `GET /users/me`
- Response: 200 OK with user profile

✅ Update User Settings: Successfully tested
- Endpoint: `PUT /users/me/settings`
- Request body: `{ analysis_prompt_template, notification_preferences }`
- Response: 200 OK with updated settings

## Authentication

### User Registration

```typescript
async function registerUser(
    username: string,
    email: string,
    password: string
): Promise<User> {
    const response = await fetch('https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
    });

    const data = await response.json();
    if (data.status === 'success') {
        localStorage.setItem('access_token', data.data.access_token);
        // Store refresh token in HTTP-only cookie
        return data.data.user;
    }
    throw new Error(data.message);
}
```

### User Login

```typescript
async function login(email: string, password: string): Promise<User> {
    const response = await fetch('https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (data.status === 'success') {
        localStorage.setItem('access_token', data.data.access_token);
        // Store refresh token in HTTP-only cookie
        return data.data.user;
    }
    throw new Error(data.message);
}
```

### Token Refresh

```typescript
async function refreshToken(): Promise<void> {
    const response = await fetch('https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include' // Include cookies
    });

    const data = await response.json();
    if (data.status === 'success') {
        localStorage.setItem('access_token', data.data.access_token);
    } else {
        // Token refresh failed, redirect to login
        window.location.href = '/login';
    }
}
```

### API Client

```typescript
class ApiClient {
    private baseUrl = 'https://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1';
    private accessToken: string | null = null;

    constructor() {
        this.accessToken = localStorage.getItem('access_token');
    }

    private async request(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<any> {
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.accessToken}`
        };

        try {
            const response = await fetch(
                `${this.baseUrl}${endpoint}`,
                { ...options, headers }
            );

            if (response.status === 401) {
                await refreshToken();
                return this.request(endpoint, options);
            }

            const data = await response.json();
            if (data.status === 'success') {
                return data.data;
            }
            throw new Error(data.message);
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
}
```

## Session Management

### Create Session

```typescript
class SessionService extends ApiClient {
    async createSession(
        title: string,
        description: string
    ): Promise<Session> {
        return this.request('/sessions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description })
        });
    }

    async uploadContent(
        sessionId: string,
        file: File
    ): Promise<Upload> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', file.type.split('/')[0]);

        return this.request(`/sessions/${sessionId}/content`, {
            method: 'POST',
            body: formData
        });
    }

    async getAnalysisStatus(
        sessionId: string
    ): Promise<AnalysisStatus> {
        return this.request(
            `/sessions/${sessionId}/analysis/status`
        );
    }
}
```

## Real-time Updates

### WebSocket Connection

```typescript
class WebSocketClient {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;

    constructor(
        private sessionId: string,
        private handlers: {
            onProgress: (progress: number) => void;
            onEmotion: (emotion: Emotion) => void;
            onTopic: (topic: Topic) => void;
            onInsight: (insight: Insight) => void;
            onError: (error: Error) => void;
        }
    ) {}

    connect() {
        this.ws = new WebSocket(
            `wss://insight-journey-backend-a47jf6g6sa-uc.a.run.app/api/v1/sessions/${this.sessionId}/events`
        );

        this.ws.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);
            switch (type) {
                case 'analysis_progress':
                    this.handlers.onProgress(data.progress);
                    break;
                case 'new_emotion':
                    this.handlers.onEmotion(data.emotion);
                    break;
                case 'new_topic':
                    this.handlers.onTopic(data.topic);
                    break;
                case 'new_insight':
                    this.handlers.onInsight(data.insight);
                    break;
            }
        };

        this.ws.onclose = () => {
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
            }
        };

        this.ws.onerror = (error) => {
            this.handlers.onError(error);
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
```

## React Integration

### Authentication Context

```typescript
interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = React.createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);

    const login = async (email: string, password: string) => {
        const user = await loginUser(email, password);
        setUser(user);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
    };

    const value = { user, login, logout, isAuthenticated: !!user };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}
```

### Session Component

```typescript
function SessionView({ sessionId }: { sessionId: string }) {
    const [session, setSession] = useState<Session | null>(null);
    const [emotions, setEmotions] = useState<Emotion[]>([]);
    const [topics, setTopics] = useState<Topic[]>([]);
    const [insights, setInsights] = useState<Insight[]>([]);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const sessionService = new SessionService();
        sessionService.getSession(sessionId).then(setSession);

        const wsClient = new WebSocketClient(sessionId, {
            onProgress: setProgress,
            onEmotion: (emotion) => {
                setEmotions(prev => [...prev, emotion]);
            },
            onTopic: (topic) => {
                setTopics(prev => [...prev, topic]);
            },
            onInsight: (insight) => {
                setInsights(prev => [...prev, insight]);
            },
            onError: (error) => {
                console.error('WebSocket error:', error);
            }
        });

        wsClient.connect();
        return () => wsClient.disconnect();
    }, [sessionId]);

    return (
        <div>
            <h1>{session?.title}</h1>
            <ProgressBar value={progress} />
            <EmotionList emotions={emotions} />
            <TopicList topics={topics} />
            <InsightList insights={insights} />
        </div>
    );
}
```

### File Upload Component

```typescript
function FileUpload({ sessionId }: { sessionId: string }) {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploading(true);
        try {
            const sessionService = new SessionService();
            await sessionService.uploadContent(sessionId, file);
        } catch (error) {
            console.error('Upload failed:', error);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <input
                type="file"
                onChange={handleUpload}
                disabled={uploading}
            />
            {uploading && <ProgressBar value={progress} />}
        </div>
    );
}
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

## Example Usage

### Complete Integration Example

```typescript
function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route
                        path="/sessions"
                        element={
                            <ProtectedRoute>
                                <SessionList />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/sessions/:id"
                        element={
                            <ProtectedRoute>
                                <SessionView />
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/sessions');
        } catch (error) {
            handleApiError(error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
            />
            <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
            />
            <button type="submit">Login</button>
        </form>
    );
}

function SessionList() {
    const [sessions, setSessions] = useState<Session[]>([]);

    useEffect(() => {
        const sessionService = new SessionService();
        sessionService.listSessions().then(setSessions);
    }, []);

    return (
        <div>
            {sessions.map(session => (
                <Link key={session.id} to={`/sessions/${session.id}`}>
                    {session.title}
                </Link>
            ))}
        </div>
    );
}
```

## Analysis Service Status

### Check Analysis Service Availability
✅ Service Status: Successfully tested
- Endpoint: `GET /analysis/status`
- Response: 200 OK with service status
```json
{
    "status": "available",
    "version": "1.0.0",
    "last_checked": "2024-04-22T00:00:00Z"
}
```

### Error States
- When analysis service is unavailable:
```json
{
    "status": "unavailable",
    "error": "Analysis service not available",
    "details": "Service is currently down for maintenance"
}
```

## Health Checks

### System Health
✅ Health Check: Successfully tested
- Endpoint: `GET /health`
- Response: 200 OK with system status
```json
{
    "status": "healthy",
    "services": {
        "api": "up",
        "database": "up",
        "analysis": "up",
        "websocket": "up"
    },
    "version": "1.0.0",
    "timestamp": "2024-04-22T00:00:00Z"
}
```

### Component Health
✅ Component Health: Successfully tested
- Endpoint: `GET /health/components`
- Response: 200 OK with detailed component status
```json
{
    "components": {
        "neo4j": {
            "status": "up",
            "version": "4.4.0",
            "response_time": "50ms"
        },
        "redis": {
            "status": "up",
            "version": "6.2.0",
            "memory_usage": "45%"
        },
        "celery": {
            "status": "up",
            "workers": 4,
            "tasks_queued": 0
        }
    }
}
```

## Detailed Error Responses

### Authentication Errors
```json
{
    "error": "authentication_error",
    "code": "AUTH_001",
    "message": "Invalid credentials",
    "details": "The provided email or password is incorrect"
}
```

### Validation Errors
```json
{
    "error": "validation_error",
    "code": "VAL_001",
    "message": "Invalid input",
    "details": {
        "email": ["Must be a valid email address"],
        "password": ["Must be at least 8 characters"]
    }
}
```

### Rate Limit Errors
```json
{
    "error": "rate_limit_exceeded",
    "code": "RATE_001",
    "message": "Too many requests",
    "details": {
        "limit": 100,
        "remaining": 0,
        "reset": "2024-04-22T00:05:00Z"
    }
}
```

### Service Errors
```json
{
    "error": "service_error",
    "code": "SVC_001",
    "message": "Analysis service unavailable",
    "details": "The analysis service is currently down for maintenance"
}
```

## WebSocket Events

### Connection
```typescript
interface WebSocketConnection {
    url: string;
    protocols?: string[];
    headers: {
        Authorization: string;
    };
}
```

### Event Types and Payloads

#### Analysis Progress
```typescript
interface AnalysisProgressEvent {
    type: 'analysis_progress';
    data: {
        progress: number;
        stage: 'transcription' | 'analysis' | 'extraction';
        message: string;
    };
}
```

#### Emotion Detection
```typescript
interface EmotionEvent {
    type: 'new_emotion';
    data: {
        emotion: string;
        intensity: number;
        timestamp: string;
        context: string;
    };
}
```

#### Topic Detection
```typescript
interface TopicEvent {
    type: 'new_topic';
    data: {
        topic: string;
        confidence: number;
        timestamp: string;
        context: string;
    };
}
```

#### Insight Generation
```typescript
interface InsightEvent {
    type: 'new_insight';
    data: {
        insight: string;
        category: string;
        confidence: number;
        timestamp: string;
    };
}
```

#### Error Events
```typescript
interface ErrorEvent {
    type: 'error';
    data: {
        code: string;
        message: string;
        details?: string;
    };
}
```

### WebSocket Error Handling
```typescript
interface WebSocketErrorHandlers {
    onConnectionError: (error: Error) => void;
    onMessageError: (error: Error) => void;
    onReconnect: (attempt: number) => void;
    onClose: (code: number, reason: string) => void;
}
``` 