# Integration Guide

This document provides a comprehensive guide for integrating with the Insight Journey platform, covering both frontend and backend integration.

## Overview

The Insight Journey platform provides multiple integration points:
1. RESTful API endpoints
2. WebSocket events for real-time updates
3. Message queue integration
4. Database access

## Authentication

### JWT Token Management

```typescript
// Frontend
class AuthService {
    private baseUrl = 'http://localhost:5000/api/v1';
    private accessToken: string | null = null;

    async login(email: string, password: string) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (data.status === 'success') {
            this.accessToken = data.data.access_token;
        }
        return data;
    }
}

// Backend
class InsightJourneyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None

    def login(self, email: str, password: str) -> dict:
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        if data['status'] == 'success':
            self.access_token = data['data']['access_token']
        return data
```

## Session Management

### Create and Manage Sessions

```typescript
// Frontend
class SessionService {
    async createSession(title: string, description: string) {
        return this.request('/sessions', {
            method: 'POST',
            body: JSON.stringify({ title, description })
        });
    }

    async uploadContent(sessionId: string, file: File) {
        const formData = new FormData();
        formData.append('file', file);
        return this.request(`/sessions/${sessionId}/content`, {
            method: 'POST',
            body: formData
        });
    }
}

// Backend
class SessionClient:
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
```

## Real-time Updates

### WebSocket Integration

```typescript
// Frontend
class WebSocketClient {
    constructor(private sessionId: string) {
        this.ws = new WebSocket(
            `ws://localhost:5000/api/v1/sessions/${sessionId}/events`
        );
    }

    onMessage(handler: (event: any) => void) {
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handler(data);
        };
    }
}

// Backend
class WebSocketClient:
    def __init__(self, session_id: str, access_token: str):
        self.uri = f'ws://localhost:5000/api/v1/sessions/{session_id}/events'
        self.handlers = {}

    async def connect(self):
        async with websockets.connect(self.uri) as ws:
            while True:
                message = await ws.recv()
                event = json.loads(message)
                await self.handle_event(event)
```

## Analysis Pipeline

### Message Queue Integration

```python
# Backend
celery = Celery(
    'insight_journey',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2'
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
```

## Database Integration

### Neo4j Integration

```python
# Backend
class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def create_session_node(self, session_data: Dict[str, Any]):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_session_node,
                session_data
            )
```

## Complete Integration Example

### Frontend (React)

```typescript
function SessionView({ sessionId }: { sessionId: string }) {
    const [session, setSession] = useState<Session | null>(null);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const sessionService = new SessionService();
        sessionService.getSession(sessionId).then(setSession);

        const wsClient = new WebSocketClient(sessionId);
        wsClient.onMessage((event) => {
            if (event.type === 'analysis_progress') {
                setProgress(event.data.progress);
            }
        });
    }, [sessionId]);

    return (
        <div>
            <h1>{session?.title}</h1>
            <ProgressBar value={progress} />
        </div>
    );
}
```

### Backend (Python)

```python
class InsightJourneyIntegration:
    def __init__(self, api_url: str, neo4j_uri: str):
        self.api_client = InsightJourneyClient(api_url)
        self.neo4j_client = Neo4jClient(neo4j_uri)

    async def process_session(self, title: str, content_path: str):
        # Create session
        session_data = self.api_client.create_session(title)
        session_id = session_data['data']['session']['id']

        # Store in Neo4j
        self.neo4j_client.create_session_node(session_data['data']['session'])

        # Upload content
        self.api_client.upload_content(session_id, content_path)

        # Start analysis
        task = start_analysis_pipeline(session_id)
        return task.get()
```

## Best Practices

1. **Authentication**
   - Store access tokens securely
   - Implement token refresh mechanism
   - Handle authentication errors gracefully

2. **Session Management**
   - Validate session data before processing
   - Implement proper error handling
   - Use appropriate file upload limits

3. **Real-time Updates**
   - Implement reconnection logic
   - Handle connection errors
   - Clean up resources on disconnect

4. **Database Integration**
   - Use connection pooling
   - Implement proper error handling
   - Clean up resources after use

5. **Error Handling**
   - Implement comprehensive error handling
   - Provide meaningful error messages
   - Log errors appropriately

## Common Issues and Solutions

1. **Authentication Failures**
   - Check token expiration
   - Verify token format
   - Ensure proper headers

2. **Connection Issues**
   - Check network connectivity
   - Verify server status
   - Implement retry logic

3. **Performance Issues**
   - Use connection pooling
   - Implement caching
   - Optimize queries

4. **Data Consistency**
   - Use transactions
   - Implement proper error handling
   - Validate data before processing 