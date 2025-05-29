#!/usr/bin/env python3

# Simulate the actual OpenAI response we're seeing in logs
actual_openai_response = """=== EMOTIONS ===  
Name: Anxiety  
Intensity: 4  
Context: Feeling anxious about upcoming project deadlines and balancing research  
Topic: Stress Management  
Timestamp: 11:06  
=== EMOTIONS ===  
Name: Overwhelm
Intensity: 3
Context: Feeling overwhelmed with multiple responsibilities and perfectionism  
Topic: Stress Management  
Timestamp: 11:15

=== BELIEFS ===
Name: Perfectionism  
Description: "If my research is not flawless, it's not good enough"  
Impact: Leads to procrastination and stress about academic work  
Topic: Career  
Timestamp: 11:22  

=== ACTION ITEMS ===
Name: Cognitive Restructuring Practice  
Description: Use cognitive restructuring to challenge negative social thoughts during interactions  
Topic: Relationships  
Timestamp: 11:19  

=== CHALLENGES ===
Name: Academic Pressure  
Impact: Overwhelm and procrastination due to fear of failure and high standards  
Topic: Career  
Timestamp: 11:20  

=== INSIGHTS ===
Name: Recognizing Overgeneralization  
Context: Client realized assumptions about social embarrassment are based on limited experiences and overgeneralizing  
Topic: Relationships  
Timestamp: 11:14"""

# Load our current extract_elements function
import sys
import os
sys.path.append('.')

from services.analysis_service import extract_elements

print("🔍 Testing current extract_elements with actual OpenAI response:")
print("=" * 70)

result = extract_elements(actual_openai_response)

print(f"\n📊 Current Extraction Results:")
for element_type, elements in result.items():
    print(f"  • {element_type}: {len(elements)} items")
    for i, element in enumerate(elements):
        print(f"    {i+1}. {element.get('name', 'N/A')}")

print(f"\n🔍 Looking for the issue...")

# Test if it's the duplicate section headers causing issues
import re

print(f"\n🔍 Testing emotions section detection:")
emotion_section_match = re.search(r'===\s*EMOTIONS\s*===\s*\n(.*?)(?=\n\s*===|\Z)', actual_openai_response, re.DOTALL)
if emotion_section_match:
    emotion_section = emotion_section_match.group(1)
    print(f"✅ Found emotion section: {len(emotion_section)} characters")
    print(f"📝 Emotion section content:")
    print(repr(emotion_section[:200]) + "...")
    
    # Test emotion pattern
    emotion_pattern = re.compile(r"""
        Name:\s*(?P<name>[^\n]+)\n
        Intensity:\s*(?P<intensity>\d+)\n
        Context:\s*(?P<context>[^\n]+)\n
        Topic:\s*(?P<topic>[^\n]+)\n
        Timestamp:\s*(?P<timestamp>[^\n]+)
    """, re.VERBOSE)
    
    matches = list(emotion_pattern.finditer(emotion_section))
    print(f"🔍 Found {len(matches)} emotion matches")
    for i, match in enumerate(matches):
        print(f"  {i+1}. {match.groupdict()}")
else:
    print("❌ No emotion section found")

# Let's also test what happens if we treat the duplicate sections correctly
print(f"\n🔍 Testing alternative approach - find all individual emotions regardless of sections:")

# Pattern to find emotions anywhere in the text
emotion_pattern_global = re.compile(r"""
    Name:\s*(?P<name>[^\n]+)\n
    Intensity:\s*(?P<intensity>\d+)\n
    Context:\s*(?P<context>[^\n]+)\n
    Topic:\s*(?P<topic>[^\n]+)\n
    Timestamp:\s*(?P<timestamp>[^\n]+)
""", re.VERBOSE)

global_matches = list(emotion_pattern_global.finditer(actual_openai_response))
print(f"🔍 Found {len(global_matches)} emotion matches globally")
for i, match in enumerate(global_matches):
    print(f"  {i+1}. {match.groupdict()}") 