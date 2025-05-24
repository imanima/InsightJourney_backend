"""
Pydantic models for the Insights module.

These models define the data structures for different insight types that can be
generated from therapy session data.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class InsightBase(BaseModel):
    """Base model for all insights"""
    id: Optional[str] = None
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    name: str
    description: str

class TurningPointInsight(InsightBase):
    """Model for turning point insights that show when emotions significantly changed"""
    turning_date: datetime
    emotion_name: str
    previous_intensity: float
    current_intensity: float
    insight_id: Optional[str] = None
    insight_name: Optional[str] = None
    sessions_before: Optional[List[str]] = None
    sessions_after: Optional[List[str]] = None

class CorrelationInsight(InsightBase):
    """Model for emotion and topic correlations"""
    emotion_name: str
    topic_name: str
    correlation_percentage: float
    occurrence_count: int
    confidence_score: float

class InsightNodeData(BaseModel):
    """Node data for insight cascade map"""
    id: str
    name: str
    date: datetime
    description: Optional[str] = None

class InsightEdgeData(BaseModel):
    """Edge data for insight cascade map"""
    source: str
    target: str
    strength: float = 1.0

class InsightCascadeMap(InsightBase):
    """Model for tracking how insights lead to other insights"""
    nodes: List[InsightNodeData]
    edges: List[InsightEdgeData]
    root_insight_id: str

class TopicPrediction(BaseModel):
    """Model for a single topic prediction"""
    topic_name: str
    probability: float
    related_emotions: List[Dict[str, float]] = []

class FutureFocusPrediction(InsightBase):
    """Model for predicting future topics based on Markov chains"""
    predictions: List[TopicPrediction]
    confidence_score: float
    based_on_sessions: List[str]
    
class ChallengeBadge(BaseModel):
    """Model for achievement badges earned by overcoming challenges"""
    id: str
    name: str
    description: str
    earned_at: datetime
    challenge_id: str
    challenge_name: str
    session_count: int
    
class ChallengePersistenceInsight(InsightBase):
    """Model for tracking challenge persistence and achievements"""
    challenge_id: str
    challenge_name: str
    first_appearance: datetime
    persistence_days: int
    session_count: int
    current_status: str
    badges_earned: List[ChallengeBadge] = []
    progress_percentage: float

class TherapistSnapshotSection(BaseModel):
    """Section of the therapist snapshot"""
    title: str
    data: Dict[str, Any]
    visualization_type: str
    
class TherapistSnapshot(InsightBase):
    """Comprehensive therapist-friendly summary of progress"""
    progress_overview: TherapistSnapshotSection
    breakthrough_timeline: TherapistSnapshotSection
    belief_shifts: TherapistSnapshotSection
    action_item_adherence: TherapistSnapshotSection
    next_session_forecast: Optional[TherapistSnapshotSection] = None
    client_reflection: Optional[str] = None
    start_date: datetime
    end_date: datetime
    session_count: int 