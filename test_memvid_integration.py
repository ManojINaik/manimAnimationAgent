#!/usr/bin/env python3
"""
Test script to verify Memvid integration is working correctly.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_memvid_import():
    """Test if memvid can be imported successfully."""
    print("🔍 Testing Memvid import...")
    
    try:
        from src.rag.memvid_integration import MemvidRAGIntegration, get_memvid_integration
        print("✅ Memvid integration module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import memvid integration: {e}")
        return False

def test_memvid_dependencies():
    """Test if memvid dependencies are available."""
    print("\n🔍 Testing Memvid dependencies...")
    
    dependencies = [
        ('memvid', 'memvid'),
        ('opencv-python', 'cv2'),
        ('sentence-transformers', 'sentence_transformers'),
        ('qrcode', 'qrcode'),
        ('pyzbar', 'pyzbar'),
        ('numpy', 'numpy'),
        ('google-generativeai', 'google.generativeai')
    ]
    
    all_available = True
    for pkg_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {pkg_name} is available")
        except ImportError:
            print(f"❌ {pkg_name} is missing")
            all_available = False
    
    return all_available

def test_memvid_files():
    """Test if memvid memory files exist."""
    print("\n🔍 Testing Memvid memory files...")
    
    files = [
        'manim_memory.mp4',
        'manim_memory_index.json',
        'manim_memory_index.faiss'
    ]
    
    all_exist = True
    for file_path in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} exists ({size:,} bytes)")
        else:
            print(f"❌ {file_path} is missing")
            all_exist = False
    
    return all_exist

def test_memvid_initialization():
    """Test if memvid integration can be initialized."""
    print("\n🔍 Testing Memvid initialization...")
    
    try:
        from src.rag.memvid_integration import get_memvid_integration
        
        memvid_rag = get_memvid_integration(
            video_file="manim_memory.mp4",
            index_file="manim_memory_index.json"
        )
        
        if memvid_rag and memvid_rag.is_available():
            stats = memvid_rag.get_stats()
            print(f"✅ Memvid initialized successfully")
            print(f"   📊 Stats: {stats}")
            return True
        else:
            print("❌ Memvid initialization failed - not available")
            return False
            
    except Exception as e:
        print(f"❌ Memvid initialization failed: {e}")
        return False

def test_code_generator_memvid():
    """Test if CodeGenerator can use memvid."""
    print("\n🔍 Testing CodeGenerator with Memvid...")
    
    try:
        from src.core.code_generator import CodeGenerator
        from mllm_tools.litellm import LiteLLMWrapper
        
        # Create a minimal model for testing
        model = LiteLLMWrapper("gemini/gemini-2.5-flash-latest")
        
        # Initialize CodeGenerator with memvid enabled
        code_gen = CodeGenerator(
            scene_model=model,
            helper_model=model,
            output_dir="test_output",
            use_memvid=True,
            memvid_video_file="manim_memory.mp4",
            memvid_index_file="manim_memory_index.json"
        )
        
        if hasattr(code_gen, 'memvid_rag') and code_gen.memvid_rag:
            print("✅ CodeGenerator successfully initialized with Memvid")
            return True
        else:
            print("❌ CodeGenerator failed to initialize Memvid")
            return False
            
    except Exception as e:
        print(f"❌ CodeGenerator memvid test failed: {e}")
        return False

def main():
    """Run all memvid integration tests."""
    print("🧪 Memvid Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_memvid_import,
        test_memvid_dependencies,
        test_memvid_files,
        test_memvid_initialization,
        test_code_generator_memvid
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Memvid integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 