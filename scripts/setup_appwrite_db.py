#!/usr/bin/env python3
"""
Setup script to initialize Appwrite database structure for async video generation
Run this once to create all necessary collections and attributes
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.appwrite_integration import AppwriteVideoManager

async def main():
    """
    Main setup function
    """
    load_dotenv()
    
    print("🚀 Initializing Appwrite database structure...")
    
    # Initialize Appwrite manager
    manager = AppwriteVideoManager()
    
    if not manager.enabled:
        print("❌ Appwrite is not enabled or configured properly.")
        print("Please check your environment variables:")
        print("  - APPWRITE_API_KEY")
        print("  - APPWRITE_PROJECT_ID")
        print("  - APPWRITE_ENDPOINT")
        return
    
    # Setup database structure
    print("\n📊 Creating database and collections...")
    success = await manager.setup_database_structure()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("\nCreated structures:")
        print("  📁 Database: video_metadata")
        print("  📋 Collections:")
        print("     - videos (with progress tracking)")
        print("     - scenes (with status tracking)")
        print("     - agent_memory (for error patterns)")
        print("  🗄️ Storage Buckets:")
        print("     - final_videos")
        print("     - scene_videos")
        print("     - subtitles")
        print("     - source_code")
        
        print("\n🎯 Next steps:")
        print("1. Deploy the Appwrite function:")
        print("   appwrite functions create --functionId=video_generation --name='Video Generation'")
        print("   appwrite functions createDeployment --functionId=video_generation --entrypoint='main.py' --code='./appwrite_functions/video_generation' --activate")
        print("\n2. Set function environment variables in Appwrite Console")
        print("\n3. Run the frontend example:")
        print("   cd frontend_example")
        print("   npm install")
        print("   npm run dev")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 