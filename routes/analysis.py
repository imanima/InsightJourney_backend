"""
Analysis routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import uuid
from services import get_neo4j_service, get_session_service, get_auth_service
from services.analysis_service import analyze_transcript_and_extract
from services.session_service import SessionService
from routes.auth import User
from utils import get_current_user
import jwt

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analysis")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authentication dependency
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Get current user ID from JWT token"""
    try:
        auth_service = get_auth_service()
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        user_id_or_email = payload.get("sub")
        
        # If it's an email, get the user ID
        if "@" in str(user_id_or_email):
            neo4j_service = get_neo4j_service()
            user = neo4j_service.get_user_by_email(user_id_or_email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user["userId"]
        
        return user_id_or_email
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

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

class UpdateElementsRequest(BaseModel):
    """Request model for updating session elements"""
    elements: Dict[str, List[Dict[str, Any]]]

class UpdateElementsResponse(BaseModel):
    """Response model for updating session elements"""
    status: str
    message: str
    session_id: str

# Routes
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript(
    request: AnalysisRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Analyze a transcript and store results"""
    try:
        logger.info(f"Starting analysis for session {request.session_id}")
        logger.info(f"Transcript length: {len(request.transcript) if request.transcript else 0} characters")
        
        # Get session from database
        neo4j_service = get_neo4j_service()
        session_data = neo4j_service.get_session_data(request.session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found"
            )
        
        # Check if user owns this session
        if session_data.get("userId") != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Use transcript from request or session
        transcript = request.transcript or session_data.get("transcript", "")
        
        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transcript provided"
            )
        
        # Use analysis service to process transcript
        try:
            analysis_results = analyze_transcript_and_extract(transcript, user_id=current_user_id)
            
            if analysis_results.get("status") != "completed":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Analysis failed: {analysis_results.get('error', 'Unknown error')}"
                )
            
            # Extract elements from analysis results
            elements = analysis_results.get("elements", {})
            logger.info(f"Analysis completed successfully for session {request.session_id}")
            logger.info(f"Analysis results keys: {list(elements.keys())}")
            
            # Format the data for Neo4j storage as expected by save_session_analysis
            formatted_analysis_data = {}
            
            # Format emotions: [name, intensity, context, topics, timestamp]
            if "emotions" in elements:
                formatted_analysis_data["Emotions"] = [
                    [
                        emotion.get("name"),
                        emotion.get("intensity", 3),
                        emotion.get("context", ""),
                        emotion.get("topic"),
                        emotion.get("timestamp", "")
                    ]
                    for emotion in elements["emotions"]
                ]
            
            # Format beliefs: [id, name, description, impact, topics, timestamp]  
            if "beliefs" in elements:
                formatted_analysis_data["Beliefs"] = [
                    [
                        str(uuid.uuid4()),  # Generate unique ID
                        belief.get("name"),
                        belief.get("description", belief.get("text", "")),
                        belief.get("impact", ""),
                        belief.get("topic"),
                        belief.get("timestamp", "")
                    ]
                    for belief in elements["beliefs"]
                ]
            
            # Format action items: [id, name, description, topics, status]
            if "action_items" in elements:
                formatted_analysis_data["actionitems"] = [
                    [
                        str(uuid.uuid4()),  # Generate unique ID
                        action.get("name"),
                        action.get("description", action.get("text", "")),
                        action.get("topic"),
                        action.get("status", "hasn't started")
                    ]
                    for action in elements["action_items"]
                ]
            
            # Format challenges: [name, text, impact, topics]
            if "challenges" in elements:
                formatted_analysis_data["Challenges"] = [
                    [
                        challenge.get("name"),
                        challenge.get("description", challenge.get("text", "")),
                        challenge.get("impact", ""),
                        challenge.get("topic")
                    ]
                    for challenge in elements["challenges"]
                ]
            
            # Format insights: [name, text, context, topics]
            if "insights" in elements:
                formatted_analysis_data["Insights"] = [
                    [
                        insight.get("name"),
                        insight.get("description", insight.get("text", "")),
                        insight.get("context", ""),
                        insight.get("topic")
                    ]
                    for insight in elements["insights"]
                ]
            
            # Store the analysis results in the database using the proper Neo4j method
            try:
                success = neo4j_service.save_session_analysis(
                    session_id=request.session_id,
                    analysis_data=formatted_analysis_data,
                    user_id=current_user_id
                )
                if success:
                    logger.info(f"Successfully stored analysis results for session {request.session_id}")
                else:
                    logger.error(f"Failed to store analysis results for session {request.session_id}")
            except Exception as storage_error:
                logger.error(f"Failed to store analysis results: {str(storage_error)}")
                # Continue anyway, as we still have the results to return
            
            # Transform the results to match the expected format
            formatted_results = {
                "emotions": analysis_results.get("elements", {}).get("emotions", []),
                "insights": analysis_results.get("elements", {}).get("insights", []),
                "beliefs": analysis_results.get("elements", {}).get("beliefs", []),
                "action_items": analysis_results.get("elements", {}).get("action_items", []),
                "challenges": analysis_results.get("elements", {}).get("challenges", [])
            }
            
            return {
                "session_id": request.session_id,
                "status": "completed",
                "results": formatted_results,
                "created_at": datetime.now()
            }
            
        except Exception as analysis_error:
            logger.error(f"Analysis service error: {str(analysis_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {str(analysis_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis"
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
async def get_session_elements(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get session elements"""
    try:
        logger.info(f"Retrieving session elements for session {session_id}")
        
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Get session data with all relationships and elements
        session_data = neo4j_service.get_session_with_relationships(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Check if user owns this session
        if session_data.get("userId") != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Extract elements from session data
        elements = {
            "emotions": session_data.get("emotions", []),
            "insights": session_data.get("insights", []),
            "beliefs": session_data.get("beliefs", []),
            "action_items": session_data.get("actionitems", []),  # Note: Neo4j service uses "actionitems"
            "themes": [],  # Themes could be derived from topics
            "challenges": session_data.get("challenges", [])
        }
        
        # Process topics as themes if available
        topics = session_data.get("topics", [])
        for topic in topics:
            elements["themes"].append({
                "name": topic.get("name", ""),
                "confidence": topic.get("relevance", 0.9),  # Use relevance as confidence
                "description": topic.get("description", "")
            })
        
        logger.info(f"Retrieved {len(elements['emotions'])} emotions, {len(elements['insights'])} insights, {len(elements['beliefs'])} beliefs, {len(elements['action_items'])} action items, {len(elements['challenges'])} challenges for session {session_id}")
        
        return elements
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session elements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving session elements"
        )

@router.put("/{session_id}/elements", response_model=UpdateElementsResponse)
async def update_session_elements(
    session_id: str, 
    request: UpdateElementsRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update session elements"""
    try:
        logger.info(f"Updating session elements for session {session_id}")
        
        # Get Neo4j service
        neo4j_service = get_neo4j_service()
        
        # Verify session exists and user owns it
        session_data = neo4j_service.get_session_with_relationships(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Check if user owns this session
        if session_data.get("userId") != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Format elements for Neo4j storage (matching the format used in analyze endpoint)
        formatted_analysis_data = {}
        
        # Format emotions: [name, intensity, context, topics]
        if request.elements.get("emotions"):
            formatted_analysis_data["Emotions"] = [
                [
                    emotion.get("name", "Unnamed Emotion"),
                    emotion.get("intensity", 3),  # Default intensity
                    emotion.get("context", ""),
                    emotion.get("topic", "Personal Growth")  # Default topic
                ]
                for emotion in request.elements["emotions"]
            ]
        
        # Format beliefs: [id, name, text, impact, topics]
        if request.elements.get("beliefs"):
            formatted_analysis_data["Beliefs"] = [
                [
                    belief.get("id", str(uuid.uuid4())),  # Generate ID if not provided
                    belief.get("name", "Unnamed Belief"),
                    belief.get("description", belief.get("text", "")),  # Use text or description
                    belief.get("impact", "Medium"),  # Default impact
                    belief.get("topic", "Personal Growth")  # Default topic
                ]
                for belief in request.elements["beliefs"]
            ]
        
        # Format action items: [id, name, description, topics, status]
        if request.elements.get("action_items"):
            formatted_analysis_data["actionitems"] = [
                [
                    action.get("id", str(uuid.uuid4())),  # Generate ID if not provided
                    action.get("name", "Unnamed Action"),
                    action.get("description", ""),
                    action.get("topic", "Personal Growth"),  # Default topic
                    action.get("status", "Not Started")  # Default status
                ]
                for action in request.elements["action_items"]
            ]
        
        # Format insights: [name, text, context, topics]
        if request.elements.get("insights"):
            formatted_analysis_data["Insights"] = [
                [
                    insight.get("name", "Unnamed Insight"),
                    insight.get("description", insight.get("text", "")),  # Use text or description
                    insight.get("context", ""),
                    insight.get("topic", "Personal Growth")  # Default topic
                ]
                for insight in request.elements["insights"]
            ]
        
        # Format challenges: [name, text, impact, topics]
        if request.elements.get("challenges"):
            formatted_analysis_data["Challenges"] = [
                [
                    challenge.get("name", "Unnamed Challenge"),
                    challenge.get("description", challenge.get("text", "")),  # Use text or description
                    challenge.get("impact", "Medium"),  # Default impact
                    challenge.get("topic", "Personal Growth")  # Default topic
                ]
                for challenge in request.elements["challenges"]
            ]
        
        # Update elements using Neo4j service
        success = neo4j_service.update_session_with_elements(
            session_id=session_id,  # Use session_id directly as it's the graph ID
            elements=formatted_analysis_data,
            user_id=current_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update session elements"
            )
        
        logger.info(f"Successfully updated elements for session {session_id}")
        
        return UpdateElementsResponse(
            status="success",
            message=f"Successfully updated elements for session {session_id}",
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session elements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating session elements"
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