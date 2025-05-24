#!/bin/bash

# Secure deployment script for Insight Journey Backend
# This script reads from .env file and deploys to Google Cloud Run

set -e

echo "🚀 Insight Journey Backend Deployment"
echo "======================================"

# Load environment variables
if [ -f .env ]; then
    echo "✅ Loading environment variables from .env file"
    source .env
else
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with required variables"
    exit 1
fi

# Check required environment variables
required_vars=(
    "NEO4J_URI"
    "NEO4J_USER"
    "NEO4J_PASSWORD"
    "OPENAI_API_KEY"
    "JWT_SECRET"
)

optional_vars=(
    "PROJECT_ID"
    "REGION"
    "SERVICE_NAME"
)

echo "🔍 Checking required environment variables..."
missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    else
        echo "✅ $var is set"
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

# Set defaults for optional variables
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"insight-journey"}

echo "📋 Deployment Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME"

# Confirm deployment
echo "🤔 Do you want to proceed with deployment? (y/N)"
read -r confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "⏹️  Deployment cancelled"
    exit 0
fi

# Set GCP project
echo "🔧 Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "⚙️  Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Build and deploy
echo "🏗️  Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars="\
NEO4J_URI=$NEO4J_URI,\
NEO4J_USER=$NEO4J_USER,\
NEO4J_PASSWORD=$NEO4J_PASSWORD,\
OPENAI_API_KEY=$OPENAI_API_KEY,\
JWT_SECRET=$JWT_SECRET"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "🧪 Test with: curl $SERVICE_URL/health" 