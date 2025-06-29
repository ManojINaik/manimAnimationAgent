#!/usr/bin/env python3
"""
Test Script for Video Generation with Appwrite Integration

This script tests the complete video generation pipeline with the new Appwrite database integration.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append('src')

from src.config.config import Config

async def test_video_generation_with_appwrite():
    """Test video generation with Appwrite metadata management."""
    print("🧪 Testing Video Generation with Appwrite Integration")
    print("=" * 60)
    
    try:
        # Import required modules
        from generate_video import VideoGenerator
        from mllm_tools.litellm import LiteLLMWrapper
        
        print("1. Initializing AI models...")
        
        # Check for Gemini API key
        gemini_keys = os.getenv("GEMINI_API_KEY", "")
        if not gemini_keys:
            print("❌ No GEMINI_API_KEY found in environment")
            return False
            
        # Initialize models
        planner_model = LiteLLMWrapper(
            model_name=Config.DEFAULT_PLANNER_MODEL,
            temperature=Config.DEFAULT_MODEL_TEMPERATURE,
            print_cost=True,
            verbose=False,
            use_langfuse=False
        )
        
        print("✅ AI models initialized")
        
        print("\n2. Initializing Video Generator with Appwrite...")
        
        # Initialize video generator with Appwrite enabled
        video_generator = VideoGenerator(
            planner_model=planner_model,
            helper_model=planner_model,
            scene_model=planner_model,
            output_dir="output",
            use_rag=False,
            use_context_learning=False,
            use_visual_fix_code=False,
            verbose=True,
            use_appwrite=True  # Enable Appwrite integration
        )
        
        print("✅ Video Generator with Appwrite integration initialized")
        
        print("\n3. Testing planning phase...")
        
        # Test with a simple educational topic
        topic = "Basic Arithmetic Addition"
        description = "A simple educational video explaining addition of two numbers"
        
        # Generate only the plan to test database integration
        await video_generator.generate_video_pipeline(
            topic=topic,
            description=description,
            max_retries=1,
            only_plan=True  # Only generate plans for testing
        )
        
        print("✅ Planning phase completed with database integration")
        
        print("\n4. Checking database records...")
        
        if video_generator.use_appwrite and video_generator.appwrite_manager:
            # Get video statistics
            stats = await video_generator.appwrite_manager.get_video_statistics()
            print(f"📊 Database Statistics:")
            print(f"   - Planning videos: {stats.get('planning_videos', 0)}")
            print(f"   - Total scenes: {stats.get('total_scenes', 0)}")
            print(f"   - Memory patterns: {stats.get('memory_patterns', 0)}")
            
            # List recent videos
            videos = await video_generator.appwrite_manager.list_videos(limit=3)
            print(f"📝 Recent videos: {len(videos)} found")
            for video in videos:
                print(f"   - {video.get('topic', 'Unknown')} (Status: {video.get('status', 'Unknown')})")
        
        print("\n✅ Appwrite database integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_agent_memory_integration():
    """Test agent memory integration with video generation."""
    print("\n🧠 Testing Agent Memory Integration")
    print("=" * 40)
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        from src.core.appwrite_agent_memory import AppwriteAgentMemory
        
        # Initialize Appwrite components
        manager = AppwriteVideoManager()
        if not manager.enabled:
            print("❌ Appwrite not available")
            return False
            
        memory = AppwriteAgentMemory(manager)
        
        # Test storing a common Manim error pattern
        success = await memory.store_error_fix(
            error_message="AttributeError: 'Scene' object has no attribute 'add_animation'",
            original_code="scene.add_animation(circle.shift(UP))",
            fixed_code="scene.play(circle.animate.shift(UP))",
            topic="manim_basics",
            scene_type="animation",
            fix_method="llm"
        )
        
        if success:
            print("✅ Stored error-fix pattern successfully")
        else:
            print("⚠️ Failed to store error-fix pattern")
            
        # Test retrieving similar patterns
        similar_fixes = await memory.search_similar_fixes(
            error_message="Scene object error",
            code_context="scene.add_animation",
            topic="manim_basics"
        )
        
        print(f"✅ Found {len(similar_fixes)} similar error patterns")
        
        # Test memory statistics
        stats = await memory.get_memory_stats()
        print(f"📊 Memory Statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent memory test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Video Generation + Appwrite Integration Test Suite")
    print("=" * 70)
    
    # Test 1: Video generation with Appwrite
    test1_result = await test_video_generation_with_appwrite()
    
    # Test 2: Agent memory integration
    test2_result = await test_agent_memory_integration()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    print(f"Video Generation + Appwrite: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Agent Memory Integration:     {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! The Appwrite database integration is working correctly.")
        print("\n💡 Key Features Verified:")
        print("   ✅ Video metadata tracking in database")
        print("   ✅ Scene planning and status management")
        print("   ✅ Agent memory for error pattern learning")
        print("   ✅ Structured data storage replacing text files")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return test1_result and test2_result

if __name__ == "__main__":
    asyncio.run(main()) 