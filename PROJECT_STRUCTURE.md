# Insight Journey Backend Project Structure

This document provides an overview of the key files and directories in the Insight Journey Backend project after cleaning up unnecessary and redundant files.

## Core Files

- **main.py** - Application entry point that sets up the FastAPI app
- **requirements.txt** - Python package dependencies
- **config.py** - Configuration settings for the application
- **extensions.py** - Flask extensions module

## Key Directories

- **routes/** - API route definitions (auth, sessions, analysis, transcription)
- **services/** - Business logic (Neo4j, analysis, authentication)
- **utils/** - Utility functions and helpers
- **models/** - Data models for requests/responses
- **insights/** - Advanced insights and analytics module
- **transcripts/** - Sample therapy session transcripts
- **uploads/** - Directory for uploaded files

## API Documentation

- **API_README.md** - Comprehensive API documentation
- **swagger.json** - OpenAPI/Swagger schema for API endpoints

## Testing Files

1. **Essential Test Files**:
   - **test_analysis_debug.py** - For debugging analysis functionality
   - **test_minimal.py** - Minimal test for analysis on one file
   - **test_neo4j_async.py** - Test for Neo4j integration
   - **test_local_setup.py** - Verifies environment setup
   - **test_openai.py** - Tests OpenAI API connectivity
   - **test_prod_api.py** - Tests production API endpoints
   - **test_api_endpoints.py** - Tests all API endpoints
   - **test_analysis_endpoints.py** - Tests analysis-specific endpoints
   - **test_audio_transcription.py** - Tests audio transcription

2. **API Testing Tools**:
   - **api_test_suite.py** - Comprehensive API test suite
   - **run_api_tests.sh** - Script for running API tests
   - **api_dashboard.py** - Interactive dashboard for API testing

## Deployment Files

- **deploy.sh** - Script for deployment to GCP
- **deploy_simple.sh** - Simplified deployment script
- **Dockerfile** - Docker container configuration
- **.dockerignore** - Files to exclude from Docker builds
- **cloudbuild.yaml** - GCP Cloud Build configuration

## Process Scripts

- **process_all_users.py** - Main script for processing user transcripts
- **process_all_sessions.sh** - Script to process all sessions

## Automated Testing

- **run_tests.sh** - Interactive test runner script
- **pytest.ini** - Configuration for pytest

## Other Configuration

- **.gitignore** - Files to exclude from Git
- **initialize_db.py** - Database initialization script

## Cleanup Process

The project was cleaned up by removing:
1. Empty files and logs
2. Redundant test and utility files
3. Duplicate batch processing scripts
4. Unnecessary deployment scripts
5. Outdated documentation
6. Sample data files not needed in production

This organization makes the codebase more maintainable and easier to navigate. 