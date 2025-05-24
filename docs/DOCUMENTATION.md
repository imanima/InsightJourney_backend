# Insight Journey Backend Documentation

## Overview
Insight Journey is a therapy session analysis application that helps users track emotional patterns, insights, and personal development through AI-assisted processing of session transcripts.

## Architecture

### Core Components
- **User Management**: Authentication, user settings
- **Session Processing**: Transcript analysis, storage
- **Insight Generation**: Extract emotions, beliefs, insights, challenges, action items

### Tech Stack
- **Backend**: Python/FastAPI
- **Database**: Neo4j (graph database)
- **AI**: OpenAI API for analysis
- **Deployment**: Google Cloud Run

## Deployment

### Prerequisites
- Google Cloud Account
- Neo4j Aura instance
- OpenAI API key

### Quick Deployment Steps
1. Ensure you have a Neo4j Aura database
2. Configure environment variables in .env file
3. Run `./quickdeploy.sh` to deploy to GCP Cloud Run

```bash
# Example .env file
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
OPENAI_API_KEY=your-openai-key
JWT_SECRET=your-secret-key
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Authenticate a user
- `POST /api/v1/auth/register` - Register a new user
- `GET /api/v1/auth/me` - Get current user

### Sessions
- `POST /api/v1/sessions` - Create a new session
- `GET /api/v1/sessions/{id}` - Get session details
- `GET /api/v1/sessions` - List all sessions

### Analysis
- `POST /api/v1/analysis/analyze` - Analyze a transcript
- `GET /api/v1/analysis/status/{id}` - Check analysis status

## Data Model

### Main Entities
- **User**: Stores user account information
- **Session**: Contains therapy session data (transcript, duration, date)
- **Elements**: Emotions, beliefs, insights, challenges, action items extracted from sessions

## Local Development

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run locally: `uvicorn main:app --reload`

### Testing
1. Create a `.env.test` file with your credentials:
   ```
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   OPENAI_API_KEY=your-openai-key
   ```

2. Run tests with the test script:
   ```bash
   ./run_tests.sh
   ```

3. For more details on testing, see [Testing Guide](./TESTING.md)

## Maintenance

### Updating Dependencies
```bash
pip install -U -r requirements.txt
./quickdeploy.sh
```

### Monitoring
View logs in Google Cloud Console or use:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=insight-journey"
``` 