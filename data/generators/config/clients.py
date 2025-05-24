"""
Configuration for different types of clients with their specific needs and characteristics.
Each client has their own background, challenges, and goals.
"""

CLIENTS = {
    "tech_professionals": {
        "alex_designer": {
            "name": "Alex",
            "age": 27,
            "role": "Product Designer",
            "background": {
                "education": "BFA in Design",
                "work_experience": "5 years in tech",
                "current_role": "Senior Product Designer at a startup"
            },
            "tech_habits": [
                "Streams 'building in public' on Twitch",
                "Uses AI plugins for Figma hand-offs",
                "Active in design communities"
            ],
            "challenges": [
                "Imposter syndrome after failed launch",
                "Perfectionism in design work",
                "Work-life balance"
            ],
            "goals": [
                "Build confidence in leadership role",
                "Develop healthier work boundaries",
                "Create sustainable design process"
            ],
            "personality_traits": [
                "Creative",
                "Detail-oriented",
                "Self-critical",
                "Community-focused"
            ]
        },
        "jasmine_engineer": {
            "name": "Jasmine",
            "age": 30,
            "role": "Front-end Engineer",
            "background": {
                "education": "BS in Computer Science",
                "work_experience": "8 years in development",
                "current_role": "Senior Front-end Engineer at fintech"
            },
            "tech_habits": [
                "Remote work optimization",
                "AI-powered productivity tools",
                "Automated task management"
            ],
            "challenges": [
                "Juggling work and new motherhood",
                "Sprint deadline pressure",
                "Energy management"
            ],
            "goals": [
                "Establish work-life boundaries",
                "Optimize productivity with baby",
                "Maintain career growth"
            ],
            "personality_traits": [
                "Organized",
                "Efficient",
                "Family-oriented",
                "Problem-solver"
            ]
        },
        "mei_ops": {
            "name": "Mei",
            "age": 29,
            "role": "Operations Lead",
            "background": {
                "education": "MBA in Operations Management",
                "work_experience": "7 years in tech operations",
                "current_role": "Operations Lead at SaaS company"
            },
            "tech_habits": [
                "Wearable health tracking",
                "Ergonomic workspace setup",
                "Digital pain journaling"
            ],
            "challenges": [
                "Chronic back pain from desk work",
                "Work stress manifesting physically",
                "Difficulty maintaining exercise routine"
            ],
            "goals": [
                "Manage chronic pain effectively",
                "Develop sustainable work habits",
                "Improve physical wellbeing"
            ],
            "personality_traits": [
                "Analytical",
                "Disciplined",
                "Health-conscious",
                "Detail-oriented"
            ]
        },
        "priya_analyst": {
            "name": "Priya",
            "age": 26,
            "role": "VC Analyst",
            "background": {
                "education": "MS in Finance",
                "work_experience": "4 years in venture capital",
                "current_role": "Senior Analyst at VC firm"
            },
            "tech_habits": [
                "Sleep tracking apps",
                "Meditation apps",
                "Productivity dashboards"
            ],
            "challenges": [
                "Chronic insomnia",
                "Work-related anxiety",
                "Difficulty unwinding"
            ],
            "goals": [
                "Improve sleep quality",
                "Develop better sleep habits",
                "Reduce work-related stress"
            ],
            "personality_traits": [
                "Ambitious",
                "Data-driven",
                "High-achieving",
                "Perfectionist"
            ]
        },
        "lina_freelancer": {
            "name": "Lina",
            "age": 28,
            "role": "Freelance Developer",
            "background": {
                "education": "BS in Computer Science",
                "work_experience": "6 years freelance development",
                "current_role": "Independent contractor"
            },
            "tech_habits": [
                "Task management apps",
                "Time tracking tools",
                "AI productivity assistants"
            ],
            "challenges": [
                "ADHD task paralysis",
                "Inconsistent work schedule",
                "Project deadline management"
            ],
            "goals": [
                "Develop consistent work routines",
                "Improve task completion",
                "Better project planning"
            ],
            "personality_traits": [
                "Creative",
                "Independent",
                "Adaptable",
                "Energetic"
            ]
        },
        "zoe_researcher": {
            "name": "Zoë",
            "age": 31,
            "role": "UX Researcher",
            "background": {
                "education": "MS in Human-Computer Interaction",
                "work_experience": "8 years in UX research",
                "current_role": "Senior UX Researcher at tech company"
            },
            "tech_habits": [
                "Fertility tracking apps",
                "Meditation apps",
                "Digital journaling"
            ],
            "challenges": [
                "Fertility journey stress",
                "Work-life balance during treatment",
                "Relationship strain"
            ],
            "goals": [
                "Navigate fertility journey",
                "Maintain career growth",
                "Strengthen relationship"
            ],
            "personality_traits": [
                "Empathetic",
                "Resilient",
                "Analytical",
                "Hopeful"
            ]
        }
    },
    "students": {
        "diego_student": {
            "name": "Diego",
            "age": 24,
            "role": "Data Science Master's Student",
            "background": {
                "education": "BS in Computer Science, pursuing MS in Data Science",
                "experience": "Research assistant, hackathon participant",
                "current_role": "Graduate student"
            },
            "tech_habits": [
                "Custom GPT development",
                "Hackathon participation",
                "Research automation"
            ],
            "challenges": [
                "Social anxiety in new environment",
                "Academic pressure",
                "Homesickness"
            ],
            "goals": [
                "Build social confidence",
                "Excel in research",
                "Prepare for industry transition"
            ],
            "personality_traits": [
                "Analytical",
                "Innovative",
                "Shy",
                "Ambitious"
            ]
        },
        "omar_phd": {
            "name": "Omar",
            "age": 25,
            "role": "PhD Candidate",
            "background": {
                "education": "BS in Computer Science, pursuing PhD",
                "experience": "Research assistant, teaching assistant",
                "current_role": "PhD candidate in AI"
            },
            "tech_habits": [
                "Research paper management",
                "Academic networking tools",
                "Data analysis software"
            ],
            "challenges": [
                "Academic burnout",
                "Uncertain career path",
                "Work-life balance"
            ],
            "goals": [
                "Explore career options",
                "Develop transferable skills",
                "Find work-life balance"
            ],
            "personality_traits": [
                "Intellectual",
                "Curious",
                "Perfectionist",
                "Reflective"
            ]
        }
    },
    "entrepreneurs": {
        "sam_developer": {
            "name": "Sam",
            "age": 32,
            "role": "Indie Game Developer",
            "background": {
                "education": "Self-taught developer",
                "experience": "5 years in game development",
                "current_role": "Independent game developer"
            },
            "tech_habits": [
                "YouTube streaming",
                "Open-source contributions",
                "AI model fine-tuning"
            ],
            "challenges": [
                "Loneliness after co-founder split",
                "Creative block",
                "Financial uncertainty"
            ],
            "goals": [
                "Find new creative direction",
                "Build support network",
                "Stabilize income"
            ],
            "personality_traits": [
                "Creative",
                "Independent",
                "Resilient",
                "Technical"
            ]
        }
    },
    "healthcare_professionals": {
        "evan_engineer": {
            "name": "Evan",
            "age": 34,
            "role": "Senior DevOps Engineer",
            "background": {
                "education": "MS in Computer Science",
                "work_experience": "12 years in tech",
                "current_role": "Senior DevOps at healthcare company"
            },
            "tech_habits": [
                "Infrastructure automation",
                "AI incident prediction",
                "System monitoring"
            ],
            "challenges": [
                "Caring for father with dementia",
                "On-call stress",
                "Work-life balance"
            ],
            "goals": [
                "Manage caregiving responsibilities",
                "Reduce work stress",
                "Maintain career growth"
            ],
            "personality_traits": [
                "Responsible",
                "Technical",
                "Caring",
                "Organized"
            ]
        }
    }
} 