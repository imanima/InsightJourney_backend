#!/usr/bin/env python3
"""
Minimal test for analysis service only to isolate OpenAI client issues.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test transcript
TEST_TRANSCRIPT = """
[00:00] Therapist: Hi Sarah, how are you feeling today?
[00:05] Sarah: Hi, I'm feeling quite anxious actually. Work has been really overwhelming lately.
[00:15] Therapist: I'm sorry to hear that. Can you tell me more about what's been happening at work?
[00:25] Sarah: Well, we have this big project deadline coming up, and I feel like I'm drowning in tasks.
"""

def test_analysis_service():
    """Test the analysis service directly."""
    try:
        print("🧪 Testing Analysis Service")
        print("=" * 50)
        
        # Check OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ No OpenAI API key found")
            return False
        
        print(f"✅ OpenAI API key found: {openai_key[:10]}...")
        
        # Import analysis service
        try:
            print("📦 Importing analysis service...")
            from services.analysis_service import analyze_transcript_and_extract
            print("✅ Analysis service imported successfully")
        except Exception as e:
            print(f"❌ Failed to import analysis service: {str(e)}")
            return False
        
        # Test analysis
        try:
            print("🔍 Running analysis...")
            result = analyze_transcript_and_extract(TEST_TRANSCRIPT)
            print("✅ Analysis completed successfully")
            print(f"📊 Result keys: {list(result.keys())}")
            
            # Show counts
            for key, items in result.items():
                print(f"   {key}: {len(items)} items")
                
            return True
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            print(f"   Exception type: {type(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_analysis_service()
    sys.exit(0 if success else 1) 