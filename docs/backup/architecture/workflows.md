# Core System Workflows

This document describes the core workflows in the Insight Journey platform.

## User Management

### Registration Flow
```mermaid
sequenceDiagram
    Client->>API: POST /api/v1/auth/register
    API->>Validation: Validate Input
    Validation->>Database: Check Existing User
    Database-->>Validation: User Status
    Validation->>Password: Hash Password
    Password->>Database: Store User
    Database-->>API: User Created
    API->>Token: Generate JWT
    Token-->>Client: Auth Token
```

### Authentication Flow
```mermaid
sequenceDiagram
    Client->>API: POST /api/v1/auth/login
    API->>Database: Get User
    Database-->>API: User Data
    API->>Password: Verify Password
    Password-->>API: Password Valid
    API->>Token: Generate JWT
    Token-->>Client: Auth Token
```

## Session Management

### Session Creation
```mermaid
sequenceDiagram
    Client->>API: POST /api/v1/sessions
    API->>Auth: Validate Token
    Auth-->>API: Token Valid
    API->>SQLite: Create Session Record
    SQLite-->>API: Session ID
    API->>Neo4j: Create Session Node
    Neo4j-->>API: Node Created
    API->>Storage: Create Directories
    Storage-->>API: Directories Created
    API-->>Client: Session Details
```

### Content Upload
```mermaid
sequenceDiagram
    Client->>API: POST /api/v1/sessions/{id}/content
    API->>Auth: Validate Token
    Auth-->>API: Token Valid
    API->>Storage: Save File
    Storage-->>API: File Saved
    API->>Queue: Schedule Processing
    Queue-->>API: Task Scheduled
    API-->>Client: Upload Success
```

## Analysis Pipeline

### Content Processing
```mermaid
sequenceDiagram
    Worker->>Storage: Get Content
    Storage-->>Worker: Raw Content
    Worker->>Transcription: Process Audio/Video
    Transcription-->>Worker: Transcript
    Worker->>Storage: Save Transcript
    Worker->>Analysis: Analyze Content
    Analysis->>OpenAI: Generate Analysis
    OpenAI-->>Analysis: Analysis Results
    Analysis->>Neo4j: Store Results
    Neo4j-->>Worker: Processing Complete
```

### Emotion Analysis
```mermaid
sequenceDiagram
    Analysis->>OpenAI: Extract Emotions
    OpenAI-->>Analysis: Emotion List
    Analysis->>Neo4j: Create Emotion Nodes
    Analysis->>Neo4j: Create Relationships
    Neo4j-->>Analysis: Nodes Created
```

### Topic Analysis
```mermaid
sequenceDiagram
    Analysis->>OpenAI: Extract Topics
    OpenAI-->>Analysis: Topic List
    Analysis->>Neo4j: Create Topic Nodes
    Analysis->>Neo4j: Link to Emotions
    Neo4j-->>Analysis: Nodes Created
```

## Insight Generation

### Pattern Analysis
```mermaid
sequenceDiagram
    Worker->>Neo4j: Get Session Data
    Neo4j-->>Worker: Emotions & Topics
    Worker->>OpenAI: Analyze Patterns
    OpenAI-->>Worker: Insights
    Worker->>Neo4j: Store Insights
    Neo4j-->>Worker: Insights Stored
```

### Real-time Updates
```mermaid
sequenceDiagram
    Neo4j->>WebSocket: Node Created
    WebSocket->>Client: Update Event
    Client->>API: Get New Data
    API->>Neo4j: Fetch Details
    Neo4j-->>API: Node Details
    API-->>Client: Updated Data
```

## Error Handling

### Error Recovery
```mermaid
sequenceDiagram
    Process->>Error: Error Occurs
    Error->>Logger: Log Error
    Error->>Queue: Retry Task
    Queue->>Process: Retry Processing
    Process-->>Status: Update Status
```

### Failure Notification
```mermaid
sequenceDiagram
    Error->>Notification: Create Alert
    Notification->>Admin: Send Alert
    Notification->>Client: Update Status
    Client->>API: Get Error Details
    API-->>Client: Error Information
```

## Monitoring and Metrics

### Health Checks
```mermaid
sequenceDiagram
    Monitor->>API: Check Health
    API->>Database: Ping
    Database-->>API: Status
    API->>Neo4j: Ping
    Neo4j-->>API: Status
    API->>Storage: Check Access
    Storage-->>API: Status
    API-->>Monitor: System Health
```

### Performance Metrics
```mermaid
sequenceDiagram
    API->>Metrics: Record Request
    Worker->>Metrics: Record Processing
    Database->>Metrics: Record Query
    Metrics->>Dashboard: Update Stats
    Dashboard->>Admin: Display Metrics
```

## Backup and Recovery

### Backup Process
```mermaid
sequenceDiagram
    Schedule->>Backup: Start Backup
    Backup->>SQLite: Backup Database
    Backup->>Neo4j: Backup Graph
    Backup->>Storage: Backup Files
    Backup->>Archive: Store Backup
    Archive-->>Monitor: Backup Complete
```

### Recovery Process
```mermaid
sequenceDiagram
    Admin->>Recovery: Initiate Recovery
    Recovery->>Archive: Get Backup
    Recovery->>Database: Restore Data
    Recovery->>Storage: Restore Files
    Recovery->>Verify: Check Integrity
    Verify-->>Admin: Recovery Status
``` 