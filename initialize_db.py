#!/usr/bin/env python
"""
Initialize Neo4j database and all required nodes for Insight Journey.
This script should be run during application deployment or setup.
"""

import os
import logging
import time
from scripts.initialize_taxonomies import initialize_taxonomies
from services.neo4j_service import Neo4jService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize the Neo4j database with required nodes and relationships.
    This function should be called when the application starts to ensure
    all taxonomies are properly set up and refreshed.
    """
    logger.info("Starting database initialization process")
    
    # Create Neo4j service
    neo4j_service = Neo4jService()
    
    # Wait for Neo4j to be available
    max_retries = 10
    retry_count = 0
    connected = False
    
    while not connected and retry_count < max_retries:
        try:
            with neo4j_service.driver.session() as session:
                session.run("RETURN 1")
                connected = True
                logger.info("Successfully connected to Neo4j")
        except Exception as e:
            retry_count += 1
            wait_time = retry_count * 2  # Exponential backoff
            logger.warning(f"Failed to connect to Neo4j (attempt {retry_count}/{max_retries}): {str(e)}")
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    if not connected:
        logger.error("Could not connect to Neo4j after maximum retries")
        return False
    
    # Initialize taxonomies
    try:
        logger.info("Initializing and refreshing taxonomies")
        initialize_taxonomies()
        logger.info("Taxonomy initialization complete")
        
        # Verify that taxonomies are loaded
        try:
            from services.taxonomy_service import taxonomy_service
            logger.info(f"Loaded {len(taxonomy_service.emotion_names)} emotions and {len(taxonomy_service.topic_names)} topics")
            
            if not taxonomy_service.emotion_names or not taxonomy_service.topic_names:
                # Force reload of taxonomies if they weren't loaded properly
                logger.warning("Taxonomies appear to be empty, forcing reload")
                taxonomy_service.load_taxonomies()
                logger.info(f"After reload: {len(taxonomy_service.emotion_names)} emotions and {len(taxonomy_service.topic_names)} topics")
        except Exception as e:
            logger.error(f"Error verifying taxonomy service: {str(e)}")
    except Exception as e:
        logger.error(f"Error initializing taxonomies: {str(e)}")
        return False
    
    logger.info("Database initialization complete")
    return True

if __name__ == "__main__":
    initialize_database() 