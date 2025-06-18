#!/usr/bin/env python3
"""
Test script to verify deployment readiness for manimAnimationAgent
"""

import os
import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required imports work."""
    print("Testing imports...")
    
    try:
        import gradio as gr
        print("✅ Gradio imported successfully")
        print(f"   Version: {gr.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import Gradio: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import NumPy: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Requests: {e}")
        return False
    
    # Test optional dependencies
    try:
        import manim
        print("✅ Manim imported successfully")
    except ImportError:
        print("⚠️ Manim not available - will run in demo mode")
    
    return True

def test_app_functionality():
    """Test if the app can be imported and basic functions work."""
    print("\nTesting app functionality...")
    
    try:
        # Set demo mode for testing
        os.environ["DEMO_MODE"] = "true"
        
        # Import app components
        sys.path.insert(0, str(Path(__file__).parent))
        from app import (
            initialize_video_generator,
            simulate_video_generation,
            list_available_models,
            get_example_topics
        )
        
        print("✅ App components imported successfully")
        
        # Test initialization
        init_result = initialize_video_generator()
        print(f"   Initialization: {init_result}")
        
        # Test simulation
        sim_result = simulate_video_generation("test topic", "test context", 3)
        print(f"   Simulation result: {sim_result['success']}")
        
        # Test model listing
        models = list_available_models()
        print(f"   Available models: {len(models)} models")
        
        # Test examples
        examples = get_example_topics()
        print(f"   Example topics: {len(examples)} examples")
        
        print("✅ Basic app functionality works")
        return True
        
    except Exception as e:
        print(f"❌ App functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_gradio_interface():
    """Test if Gradio interface can be created."""
    print("\nTesting Gradio interface...")
    
    try:
        os.environ["DEMO_MODE"] = "true"
        from app import create_gradio_interface, create_api_endpoints
        
        # Test main interface creation
        interface = create_gradio_interface()
        print("✅ Main Gradio interface created successfully")
        
        # Test API interface creation
        api_interface = create_api_endpoints()
        print("✅ API interface created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Gradio interface test failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables and configuration."""
    print("\nTesting environment...")
    
    # Check demo mode
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    print(f"   Demo mode: {demo_mode}")
    
    # Check for API keys (optional)
    api_keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY")
    }
    
    for key, value in api_keys.items():
        if value:
            print(f"   {key}: ✅ Set")
        else:
            print(f"   {key}: ⚠️ Not set (demo mode will work)")
    
    # Check Python version
    python_version = sys.version_info
    print(f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version >= (3, 8):
        print("✅ Python version is compatible")
    else:
        print("❌ Python version too old (requires 3.8+)")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing manimAnimationAgent Deployment Readiness\n")
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("App Functionality", test_app_functionality),
        ("Gradio Interface", test_gradio_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} test...")
        print("="*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 ALL TESTS PASSED - Ready for deployment!")
        print("\n📋 Deployment Instructions:")
        print("1. Push code to GitHub repository")
        print("2. Create new Hugging Face Space")
        print("3. Connect to your repository")
        print("4. Set DEMO_MODE=false in Space settings (if you have API keys)")
        print("5. Add API keys as Space secrets (optional)")
        print("6. Deploy and test!")
    else:
        print("❌ SOME TESTS FAILED - Fix issues before deployment")
        print("\n🔧 Recommended actions:")
        print("- Install missing dependencies")
        print("- Fix import errors")
        print("- Ensure Python 3.8+ is being used")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 