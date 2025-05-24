def get_sample_sessions():
    """Return a list of sample therapy sessions for testing"""
    return [
        {
            "user": {
                "email": "career.transition@example.com",
                "password": "testpass123",
                "name": "Career Transition User"
            },
            "title": "Career Transition Anxiety",
            "date": "2024-03-15",
            "summary": "Client discusses anxiety about transitioning from marketing to UX design",
            "transcript": """
Client: I've been feeling really anxious about my career change. I've been in marketing for 8 years, and now I'm thinking about moving into UX design.
Therapist: That's a significant change. What's driving this decision?
Client: I feel stuck in marketing. I'm good at it, but I don't feel fulfilled anymore. UX design interests me because it combines creativity with problem-solving.
Therapist: How long have you been considering this change?
Client: About six months now. I've been taking some online courses in UX design, but I'm worried about starting over.
Therapist: What specific concerns do you have about starting over?
Client: Mainly financial security. I'm worried about taking a pay cut as a junior designer. And there's also the fear of failure.
Therapist: These are valid concerns. Let's explore how we might address them.
""",
            "emotions": [
                {"name": "Anxiety", "intensity": 0.8},
                {"name": "Fear", "intensity": 0.7},
                {"name": "Uncertainty", "intensity": 0.6}
            ],
            "beliefs": [
                {"content": "I need to be perfect in my new career", "category": "Performance"},
                {"content": "Starting over means I've failed", "category": "Self-worth"}
            ],
            "topics": [
                {"name": "Career Change", "category": "Work"},
                {"name": "Financial Security", "category": "Life Planning"}
            ],
            "insights": [
                "My fear of failure is preventing me from taking necessary risks",
                "I can leverage my marketing experience in UX design"
            ],
            "action_items": [
                {"task": "Research UX design bootcamps", "due_date": "2024-04-01"},
                {"task": "Create a financial plan for career transition", "due_date": "2024-03-30"}
            ]
        },
        {
            "user": {
                "email": "relationship.issues@example.com",
                "password": "testpass123",
                "name": "Relationship Issues User"
            },
            "title": "Relationship Communication Issues",
            "date": "2024-03-16",
            "summary": "Client addresses recurring communication problems in their relationship",
            "transcript": """
Client: My partner and I keep having the same argument over and over. It's like we're speaking different languages.
Therapist: Can you tell me more about these recurring arguments?
Client: It's usually about how we spend our time together. I feel like they're always on their phone when we're together.
Therapist: How have you communicated this concern to them?
Client: I've tried telling them directly, but they get defensive. They say I'm too demanding.
Therapist: How does it make you feel when they respond that way?
Client: Frustrated and unheard. Like my feelings don't matter.
Therapist: Let's work on some communication strategies that might help both of you feel heard.
""",
            "emotions": [
                {"name": "Frustration", "intensity": 0.7},
                {"name": "Loneliness", "intensity": 0.6},
                {"name": "Disappointment", "intensity": 0.5}
            ],
            "beliefs": [
                {"content": "My needs are too demanding", "category": "Self-worth"},
                {"content": "My partner doesn't care about my feelings", "category": "Relationships"}
            ],
            "topics": [
                {"name": "Communication", "category": "Relationships"},
                {"name": "Quality Time", "category": "Relationships"}
            ],
            "insights": [
                "I need to express my needs more clearly and calmly",
                "We both need to work on active listening"
            ],
            "action_items": [
                {"task": "Practice 'I' statements before next conversation", "due_date": "2024-03-20"},
                {"task": "Schedule device-free time together", "due_date": "2024-03-18"}
            ]
        },
        {
            "user": {
                "email": "grief.loss@example.com",
                "password": "testpass123",
                "name": "Grief and Loss User"
            },
            "title": "Grief and Loss Processing",
            "date": "2024-03-17",
            "summary": "Client processes grief over the loss of their father",
            "transcript": """
Client: It's been three months since I lost my dad, and I thought I'd be handling it better by now.
Therapist: Grief doesn't follow a timeline. What makes you feel you should be handling it differently?
Client: Everyone keeps saying I need to move on, get back to normal. But I don't even know what normal is anymore.
Therapist: How do those comments affect you?
Client: They make me feel guilty for still being sad. Like I'm doing something wrong by grieving.
Therapist: There's no right or wrong way to grieve. What do you need right now?
Client: I just need space to remember him, to talk about him without feeling like I'm bringing everyone down.
Therapist: This is a safe space to do that. Would you like to share some memories of your dad?
""",
            "emotions": [
                {"name": "Sadness", "intensity": 0.9},
                {"name": "Guilt", "intensity": 0.6},
                {"name": "Confusion", "intensity": 0.5}
            ],
            "beliefs": [
                {"content": "I should be over this by now", "category": "Grief"},
                {"content": "My grief is a burden to others", "category": "Self-worth"}
            ],
            "topics": [
                {"name": "Loss", "category": "Grief"},
                {"name": "Family", "category": "Relationships"}
            ],
            "insights": [
                "Grief is a personal journey with no set timeline",
                "I need to give myself permission to grieve"
            ],
            "action_items": [
                {"task": "Create a memory book for my father", "due_date": "2024-04-01"},
                {"task": "Join a grief support group", "due_date": "2024-03-25"}
            ]
        },
        {
            "title": "Social Anxiety Management",
            "transcript": """
Therapist: How did the work presentation go last week?

Client: I managed to do it, but it was really hard. My heart was racing the whole time, and I kept worrying that everyone could see how nervous I was.

Therapist: What specific thoughts were going through your mind during the presentation?

Client: "They're going to think I'm incompetent." "My voice is shaking." "Someone's going to ask a question I can't answer." The usual greatest hits of my anxiety.

Therapist: And did any of those fears come true?

Client: Well, no. Actually, my boss said it was well-done. But it's hard to believe that when my internal voice is so critical.

Therapist: Let's explore that internal voice. When did you first start hearing these kinds of critical thoughts?

Client: Probably in middle school. I had to give a class presentation and messed up. Some kids laughed, and ever since then, public speaking has been terrifying.

Therapist: That sounds like a really formative experience. How does that 13-year-old's experience still influence you today?

Client: I guess I'm still carrying that fear of humiliation. But I'm not 13 anymore, and my coworkers aren't middle school kids.

Therapist: That's a powerful realization. How might your presentations be different if you could separate past fears from present reality?

Client: Maybe I could focus more on the content and less on my anxiety. I actually know my material really well, but the anxiety overshadows that.

Therapist: Would you be interested in learning some techniques to help stay grounded in the present moment during presentations?
"""
        },
        {
            "title": "Work-Life Balance Struggles",
            "transcript": """
Therapist: How has the new boundary-setting at work been going?

Client: Mixed results. I managed to say no to one extra project, but then I felt so guilty that I ended up staying late three days this week to help with something else.

Therapist: What was different about the time you were able to say no?

Client: I had already promised to take my kids to their school event, so I had a concrete reason. It felt more legitimate somehow.

Therapist: It's interesting that you needed an external commitment to feel your "no" was legitimate. What makes your own need for rest or personal time feel less valid?

Client: *sighs* I guess I've always equated productivity with worth. My parents were both workaholics, and that was kind of the model I grew up with.

Therapist: How is that model affecting your relationships and wellbeing now?

Client: My partner mentioned last week that the kids miss our weekend adventures. We used to go hiking or to the park, but lately, I've been too tired or catching up on work.

Therapist: What emotions come up when you hear that?

Client: Sadness... and frustration with myself. I don't want my kids to grow up with the same message I got - that work always comes first.

Therapist: It sounds like you're at a crossroads between the patterns you learned and the parent you want to be.

Client: Yes, exactly. I want to break this cycle, but it's hard to shake the feeling that I'm letting people down when I'm not constantly working.

Therapist: Let's explore what "letting people down" means to you, and maybe identify some small steps toward change.
"""
        }
    ]

if __name__ == "__main__":
    # Print all sessions for testing
    sessions = get_sample_sessions()
    for i, session in enumerate(sessions, 1):
        print(f"\nSession {i}: {session['title']}")
        print("=" * 50)
        print(f"User: {session['user']['name']} ({session['user']['email']})")
        print(f"Date: {session['date']}")
        print(f"Summary: {session['summary']}")
        print("\nEmotions:")
        for emotion in session['emotions']:
            print(f"- {emotion['name']} ({emotion['intensity']})")
        print("\nBeliefs:")
        for belief in session['beliefs']:
            print(f"- {belief['content']} ({belief['category']})")
        print("\nTopics:")
        for topic in session['topics']:
            print(f"- {topic['name']} ({topic['category']})")
        print("\nInsights:")
        for insight in session['insights']:
            print(f"- {insight}")
        print("\nAction Items:")
        for item in session['action_items']:
            print(f"- {item['task']} (due: {item['due_date']})")
        print("\n" + "=" * 50) 