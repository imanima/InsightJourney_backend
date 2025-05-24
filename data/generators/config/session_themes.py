"""
Configuration for session themes and progression that can be customized based on client and professional types.
Each theme includes specific topics, techniques, and expected outcomes.
"""

SESSION_THEMES = {
    "tech_professionals": {
        "imposter_syndrome": {
            "topics": [
                "Identifying triggers",
                "Understanding core beliefs",
                "Building confidence",
                "Managing perfectionism"
            ],
            "techniques": [
                "Cognitive restructuring",
                "Evidence collection",
                "Mindfulness practice",
                "Progress tracking"
            ],
            "expected_outcomes": [
                "Increased self-awareness",
                "Reduced anxiety",
                "Improved confidence",
                "Better work performance"
            ]
        },
        "work_life_balance": {
            "topics": [
                "Boundary setting",
                "Time management",
                "Energy optimization",
                "Family integration"
            ],
            "techniques": [
                "Time blocking",
                "Priority mapping",
                "Assertive communication",
                "Self-care planning"
            ],
            "expected_outcomes": [
                "Clear work boundaries",
                "Improved time management",
                "Better energy management",
                "Enhanced family time"
            ]
        },
        "chronic_pain": {
            "topics": [
                "Pain pattern identification",
                "Stress-pain connection",
                "Ergonomic optimization",
                "Movement integration"
            ],
            "techniques": [
                "Body scanning",
                "Breath work",
                "Movement therapy",
                "Pain journaling"
            ],
            "expected_outcomes": [
                "Reduced pain intensity",
                "Better pain management",
                "Improved work comfort",
                "Sustainable movement habits"
            ]
        },
        "sleep_issues": {
            "topics": [
                "Sleep hygiene",
                "Stress management",
                "Bedtime routine",
                "Work-life boundaries"
            ],
            "techniques": [
                "Sleep restriction",
                "Stimulus control",
                "Relaxation training",
                "Cognitive restructuring"
            ],
            "expected_outcomes": [
                "Improved sleep quality",
                "Better sleep habits",
                "Reduced insomnia",
                "Enhanced daytime energy"
            ]
        },
        "adhd_management": {
            "topics": [
                "Task organization",
                "Time management",
                "Focus strategies",
                "Energy regulation"
            ],
            "techniques": [
                "Task chunking",
                "Time blocking",
                "External reminders",
                "Progress tracking"
            ],
            "expected_outcomes": [
                "Better task completion",
                "Improved time management",
                "Enhanced focus",
                "Reduced overwhelm"
            ]
        },
        "fertility_journey": {
            "topics": [
                "Emotional processing",
                "Relationship dynamics",
                "Work-life balance",
                "Self-care strategies"
            ],
            "techniques": [
                "Emotion tracking",
                "Communication exercises",
                "Stress management",
                "Support network building"
            ],
            "expected_outcomes": [
                "Emotional resilience",
                "Stronger relationship",
                "Better stress management",
                "Balanced life approach"
            ]
        }
    },
    "students": {
        "academic_pressure": {
            "topics": [
                "Stress management",
                "Study optimization",
                "Social integration",
                "Future planning"
            ],
            "techniques": [
                "Stress reduction exercises",
                "Study skill development",
                "Social exposure practice",
                "Goal setting"
            ],
            "expected_outcomes": [
                "Reduced academic anxiety",
                "Improved study efficiency",
                "Better social confidence",
                "Clear academic path"
            ]
        },
        "career_transition": {
            "topics": [
                "Career exploration",
                "Skill assessment",
                "Industry research",
                "Network building"
            ],
            "techniques": [
                "Strengths assessment",
                "Career mapping",
                "Informational interviews",
                "Resume development"
            ],
            "expected_outcomes": [
                "Clear career direction",
                "Identified transferable skills",
                "Strong professional network",
                "Confident transition plan"
            ]
        }
    },
    "entrepreneurs": {
        "creative_block": {
            "topics": [
                "Creative process analysis",
                "Motivation exploration",
                "Resource planning",
                "Support network building"
            ],
            "techniques": [
                "Creative visualization",
                "Goal setting",
                "Resource mapping",
                "Network development"
            ],
            "expected_outcomes": [
                "Renewed creative energy",
                "Clear project direction",
                "Resource optimization",
                "Strong support network"
            ]
        }
    },
    "healthcare_professionals": {
        "caregiver_stress": {
            "topics": [
                "Stress identification",
                "Support system development",
                "Self-care planning",
                "Work-life integration"
            ],
            "techniques": [
                "Stress management",
                "Support network mapping",
                "Self-care scheduling",
                "Boundary setting"
            ],
            "expected_outcomes": [
                "Reduced caregiver stress",
                "Strong support network",
                "Sustainable self-care",
                "Better work-life balance"
            ]
        }
    }
}

SESSION_PROGRESSION = {
    "initial_assessment": {
        "session_number": 1,
        "duration": 60,
        "focus": "Understanding client's situation and goals",
        "key_activities": [
            "Background exploration",
            "Challenge identification",
            "Goal setting",
            "Initial rapport building"
        ]
    },
    "core_work": {
        "session_number": 2,
        "duration": 45,
        "focus": "Deep dive into primary challenges",
        "key_activities": [
            "Pattern identification",
            "Technique introduction",
            "Action planning",
            "Progress tracking"
        ]
    },
    "integration": {
        "session_number": 3,
        "duration": 45,
        "focus": "Applying insights and techniques",
        "key_activities": [
            "Progress review",
            "Technique refinement",
            "Challenge navigation",
            "Support planning"
        ]
    },
    "closure": {
        "session_number": 4,
        "duration": 45,
        "focus": "Consolidating progress and planning ahead",
        "key_activities": [
            "Achievement celebration",
            "Future planning",
            "Resource identification",
            "Next steps discussion"
        ]
    }
} 