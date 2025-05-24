#!/bin/bash

# Exit on error
set -e

# Check for project ID
if [ -z "$1" ]; then
    echo "Usage: ./deploy_simple.sh PROJECT_ID NEO4J_URI NEO4J_USER NEO4J_PASSWORD OPENAI_API_KEY"
    echo "Example: ./deploy_simple.sh myproject-id bolt://xxx.databases.neo4j.io:7687 neo4j my-password sk-..."
    exit 1
fi

# Variables from command line
PROJECT_ID=$1
NEO4J_URI=${2:-"bolt://localhost:7687"}
NEO4J_USER=${3:-"neo4j"}
NEO4J_PASSWORD=${4:-"password"}
OPENAI_API_KEY=${5:-"sk-your-openai-key"}
JWT_SECRET=$(openssl rand -base64 32)

echo "=== Deployment Configuration ==="
echo "Project ID: $PROJECT_ID"
echo "Neo4j URI: $NEO4J_URI"
echo "Neo4j User: $NEO4J_USER"
echo "JWT Secret: Generated automatically"
echo "==============================="

# Set the project
echo "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com

# Create secrets in Secret Manager
echo "Setting up Secret Manager..."
for SECRET_NAME in neo4j-uri neo4j-user neo4j-password openai-api-key jwt-secret; do
    if ! gcloud secrets describe $SECRET_NAME >/dev/null 2>&1; then
        echo "Creating secret: $SECRET_NAME"
        case "$SECRET_NAME" in
            "neo4j-uri") VALUE="$NEO4J_URI" ;;
            "neo4j-user") VALUE="$NEO4J_USER" ;;
            "neo4j-password") VALUE="$NEO4J_PASSWORD" ;;
            "openai-api-key") VALUE="$OPENAI_API_KEY" ;;
            "jwt-secret") VALUE="$JWT_SECRET" ;;
        esac
        echo -n "$VALUE" | gcloud secrets create $SECRET_NAME --replication-policy="automatic" --data-file=-
    else
        echo "Secret $SECRET_NAME already exists, updating value..."
        case "$SECRET_NAME" in
            "neo4j-uri") VALUE="$NEO4J_URI" ;;
            "neo4j-user") VALUE="$NEO4J_USER" ;;
            "neo4j-password") VALUE="$NEO4J_PASSWORD" ;;
            "openai-api-key") VALUE="$OPENAI_API_KEY" ;;
            "jwt-secret") VALUE="$JWT_SECRET" ;;
        esac
        echo -n "$VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=-
    fi
done

# Build and deploy the container
echo "Building and deploying to Cloud Run..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/insight-journey

# Deploy to Cloud Run
gcloud run deploy insight-journey \
    --image gcr.io/$PROJECT_ID/insight-journey \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets="NEO4J_URI=neo4j-uri:latest,NEO4J_USER=neo4j-user:latest,NEO4J_PASSWORD=neo4j-password:latest,OPENAI_API_KEY=openai-api-key:latest,JWT_SECRET=jwt-secret:latest"

# Get the deployed URL
URL=$(gcloud run services describe insight-journey --platform managed --region us-central1 --format='value(status.url)')

echo "Deployment complete!"
echo "Your application is available at: $URL" 