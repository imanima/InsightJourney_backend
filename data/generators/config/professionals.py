"""
Configuration for different types of professionals (coaches, therapists, etc.).
Each professional has their own style, expertise, and approach.
"""

PROFESSIONALS = {
    "coaches": {
        "riley_chen": {
            "name": "Riley Chen",
            "age": 38,
            "role": "Executive Function & ADHD Coach",
            "background": {
                "education": "MA in Organizational Psychology, ADHD Coaching Certification",
                "experience": "10 years coaching tech professionals",
                "specialization": "ADHD, Executive Function, Work-Life Balance"
            },
            "style": {
                "approach": "Playful gamification with structured systems",
                "strengths": [
                    "Habit formation",
                    "Routine building",
                    "Life role balance",
                    "Task management"
                ],
                "techniques": [
                    "Gamified goal setting",
                    "Habit tracking",
                    "Time blocking",
                    "Accountability systems"
                ]
            },
            "tech_usage": [
                "Notion templates",
                "AI Kanban boards",
                "Habit score dashboards",
                "Weekly video check-ins"
            ]
        },
        "malik_johnson": {
            "name": "Malik Johnson",
            "age": 45,
            "role": "Narrative & Career Transition Coach",
            "background": {
                "education": "PhD in Narrative Psychology, Career Coaching Certification",
                "experience": "15 years in career development",
                "specialization": "Career transitions, Purpose discovery, Burnout recovery"
            },
            "style": {
                "approach": "Strengths-based narrative coaching",
                "strengths": [
                    "Story reframing",
                    "Purpose discovery",
                    "Career mapping",
                    "Values alignment"
                ],
                "techniques": [
                    "Hero journey mapping",
                    "Strengths storytelling",
                    "Career path exploration",
                    "Values clarification"
                ]
            },
            "tech_usage": [
                "AI storytelling tools",
                "Career path suggestion engine",
                "Miro journey maps",
                "Digital reflection journals"
            ]
        }
    },
    "therapists": {
        "dr_harper_torres": {
            "name": "Dr. Harper Torres",
            "age": 34,
            "role": "Licensed Clinical Psychologist",
            "background": {
                "education": "PhD in Clinical Psychology, CBT Certification",
                "experience": "8 years in private practice",
                "specialization": "Anxiety, Perfectionism, Sleep Issues"
            },
            "style": {
                "approach": "Data-driven CBT and ACT",
                "strengths": [
                    "Anxiety treatment",
                    "Sleep improvement",
                    "Perfectionism work",
                    "Goal setting"
                ],
                "techniques": [
                    "Cognitive restructuring",
                    "Exposure therapy",
                    "Sleep hygiene",
                    "Mindfulness integration"
                ]
            },
            "tech_usage": [
                "HIPAA-compliant tele-therapy",
                "AI mood trackers",
                "Sleep metric integrations",
                "Progress tracking apps"
            ]
        },
        "mara_ortiz": {
            "name": "Mara Ortiz",
            "age": 36,
            "role": "Somatic Therapist & Pilates Instructor",
            "background": {
                "education": "MA in Somatic Psychology, Pilates Certification",
                "experience": "12 years in body-mind integration",
                "specialization": "Stress-related pain, Body awareness, Movement therapy"
            },
            "style": {
                "approach": "Body-mind integration",
                "strengths": [
                    "Pain management",
                    "Stress reduction",
                    "Body awareness",
                    "Movement therapy"
                ],
                "techniques": [
                    "Somatic experiencing",
                    "Pilates integration",
                    "Body scanning",
                    "Breath work"
                ]
            },
            "tech_usage": [
                "Wearable posture feedback",
                "AI session transcripts",
                "Movement tracking apps",
                "Virtual session tools"
            ]
        },
        "dr_serena_bianchi": {
            "name": "Dr. Serena Bianchi",
            "age": 40,
            "role": "Couples & Family Therapist",
            "background": {
                "education": "PhD in Marriage and Family Therapy",
                "experience": "15 years in relationship counseling",
                "specialization": "Couples therapy, Family systems, Fertility counseling"
            },
            "style": {
                "approach": "Emotion-Focused Therapy",
                "strengths": [
                    "Relationship repair",
                    "Family dynamics",
                    "Fertility support",
                    "Communication skills"
                ],
                "techniques": [
                    "Emotion tracking",
                    "Attachment work",
                    "Family systems mapping",
                    "Communication exercises"
                ]
            },
            "tech_usage": [
                "Secure sentiment analysis",
                "Shared timeline tools",
                "Communication tracking",
                "Virtual session platforms"
            ]
        }
    }
} 