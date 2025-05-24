#!/bin/bash

# Set error handling
set -e

echo "Starting local deployment test for Insight Journey Backend"

# Check for .env file
if [ ! -f .env ]; then
    echo "No .env file found. Creating one from .env.example"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env file from .env.example"
        echo "Please update the values in .env before continuing"
        exit 1
    else
        echo "No .env.example file found. Please create a .env file"
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the test script
echo "Running tests..."
python test_local_setup.py

# If test was successful, start the application
if [ $? -eq 0 ]; then
    echo "Tests passed! Starting the application..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8080
else
    echo "Tests failed. Please fix the issues before continuing."
    exit 1
fi 