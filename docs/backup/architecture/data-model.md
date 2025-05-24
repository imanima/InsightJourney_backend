# Data Model

## Overview

The Insight Journey platform uses a hybrid data model combining:
- Neo4j for relationship-based data (emotions, topics, insights, transcripts)
- SQLite for transactional data (users, sessions, analysis jobs)
- File system for media storage

## Neo4j Graph Model

### Key Nodes

1. **User**
   ```cypher
   CREATE (u:User {
     id: String,
     name: String,
     email: String,
     created_at: DateTime,
     updated_at: DateTime,
     role: String,
     status: String,
     last_login: DateTime
   })
   ```

2. **Session**
   ```cypher
   CREATE (s:Session {
     id: String,
     user_id: String,
     title: String,
     date: DateTime,
     status: String,
     duration: Integer,
     recording_url: String,
     analysis_status: String,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

3. **Transcript**
   ```cypher
   CREATE (t:Transcript {
     id: String,
     session_id: String,
     text: String,
     language: String,
     duration: Float,
     segments: List,
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

4. **Emotion**
   ```cypher
   CREATE (e:Emotion {
     id: String,
     session_id: String,
     name: String,
     intensity: Float,
     context: String,
     timestamp: DateTime,
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

5. **Topic**
   ```cypher
   CREATE (t:Topic {
     id: String,
     session_id: String,
     name: String,
     category: String,
     confidence: Float,
     timestamp: DateTime,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

6. **Insight**
   ```cypher
   CREATE (i:Insight {
     id: String,
     session_id: String,
     text: String,
     type: String,
     confidence: Float,
     context: String,
     timestamp: DateTime,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

7. **Belief**
   ```cypher
   CREATE (b:Belief {
     id: String,
     session_id: String,
     text: String,
     impact: Float,
     confidence: Float,
     timestamp: DateTime,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

8. **Challenge**
   ```cypher
   CREATE (c:Challenge {
     id: String,
     session_id: String,
     text: String,
     impact: Float,
     severity: String,
     confidence: Float,
     timestamp: DateTime,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

9. **ActionItem**
   ```cypher
   CREATE (a:ActionItem {
     id: String,
     session_id: String,
     text: String,
     priority: String,
     status: String,
     due_date: DateTime,
     context: String,
     created_at: DateTime,
     updated_at: DateTime
   })
   ```

### Key Relationships

1. **User-Session**
   ```cypher
   MATCH (u:User), (s:Session)
   WHERE u.id = s.user_id
   CREATE (u)-[:HAS_SESSION {
     created_at: DateTime,
     updated_at: DateTime
   }]->(s)
   ```

2. **Session-Transcript**
   ```cypher
   MATCH (s:Session), (t:Transcript)
   WHERE s.id = t.session_id
   CREATE (s)-[:HAS_TRANSCRIPT {
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)
   ```

3. **Session-Emotion**
   ```cypher
   MATCH (s:Session), (e:Emotion)
   WHERE s.id = e.session_id
   CREATE (s)-[:HAS_EMOTION {
     context: String,
     intensity: Float,
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   }]->(e)
   ```

4. **Session-Topic**
   ```cypher
   MATCH (s:Session), (t:Topic)
   WHERE s.id = t.session_id
   CREATE (s)-[:HAS_TOPIC {
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)
   ```

5. **Session-Insight**
   ```cypher
   MATCH (s:Session), (i:Insight)
   WHERE s.id = i.session_id
   CREATE (s)-[:HAS_INSIGHT {
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   }]->(i)
   ```

6. **Session-Belief**
   ```cypher
   MATCH (s:Session), (b:Belief)
   WHERE s.id = b.session_id
   CREATE (s)-[:HAS_BELIEF {
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   }]->(b)
   ```

7. **Session-Challenge**
   ```cypher
   MATCH (s:Session), (c:Challenge)
   WHERE s.id = c.session_id
   CREATE (s)-[:HAS_CHALLENGE {
     confidence: Float,
     created_at: DateTime,
     updated_at: DateTime
   }]->(c)
   ```

8. **Session-ActionItem**
   ```cypher
   MATCH (s:Session), (a:ActionItem)
   WHERE s.id = a.session_id
   CREATE (s)-[:HAS_ACTION_ITEM {
     created_at: DateTime,
     updated_at: DateTime
   }]->(a)
   ```

9. **Element-Topic Relationships**
   ```cypher
   // Emotion-Topic
   MATCH (e:Emotion), (t:Topic)
   CREATE (e)-[:RELATED_TO {
     strength: Float,
     context: String,
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)

   // Belief-Topic
   MATCH (b:Belief), (t:Topic)
   CREATE (b)-[:RELATED_TO {
     strength: Float,
     context: String,
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)

   // Insight-Topic
   MATCH (i:Insight), (t:Topic)
   CREATE (i)-[:RELATED_TO {
     strength: Float,
     context: String,
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)

   // Challenge-Topic
   MATCH (c:Challenge), (t:Topic)
   CREATE (c)-[:RELATED_TO {
     strength: Float,
     context: String,
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)

   // ActionItem-Topic
   MATCH (a:ActionItem), (t:Topic)
   CREATE (a)-[:RELATED_TO {
     strength: Float,
     context: String,
     created_at: DateTime,
     updated_at: DateTime
   }]->(t)
   ```

## SQLite Schema

### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Analysis Jobs Table
```sql
CREATE TABLE analysis_jobs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    transcript_id TEXT NOT NULL,
    status TEXT NOT NULL,
    progress FLOAT,
    error TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

## File Storage Structure

```
insight-journey/
├── uploads/
│   ├── {user_id}/
│   │   ├── sessions/
│   │   │   ├── {session_id}/
│   │   │   │   ├── original/
│   │   │   │   │   └── {filename}
│   │   │   │   ├── processed/
│   │   │   │   │   └── {filename}
│   │   │   │   └── transcript.txt
│   │   │   │   └── profile/
│   │   │   │       └── {filename}
│   └── temp/
│       └── {session_id}/
│           └── {filename}
```

## Data Access Patterns

1. **User Data**
   - Read: Frequent (profile, settings)
   - Write: Infrequent (updates, preferences)

2. **Session Data**
   - Read: Frequent (analysis, playback)
   - Write: During creation and updates

3. **Transcript Data**
   - Read: During analysis and playback
   - Write: After transcription

4. **Analysis Elements**
   - Read: Frequent (insights, patterns)
   - Write: During analysis processing
   - Graph queries for relationships

5. **Media Files**
   - Read: During playback
   - Write: During upload and processing

## Performance Considerations

1. **Neo4j Indexing**
   - User ID indexes
   - Session ID indexes
   - Element type indexes
   - Timestamp indexes
   - Text search indexes

2. **SQLite Indexing**
   - User ID indexes
   - Session ID indexes
   - Job status indexes
   - Timestamp indexes

3. **Caching**
   - User session data
   - Recent analysis results
   - Frequently accessed files
   - Graph query results

4. **Query Optimization**
   - Use appropriate indexes
   - Batch operations
   - Connection pooling
   - Graph traversal optimization

## Migration Strategy

1. **Schema Changes**
   - Version control for schemas
   - Migration scripts
   - Rollback procedures
   - Data validation

2. **Data Migration**
   - Backup procedures
   - Validation checks
   - Progress tracking
   - Graph data integrity

3. **Version Control**
   - Schema versioning
   - Data versioning
   - Compatibility checks
   - Graph structure validation 