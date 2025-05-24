# Insights Module

## Overview

The Insights module provides advanced analytics and pattern discovery capabilities for the Insight Journey application. It analyzes therapy session data to generate meaningful visualizations and actionable insights that help both clients and therapists understand progress and patterns.

## Features

### 1. Turning-Point Storyboard

Identifies significant emotional turning points where anxiety or other emotions decreased substantially. Shows the exact session snapshot so progress feels cinematic.

**API Endpoint:** `GET /api/v1/insights/turning-point`

### 2. Emotion × Topic Correlation Spotlight

Identifies correlations between emotions and topics across sessions. Shows which topics tend to trigger specific emotions, such as "Anxiety spikes 78% of the time when 'Deadline' appears."

**API Endpoint:** `GET /api/v1/insights/correlations`

### 3. Insight Cascade Map

Creates a map showing how insights lead to other insights, visualizing the chain of breakthroughs. Feels like watching personal growth unfold in real-time.

**API Endpoint:** `GET /api/v1/insights/cascade-map`

### 4. Future-Focus Predictor

Uses Markov chains to predict likely topics and emotions for upcoming sessions. Helps therapists prepare and clients anticipate.

**API Endpoint:** `GET /api/v1/insights/future-prediction`

### 5. Challenge Persistence Ring & Badge System

Tracks how long challenges persist and provides badges for overcoming persistent challenges. Gamifies deep work and creates share-worthy moments.

**API Endpoint:** `GET /api/v1/insights/challenge-persistence`

### 6. Therapist Snapshot

A comprehensive therapist-friendly summary that includes:
- Progress at a glance (emotion changes)
- Breakthrough timeline
- Belief shifts
- Action-item adherence
- Next-session forecast
- Client reflection

**API Endpoint:** `GET /api/v1/insights/therapist-snapshot`

## Implementation

The module is implemented using:

1. **Neo4j Graph Database** - Leverages the existing graph structure to find patterns and connections
2. **Cypher Queries** - Uses advanced Cypher queries to extract insights from session data
3. **FastAPI Endpoints** - Provides RESTful endpoints for accessing insights
4. **Pydantic Models** - Defines data structures for different insight types

## Cypher Queries

The module uses several key Cypher queries:

1. **Turning-Point Query:**
```cypher
MATCH (s:Session)-[r:HAS_EMOTION]->(e:Emotion)
WHERE e.name = 'Anxiety'
WITH s, r.intensity AS intensity
ORDER BY s.date
WITH collect({date: s.date, id: s.id, intensity: intensity}) AS points
UNWIND range(1, size(points)-1) AS i
WITH points[i-1] AS prev, points[i] AS curr
WHERE curr.intensity < prev.intensity - 1.0
RETURN curr.date AS turning_date, 
       curr.id AS session_id,
       prev.intensity AS previous_intensity, 
       curr.intensity AS current_intensity
ORDER BY turning_date DESC
LIMIT 1
```

2. **Correlation Query:**
```cypher
MATCH (s:Session)-[:HAS_EMOTION]->(e:Emotion), 
      (s:Session)-[:HAS_TOPIC]->(t:Topic)
WITH e.name AS emotion, t.name AS topic, count(s) AS together_count
MATCH (s:Session)-[:HAS_EMOTION]->(e:Emotion)
WHERE e.name = emotion
WITH emotion, topic, together_count, count(s) AS emotion_count
MATCH (s:Session)-[:HAS_TOPIC]->(t:Topic)
WHERE t.name = topic
WITH emotion, topic, together_count, emotion_count, count(s) AS topic_count
MATCH (s:Session)
WITH emotion, topic, together_count, emotion_count, topic_count, count(s) AS total_sessions
RETURN emotion, 
       topic, 
       together_count,
       emotion_count,
       topic_count,
       total_sessions,
       (1.0 * together_count / emotion_count) * 100 AS correlation_percentage
ORDER BY correlation_percentage DESC
LIMIT 10
```

## Usage

Access insights through the API endpoints after user authentication. All endpoints require a valid user token and return insights specific to that user's session data.

## Dependencies

- Neo4j graph database
- FastAPI
- Authentication service
- Session data with emotions, topics, insights, and challenges

## Future Enhancements

1. Machine learning integration for more accurate predictions
2. Personalized insight recommendations
3. Advanced visualization capabilities
4. Social sharing of achievements and insights 