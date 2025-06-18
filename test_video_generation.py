#!/usr/bin/env python3
"""
Test script for video generation functionality
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_video_generation():
    """Test the video generation pipeline."""
    
    # Check API keys
    gemini_keys = os.getenv("GEMINI_API_KEY", "")
    if not gemini_keys:
        print("❌ No GEMINI_API_KEY found. Please set environment variable.")
        print("Example: export GEMINI_API_KEY='key1,key2,key3'")
        return False
    
    key_count = len([k.strip() for k in gemini_keys.split(',') if k.strip()])
    print(f"✅ Found {key_count} Gemini API key(s)")
    
    try:
        # Import dependencies
        from generate_video import VideoGenerator
        from mllm_tools.litellm import LiteLLMWrapper
        print("✅ Successfully imported video generation dependencies")
        
        # Initialize models
        planner_model = LiteLLMWrapper(
            model_name="gemini/gemini-2.0-flash-exp",
            temperature=0.7,
            print_cost=True,
            verbose=True,
            use_langfuse=False
        )
        
        # Initialize video generator
        video_generator = VideoGenerator(
            planner_model=planner_model,  
            helper_model=planner_model,
            scene_model=planner_model,
            output_dir="test_output",
            use_rag=False,
            use_context_learning=False,
            use_visual_fix_code=False,
            verbose=True
        )
        
        print("✅ Video generator initialized successfully")
        
        # Test video generation
        test_topic = "Pythagorean Theorem"
        test_description = "Basic mathematical proof with geometric visualization"
        
        print(f"\n🚀 Testing video generation for: {test_topic}")
        print(f"📝 Description: {test_description}")
        
        result = await video_generator.generate_video_pipeline(
            topic=test_topic,
            description=test_description,
            max_retries=2,
            only_plan=False,
            specific_scenes=[1, 2]  # Just test 2 scenes
        )
        
        print("✅ Video generation pipeline completed successfully!")
        
        # Check output files
        file_prefix = test_topic.lower().replace(' ', '_')
        file_prefix = ''.join(c for c in file_prefix if c.isalnum() or c == '_')
        
        output_folder = os.path.join("test_output", file_prefix)
        if os.path.exists(output_folder):
            print(f"📁 Output folder created: {output_folder}")
            
            # List files in output folder
            for root, dirs, files in os.walk(output_folder):
                level = root.replace(output_folder, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Video Generation System\n")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(test_video_generation())
        if success:
            print("\n🎉 Test completed successfully!")
            print("The video generation system is working properly.")
        else:
            print("\n❌ Test failed.")
            print("Please check the error messages above and fix any issues.")
    finally:
        loop.close() 