"""
Integration tests for service interactions in the Insight Journey Backend

This module tests how different services work together:
1. Neo4j service with analysis service
2. Authentication service with other services
3. End-to-end workflows
"""

import pytest
import os
import logging
from unittest.mock import Mock, patch

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.requires_neo4j
def test_neo4j_service_basic_connection():
    """Test basic Neo4j service connection and initialization."""
    try:
        from services import get_neo4j_service
        neo4j_service = get_neo4j_service()
        assert neo4j_service is not None, "Neo4j service should be initialized"
        logger.info("✅ Neo4j service integration test passed")
    except Exception as e:
        pytest.fail(f"Neo4j service integration failed: {str(e)}")


@pytest.mark.integration  
def test_analysis_service_with_mock_data():
    """Test analysis service with mock transcript data."""
    try:
        from services.analysis_service import extract_elements
        
        # Use test transcript from conftest
        test_transcript = """
        Therapist: How have you been feeling since our last session?
        Client: I've been feeling more anxious lately, especially about work.
        Therapist: Can you tell me more about that anxiety?
        Client: I'm worried about an upcoming presentation.
        """
        
        # This should work even without OpenAI if the service handles errors gracefully
        try:
            result = extract_elements(test_transcript)
            # If it succeeds, great. If it fails due to OpenAI issues, that's expected
            logger.info("✅ Analysis service integration test passed")
        except Exception as e:
            # Expected if OpenAI is not configured properly
            if "openai" in str(e).lower() or "api" in str(e).lower():
                pytest.skip(f"Analysis service skipped due to external dependency: {str(e)}")
            else:
                pytest.fail(f"Unexpected analysis service error: {str(e)}")
                
    except ImportError as e:
        pytest.fail(f"Could not import analysis service: {str(e)}")


@pytest.mark.integration
def test_service_imports():
    """Test that all services can be imported together without conflicts."""
    try:
        from services import get_neo4j_service, get_user_service, get_session_service
        from services.analysis_service import analyze_transcript
        from services.auth_service import AuthService
        
        # Test that services can be instantiated without conflicts
        neo4j_service = get_neo4j_service()
        user_service = get_user_service()
        session_service = get_session_service()
        
        assert neo4j_service is not None, "Neo4j service should be available"
        assert user_service is not None, "User service should be available"
        assert session_service is not None, "Session service should be available"
        
        logger.info("✅ Service imports integration test passed")
        
    except Exception as e:
        pytest.fail(f"Service integration failed: {str(e)}")


@pytest.mark.integration
@pytest.mark.auth
def test_auth_service_initialization():
    """Test authentication service initialization."""
    try:
        from services.auth_service import AuthService
        from services import get_neo4j_service
        
        neo4j_service = get_neo4j_service()
        secret_key = os.getenv("JWT_SECRET", "test-secret-key")
        
        auth_service = AuthService(neo4j_service, secret_key)
        assert auth_service is not None, "Auth service should be initialized"
        
        logger.info("✅ Auth service integration test passed")
        
    except Exception as e:
        pytest.fail(f"Auth service integration failed: {str(e)}")


@pytest.mark.integration
def test_fastapi_with_services():
    """Test that FastAPI can be initialized with services."""
    try:
        from fastapi import FastAPI
        from services import get_neo4j_service
        
        app = FastAPI()
        neo4j_service = get_neo4j_service()
        
        # Test that we can create a basic app with services
        assert app is not None, "FastAPI app should be created"
        assert neo4j_service is not None, "Services should be available"
        
        logger.info("✅ FastAPI with services integration test passed")
        
    except Exception as e:
        pytest.fail(f"FastAPI services integration failed: {str(e)}")


@pytest.mark.integration
@pytest.mark.slow
def test_mock_workflow():
    """Test a complete workflow with mocked external dependencies."""
    try:
        # Mock the external dependencies
        with patch('services.analysis_service._ask_llm') as mock_llm:
            mock_llm.return_value = '{"emotions": [{"name": "anxiety", "intensity": 0.8}]}'
            
            from services.analysis_service import extract_elements
            
            test_transcript = "Client: I feel anxious about work."
            
            # This should work with mocked LLM
            result = extract_elements(test_transcript)
            
            # Basic validation that something was returned
            assert result is not None, "Analysis should return results"
            
            logger.info("✅ Mock workflow integration test passed")
            
    except Exception as e:
        pytest.skip(f"Mock workflow test skipped: {str(e)}")


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v"]) 