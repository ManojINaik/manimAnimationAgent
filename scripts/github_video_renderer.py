#!/usr/bin/env python3
"""
GitHub Actions Video Renderer
Processes videos from Appwrite queue and uploads results back
"""

import os
import sys
import json
import asyncio
from typing import List, Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from datetime import datetime, timezone

from generate_video import VideoGenerator
from mllm_tools.litellm import LiteLLMWrapper
from src.core.appwrite_integration import AppwriteVideoManager

class GitHubVideoRenderer:
    """Handles video rendering in GitHub Actions environment"""
    
    def __init__(self):
        """Initialize the renderer with Appwrite connection"""
        self.client = Client()
        self.client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        self.client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        self.client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        self.databases = Databases(self.client)
        self.appwrite_manager = AppwriteVideoManager()
        
    async def get_queued_videos(self) -> List[dict]:
        """Get videos that need rendering"""
        try:
            result = self.databases.list_documents(
                database_id="video_metadata",
                collection_id="videos",
                queries=[
                    Query.equal("status", ["queued_for_render", "ready_for_render"]),
                    Query.limit(5)  # Process 5 videos max per run
                ]
            )
            return result['documents']
        except Exception as e:
            print(f"Error fetching queued videos: {e}")
            return []
    
    async def update_video_status(self, video_id: str, status: str, error_message: str = None):
        """Update video status in database"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            if error_message:
                update_data["error_message"] = error_message
                
            self.databases.update_document(
                database_id="video_metadata",
                collection_id="videos",
                document_id=video_id,
                data=update_data
            )
            print(f"Updated video {video_id} status to: {status}")
        except Exception as e:
            print(f"Error updating video status: {e}")
    
    async def render_video(self, video_doc: dict) -> bool:
        """Render a single video"""
        video_id = video_doc['$id']
        topic = video_doc['topic']
        description = video_doc.get('description', '')
        
        print(f"Starting video rendering for: {topic} (ID: {video_id})")
        
        try:
            # Update status to rendering
            await self.update_video_status(video_id, "rendering")
            
            # Initialize models
            planner_model = LiteLLMWrapper(
                model_name=os.getenv('DEFAULT_PLANNER_MODEL', 'gemini/gemini-1.5-flash-002')
            )
            scene_model = LiteLLMWrapper(
                model_name=os.getenv('DEFAULT_SCENE_MODEL', 'gemini/gemini-1.5-flash-002')
            )
            
            # Initialize video generator
            generator = VideoGenerator(
                planner_model=planner_model,
                scene_model=scene_model,
                output_dir=f"output/{video_id}",
                verbose=True,
                use_rag=True,
                use_context_learning=True,
                use_visual_fix_code=True,
                use_appwrite=True
            )
            
            print(f"Generating video for topic: {topic}")
            
            # Generate the video using the pipeline
            await generator.generate_video_pipeline(
                topic=topic,
                description=description,
                max_retries=3
            )
            
            # Update status to completed
            await self.update_video_status(video_id, "completed")
            print(f"Successfully rendered video {video_id}")
            return True
            
        except Exception as e:
            print(f"Error rendering video {video_id}: {str(e)}")
            await self.update_video_status(video_id, "failed", str(e))
            return False
    
    async def process_queue(self):
        """Process all queued videos"""
        print("Checking for queued videos...")
        
        videos = await self.get_queued_videos()
        
        if not videos:
            print("No videos in queue")
            return
            
        print(f"Found {len(videos)} videos to process")
        
        success_count = 0
        for video in videos:
            try:
                success = await self.render_video(video)
                if success:
                    success_count += 1
            except Exception as e:
                print(f"Failed to process video {video['$id']}: {e}")
        
        print(f"Processed {success_count}/{len(videos)} videos successfully")

async def main():
    """Main entry point"""
    renderer = GitHubVideoRenderer()
    
    # Check if specific video ID was provided
    video_id = os.getenv('VIDEO_ID')
    if video_id:
        print(f"Processing specific video: {video_id}")
        # Get the specific video document
        try:
            video_doc = renderer.databases.get_document(
                database_id="video_metadata",
                collection_id="videos", 
                document_id=video_id
            )
            await renderer.render_video(video_doc)
        except Exception as e:
            print(f"Error processing video {video_id}: {e}")
    else:
        # Process all queued videos
        await renderer.process_queue()

if __name__ == "__main__":
    asyncio.run(main()) 