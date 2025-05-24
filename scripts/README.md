# Scripts Directory

This directory contains shell scripts organized by functionality to support deployment, testing, processing, and maintenance operations.

## Directory Structure

```
scripts/
├── deployment/    # Deployment and release scripts
├── processing/    # Data processing and batch operation scripts
├── testing/       # Testing automation scripts
└── maintenance/   # System maintenance and cleanup scripts
```

## Deployment Scripts (`deployment/`)

- **deploy_simple.sh**: Simple deployment script for quick releases
- **quickdeploy.sh**: Fast deployment with minimal checks

### Usage:
```bash
# Simple deployment
./scripts/deployment/deploy_simple.sh

# Quick deployment
./scripts/deployment/quickdeploy.sh
```

## Processing Scripts (`processing/`)

- **process_all_batches.sh**: Process all data batches sequentially
- **process_all_sessions.sh**: Process all therapy sessions
- **process_next_batches.sh**: Process the next set of batches
- **continue_all_sessions.sh**: Continue processing from where it left off

### Usage:
```bash
# Process all sessions
./scripts/processing/process_all_sessions.sh

# Process specific batches
./scripts/processing/process_next_batches.sh [start_batch] [num_batches]

# Continue processing
./scripts/processing/continue_all_sessions.sh
```

## Testing Scripts (`testing/`)

- **run_api_tests.sh**: Run comprehensive API tests
- **run_tests.sh**: Legacy test runner (replaced by Python version)

### Usage:
```bash
# Run API tests with verbose output
./scripts/testing/run_api_tests.sh -v

# Run specific endpoint tests
./scripts/testing/run_api_tests.sh -e auth

# Run with transcription testing
./scripts/testing/run_api_tests.sh -T -a ./test_data/test_audio.mp3
```

## Maintenance Scripts (`maintenance/`)

- **clean_docs.sh**: Clean up documentation files
- **cleanup.sh**: General cleanup operations

### Usage:
```bash
# Clean documentation
./scripts/maintenance/clean_docs.sh

# General cleanup
./scripts/maintenance/cleanup.sh
```

## Script Guidelines

### Prerequisites
- Ensure all environment variables are set
- Have proper permissions for script execution
- Test in development environment first

### Best Practices
1. **Error Handling**: All scripts should handle errors gracefully
2. **Logging**: Include proper logging and status messages
3. **Validation**: Validate inputs and environment before execution
4. **Documentation**: Keep this README updated with new scripts
5. **Testing**: Test scripts thoroughly before production use

### Making Scripts Executable
```bash
chmod +x scripts/[category]/[script_name].sh
```

### Environment Requirements
Most scripts require:
- Bash shell
- Required environment variables set
- Proper database and API access
- Sufficient disk space for processing operations

## Adding New Scripts

When adding new scripts:

1. Place them in the appropriate category directory
2. Follow the existing naming conventions (use underscores, .sh extension)
3. Include proper shebang (`#!/bin/bash`)
4. Add error handling and validation
5. Update this README with usage instructions
6. Make the script executable
7. Test thoroughly before committing 