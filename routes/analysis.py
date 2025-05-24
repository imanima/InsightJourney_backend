"""
Analysis routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from services import get_neo4j_service
from fastapi.responses import JSONResponse
from routes.auth import User, oauth2_scheme
from utils import get_current_user

# Configure logger
logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(prefix="/analysis")

# Models
class AnalysisRequest(BaseModel):
    session_id: str
    transcript: Optional[str] = None

class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()

class AnalysisResults(BaseModel):
    emotions: List[Dict[str, Any]] = []
    insights: List[Dict[str, Any]] = []
    beliefs: List[Dict[str, Any]] = []
    action_items: List[Dict[str, Any]] = []
    themes: List[Dict[str, Any]] = []
    summary: Optional[str] = None
    timestamp: datetime = datetime.now()

class SessionElements(BaseModel):
    emotions: List[Dict[str, Any]] = []
    insights: List[Dict[str, Any]] = []
    beliefs: List[Dict[str, Any]] = []
    action_items: List[Dict[str, Any]] = []
    themes: List[Dict[str, Any]] = []
    challenges: List[Dict[str, Any]] = []

class ExportRequest(BaseModel):
    """Request model for Neo4j export endpoint"""
    session_id: str

class ExportResponse(BaseModel):
    """Response model for Neo4j export endpoint"""
    success: bool
    message: str
    elements_exported: Dict[str, int] = {}

# Routes
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript(request: AnalysisRequest):
    """Analyze a session transcript"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Mock analysis
        return {
            "session_id": request.session_id,
            "status": "completed",
            "results": {
                "emotions": [
                    {"name": "Joy", "intensity": 0.8},
                    {"name": "Frustration", "intensity": 0.4}
                ],
                "insights": [
                    {"text": "Client shows progress in managing anxiety"}
                ],
                "beliefs": [
                    {"text": "Client believes they need to be perfect"}
                ],
                "action_items": [
                    {"description": "Practice daily mindfulness"}
                ]
            },
            "created_at": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/status/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Mock analysis status
        return {
            "session_id": analysis_id,
            "status": "completed",
            "results": None,
            "created_at": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/{session_id}/results", response_model=AnalysisResults)
async def get_analysis_results(session_id: str):
    """Get analysis results for a session"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Mock analysis results
        return {
            "emotions": [
                {"name": "Joy", "intensity": 0.8},
                {"name": "Frustration", "intensity": 0.4}
            ],
            "insights": [
                {"text": "Client shows progress in managing anxiety"}
            ],
            "beliefs": [
                {"text": "Client believes they need to be perfect"}
            ],
            "action_items": [
                {"description": "Practice daily mindfulness"}
            ],
            "themes": [
                {"name": "Anxiety", "confidence": 0.9},
                {"name": "Personal Growth", "confidence": 0.8}
            ],
            "summary": "Client is making progress in managing anxiety through mindfulness practices.",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting analysis results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/{session_id}/elements", response_model=SessionElements)
async def get_session_elements(session_id: str):
    """Get session elements"""
    try:
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Mock session elements
        return {
            "emotions": [
                {"name": "Joy", "intensity": 0.8, "timestamp": datetime.now()},
                {"name": "Frustration", "intensity": 0.4, "timestamp": datetime.now()}
            ],
            "insights": [
                {
                    "text": "Client shows progress in managing anxiety",
                    "topic": "Personal Growth",
                    "timestamp": datetime.now()
                }
            ],
            "beliefs": [
                {
                    "text": "Client believes they need to be perfect",
                    "impact": "High",
                    "topic": "Self-Esteem",
                    "timestamp": datetime.now()
                }
            ],
            "action_items": [
                {
                    "description": "Practice daily mindfulness",
                    "priority": "High",
                    "status": "Pending",
                    "timestamp": datetime.now()
                }
            ],
            "themes": [
                {"name": "Anxiety", "confidence": 0.9},
                {"name": "Personal Growth", "confidence": 0.8}
            ],
            "challenges": [
                {
                    "name": "Public speaking anxiety",
                    "impact": "High",
                    "topic": "Career",
                    "timestamp": datetime.now()
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error getting session elements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

class Neo4jQueryRequest(BaseModel):
    """Request model for Neo4j query endpoint"""
    query: str
    parameters: Optional[Dict[str, Any]] = None

class Neo4jQueryResponse(BaseModel):
    """Response model for Neo4j query endpoint"""
    results: List[Dict[str, Any]]
    query: str
    execution_time: float

@router.post("/neo4j/query", response_model=Neo4jQueryResponse)
async def run_neo4j_query(request: Neo4jQueryRequest):
    """Run a Neo4j query through the API"""
    try:
        # Log the query for auditing
        logger.info(f"Executing Neo4j query via API: {request.query}")
        
        # Input validation
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
            
        # Security checks
        prohibited_operations = ["DELETE", "DETACH DELETE", "DROP"]
        for operation in prohibited_operations:
            if operation in request.query.upper():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operation '{operation}' is not allowed through this API endpoint"
                )
        
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Time the query execution
        start_time = datetime.now()
        
        # Execute the query
        results = neo4j_service.run_query(request.query, request.parameters)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if results is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to execute Neo4j query"
            )
            
        return {
            "results": results,
            "query": request.query,
            "execution_time": execution_time
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing Neo4j query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/export", response_model=ExportResponse)
async def export_to_neo4j(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Export session analysis data to Neo4j
    """
    try:
        neo4j_service = get_neo4j_service()
        
        # Get session to verify it exists
        session = neo4j_service.get_session_data(request.session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": f"Session {request.session_id} not found"}
            )
        
        # Get elements for the session
        elements = neo4j_service.get_session_elements(request.session_id)
        
        # Count elements by type
        element_counts = {
            "emotions": len(elements.get("emotions", [])),
            "beliefs": len(elements.get("beliefs", [])),
            "insights": len(elements.get("insights", [])),
            "challenges": len(elements.get("challenges", [])),
            "action_items": len(elements.get("action_items", []))
        }
        
        # Export to Neo4j (this part depends on your Neo4j service implementation)
        # This is a simplified example
        success = neo4j_service.update_session_with_elements(
            request.session_id, 
            elements,
            current_user.id
        )
        
        if success:
            return {
                "success": True,
                "message": "Session data exported to Neo4j successfully",
                "elements_exported": element_counts
            }
        else:
            return {
                "success": False,
                "message": "Failed to export session data to Neo4j",
                "elements_exported": {}
            }
            
    except Exception as e:
        logger.error(f"Error exporting to Neo4j: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error exporting to Neo4j: {str(e)}"}
        ) 