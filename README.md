# Insight Journey Backend

A backend service for analyzing therapy session transcripts, extracting insights, emotions, and other elements, and storing them in a Neo4j graph database.

## Features

- **Therapy Session Analysis**: Process therapy transcripts using OpenAI's API
- **Element Extraction**: Identify emotions, beliefs, challenges, insights, and action items
- **Graph Database**: Store results in Neo4j for complex relationship querying
- **RESTful API**: FastAPI endpoints for client integration
- **Authentication**: JWT-based user authentication

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Run the application: `uvicorn main:app --reload`

## Environment Setup

Create a `.env` file with the following variables:

```
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET=your-jwt-secret
PORT=8080
```

## Testing

We provide a convenient test runner script with an interactive menu:

```bash
./run_tests.sh
```

This script allows you to:
- Run individual test files with descriptions
- Run all tests sequentially
- Check environment setup before running tests

For detailed information about available test files:
- See [Test Files Documentation](./TEST_FILES_README.md)
- See [Test Files Cleanup](./test_files_cleanup.md) for information about redundant files

### Main Test Files

1. **test_analysis_debug.py** - Debug transcript analysis with detailed output
2. **test_minimal.py** - Run a minimal test with Neo4j integration
3. **test_neo4j_async.py** - Process transcripts with Neo4j
4. **test_local_setup.py** - Verify the environment setup
5. **test_openai.py** - Test OpenAI API connectivity
6. **test_api_endpoints.py** - Test the API endpoints
7. **test_audio_transcription.py** - Test audio transcription

## Deployment

1. Ensure you have the GCP project ID, Neo4j Aura instance, and OpenAI API key
2. Deploy to Google Cloud Run:
   ```bash
   ./deploy_simple.sh PROJECT_ID NEO4J_URI NEO4J_USER NEO4J_PASSWORD OPENAI_API_KEY
   ```

3. For detailed deployment instructions, see the [Deployment Documentation](./docs/DOCUMENTATION.md)

## Documentation

- [Full Documentation](./docs/DOCUMENTATION.md)
- [API Endpoints](./docs/DOCUMENTATION.md#api-endpoints)
- [Test Files Documentation](./TEST_FILES_README.md)

## Architecture

The system uses FastAPI for the REST API, Neo4j for the graph database, and OpenAI for transcript analysis. The main components are:

- **Routes**: API endpoints for authentication, sessions, and analysis
- **Services**: Business logic for Neo4j interaction, analysis, and authentication
- **Models**: Data models for request/response handling
- **Middleware**: Authentication middleware for securing endpoints

## Project Structure

```
.
├── main.py              # FastAPI application entry point
├── requirements.txt     # Project dependencies
├── Dockerfile          # Container configuration
├── .dockerignore       # Docker build exclusions
├── .env               # Environment variables (create from .env.example)
├── process_all_users.py # Main script for processing transcripts
├── run_tests.sh        # Interactive test runner
├── TEST_FILES_README.md # Test files documentation
├── routes/            # API route definitions
│   ├── __init__.py
│   ├── auth.py       # Authentication endpoints
│   ├── sessions.py   # Session management
│   └── analysis.py   # Analysis endpoints
└── services/         # Business logic
    ├── __init__.py
    ├── neo4j_service.py    # Neo4j database service
    ├── auth_service.py     # Authentication service
    └── analysis_service.py # Analysis service
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with required environment variables:
```
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password
JWT_SECRET=your_jwt_secret
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Deployment

The application is configured for deployment to Google Cloud Run:

1. Build the container:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/insight-journey
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy insight-journey \
  --image gcr.io/YOUR_PROJECT_ID/insight-journey \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Documentation
See [docs](./docs) for detailed documentation.

## Support
- Email: support@insightjourney.com
- GitHub Issues: https://github.com/insightjourney/backend/issues

## License
MIT 