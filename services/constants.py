from typing import Dict, List, Any
import re

# Default analysis elements
DEFAULT_ANALYSIS_ELEMENTS: List[Dict[str, Any]] = [
    {
        'name': 'Emotions',
        'enabled': True,
        'description': 'Emotional states and their intensities',
        'categories': ['Joy', 'Fear', 'Anger', 'Sadness', 'Surprise', 'Love'],
        'format_template': '[Emotion] (intensity: 1-10) - [Context]',
        'system_instructions': 'Identify emotions with their intensity (1-10) and context.',
        'analysis_instructions': 'List emotions with intensity and context. Format: Emotion (intensity: X) - Context',
        'requires_topic': False,
        'requires_timestamp': True,
        'additional_fields': ['intensity', 'context']
    },
    {
        'name': 'Topics',
        'enabled': True,
        'description': 'Main themes and subjects discussed',
        'categories': [],
        'format_template': '[Topic]',
        'system_instructions': 'Identify main topics and themes discussed.',
        'analysis_instructions': 'List main topics discussed in the session.',
        'requires_topic': True,
        'requires_timestamp': False,
        'additional_fields': []
    },
    {
        'name': 'Insights',
        'enabled': True,
        'description': 'Key learnings and reflections',
        'categories': [],
        'format_template': '[Insight]',
        'system_instructions': 'Identify key insights and learnings.',
        'analysis_instructions': 'List key insights and learnings from the session.',
        'requires_topic': True,
        'requires_timestamp': True,
        'additional_fields': ['confidence']
    },
    {
        'name': 'Action Items',
        'enabled': True,
        'description': 'Specific commitments and next steps',
        'categories': [],
        'format_template': '[Action Item]',
        'system_instructions': 'Identify specific action items and commitments.',
        'analysis_instructions': 'List specific action items and commitments made.',
        'requires_topic': True,
        'requires_timestamp': True,
        'additional_fields': ['priority', 'due_date']
    },
    {
        'name': 'Beliefs',
        'enabled': True,
        'description': 'Core beliefs and assumptions',
        'categories': [],
        'format_template': '[Belief]',
        'system_instructions': 'Identify core beliefs and assumptions.',
        'analysis_instructions': 'List core beliefs and assumptions identified.',
        'requires_topic': True,
        'requires_timestamp': True,
        'additional_fields': ['type', 'impact']
    }
]

# Available GPT models and their configurations
GPT_MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    'gpt-4': {
        'description': 'Multimodal model capable of processing both text and images',
        'max_tokens': 8192,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.03
    },
    'gpt-4o': {
        'description': 'Enhanced version of GPT-4, capable of analyzing and generating text, images, and sound. Twice as fast and half the cost of GPT-4 Turbo',
        'max_tokens': 128000,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.01
    },
    'gpt-4o-mini': {
        'description': 'Smaller, cost-effective variant of GPT-4o, balancing performance and affordability',
        'max_tokens': 8192,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.005
    },
    'gpt-4.5': {
        'description': 'Released in February 2025, featuring reduced inaccuracies and enhanced pattern recognition, creativity, and user interaction',
        'max_tokens': 128000,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.02
    },
    'o1': {
        'description': 'Designed to solve complex problems by spending more time "thinking" before responding, excelling in areas like mathematics and scientific reasoning',
        'max_tokens': 8192,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.015
    },
    'o1-mini': {
        'description': 'Smaller, faster version of o1, offering a balance between capability and efficiency',
        'max_tokens': 4096,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.008
    },
    'o3': {
        'description': 'Successor to the o1 model, currently in testing phases, aimed at further enhancing reasoning capabilities',
        'max_tokens': 8192,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.02
    },
    'o3-mini': {
        'description': 'A lighter, faster version of o3, designed for applications requiring quick responses with reasonable reasoning abilities',
        'max_tokens': 4096,
        'default_temp': 0.7,
        'cost_per_1k_tokens': 0.01
    }
}

# Available GPT models list
AVAILABLE_GPT_MODELS: List[str] = list(GPT_MODEL_CONFIGS.keys())

# Default settings
DEFAULT_SETTINGS: Dict[str, Any] = {
    'gpt_model': 'gpt-4o',
    'max_tokens': 2000,
    'temperature': 0.7,
    'analysis_elements': DEFAULT_ANALYSIS_ELEMENTS,
    'max_sessions': 10,
    'max_duration': 3600,
    'allowed_file_types': ['mp3', 'wav', 'm4a']
}

# Emotion categories for analysis
EMOTION_CATEGORIES: Dict[str, List[str]] = {
    'positive': ['joy', 'happiness', 'excitement', 'gratitude', 'pride', 'love', 'hope', 'optimism'],
    'negative': ['sadness', 'anger', 'fear', 'anxiety', 'frustration', 'disappointment', 'guilt', 'shame'],
    'neutral': ['surprise', 'curiosity', 'confusion', 'interest', 'boredom', 'calmness', 'peace']
}

# Patterns for extracting elements from analyzed text
PATTERNS: Dict[str, str] = {
    'emotion': r'^([^\(]+)\s*\(intensity:\s*(\d+)\)\s*-\s*(.+)$',
    'topic': r'topic:\s*([^-]+)',
    'timestamp': r'timestamp:\s*([^-]+)',
    'insight': r'^([^\(]+)\s*\(confidence:\s*(\d+)\)\s*-\s*(.+)$',
    'action_item': r'^([^\(]+)\s*\(priority:\s*([^\)]+)\)\s*-\s*(.+)$',
    'belief': r'^([^\(]+)\s*\(type:\s*([^\)]+)\)\s*-\s*(.+)$'
}

# Compile regex patterns for better performance
COMPILED_PATTERNS: Dict[str, re.Pattern] = {
    key: re.compile(pattern) for key, pattern in PATTERNS.items()
} 