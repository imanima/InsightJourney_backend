# Test Files Documentation

This document explains the purpose of each test file in the Insight Journey Backend project and provides guidance on when to use each one.

## Main Test Files

1. **test_analysis_debug.py**
   - **Purpose**: Debug the transcript analysis process with detailed output
   - **When to use**: When you need to see exactly what the analysis service returns and how it's processed
   - **Run with**: `python test_analysis_debug.py`

2. **test_minimal.py**
   - **Purpose**: A minimal test for running analysis on one file with Neo4j integration
   - **When to use**: Quick testing of the analysis and Neo4j integration with minimal setup
   - **Run with**: `python test_minimal.py`

3. **test_neo4j_async.py**
   - **Purpose**: Process transcripts and store results in Neo4j using async service
   - **When to use**: When testing the Neo4j integration with multiple files
   - **Run with**: `python test_neo4j_async.py`

4. **test_local_setup.py**
   - **Purpose**: Verify that your local environment is set up correctly
   - **When to use**: After installation or when environment configuration changes
   - **Run with**: `python test_local_setup.py`

5. **test_openai.py**
   - **Purpose**: Test OpenAI API connectivity and verify API key
   - **When to use**: To verify your OpenAI API key is working correctly
   - **Run with**: `python test_openai.py`

6. **test_prod_api.py**
   - **Purpose**: Test production API endpoints
   - **When to use**: When testing the production API server
   - **Run with**: `python test_prod_api.py`

7. **test_api_endpoints.py**
   - **Purpose**: Test all API endpoints including authentication and session management
   - **When to use**: When making changes to the API endpoints or handlers
   - **Run with**: `python test_api_endpoints.py`

8. **test_analysis_endpoints.py**
   - **Purpose**: Test the analysis-specific API endpoints
   - **When to use**: When making changes to the analysis API functionality
   - **Run with**: `python test_analysis_endpoints.py`

9. **test_audio_transcription.py**
   - **Purpose**: Test audio transcription functionality
   - **When to use**: When working with audio files that need to be transcribed
   - **Run with**: `python test_audio_transcription.py`

## API Testing Files

1. **api_test_suite.py**
   - **Purpose**: Comprehensive API test suite that tests all API endpoints
   - **When to use**: When testing the entire API or specific endpoint categories
   - **Run with**: `python api_test_suite.py [--verbose] [--endpoint=<name>] [--transcription] [--audio-file=<path>]`

2. **run_api_tests.sh**
   - **Purpose**: Shell script for running API tests with various options
   - **When to use**: When you want to run API tests from the command line
   - **Run with**: `./run_api_tests.sh [options]`
   - **Options**:
     - `-v, --verbose`: Show detailed request/response information
     - `-e, --endpoint <name>`: Test only a specific endpoint category
     - `-T, --transcription`: Run only transcription tests
     - `-a, --audio-file <path>`: Specify a test audio file

3. **API_README.md**
   - **Purpose**: Comprehensive API documentation
   - **When to use**: When you need to understand the API endpoints and usage
   - **Access**: Open in a text editor or browser

4. **api_dashboard.py**
   - **Purpose**: Interactive dashboard for API testing and documentation
   - **When to use**: When you want a user-friendly interface for API testing
   - **Run with**: `python api_dashboard.py`

## Production Scripts

1. **process_all_users.py**
   - **Purpose**: Process all transcripts for all users and save results to Neo4j
   - **When to use**: When processing many files in production
   - **Run with**: `python process_all_users.py [options]`
   - **Options**:
     - `--user <user_id>`: Process only a specific user
     - `--all-sessions`: Process all sessions (not just new ones)
     - `--batch-size <n>`: Number of files to process in one batch
     - `--batch-start <n>`: Starting index for batch processing

## Shell Scripts

1. **run_tests.sh**
   - **Purpose**: Interactive menu for running test files
   - **When to use**: When you want to run a specific test file or all tests
   - **Run with**: `./run_tests.sh`

2. **process_all_sessions.sh**
   - **Purpose**: Process all sessions for all users
   - **When to use**: When processing many files in production
   - **Run with**: `./process_all_sessions.sh`

3. **process_all_batches.sh**
   - **Purpose**: Process all batches of transcripts
   - **When to use**: When processing files in batches
   - **Run with**: `./process_all_batches.sh`

4. **process_next_batches.sh**
   - **Purpose**: Process the next batch of transcripts
   - **When to use**: When processing the next batch after previous batches
   - **Run with**: `./process_next_batches.sh <start_batch> <num_batches>`

5. **continue_all_sessions.sh**
   - **Purpose**: Continue processing from where previous batch left off
   - **When to use**: When resuming batch processing
   - **Run with**: `./continue_all_sessions.sh`

## Best Practices

1. **For Development**:
   - Use `test_analysis_debug.py` for debugging analysis functionality
   - Use `test_minimal.py` for quick testing of analysis and Neo4j integration
   - Use `test_local_setup.py` to verify your environment

2. **For API Testing**:
   - Use `api_dashboard.py` for an interactive testing experience
   - Use `run_api_tests.sh` for command-line testing
   - Use `api_test_suite.py` directly for the most control

3. **For Production**:
   - When processing many files in production, use the shell scripts with `process_all_users.py`
   - Use batch processing for large numbers of files

4. **For Documentation**:
   - Refer to API_README.md for API endpoints and usage
   - Use the api_dashboard.py to explore available endpoints

## Files to Remove (Safe to Delete)

The following files are redundant or outdated and can be safely deleted:

1. **test_analysis_long.py** - Superseded by process_all_users.py
2. **test_neo4j_direct.py** - Already deleted
3. **test_neo4j_fix.py** - Already deleted
4. **test_neo4j_simple.py** - Prototype for Neo4j integration
5. **test_neo4j_connection.py** - Basic connection test, redundant with test_local_setup.py
6. **test_neo4j_export.py** - Covered by test_api_endpoints.py
7. **test_file_only.py** - Already deleted
8. **test_analysis_one.py** - Redundant with test_minimal.py

## Tips for Test File Use

- Always verify your Neo4j and OpenAI credentials before running tests
- Start with `test_local_setup.py` to ensure your environment is configured correctly
- Use `test_analysis_debug.py` when you need to debug issues with the analysis results
- For full integration testing, run `test_api_endpoints.py`
- When processing many files in production, use the shell scripts with `process_all_users.py` 