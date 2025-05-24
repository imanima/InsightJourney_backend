#!/bin/bash

# Exit on error
set -e

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if project ID is provided
if [ -z "$1" ]; then
    echo "Please provide a GCP project ID"
    echo "Usage: ./deploy_gcp.sh <project-id>"
    exit 1
fi

PROJECT_ID=$1

# Set the project
echo "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    vpcaccess.googleapis.com

# Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create insight-journey-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=$(openssl rand -base64 32)

# Create Cloud Storage bucket
echo "Creating Cloud Storage bucket..."
BUCKET_NAME="insight-journey-files-$PROJECT_ID"
gsutil mb -l us-central1 gs://$BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Create VPC connector
echo "Creating VPC connector..."
gcloud compute networks vpc-access connectors create insight-journey-vpc-connector \
    --network=default \
    --region=us-central1 \
    --range=10.8.0.0/28

# Create secrets in Secret Manager
echo "Creating secrets in Secret Manager..."
gcloud secrets create neo4j-uri --replication-policy="automatic"
gcloud secrets create neo4j-username --replication-policy="automatic"
gcloud secrets create neo4j-password --replication-policy="automatic"
gcloud secrets create openai-api-key --replication-policy="automatic"

# Prompt for secret values
echo "Please enter the following secret values:"
read -p "Neo4j URI: " NEO4J_URI
read -p "Neo4j Username: " NEO4J_USERNAME
read -p "Neo4j Password: " NEO4J_PASSWORD
read -p "OpenAI API Key: " OPENAI_API_KEY

# Store secrets
echo -n "$NEO4J_URI" | gcloud secrets versions add neo4j-uri --data-file=-
echo -n "$NEO4J_USERNAME" | gcloud secrets versions add neo4j-username --data-file=-
echo -n "$NEO4J_PASSWORD" | gcloud secrets versions add neo4j-password --data-file=-
echo -n "$OPENAI_API_KEY" | gcloud secrets versions add openai-api-key --data-file=-

# Get database connection string
DB_URI=$(gcloud sql instances describe insight-journey-db --format="get(connectionName)")

# Create Cloud Build trigger
echo "Creating Cloud Build trigger..."
gcloud builds triggers create github \
    --name="insight-journey-deploy" \
    --region="us-central1" \
    --repo-name="insight-journey" \
    --branch-pattern="^main$" \
    --build-config="backend/cloudbuild.yaml" \
    --substitutions="_DB_URI=$DB_URI,_NEO4J_URI=$NEO4J_URI,_NEO4J_USERNAME=$NEO4J_USERNAME,_NEO4J_PASSWORD=$NEO4J_PASSWORD,_OPENAI_API_KEY=$OPENAI_API_KEY"

echo "GCP setup completed successfully!"
echo "Next steps:"
echo "1. Push your code to the main branch to trigger the deployment"
echo "2. Monitor the deployment in the Cloud Build console"
echo "3. Once deployed, your application will be available at:"
echo "   https://insight-journey-backend-xxxxx-uc.a.run.app" 