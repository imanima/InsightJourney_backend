#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from services.analysis_service import extract_elements

# Test with the exact OpenAI response format we're getting
test_openai_response = """=== EMOTIONS ===
Name: Anxiety
Intensity: 4
Context: Feeling anxious about upcoming project deadlines and balancing research with coursework
Topic: Stress Management
Timestamp: 11:05

Name: Overwhelm
Intensity: 3
Context: Feeling overwhelmed with multiple responsibilities and perfectionism
Topic: Stress Management
Timestamp: 11:15

=== BELIEFS ===
Name: Perfectionism Belief
Description: "Everything must be perfect before I can move forward"
Impact: Causes procrastination and increased anxiety
Topic: Self-Esteem
Timestamp: 11:20

Name: Social Inadequacy
Description: "I'm awkward and will embarrass myself in social situations"
Impact: Avoids social interactions and limits networking opportunities
Topic: Relationships
Timestamp: 11:10

=== ACTION ITEMS ===
Name: Practice Cognitive Restructuring
Description: Challenge negative automatic thoughts in social situations
Topic: Personal Growth
Timestamp: 11:15

Name: Break Tasks Into Steps
Description: Create step-by-step plan for project to reduce overwhelm
Topic: Stress Management
Timestamp: 11:25

=== CHALLENGES ===
Name: Academic Perfectionism
Impact: Procrastination and increased stress around deadlines
Topic: Career
Timestamp: 11:20

=== INSIGHTS ===
Name: Mindfulness Effectiveness
Context: Recognized that breathing exercises help calm racing thoughts
Topic: Stress Management
Timestamp: 11:10"""

def test_extraction():
    print("🧪 Testing analysis extraction fix...")
    
    result = extract_elements(test_openai_response)
    
    print(f"\n✅ Extraction Results:")
    print(f"   • Emotions: {len(result['emotions'])} items")
    for i, emotion in enumerate(result['emotions']):
        print(f"     {i+1}. {emotion['name']} (intensity: {emotion['intensity']})")
    
    print(f"   • Beliefs: {len(result['beliefs'])} items")
    for i, belief in enumerate(result['beliefs']):
        print(f"     {i+1}. {belief['name']}")
    
    print(f"   • Action Items: {len(result['action_items'])} items")
    for i, action in enumerate(result['action_items']):
        print(f"     {i+1}. {action['name']}")
    
    print(f"   • Challenges: {len(result['challenges'])} items")
    for i, challenge in enumerate(result['challenges']):
        print(f"     {i+1}. {challenge['name']}")
    
    print(f"   • Insights: {len(result['insights'])} items")
    for i, insight in enumerate(result['insights']):
        print(f"     {i+1}. {insight['name']}")
    
    total_elements = sum(len(result[key]) for key in result.keys())
    print(f"\n📊 Total elements extracted: {total_elements}")
    
    expected_counts = {
        'emotions': 2,
        'beliefs': 2,
        'action_items': 2,
        'challenges': 1,
        'insights': 1
    }
    
    success = True
    for key, expected in expected_counts.items():
        actual = len(result[key])
        if actual != expected:
            print(f"❌ {key}: expected {expected}, got {actual}")
            success = False
        else:
            print(f"✅ {key}: {actual} items (correct)")
    
    if success:
        print(f"\n🎉 All extraction tests passed!")
        return True
    else:
        print(f"\n❌ Some extraction tests failed!")
        return False

if __name__ == "__main__":
    test_extraction() 