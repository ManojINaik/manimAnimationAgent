#!/usr/bin/env python3
"""
Test script to verify app startup for HF Spaces debugging
"""

import os
import sys

def test_imports():
    """Test all required imports."""
    print("🧪 Testing imports...")
    
    try:
        import gradio as gr
        print("✅ Gradio imported successfully")
    except ImportError as e:
        print(f"❌ Gradio import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    return True

def test_app_functions():
    """Test app functions without launching."""
    print("🧪 Testing app functions...")
    
    try:
        # Import app functions
        sys.path.insert(0, '.')
        from app import check_dependencies, setup_environment
        
        print("✅ App imports successful")
        
        # Test dependency check
        dep_result = check_dependencies()
        print(f"📦 Dependencies: {dep_result}")
        
        # Test environment setup
        env_result = setup_environment()
        print(f"🔧 Environment: {env_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ App function test failed: {e}")
        return False

def test_gradio_basic():
    """Test basic Gradio functionality."""
    print("🧪 Testing Gradio basic functionality...")
    
    try:
        import gradio as gr
        
        # Create a simple test interface
        def test_fn(text):
            return f"Test successful: {text}"
        
        with gr.Blocks() as test_demo:
            input_text = gr.Textbox(label="Test Input")
            output_text = gr.Textbox(label="Test Output")
            test_btn = gr.Button("Test")
            test_btn.click(test_fn, inputs=[input_text], outputs=[output_text])
        
        print("✅ Gradio interface created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Gradio test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting HF Spaces compatibility tests...")
    print(f"🐍 Python version: {sys.version}")
    print(f"📂 Current directory: {os.getcwd()}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return False
    
    # Test Gradio basic
    if not test_gradio_basic():
        print("❌ Gradio tests failed")
        return False
    
    # Test app functions
    if not test_app_functions():
        print("❌ App function tests failed")
        return False
    
    print("✅ All tests passed! App should be compatible with HF Spaces.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 