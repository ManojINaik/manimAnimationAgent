#!/usr/bin/env python3
"""
Test script to validate API keys for TheoremExplainAgent
Usage: python test_api_keys.py
"""

import os
import sys
from dotenv import load_dotenv

def test_gemini_api():
    """Test Gemini API key(s)"""
    print("Testing Gemini API...")
    
    try:
        import google.generativeai as genai
        import random
        
        # Load environment variables
        load_dotenv()
        
        # Get API key with fallback support
        gemini_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key_env:
            print("❌ No GEMINI_API_KEY found in environment")
            print("   Please set GEMINI_API_KEY in your .env file")
            print("   Get your API key from: https://aistudio.google.com/app/apikey")
            return False
        
        # Handle multiple keys
        if ',' in gemini_key_env:
            keys = [key.strip() for key in gemini_key_env.split(',') if key.strip()]
            print(f"   Found {len(keys)} API keys to test")
            api_key = random.choice(keys)
            print(f"   Testing random key: {api_key[:20]}...")
        else:
            api_key = gemini_key_env
            print(f"   Testing key: {api_key[:20]}...")
        
        # Configure and test
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Simple test
        response = model.generate_content("Say hello in one word")
        print(f"✅ Gemini API works! Response: {response.text.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_elevenlabs_api():
    """Test ElevenLabs API key"""
    print("\nTesting ElevenLabs API...")
    
    try:
        import requests
        
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("❌ No ELEVENLABS_API_KEY found in environment")
            print("   Please set ELEVENLABS_API_KEY in your .env file")
            print("   Get your API key from: https://elevenlabs.io/app/settings/api-keys")
            return False
        
        print(f"   Testing key: {api_key[:20]}...")
        
        # Test API with a simple request
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ ElevenLabs API works! User: {user_data.get('email', 'Unknown')}")
            return True
        else:
            print(f"❌ ElevenLabs API test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ElevenLabs API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing API Keys for TheoremExplainAgent\n")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("   Please create a .env file based on .env.template")
        print("   Run: cp .env.template .env")
        return
    
    gemini_ok = test_gemini_api()
    elevenlabs_ok = test_elevenlabs_api()
    
    print("\n" + "="*50)
    if gemini_ok and elevenlabs_ok:
        print("✅ All API keys are working correctly!")
        print("   You can now run generate_video.py")
    elif gemini_ok:
        print("⚠️  Gemini API works, but ElevenLabs API failed")
        print("   Video generation will work but TTS might fail")
    elif elevenlabs_ok:
        print("⚠️  ElevenLabs API works, but Gemini API failed")
        print("   TTS will work but video generation will fail")
    else:
        print("❌ Both API keys failed")
        print("   Please check your .env file and API keys")

if __name__ == "__main__":
    main() 