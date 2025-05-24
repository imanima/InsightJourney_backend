# Element Settings

This document describes how to configure analysis elements in the Insight Journey platform.

## Overview

Element settings control how different types of analysis (emotions, topics, insights) are processed and generated.

## Configuration File

Element settings are defined in `config/elements.json`:

```json
{
    "emotions": {
        "enabled": true,
        "categories": ["basic", "complex"],
        "threshold": 0.5,
        "format_template": "{name} (intensity: {intensity})",
        "prompt_template": "Analyze the emotional content in: {text}",
        "models": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        }
    },
    "topics": {
        "enabled": true,
        "categories": ["personal", "professional"],
        "threshold": 0.7,
        "format_template": "{name} ({category})",
        "prompt_template": "Identify key topics in: {text}",
        "models": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        }
    },
    "insights": {
        "enabled": true,
        "types": ["pattern", "recommendation", "observation"],
        "threshold": 0.8,
        "format_template": "{type}: {content}",
        "prompt_template": "Generate insights from: {text}",
        "models": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        }
    }
}
```

## Element Types

### Emotions

```json
{
    "emotions": {
        "enabled": true,
        "categories": {
            "basic": [
                "happy",
                "sad",
                "angry",
                "fearful",
                "surprised",
                "disgusted"
            ],
            "complex": [
                "proud",
                "ashamed",
                "grateful",
                "guilty",
                "jealous",
                "anxious"
            ]
        },
        "threshold": 0.5,
        "format_template": "{name} (intensity: {intensity})",
        "prompt_template": "Analyze the emotional content in: {text}",
        "models": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        },
        "analysis": {
            "window_size": 100,
            "overlap": 50,
            "batch_size": 10
        },
        "storage": {
            "node_label": "Emotion",
            "relationships": [
                {
                    "type": "CONTAINS",
                    "direction": "incoming",
                    "source_label": "Session"
                },
                {
                    "type": "RELATES_TO",
                    "direction": "outgoing",
                    "target_label": "Topic"
                }
            ]
        }
    }
}
```

### Topics

```json
{
    "topics": {
        "enabled": true,
        "categories": {
            "personal": [
                "relationships",
                "health",
                "hobbies",
                "goals"
            ],
            "professional": [
                "work",
                "career",
                "education",
                "skills"
            ]
        },
        "threshold": 0.7,
        "format_template": "{name} ({category})",
        "prompt_template": "Identify key topics in: {text}",
        "models": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        },
        "analysis": {
            "window_size": 200,
            "overlap": 100,
            "batch_size": 5
        },
        "storage": {
            "node_label": "Topic",
            "relationships": [
                {
                    "type": "DISCUSSES",
                    "direction": "incoming",
                    "source_label": "Session"
                },
                {
                    "type": "LEADS_TO",
                    "direction": "outgoing",
                    "target_label": "Insight"
                }
            ]
        }
    }
}
```

### Insights

```json
{
    "insights": {
        "enabled": true,
        "types": {
            "pattern": {
                "description": "Recurring themes or behaviors",
                "threshold": 0.8
            },
            "recommendation": {
                "description": "Suggested actions or changes",
                "threshold": 0.9
            },
            "observation": {
                "description": "Notable single events or moments",
                "threshold": 0.7
            }
        },
        "format_template": "{type}: {content}",
        "prompt_template": "Generate insights from: {text}",
        "models": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        },
        "analysis": {
            "window_size": 500,
            "overlap": 250,
            "batch_size": 2
        },
        "storage": {
            "node_label": "Insight",
            "relationships": [
                {
                    "type": "REVEALS",
                    "direction": "incoming",
                    "source_label": "Session"
                },
                {
                    "type": "BASED_ON",
                    "direction": "outgoing",
                    "target_label": ["Emotion", "Topic"]
                }
            ]
        }
    }
}
```

## Configuration Options

### Common Settings

| Setting | Type | Description |
|---------|------|-------------|
| enabled | boolean | Enable/disable the element |
| threshold | number | Minimum confidence score (0-1) |
| format_template | string | Output format template |
| prompt_template | string | Analysis prompt template |

### Analysis Settings

| Setting | Type | Description |
|---------|------|-------------|
| window_size | number | Text window size for analysis |
| overlap | number | Overlap between windows |
| batch_size | number | Number of windows per batch |

### Storage Settings

| Setting | Type | Description |
|---------|------|-------------|
| node_label | string | Neo4j node label |
| relationships | array | Neo4j relationship definitions |

## Integration

### Analysis Service

```python
class AnalysisService:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)

    def analyze_emotions(self, text: str) -> List[Dict]:
        if not self.config['emotions']['enabled']:
            return []

        emotions = []
        window_size = self.config['emotions']['analysis']['window_size']
        overlap = self.config['emotions']['analysis']['overlap']
        
        windows = self._create_windows(text, window_size, overlap)
        for window in windows:
            prompt = self.config['emotions']['prompt_template'].format(
                text=window
            )
            result = self._analyze_with_gpt(prompt)
            emotions.extend(self._format_emotions(result))
        
        return emotions

    def analyze_topics(self, text: str) -> List[Dict]:
        if not self.config['topics']['enabled']:
            return []

        # Similar implementation as analyze_emotions
        pass

    def generate_insights(self, text: str) -> List[Dict]:
        if not self.config['insights']['enabled']:
            return []

        # Similar implementation as analyze_emotions
        pass

    def _create_windows(self, text: str, size: int, overlap: int) -> List[str]:
        # Implementation for text windowing
        pass

    def _analyze_with_gpt(self, prompt: str) -> Dict:
        # Implementation for GPT API call
        pass

    def _format_emotions(self, result: Dict) -> List[Dict]:
        # Implementation for formatting results
        pass
```

### Neo4j Integration

```python
class Neo4jStorage:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)

    def store_emotion(self, session_id: str, emotion: Dict):
        query = """
        MATCH (s:Session {id: $session_id})
        CREATE (e:Emotion {
            id: $id,
            name: $name,
            intensity: $intensity,
            category: $category,
            timestamp: $timestamp
        })
        CREATE (s)-[:CONTAINS]->(e)
        """
        # Execute query with parameters

    def store_topic(self, session_id: str, topic: Dict):
        # Similar implementation as store_emotion
        pass

    def store_insight(self, session_id: str, insight: Dict):
        # Similar implementation as store_emotion
        pass

    def create_relationships(self):
        # Implementation for creating relationships
        pass
```

## Example Usage

```python
# Initialize services
analysis_service = AnalysisService('config/elements.json')
storage_service = Neo4jStorage('config/elements.json')

# Analyze content
text = "Sample text for analysis"
emotions = analysis_service.analyze_emotions(text)
topics = analysis_service.analyze_topics(text)
insights = analysis_service.generate_insights(text)

# Store results
session_id = "sample_session"
for emotion in emotions:
    storage_service.store_emotion(session_id, emotion)
for topic in topics:
    storage_service.store_topic(session_id, topic)
for insight in insights:
    storage_service.store_insight(session_id, insight)

# Create relationships
storage_service.create_relationships()
``` 