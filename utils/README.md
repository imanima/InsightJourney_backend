# Utilities Directory

This directory contains various utility scripts and tools organized by functionality to support the Insight Journey Backend development and operations.

## Directory Structure

```
utils/
├── auth/           # Authentication utilities and debugging tools
├── data/           # Data management and sample data creation
├── debug/          # Debugging and diagnostic utilities
├── scripts/        # Deployment and operational scripts
└── transcription/  # Audio transcription utilities
```

## Authentication Utilities (`auth/`)

- **auth_test_fix.py**: Authentication testing and fixing utilities
- **login_debug.py**: Login process debugging tools
- **login_existing_user.py**: Utility for testing login with existing users
- **quick_auth_check.py**: Quick authentication validation checks
- **verify_login.py**: Login verification and validation tools

## Data Utilities (`data/`)

- **create_sample_data.py**: Generate sample data for testing and development
- **process_all_users.py**: Batch processing utility for user data
- **reset_test_user.py**: Reset test user data for clean testing

## Debug Utilities (`debug/`)

- **check_db.py**: Database connection and status checking
- **debug_local_error.py**: Local environment error debugging

## Scripts (`scripts/`)

- **fix_auth_deploy.sh**: Authentication deployment fixes

## Transcription Utilities (`transcription/`)

- **transcribe_audio.py**: Audio file transcription processing

## Usage Guidelines

### Authentication Utilities
Use these tools when debugging authentication issues or testing login functionality:

```bash
# Quick authentication check
python utils/auth/quick_auth_check.py

# Debug login issues
python utils/auth/login_debug.py

# Verify login functionality
python utils/auth/verify_login.py
```

### Data Management
Use these tools for managing test data and batch processing:

```bash
# Create sample data for testing
python utils/data/create_sample_data.py

# Process user data in batches
python utils/data/process_all_users.py

# Reset test user for clean testing
python utils/data/reset_test_user.py
```

### Debugging
Use these tools for diagnosing system issues:

```bash
# Check database connectivity
python utils/debug/check_db.py

# Debug local environment issues
python utils/debug/debug_local_error.py
```

### Audio Processing
Use these tools for audio transcription:

```bash
# Transcribe audio files
python utils/transcription/transcribe_audio.py [audio_file]
```

## Best Practices

1. **Environment Setup**: Ensure all required environment variables are set before running utilities
2. **Testing**: Use utilities in a test environment before production
3. **Documentation**: Update this README when adding new utilities
4. **Error Handling**: All utilities should handle errors gracefully
5. **Logging**: Use proper logging for debugging and monitoring

## Dependencies

Most utilities require:
- Python 3.8+
- Environment variables configured (see main README)
- Access to Neo4j database
- Valid API keys where applicable

## Adding New Utilities

When adding new utilities:

1. Place them in the appropriate subdirectory
2. Follow the existing naming conventions
3. Include proper error handling and logging
4. Add documentation to this README
5. Test thoroughly before committing 