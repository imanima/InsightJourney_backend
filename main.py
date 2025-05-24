"""
Main FastAPI application entry point.
Imports and includes all route handlers and middleware.
"""

import os
import json
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, sessions_router, analysis_router
from routes.transcription_routes import router as transcription_router
from insights import insights_router  # Import the new insights router

# Configure logging - container-friendly configuration 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Only log to stdout/stderr for containers
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Insight Journey API",
    description="Backend API for therapy session analysis and insights",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://insight-journey.vercel.app",
    "https://app.insightjourney.ai"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API prefix
API_PREFIX = "/api/v1"

# Root endpoint for basic health check
@app.get("/")
async def root():
    """Root endpoint for basic health check"""
    return {"status": "ok", "message": "Insight Journey API is running"}

# Include routers - all routers now have their own prefixes
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(sessions_router, prefix=API_PREFIX)
app.include_router(analysis_router, prefix=API_PREFIX)
app.include_router(transcription_router, prefix=API_PREFIX)
app.include_router(insights_router, prefix=API_PREFIX)  # Add the insights router

# Health check endpoint
@app.get(f"{API_PREFIX}/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "healthy", "api_version": "1.0.0"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404, 
        content={"detail": f"The requested endpoint {request.url.path} was not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8080, 
        reload=True,
        log_level="info"
    ) 