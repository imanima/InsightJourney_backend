# Insight Journey Architecture

## Purpose
Insight Journey is a personal growth application that helps users track emotional patterns, insights, and personal development through AI-assisted reflection sessions. It analyzes user sessions to identify emotions, topics, beliefs, and action items.

## Core Components

### 1. User Management
- **Authentication**: Registration, login, session management
- **User Settings**: Model preferences, analysis configuration
- **Admin Controls**: System settings, user management

### 2. Session Processing
- **Recording**: Audio capture and transcription
- **Analysis**: AI processing using OpenAI
- **Storage**: Session data, elements, and relationships

### 3. Insight Generation
- **Element Extraction**: Emotions, topics, insights, beliefs, challenges, actions
- **Pattern Recognition**: Trends across sessions
- **Progress Tracking**: Action item follow-up

## Data Model

### Key Nodes
- **User**: `{id, name, email, created_at, updated_at, role, status, last_login}` (email and id are unique)
- **Session**: `{id, user_id, title, date, transcript, status, duration, recording_url, analysis_status, created_at, updated_at}` (merge on userId + sessionId)
- **Emotion**: `{id, user_id, name, description, created_at, updated_at}` (merge on emotionName + user_id)
- **Topic**: `{id, user_id, name, description, created_at, updated_at}` (merge on topicName + user_id)
- **Insight**: `{id, user_id, text, insightName, confidence, created_at, updated_at}` (merge on insightName + user_id)
- **Belief**: `{id, user_id, text, beliefName, confidence, created_at, updated_at}` (merge on beliefName + user_id)
- **Challenge**: `{id, user_id, text, severity, status, created_at, updated_at}`
- **ActionItem**: `{id, user_id, description, actionName, status, priority, due_date, completed_at, created_at, updated_at}` (merge on ActionName + user_id)
- **EmotionTaxonomy**: `{id, name, level, parent_id, description, created_at, updated_at}` (merge on name)
- **TopicTaxonomy**: `{id, name, level, parent_id, description, created_at, updated_at}` (merge on name)

### Key Relationships
- **User-Session**: `(:User)-[:HAS_SESSION {created_at, updated_at}]->(:Session)`
- **Session-Emotion**: `(:Session)-[:HAS_EMOTION {context, intensity, confidence, created_at, updated_at, modified_by}]->(:Emotion)`
- **Emotion-Topic**: `(:Emotion)-[:RELATED_TO {strength, context, created_at, updated_at, modified_by}]->(:Topic)`
- **Session-Insight**: `(:Session)-[:HAS_INSIGHT {confidence, context, created_at, updated_at, modified_by}]->(:Insight)`
- **Session-Belief**: `(:Session)-[:HAS_BELIEF {confidence, context, created_at, updated_at, modified_by}]->(:Belief)`
- **Session-Challenge**: `(:Session)-[:HAS_CHALLENGE {severity, context, created_at, updated_at, modified_by}]->(:Challenge)`
- **Session-ActionItem**: `(:Session)-[:HAS_ACTION_ITEM {priority, context, created_at, updated_at, modified_by}]->(:ActionItem)`
- **Insight-Topic**: `(:Insight)-[:RELATED_TO {relevance, context, created_at, updated_at, modified_by}]->(:Topic)`
- **Belief-Topic**: `(:Belief)-[:RELATED_TO {relevance, context, created_at, updated_at, modified_by}]->(:Topic)`
- **Challenge-Topic**: `(:Challenge)-[:RELATED_TO {relevance, context, created_at, updated_at, modified_by}]->(:Topic)`
- **ActionItem-Topic**: `(:ActionItem)-[:RELATED_TO {relevance, context, created_at, updated_at, modified_by}]->(:Topic)`
- **Emotion-Taxonomy**: `(:Emotion)-[:CLASSIFIES_AS {confidence, created_at, updated_at, modified_by}]->(:EmotionTaxonomy)`
- **EmotionTaxonomy-Hierarchy**: `(:EmotionTaxonomy)-[:CLASSIFIES_AS {level, created_at, updated_at, modified_by}]->(:EmotionTaxonomy)`
- **Topic-Taxonomy**: `(:Topic)-[:CLASSIFIES_AS {confidence, created_at, updated_at, modified_by}]->(:TopicTaxonomy)`
- **TopicTaxonomy-Hierarchy**: `(:TopicTaxonomy)-[:CLASSIFIES_AS {level, created_at, updated_at, modified_by}]->(:TopicTaxonomy)`

## Core APIs

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - Authenticate user
- `GET /auth/me` - Get current user info

### Sessions
- `POST /sessions` - Create new session
- `GET /sessions/{id}` - Get session details
- `DELETE /sessions/{id}` - Delete session

### Analysis
- `POST /sessions/{id}/analyze` - Start analysis
- `GET /sessions/{id}/analysis` - Get analysis results
- `GET /sessions/{id}/transcript` - Get session transcript

### Admin
- `GET/PUT /admin/settings` - Manage system settings
- `GET/PUT /admin/analysis-elements` - Configure analysis elements
- `GET/PUT /admin/users/{id}` - Manage users

## Workflows

### 1. Session Creation
1. User records or uploads session
2. System transcribes audio
3. AI analyzes transcript
4. Elements are extracted and stored
5. Relationships are established

### 2. Insight Generation
1. Elements are analyzed for patterns
   - Emotions are identified and categorized
   - Emotional patterns and trends are detected
   - Emotional intensity variations are tracked
2. Topics are derived from elements
   - Topics are linked to emotional states
   - Topic-emotion correlations are established
3. Insights are generated from patterns
   - Emotional patterns are analyzed
   - Topic-emotion relationships are evaluated
   - Combined emotional and topical insights are formed
4. Action items are suggested
   - Based on emotional patterns
   - Addressing emotional challenges
   - Supporting emotional growth

### 3. Progress Tracking
1. User reviews insights
2. User updates action items
3. System tracks completion
4. Patterns are identified across sessions

## Technical Implementation

### Database
- **Neo4j**: Graph database for relationships
- **Key Indexes**: `User.id`, `Session.id`, `Element.id`
- **Queries**: Cypher for graph traversal

### Backend
- **Python/FastAPI**: API server
- **Neo4j Driver**: Database connectivity
- **OpenAI SDK**: AI analysis

### Authentication
- **Session-based**: Cookie authentication
- **Role-based**: Admin vs regular users

## Best Practices

### Data Integrity
- Unique IDs for all nodes
- Consistent timestamp tracking
- Proper relationship management

### Query Optimization
- Use `MERGE` for ensuring uniqueness
- Use `MATCH` with indexes for performance
- Batch operations for efficiency

### Security
- Validate all inputs
- Sanitize user data
- Proper error handling