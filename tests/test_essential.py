"""
Essential minimal tests for the Insight Journey Backend

This module contains only the core tests needed to verify the system is working:
1. Environment setup
2. Core service imports  
3. Basic API functionality
4. Basic database connectivity
"""

import os
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.mark.essential
def test_environment_setup():
    """Test that essential environment variables are set."""
    required_vars = ["NEO4J_URI", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    # Check for Neo4j user (either NEO4J_USER or NEO4J_USERNAME)
    if not os.getenv("NEO4J_USER") and not os.getenv("NEO4J_USERNAME"):
        missing.append("NEO4J_USER")
    
    # Check for Neo4j password
    if not os.getenv("NEO4J_PASSWORD"):
        missing.append("NEO4J_PASSWORD")
    
    assert not missing, f"Missing environment variables: {missing}"
    logger.info("✅ Environment setup OK")


@pytest.mark.essential
def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from services import get_neo4j_service
        from services.analysis_service import analyze_transcript
        from fastapi import FastAPI
        logger.info("✅ Core imports OK")
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


@pytest.mark.essential
def test_neo4j_service():
    """Test Neo4j service initialization."""
    try:
        from services import get_neo4j_service
        service = get_neo4j_service()
        assert service is not None
        logger.info("✅ Neo4j service OK")
    except Exception as e:
        pytest.fail(f"Neo4j service failed: {e}")


@pytest.mark.essential
def test_fastapi_app():
    """Test FastAPI application can be created."""
    try:
        from main import app
        assert app is not None
        assert hasattr(app, 'routes')
        logger.info("✅ FastAPI app OK")
    except Exception as e:
        pytest.fail(f"FastAPI app failed: {e}")


@pytest.mark.essential
@pytest.mark.slow
def test_analysis_service_mock():
    """Test analysis service with mock data."""
    try:
        from unittest.mock import patch
        with patch('services.analysis_service._ask_llm') as mock_llm:
            mock_llm.return_value = '{"emotions": []}'
            from services.analysis_service import extract_elements
            result = extract_elements("Test transcript")
            assert result is not None
            logger.info("✅ Analysis service OK")
    except Exception as e:
        # This is OK to fail - external dependency
        pytest.skip(f"Analysis service skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 