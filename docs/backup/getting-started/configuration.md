# Configuration Guide

This guide explains how to configure the Insight Journey platform.

## Environment Variables

The platform uses environment variables for configuration. Copy `.env.example` to `.env` and set the following variables:

### Flask Configuration
```bash
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
```

### Database Configuration
```bash
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

### Neo4j Configuration
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### OpenAI Configuration
```bash
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4
```

### Application Configuration
```bash
UPLOAD_FOLDER=uploads
TRANSCRIPTS_FOLDER=transcripts
ANALYSIS_FOLDER=analysis
```

## File Structure

The application creates the following directory structure:
```
insight-journey/
├── uploads/          # Uploaded files
├── transcripts/      # Generated transcripts
├── analysis/         # Analysis results
└── app.db           # SQLite database
```

## Neo4j Configuration

### Database Setup
1. Start Neo4j server
2. Access Neo4j Browser at http://localhost:7474
3. Set initial password
4. Create indexes for performance:
```cypher
CREATE INDEX session_id IF NOT EXISTS FOR (s:Session) ON (s.id);
CREATE INDEX user_id IF NOT EXISTS FOR (u:User) ON (u.id);
```

### Security
1. Change default password
2. Enable authentication
3. Configure network access
4. Set up SSL if needed

## Analysis Configuration

### Element Settings
Configure analysis elements in `config/elements.json`:
```json
{
    "emotion": {
        "enabled": true,
        "categories": ["basic", "complex"],
        "format_template": "{name} (intensity: {intensity})"
    },
    "topic": {
        "enabled": true,
        "categories": ["personal", "professional"]
    }
}
```

### OpenAI Settings
1. Set API key in `.env`
2. Configure model parameters:
   - Temperature
   - Max tokens
   - Top P
   - Frequency penalty
   - Presence penalty

## Security Configuration

### JWT Settings
```bash
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

### CORS Settings
```bash
CORS_ORIGINS=http://localhost:3000
CORS_METHODS=GET,POST,PUT,DELETE
CORS_HEADERS=Content-Type,Authorization
```

## Logging Configuration

Configure logging in `config/logging.conf`:
```ini
[loggers]
keys=root,app

[handlers]
keys=console,file

[formatters]
keys=default

[logger_root]
level=INFO
handlers=console,file

[logger_app]
level=DEBUG
handlers=console,file
qualname=app
```

## Performance Tuning

### Database
1. Configure connection pool
2. Set appropriate timeouts
3. Enable query caching
4. Create necessary indexes

### Application
1. Configure worker processes
2. Set appropriate timeouts
3. Enable response compression
4. Configure static file serving

## Monitoring

### Health Checks
1. API health endpoint: `/api/v1/health`
2. Database health: `/api/v1/health/db`
3. Neo4j health: `/api/v1/health/neo4j`

### Metrics
1. Request latency
2. Error rates
3. Database performance
4. Memory usage

## Backup and Recovery

### Database Backups
1. Schedule regular Neo4j backups
2. Backup SQLite database
3. Store backups securely
4. Test recovery procedures

### Configuration Backups
1. Version control configuration files
2. Backup environment variables
3. Document changes
4. Maintain change history 