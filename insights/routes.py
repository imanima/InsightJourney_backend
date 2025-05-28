"""
API routes for the Insights module.

These routes provide access to advanced insights generated from therapy session data.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import List, Dict, Any, Optional
from services import neo4j_service
from services.auth_service import get_current_user
from .service import InsightsService

# Initialize router
router = APIRouter(
    prefix="/insights",
    tags=["insights"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# Create insights service instance
insights_service = None


async def get_insights_service():
    """Get or create insights service"""
    global insights_service
    if insights_service is None:
        insights_service = InsightsService(neo4j_service)
    return insights_service


@router.get("/turning-point")
async def get_turning_point(
    emotion: str = Query("Anxiety", description="The emotion to track for turning points"),
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a turning point insight for when a specific emotion significantly changed.
    
    This identifies the session where the biggest positive change occurred.
    """
    user_id = current_user["userId"]
    result = service.calculate_turning_point(user_id, emotion)
    
    if not result:
        raise HTTPException(status_code=404, detail="No turning point found")
    
    return result


@router.get("/correlations")
async def get_correlations(
    limit: int = Query(5, description="Maximum number of correlations to return"),
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get correlations between emotions and topics.
    
    This identifies which topics tend to appear together with specific emotions.
    """
    user_id = current_user["userId"]
    results = service.calculate_correlations(user_id, limit)
    
    return {"correlations": results}


@router.get("/cascade-map")
async def get_insight_cascade(
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a cascade map showing how insights lead to other insights.
    
    This visualizes the connection between different insights over time.
    """
    user_id = current_user["userId"]
    result = service.build_insight_cascade(user_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="No insight cascade found")
    
    return result


@router.get("/future-prediction")
async def get_future_prediction(
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get predictions for future session topics based on previous patterns.
    
    Uses a Markov chain model to predict likely upcoming topics.
    """
    user_id = current_user["userId"]
    result = service.predict_future_focus(user_id)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Not enough session data to make predictions"
        )
    
    return result


@router.get("/challenge-persistence")
async def get_challenge_persistence(
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get insights about challenge persistence and achievement badges.
    
    Tracks how challenges persist over time and provides badge achievements.
    """
    user_id = current_user["userId"]
    results = service.track_challenge_persistence(user_id)
    
    return {"challenges": results}


@router.get("/therapist-snapshot")
async def get_therapist_snapshot(
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate a comprehensive therapist-friendly snapshot of progress.
    
    Includes emotion progress, breakthrough timeline, belief shifts,
    action item adherence, and next session forecast.
    """
    user_id = current_user["userId"]
    result = service.generate_therapist_snapshot(user_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Not enough data for therapist snapshot")
    
    return result


@router.post("/therapist-snapshot/reflection")
async def add_client_reflection(
    reflection: str = Body(..., embed=True),
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a client reflection to the therapist snapshot.
    
    This allows the client to add their own thoughts about therapy progress.
    """
    # This would update the snapshot with the client's reflection
    # For now we'll just return a success message
    return {"status": "success", "message": "Reflection added to therapist snapshot"}


@router.get("/all")
async def get_all_insights(
    service: InsightsService = Depends(get_insights_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all available insights for the current user.
    
    Returns a collection of the most relevant insights from all categories.
    """
    user_id = current_user["userId"]
    
    # Collect insights from all categories
    turning_point = service.calculate_turning_point(user_id)
    correlations = service.calculate_correlations(user_id, limit=3)
    cascade = service.build_insight_cascade(user_id)
    prediction = service.predict_future_focus(user_id)
    challenges = service.track_challenge_persistence(user_id)
    
    # Combine results
    results = {
        "turning_point": turning_point if turning_point else None,
        "correlations": correlations[:3] if correlations else [],
        "cascade_map": cascade if cascade else None,
        "future_prediction": prediction if prediction else None,
        "challenges": challenges[:3] if challenges else []
    }
    
    return results 