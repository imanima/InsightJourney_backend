"""
Minimal pytest configuration for Insight Journey Backend tests
"""

import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Auto-setup test environment variables."""
    # Set test environment variables if not already set
    if not os.getenv("NEO4J_USER"):
        os.environ["NEO4J_USER"] = "neo4j"
    if not os.getenv("JWT_SECRET"):
        os.environ["JWT_SECRET"] = "test-secret-key"


@pytest.fixture
def test_transcript():
    """Provide a simple test transcript."""
    return """
    Therapist: How are you feeling today?
    Client: I'm feeling anxious about work.
    Therapist: Can you tell me more about that?
    Client: I have a big presentation coming up.
    """


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "essential: Essential tests for basic functionality")
    config.addinivalue_line("markers", "slow: Tests that take a long time to run")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "requires_neo4j: Tests requiring Neo4j connection")
    config.addinivalue_line("markers", "requires_openai: Tests requiring OpenAI API") 