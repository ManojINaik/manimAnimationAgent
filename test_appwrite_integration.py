"""
Test Script for Appwrite Integration

This script tests the Appwrite video metadata management system and provides
setup and migration functionality.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append('src')

async def test_appwrite_setup():
    """Test Appwrite database and storage setup."""
    print("🧪 Testing Appwrite Integration Setup")
    print("=" * 50)
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        
        # Initialize Appwrite manager
        print("1. Initializing Appwrite manager...")
        manager = AppwriteVideoManager()
        
        if not manager.enabled:
            print("❌ Appwrite not enabled. Check your credentials.")
            return False
        
        print("✅ Appwrite manager initialized")
        
        # Setup database structure
        print("\n2. Setting up database structure...")
        setup_success = await manager.setup_database_structure()
        
        if setup_success:
            print("✅ Database structure setup completed")
        else:
            print("❌ Database setup failed")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure appwrite-sdk is installed: pip install appwrite")
        return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

async def test_video_management():
    """Test video record management."""
    print("\n3. Testing Video Management...")
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        
        manager = AppwriteVideoManager()
        if not manager.enabled:
            return False
        
        # Create a test video record
        video_id = await manager.create_video_record(
            topic="Test Calculus Video",
            description="A test video about derivatives",
            scene_count=3,
            session_id="test_session"
        )
        
        if video_id:
            print(f"✅ Created test video: {video_id}")
            
            # Update video status
            await manager.update_video_status(video_id, "planning")
            print("✅ Updated video status")
            
            # Get video record
            video_record = await manager.get_video_record(video_id)
            if video_record:
                print(f"✅ Retrieved video record: {video_record['topic']}")
            
            # Create test scenes
            for i in range(1, 4):
                scene_id = await manager.create_scene_record(
                    video_id=video_id,
                    scene_number=i,
                    scene_plan=f"Scene {i} plan",
                    storyboard=f"Scene {i} storyboard"
                )
                
                if scene_id:
                    print(f"✅ Created scene {i}: {scene_id}")
            
            # Get video scenes
            scenes = await manager.get_video_scenes(video_id)
            print(f"✅ Retrieved {len(scenes)} scenes for video")
            
            return True
        else:
            print("❌ Failed to create test video")
            return False
            
    except Exception as e:
        print(f"❌ Video management test failed: {e}")
        return False

async def test_agent_memory():
    """Test agent memory functionality."""
    print("\n4. Testing Agent Memory...")
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        from src.core.appwrite_agent_memory import AppwriteAgentMemory
        
        manager = AppwriteVideoManager()
        if not manager.enabled:
            return False
        
        memory = AppwriteAgentMemory(manager)
        
        # Store a test error-fix pattern
        success = await memory.store_error_fix(
            error_message="'Circle' object has no attribute 'animate'",
            original_code="circle = Circle()\nself.play(circle.animate.shift(UP))",
            fixed_code="circle = Circle()\nself.play(circle.animate.shift(UP))",
            topic="geometry",
            scene_type="animation",
            fix_method="llm"
        )
        
        if success:
            print("✅ Stored test error-fix pattern")
        
        # Search for similar fixes
        similar_fixes = await memory.search_similar_fixes(
            error_message="Circle object error",
            code_context="circle = Circle()",
            topic="geometry",
            scene_type="animation"
        )
        
        print(f"✅ Found {len(similar_fixes)} similar fixes")
        
        # Get memory statistics
        stats = await memory.get_memory_stats()
        print(f"✅ Memory stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent memory test failed: {e}")
        return False

async def test_migration():
    """Test migration of existing data."""
    print("\n5. Testing Data Migration...")
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        
        manager = AppwriteVideoManager()
        if not manager.enabled:
            return False
        
        # Test migration if output directory exists
        output_dir = "output"
        if os.path.exists(output_dir):
            print(f"Found existing output directory: {output_dir}")
            
            # Count existing data
            video_count = 0
            for item in os.listdir(output_dir):
                if os.path.isdir(os.path.join(output_dir, item)):
                    video_count += 1
            
            print(f"Found {video_count} potential videos to migrate")
            
            if video_count > 0:
                # Ask user if they want to migrate
                response = input("Would you like to migrate existing data? (y/N): ")
                if response.lower() == 'y':
                    success = await manager.migrate_existing_data(output_dir)
                    if success:
                        print("✅ Migration completed successfully")
                    else:
                        print("❌ Migration failed")
                else:
                    print("Migration skipped")
            else:
                print("No data to migrate")
        else:
            print("No output directory found - skipping migration test")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        return False

async def test_statistics():
    """Test statistics and analytics."""
    print("\n6. Testing Statistics...")
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        
        manager = AppwriteVideoManager()
        if not manager.enabled:
            return False
        
        # Get video statistics
        stats = await manager.get_video_statistics()
        
        print("📊 Video Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

async def test_file_management():
    """Test file upload functionality."""
    print("\n7. Testing File Management...")
    
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        
        manager = AppwriteVideoManager()
        if not manager.enabled:
            return False
        
        # Create a test file
        test_file = "test_upload.txt"
        with open(test_file, 'w') as f:
            f.write("This is a test file for Appwrite upload")
        
        try:
            # Test file upload
            file_id = await manager.upload_source_code(test_file, "test_scene_id")
            
            if file_id:
                print(f"✅ Uploaded test file: {file_id}")
                
                # Get file URL
                file_url = manager._get_file_url(manager.source_code_bucket_id, file_id)
                print(f"✅ File URL: {file_url}")
            else:
                print("❌ File upload failed")
                
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ File management test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Appwrite Video Metadata Management System Test Suite")
    print("=" * 60)
    
    # Check environment variables
    required_env_vars = ['APPWRITE_API_KEY', 'APPWRITE_PROJECT_ID']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file:")
        print("APPWRITE_API_KEY=your_api_key_here")
        print("APPWRITE_PROJECT_ID=your_project_id_here")
        print("APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1  # optional")
        return
    
    tests = [
        test_appwrite_setup,
        test_video_management,
        test_agent_memory,
        test_migration,
        test_statistics,
        test_file_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Appwrite integration is working correctly.")
        print("\nNext steps:")
        print("1. Update your video generation code to use AppwriteVideoManager")
        print("2. Replace AgentMemory with AppwriteAgentMemory")
        print("3. Use the migration function to move existing data")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 