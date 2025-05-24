# Insight Journey Documentation

## Documentation

All documentation is now consolidated in a single file:
- [Comprehensive Documentation](./DOCUMENTATION.md)

## Project URL

Your application is deployed at:
- https://insight-journey-556782120038.us-central1.run.app

## Quick Commands

### Local Development
```bash
# Run locally
uvicorn main:app --reload --port 8080
```

### Deployment
```bash
# Deploy to GCP
./quickdeploy.sh
```

### Monitoring
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=insight-journey" --limit 20
``` 