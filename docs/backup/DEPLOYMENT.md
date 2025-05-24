# Insight Journey Backend Deployment Guide

## Simple GCP Deployment with Neo4j Aura

### Prerequisites
1. Google Cloud Account with billing enabled
2. Google Cloud SDK installed
3. Docker installed locally
4. Neo4j Aura account (https://neo4j.com/cloud/aura/)

### 1. Project Setup

```bash
# Create a new GCP project
gcloud projects create insight-journey --name="Insight Journey"

# Set the project as default
gcloud config set project insight-journey

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com
```

### 2. Neo4j Aura Setup

1. Go to https://neo4j.com/cloud/aura/
2. Create a new database
3. Choose the free tier or appropriate plan
4. Note down the connection URI and credentials

### 3. Application Configuration

Create a `.env` file:
```env
NEO4J_URI=your-aura-uri
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
PORT=8080
```

### 4. Docker Setup

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["python", "main.py"]
```

### 5. Cloud Build Setup

Create a `cloudbuild.yaml`:
```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/insight-journey:$COMMIT_SHA', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/insight-journey:$COMMIT_SHA']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'insight-journey'
      - '--image'
      - 'gcr.io/$PROJECT_ID/insight-journey:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'NEO4J_URI=$$NEO4J_URI,NEO4J_USER=$$NEO4J_USER,NEO4J_PASSWORD=$$NEO4J_PASSWORD'

images:
  - 'gcr.io/$PROJECT_ID/insight-journey:$COMMIT_SHA'
```

### 6. Deployment

#### 6.1 Set up secrets
```bash
# Store Neo4j credentials
echo -n "your-aura-uri" | gcloud secrets create neo4j-uri --data-file=-
echo -n "neo4j" | gcloud secrets create neo4j-user --data-file=-
echo -n "your-password" | gcloud secrets create neo4j-password --data-file=-
```

#### 6.2 Deploy using Cloud Build
```bash
# Trigger the build
gcloud builds submit --config cloudbuild.yaml
```

### 7. Monitoring

```bash
# Enable basic monitoring
gcloud services enable monitoring.googleapis.com

# Create log-based metrics
gcloud logging metrics create insight-journey-errors \
  --description="Count of error logs" \
  --log-filter="severity>=ERROR"
```

### 8. Cost Estimation

Monthly estimated costs (based on minimal usage):
- Cloud Run: ~$10
- Network egress: ~$5
- Neo4j Aura (Free tier): $0
- Total: ~$15/month

### 9. Next Steps

1. **Immediate Actions**
   - Set up Neo4j Aura database
   - Deploy the application
   - Test the endpoints

2. **Post-Deployment**
   - Verify Neo4j connection
   - Test all API endpoints
   - Set up basic monitoring

3. **Future Improvements**
   - Add more regions if needed
   - Implement auto-scaling
   - Set up CDN if required 