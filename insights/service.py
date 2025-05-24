"""
Service module for the Insights feature.

This module contains functions for calculating various insights from therapy session data.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
from neo4j import GraphDatabase
from .utils import (
    generate_insight_id,
    calculate_percentage,
    detect_significant_change,
    markov_chain_prediction,
    calculate_correlation,
    format_turning_point_description,
    format_correlation_description,
    get_emotion_emoji,
    generate_cypher_query_turning_point,
    generate_cypher_query_correlation,
    generate_cypher_query_insight_cascade,
    generate_cypher_query_challenge_persistence
)

logger = logging.getLogger(__name__)

class InsightsService:
    """Service for generating insights from therapy session data"""
    
    def __init__(self, neo4j_service):
        """Initialize with a Neo4j service instance"""
        self.neo4j = neo4j_service
        self.logger = logging.getLogger(__name__)
    
    async def calculate_turning_point(self, user_id: str, emotion_name: str = "Anxiety") -> Dict[str, Any]:
        """
        Calculate a turning point where an emotion significantly decreased
        
        Args:
            user_id: The user ID to calculate for
            emotion_name: The emotion to track (default is Anxiety)
            
        Returns:
            Dictionary with turning point data or empty dict if none found
        """
        try:
            query = generate_cypher_query_turning_point(emotion_name, threshold=1.0)
            
            # Modify query to filter by user
            user_filter_query = query.replace(
                "MATCH (s:Session)",
                f"MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)"
            )
            
            result = await self.neo4j.run_query(user_filter_query)
            
            if not result or len(result) == 0:
                self.logger.info(f"No turning point found for user {user_id} and emotion {emotion_name}")
                return {}
            
            turning_point = result[0]
            
            # Find any insight that occurred in the same session
            session_id = turning_point.get("session_id")
            insight_query = f"""
            MATCH (s:Session {{id: '{session_id}'}})-[:HAS_INSIGHT]->(i:Insight)
            RETURN i.id as insight_id, i.name as insight_name
            LIMIT 1
            """
            
            insight_result = await self.neo4j.run_query(insight_query)
            insight_id = None
            insight_name = None
            
            if insight_result and len(insight_result) > 0:
                insight_id = insight_result[0].get("insight_id")
                insight_name = insight_result[0].get("insight_name")
            
            # Format the description
            description = format_turning_point_description(
                emotion=emotion_name,
                date=turning_point.get("turning_date"),
                previous_intensity=turning_point.get("previous_intensity"),
                current_intensity=turning_point.get("current_intensity"),
                insight_name=insight_name
            )
            
            # Get sessions before and after
            sessions_query = f"""
            MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)
            WHERE datetime(s.date) <= datetime('{turning_point.get("turning_date")}')
            RETURN s.id as session_id
            ORDER BY s.date DESC
            LIMIT 5
            """
            
            sessions_before = await self.neo4j.run_query(sessions_query)
            sessions_before_ids = [s.get("session_id") for s in sessions_before] if sessions_before else []
            
            sessions_after_query = f"""
            MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)
            WHERE datetime(s.date) > datetime('{turning_point.get("turning_date")}')
            RETURN s.id as session_id
            ORDER BY s.date ASC
            LIMIT 5
            """
            
            sessions_after = await self.neo4j.run_query(sessions_after_query)
            sessions_after_ids = [s.get("session_id") for s in sessions_after] if sessions_after else []
            
            # Construct result
            return {
                "id": generate_insight_id("TURN"),
                "user_id": user_id,
                "name": f"{emotion_name} Turning Point",
                "description": description,
                "created_at": datetime.now().isoformat(),
                "turning_date": turning_point.get("turning_date"),
                "emotion_name": emotion_name,
                "previous_intensity": turning_point.get("previous_intensity"),
                "current_intensity": turning_point.get("current_intensity"),
                "insight_id": insight_id,
                "insight_name": insight_name,
                "sessions_before": sessions_before_ids,
                "sessions_after": sessions_after_ids
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating turning point: {str(e)}")
            return {}
    
    async def calculate_correlations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Calculate correlations between emotions and topics
        
        Args:
            user_id: The user ID to calculate for
            limit: Maximum number of correlations to return
            
        Returns:
            List of correlation dictionaries
        """
        try:
            # Modify the query to filter by user
            query = generate_cypher_query_correlation()
            user_filter_query = query.replace(
                "MATCH (s:Session)",
                f"MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)"
            )
            
            # Replace the LIMIT with our parameter
            user_filter_query = user_filter_query.replace(
                "LIMIT 10",
                f"LIMIT {limit}"
            )
            
            result = await self.neo4j.run_query(user_filter_query)
            
            if not result:
                return []
            
            correlations = []
            for r in result:
                emotion = r.get("emotion")
                topic = r.get("topic")
                correlation_percentage = r.get("correlation_percentage")
                
                if correlation_percentage < 50:  # Only include strong correlations
                    continue
                    
                # Calculate confidence based on sample size
                correlation_pct, confidence = calculate_correlation(
                    r.get("together_count"),
                    r.get("emotion_count"),
                    r.get("topic_count"),
                    r.get("total_sessions")
                )
                
                description = format_correlation_description(
                    emotion=emotion,
                    topic=topic,
                    percentage=correlation_pct
                )
                
                correlations.append({
                    "id": generate_insight_id("CORR"),
                    "user_id": user_id,
                    "name": f"{emotion} × {topic} Correlation",
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "emotion_name": emotion,
                    "topic_name": topic,
                    "correlation_percentage": correlation_pct,
                    "occurrence_count": r.get("together_count"),
                    "confidence_score": confidence
                })
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error calculating correlations: {str(e)}")
            return []
    
    async def build_insight_cascade(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Build a cascade map showing how insights lead to other insights
        
        Args:
            user_id: The user ID to calculate for
            
        Returns:
            Dictionary with nodes and edges for visualization
        """
        try:
            # Modify the query to filter by user
            query = generate_cypher_query_insight_cascade()
            user_filter_query = query.replace(
                "MATCH path=(i1:Insight)",
                f"MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)-[:HAS_INSIGHT]->(i:Insight)\n"
                f"WITH collect(i) as insights\n"
                f"UNWIND insights as i1\n"
                f"MATCH path=(i1)"
            )
            
            result = await self.neo4j.run_query(user_filter_query)
            
            if not result or len(result) == 0:
                return None
            
            # Process results into nodes and edges
            nodes = {}  # Use dict to deduplicate nodes
            edges = []
            
            for r in result:
                # Add source node
                source_id = r.get("source_id")
                if source_id not in nodes:
                    nodes[source_id] = {
                        "id": source_id,
                        "name": r.get("source_name"),
                        "date": r.get("source_date")
                    }
                
                # Add target node
                target_id = r.get("target_id")
                if target_id not in nodes:
                    nodes[target_id] = {
                        "id": target_id,
                        "name": r.get("target_name"),
                        "date": r.get("target_date")
                    }
                
                # Add edge
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "strength": 1.0 / r.get("distance")  # Closer nodes have stronger connections
                })
            
            # Find root node (the one with most outgoing connections)
            node_connections = {}
            for edge in edges:
                source = edge["source"]
                node_connections[source] = node_connections.get(source, 0) + 1
            
            root_insight_id = max(node_connections.items(), key=lambda x: x[1])[0] if node_connections else None
            
            if not root_insight_id and nodes:
                # Fallback: use earliest insight as root
                root_insight_id = min(nodes.values(), key=lambda x: x["date"])["id"]
            
            return {
                "id": generate_insight_id("CASC"),
                "user_id": user_id,
                "name": "Insight Cascade Map",
                "description": "Map showing how insights connect and lead to each other",
                "created_at": datetime.now().isoformat(),
                "nodes": list(nodes.values()),
                "edges": edges,
                "root_insight_id": root_insight_id
            }
            
        except Exception as e:
            self.logger.error(f"Error building insight cascade: {str(e)}")
            return None
    
    async def predict_future_focus(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Predict future topics based on topic transition patterns
        
        Args:
            user_id: The user ID to calculate for
            
        Returns:
            Dictionary with topic predictions
        """
        try:
            # Get topic sequence from sessions
            query = f"""
            MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)-[:HAS_TOPIC]->(t:Topic)
            WITH s, t
            ORDER BY s.date
            RETURN s.id as session_id, collect(t.name) as topics
            ORDER BY s.date
            """
            
            result = await self.neo4j.run_query(query)
            
            if not result or len(result) < 3:  # Need at least 3 sessions for predictions
                return None
            
            # Build transition matrix
            transitions = {}
            prev_topics = None
            session_ids = []
            
            for r in result:
                session_ids.append(r.get("session_id"))
                topics = r.get("topics")
                
                if prev_topics:
                    for prev_topic in prev_topics:
                        if prev_topic not in transitions:
                            transitions[prev_topic] = {}
                        
                        for curr_topic in topics:
                            transitions[prev_topic][curr_topic] = transitions[prev_topic].get(curr_topic, 0) + 1
                
                prev_topics = topics
            
            if not transitions:
                return None
            
            # Make predictions using the latest topics
            latest_topics = result[-1].get("topics")
            predictions = []
            
            for topic in latest_topics:
                if topic in transitions:
                    topic_predictions = markov_chain_prediction(transitions, topic)
                    
                    for next_topic, probability in topic_predictions.items():
                        if probability > 0.2:  # Only include predictions with reasonable probability
                            # Get related emotions for this topic
                            emotion_query = f"""
                            MATCH (t:Topic {{name: '{next_topic}'}})<-[:HAS_TOPIC]-(s:Session)-[:HAS_EMOTION]->(e:Emotion)
                            WITH e.name as emotion, avg(r.intensity) as avg_intensity
                            ORDER BY avg_intensity DESC
                            LIMIT 3
                            RETURN emotion, avg_intensity
                            """
                            
                            emotion_result = await self.neo4j.run_query(emotion_query)
                            related_emotions = []
                            
                            if emotion_result:
                                for er in emotion_result:
                                    related_emotions.append({
                                        er.get("emotion"): er.get("avg_intensity")
                                    })
                            
                            predictions.append({
                                "topic_name": next_topic,
                                "probability": probability,
                                "related_emotions": related_emotions
                            })
            
            # Sort by probability
            predictions.sort(key=lambda x: x["probability"], reverse=True)
            
            # Get overall confidence based on number of sessions and transitions
            confidence_score = min(1.0, len(result) / 10)  # Max confidence at 10+ sessions
            
            return {
                "id": generate_insight_id("PRED"),
                "user_id": user_id,
                "name": "Future Focus Prediction",
                "description": "Predictions of topics likely to emerge in upcoming sessions",
                "created_at": datetime.now().isoformat(),
                "predictions": predictions[:5],  # Top 5 predictions
                "confidence_score": confidence_score,
                "based_on_sessions": session_ids[-5:]  # Last 5 sessions used
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting future focus: {str(e)}")
            return None
    
    async def track_challenge_persistence(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Track challenge persistence and badge achievements
        
        Args:
            user_id: The user ID to track for
            
        Returns:
            List of challenge persistence insights
        """
        try:
            # Modify query to filter by user
            query = generate_cypher_query_challenge_persistence()
            user_filter_query = query.replace(
                "MATCH (c:Challenge)",
                f"MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)-[:HAS_CHALLENGE]->(c:Challenge)"
            )
            
            result = await self.neo4j.run_query(user_filter_query)
            
            if not result:
                return []
            
            # Calculate persistence insights
            insights = []
            for r in result:
                challenge_id = r.get("challenge_id")
                challenge_name = r.get("challenge_name")
                session_count = r.get("session_count")
                persistence_days = r.get("persistence_days")
                
                # Check if challenge is still active
                last_date = r.get("last_date")
                last_date_obj = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
                days_since_last = (datetime.now() - last_date_obj).days
                
                current_status = "active" if days_since_last < 30 else "inactive"
                
                # Calculate progress percentage (inverse of persistence)
                # More sessions with same challenge = less progress
                if session_count <= 2:
                    progress_percentage = 75  # Just appeared
                elif session_count <= 4:
                    progress_percentage = 50  # Working on it
                elif session_count <= 6:
                    progress_percentage = 25  # Struggling
                else:
                    progress_percentage = 10  # Stuck
                
                # Check for badges
                badges = []
                
                # Add badges based on challenge status and progress
                if session_count >= 3 and current_status == "inactive":
                    # Challenge overcome badge
                    badges.append({
                        "id": generate_insight_id("BADGE"),
                        "name": "Challenge Overcome",
                        "description": f"Successfully overcame the challenge '{challenge_name}'",
                        "earned_at": last_date,
                        "challenge_id": challenge_id,
                        "challenge_name": challenge_name,
                        "session_count": session_count
                    })
                elif session_count >= 5:
                    # Persistent worker badge
                    badges.append({
                        "id": generate_insight_id("BADGE"),
                        "name": "Persistent Worker",
                        "description": f"Consistently working on the challenge '{challenge_name}'",
                        "earned_at": datetime.now().isoformat(),
                        "challenge_id": challenge_id,
                        "challenge_name": challenge_name,
                        "session_count": session_count
                    })
                
                # Create insight
                insights.append({
                    "id": generate_insight_id("CHAL"),
                    "user_id": user_id,
                    "name": f"Challenge Persistence: {challenge_name}",
                    "description": f"Track progress on the challenge '{challenge_name}'",
                    "created_at": datetime.now().isoformat(),
                    "challenge_id": challenge_id,
                    "challenge_name": challenge_name,
                    "first_appearance": r.get("first_date"),
                    "persistence_days": persistence_days,
                    "session_count": session_count,
                    "current_status": current_status,
                    "badges_earned": badges,
                    "progress_percentage": progress_percentage
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error tracking challenge persistence: {str(e)}")
            return []
    
    async def generate_therapist_snapshot(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a comprehensive therapist-friendly snapshot
        
        Args:
            user_id: The user ID to generate for
            
        Returns:
            Dictionary with therapist snapshot data
        """
        try:
            # Get user sessions
            sessions_query = f"""
            MATCH (u:User {{userId: '{user_id}'}})-[:HAS_SESSION]->(s:Session)
            RETURN s.id as session_id, s.date as date
            ORDER BY s.date DESC
            LIMIT 6
            """
            
            sessions_result = await self.neo4j.run_query(sessions_query)
            
            if not sessions_result or len(sessions_result) == 0:
                return None
            
            session_ids = [s.get("session_id") for s in sessions_result]
            start_date = sessions_result[-1].get("date")
            end_date = sessions_result[0].get("date")
            
            # 1. Progress at a glance - top 3 emotions
            emotions_query = f"""
            MATCH (s:Session)-[r:HAS_EMOTION]->(e:Emotion)
            WHERE s.id IN {session_ids}
            WITH e.name as emotion, collect(r.intensity) as intensities
            WITH emotion, intensities, 
                 intensities[0] as latest,
                 intensities[size(intensities)-1] as earliest
            RETURN emotion, latest, earliest, (latest - earliest) as change
            ORDER BY abs(change) DESC
            LIMIT 3
            """
            
            emotions_result = await self.neo4j.run_query(emotions_query)
            
            progress_data = {}
            if emotions_result:
                for e in emotions_result:
                    progress_data[e.get("emotion")] = {
                        "latest": e.get("latest"),
                        "earliest": e.get("earliest"),
                        "change": e.get("change")
                    }
            
            # 2. Breakthrough timeline
            breakthrough_query = f"""
            MATCH (c:Challenge)<-[:HAS_CHALLENGE]-(s1:Session)
            WHERE s1.id IN {session_ids}
            WITH c, min(s1.date) as first_appearance
            OPTIONAL MATCH (c)<-[:RELATES_TO]-(i:Insight)<-[:HAS_INSIGHT]-(s2:Session)
            WHERE s2.id IN {session_ids}
            WITH c, first_appearance, min(s2.date) as insight_date
            RETURN c.name as challenge, 
                   first_appearance,
                   insight_date,
                   CASE WHEN insight_date IS NOT NULL 
                        THEN duration.between(datetime(first_appearance), datetime(insight_date)).days 
                        ELSE NULL 
                   END as days_to_insight
            ORDER BY days_to_insight
            """
            
            breakthrough_result = await self.neo4j.run_query(breakthrough_query)
            
            breakthrough_data = {}
            if breakthrough_result:
                for b in breakthrough_result:
                    challenge = b.get("challenge")
                    breakthrough_data[challenge] = {
                        "first_appearance": b.get("first_appearance"),
                        "insight_date": b.get("insight_date"),
                        "days_to_insight": b.get("days_to_insight")
                    }
            
            # 3. Belief shifts
            belief_query = f"""
            MATCH (s:Session)-[r:HAS_BELIEF]->(b:Belief)
            WHERE s.id IN {session_ids}
            WITH b.name as belief, collect({{session: s.id, date: s.date, valence: r.valence}}) as appearances
            RETURN belief, appearances
            ORDER BY size(appearances) DESC
            LIMIT 5
            """
            
            belief_result = await self.neo4j.run_query(belief_query)
            
            belief_data = {}
            if belief_result:
                for b in belief_result:
                    belief = b.get("belief")
                    appearances = b.get("appearances")
                    
                    # Track valence over time to see shifts
                    belief_data[belief] = appearances
            
            # 4. Action item adherence
            action_query = f"""
            MATCH (s:Session)-[:HAS_ACTION_ITEM]->(a:ActionItem)
            WHERE s.id IN {session_ids}
            WITH a.name as action, a.completed as completed, a.date_created as created, a.date_completed as completed_date
            RETURN 
                count(action) as total_actions,
                sum(CASE WHEN completed THEN 1 ELSE 0 END) as completed_actions,
                max(duration.between(datetime(created), datetime(completed_date)).days) as longest_streak
            """
            
            action_result = await self.neo4j.run_query(action_query)
            
            action_data = {}
            if action_result and len(action_result) > 0:
                action_data = {
                    "total_actions": action_result[0].get("total_actions", 0),
                    "completed_actions": action_result[0].get("completed_actions", 0),
                    "completion_rate": calculate_percentage(
                        action_result[0].get("completed_actions", 0),
                        action_result[0].get("total_actions", 1)
                    ),
                    "longest_streak": action_result[0].get("longest_streak", 0)
                }
            
            # 5. Next session forecast (optional)
            forecast = await self.predict_future_focus(user_id)
            forecast_data = {}
            
            if forecast and forecast.get("predictions"):
                forecast_data = {
                    "likely_topics": [p.get("topic_name") for p in forecast.get("predictions")[:3]],
                    "confidence": forecast.get("confidence_score")
                }
            
            # Create the therapist snapshot
            return {
                "id": generate_insight_id("THER"),
                "user_id": user_id,
                "name": "Therapy Value Snapshot",
                "description": "Comprehensive summary of therapy progress for therapist review",
                "created_at": datetime.now().isoformat(),
                "progress_overview": {
                    "title": "Progress at a Glance",
                    "data": progress_data,
                    "visualization_type": "emotion_chart"
                },
                "breakthrough_timeline": {
                    "title": "Breakthrough Timeline",
                    "data": breakthrough_data,
                    "visualization_type": "timeline"
                },
                "belief_shifts": {
                    "title": "Belief Shifts",
                    "data": belief_data,
                    "visualization_type": "heatmap"
                },
                "action_item_adherence": {
                    "title": "Action Item Adherence",
                    "data": action_data,
                    "visualization_type": "progress_bar"
                },
                "next_session_forecast": {
                    "title": "Next Session Forecast",
                    "data": forecast_data,
                    "visualization_type": "prediction"
                },
                "client_reflection": None,  # To be filled by user
                "start_date": start_date,
                "end_date": end_date,
                "session_count": len(session_ids)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating therapist snapshot: {str(e)}")
            return None 