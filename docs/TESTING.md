# Testing Guide for Insight Journey Backend

## Overview
This guide explains how to test the Insight Journey backend application, focusing on the therapy session analysis pipeline.

## Test Scripts

### `test_analysis_one.py`
This script tests the core functionality of the backend by:
1. Connecting to Neo4j database
2. Creating/finding a test user
3. Processing a transcript file from the `transcripts` directory
4. Analyzing the transcript with OpenAI
5. Extracting elements (emotions, beliefs, insights, etc.)
6. Saving the analysis to Neo4j

#### How to Run

1. Make sure you have the required environment variables in a `.env.test` file:
   ```
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   OPENAI_API_KEY=your-openai-api-key
   ```

2. Run the script with the environment variables:
   ```bash
   env $(cat .env.test) python test_analysis_one.py
   ```

3. Check the output for successful completion. Look for:
   - "Neo4j service initialized"
   - "Successfully read [X] characters"
   - "Summary of extracted elements"
   - "Successfully created session"
   - "Successfully processed [filename]"

### Expected Output

The script processes a single transcript file and should output information about:
- Emotions (name, intensity, context, topic)
- Beliefs (name, description, impact, topic)
- Insights (name, context, topic)
- Challenges (name, impact, topic)
- Action Items (name, description, topic)

The analysis results are saved to both:
1. A JSON file in the `analysis_results` directory
2. Neo4j database (connected to a User and Session node)

## Troubleshooting

### Neo4j Connection Issues
- Verify the Neo4j URI, username, and password are correct
- Check that the Neo4j Aura instance is running
- Ensure the Neo4j driver is properly initialized with `await neo4j_service.initialize()`

### OpenAI API Issues
- Verify the OpenAI API key is valid
- Check for rate limiting errors
- Ensure the model being used is available

### File Processing Issues
- Ensure the `transcripts` directory exists and contains text files
- Check file permissions and encoding

## Manual Testing via API

You can also test the API endpoints directly:

1. Start the server:
   ```bash
   uvicorn main:app --reload --port 8080
   ```

2. Test the health endpoint:
   ```bash
   curl http://localhost:8080/health
   ```

3. Analyze a transcript (requires authentication):
   ```bash
   curl -X POST http://localhost:8080/api/v1/analysis/analyze \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"transcript": "Your transcript text here...", "sessionId": "optional-session-id"}'
   ``` 