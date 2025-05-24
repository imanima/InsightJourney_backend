# Installation Guide

This guide will help you install and set up the Insight Journey platform.

## Prerequisites

- Python 3.11 or higher
- Neo4j database (running locally or accessible)
- OpenAI API key
- Git

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/your-org/insight-journey.git
cd insight-journey
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start Neo4j database:
```bash
# If using Docker:
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/insight_password \
    neo4j:latest

# Or if Neo4j is already installed:
neo4j start
```

6. Initialize the database:
```bash
python initialize_db.py
```

7. Start the application:
```bash
python run.py
```

## Verifying Installation

1. Check Neo4j is running:
```bash
curl http://localhost:7474
```

2. Check the API is running:
```bash
curl http://localhost:5001/api/v1/health
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Issues**
   - Verify Neo4j is running
   - Check connection credentials in .env
   - Ensure ports 7474 and 7687 are available

2. **Python Package Issues**
   - Try recreating the virtual environment
   - Check Python version compatibility
   - Update pip: `pip install --upgrade pip`

3. **Environment Variables**
   - Verify all required variables are set
   - Check for typos in variable names
   - Ensure values are properly formatted

### Getting Help

If you encounter issues not covered here:
1. Check the [FAQ](../FAQ.md)
2. Search existing issues
3. Create a new issue with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details 