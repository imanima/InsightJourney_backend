#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
  source .env
fi

# Default values if not set
PROJECT_ID=${PROJECT_ID:-"insightjourney-api"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"insight-journey"}

# Check if required environment variables are set
required_vars=(
  "NEO4J_URI"
  "NEO4J_USERNAME"
  "NEO4J_PASSWORD"
  "FLASK_SECRET_KEY"
)

# Verify environment variables
missing_vars=0
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Error: $var is not set"
    missing_vars=$((missing_vars + 1))
  fi
done

if [ $missing_vars -gt 0 ]; then
  echo "Please set the required environment variables and try again."
  exit 1
fi

echo "===================================================="
echo "         AUTHENTICATION FIX DEPLOYMENT"
echo "===================================================="
echo "PROJECT_ID: $PROJECT_ID"
echo "REGION: $REGION"
echo "SERVICE_NAME: $SERVICE_NAME"
echo "NEO4J_URI: $NEO4J_URI"
echo "NEO4J_USERNAME: $NEO4J_USERNAME"
echo "FLASK_SECRET_KEY: [MASKED]"
echo "===================================================="

# Confirm before proceeding
read -p "Do you want to update the Cloud Run service? (y/n) " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
  echo "Deployment canceled."
  exit 0
fi

echo "Updating Cloud Run service with environment variables..."

# Update Cloud Run service with the correct environment variables
gcloud run services update $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --set-env-vars="\
NEO4J_URI=$NEO4J_URI,\
NEO4J_USERNAME=$NEO4J_USERNAME,\
NEO4J_PASSWORD=$NEO4J_PASSWORD,\
FLASK_SECRET_KEY=$FLASK_SECRET_KEY,\
FLASK_ENV=production"

echo "Cloud Run service update completed successfully!"
echo "Testing authentication after deployment..."

# Wait a moment for the service to update
sleep 5

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

# Test the health endpoint
echo "Testing health endpoint..."
curl -s "$SERVICE_URL/api/v1/health" | jq .

echo "Authentication fix deployment complete!"
echo "Service URL: $SERVICE_URL"
echo ""
echo "To verify the fix works, run the following command:"
echo "python verify_login.py" 