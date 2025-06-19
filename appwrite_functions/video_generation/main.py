"""
Appwrite Function for Asynchronous Video Generation
Handles video generation requests asynchronously with real-time status updates
"""

import os
import sys
import json
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.realtime import Realtime
from appwrite.exception import AppwriteException
from appwrite.id import ID

# Import our video generation modules
from mllm_tools.litellm import LiteLLMWrapper
from generate_video import VideoGenerator
from src.core.appwrite_integration import AppwriteVideoManager

class AsyncVideoGenerator:
    """
    Handles asynchronous video generation with real-time status updates
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the async video generator with Appwrite context
        
        Args:
            context: Appwrite function context
        """
        self.context = context
        self.req = context['req']
        self.res = context['res']
        self.log = context['log']
        self.error = context['error']
        
        # Initialize Appwrite client with function's API key
        self.client = Client()
        self.client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        self.client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        self.client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        self.databases = Databases(self.client)
        self.storage = Storage(self.client)
        self.appwrite_manager = AppwriteVideoManager()
        
        # Database IDs
        self.database_id = "video_metadata"
        self.videos_collection_id = "videos"
        self.scenes_collection_id = "scenes"
        
    async def update_video_status(self, 
                                  video_id: str, 
                                  status: str, 
                                  progress: int = None,
                                  current_scene: int = None,
                                  error_message: str = None):
        """
        Update video status in database and trigger realtime update
        
        Args:
            video_id: Video document ID
            status: Current status (planning, rendering, completed, failed)
            progress: Progress percentage (0-100)
            current_scene: Current scene being processed
            error_message: Error message if failed
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if progress is not None:
                update_data["progress"] = progress
                
            if current_scene is not None:
                update_data["current_scene"] = current_scene
                
            if error_message:
                update_data["error_message"] = error_message
            
            # Update database document
            await self.appwrite_manager.update_video_status(
                video_id=video_id,
                status=status,
                error_message=error_message
            )
            
            self.log(f"Updated video {video_id} status to: {status}")
            
        except Exception as e:
            self.error(f"Failed to update video status: {str(e)}")
    
    async def process_video_generation(self, 
                                       topic: str, 
                                       description: str,
                                       user_id: str,
                                       video_id: str):
        """
        Process the video generation pipeline asynchronously
        
        Args:
            topic: Video topic
            description: Video description
            user_id: User ID making the request
            video_id: Pre-created video document ID
        """
        try:
            # Update status to planning
            await self.update_video_status(video_id, "planning", progress=10)
            
            # Initialize video generator
            self.log("Initializing video generator...")
            
            # Initialize models
            planner_model = LiteLLMWrapper(
                model=os.getenv('DEFAULT_PLANNER_MODEL', 'gemini/gemini-1.5-flash-002')
            )
            scene_model = LiteLLMWrapper(
                model=os.getenv('DEFAULT_SCENE_MODEL', 'gemini/gemini-1.5-flash-002')
            )
            
            generator = VideoGenerator(
                planner_model=planner_model,
                scene_model=scene_model,
                output_dir=f"/tmp/video_output/{video_id}",
                verbose=True,
                use_rag=True,
                use_context_learning=True,
                use_visual_fix_code=True,
                use_appwrite=True
            )
            
            # Generate scene outline
            self.log(f"Generating scene outline for topic: {topic}")
            await self.update_video_status(video_id, "planning", progress=20)
            
            scene_outline = generator.generate_scene_outline(
                topic=topic,
                description=description,
                session_id=video_id
            )
            
            # Generate scene implementations
            self.log("Generating scene implementations...")
            await self.update_video_status(video_id, "planning", progress=40)
            
            implementation_plans = await generator.generate_scene_implementation_concurrently(
                topic=topic,
                description=description,
                plan=scene_outline,
                session_id=video_id
            )
            
            # Create scene records in database
            scene_ids = await self.appwrite_manager.create_scene_records(
                video_id=video_id,
                scene_plans=implementation_plans
            )
            
            # Update status to rendering
            await self.update_video_status(video_id, "rendering", progress=50)
            
            # Render scenes with progress updates
            total_scenes = len(implementation_plans)
            for i, (plan, scene_id) in enumerate(zip(implementation_plans, scene_ids)):
                current_progress = 50 + (40 * (i + 1) // total_scenes)
                await self.update_video_status(
                    video_id, 
                    "rendering", 
                    progress=current_progress,
                    current_scene=i + 1
                )
                
                self.log(f"Rendering scene {i + 1}/{total_scenes}")
                
                # Render scene
                await generator.render_video_fix_code(
                    topic=topic,
                    description=description,
                    scene_outline=scene_outline,
                    implementation_plans=[plan],
                    session_id=video_id,
                    scene_ids=[scene_id]
                )
            
            # Combine videos
            self.log("Combining video scenes...")
            await self.update_video_status(video_id, "rendering", progress=90)
            
            generator.combine_videos(topic)
            
            # Upload final video
            self.log("Uploading final video...")
            await self.update_video_status(video_id, "rendering", progress=95)
            
            final_video_path = os.path.join(
                generator.output_dir, 
                f"{topic.lower().replace(' ', '_')}_combined.mp4"
            )
            
            if os.path.exists(final_video_path):
                video_file_id = await self.appwrite_manager.upload_video_file(
                    final_video_path, 
                    video_id
                )
                
                if video_file_id:
                    video_url = self.appwrite_manager._get_file_url(
                        self.appwrite_manager.final_videos_bucket_id,
                        video_file_id
                    )
                    
                    # Update final status
                    await self.appwrite_manager.update_video_status(
                        video_id=video_id,
                        status="completed",
                        combined_video_url=video_url
                    )
                    await self.update_video_status(video_id, "completed", progress=100)
                    
                    self.log(f"Video generation completed successfully: {video_url}")
                else:
                    raise Exception("Failed to upload final video")
            else:
                raise Exception("Final video file not found")
                
        except Exception as e:
            self.error(f"Video generation failed: {str(e)}")
            await self.update_video_status(
                video_id, 
                "failed", 
                error_message=str(e)
            )
            raise

async def main(context):
    """
    Main entry point for the Appwrite function
    
    Args:
        context: Appwrite function context
    """
    req = context['req']
    res = context['res']
    log = context['log']
    error = context['error']
    
    try:
        # Parse request body
        body = json.loads(req['body'] or '{}')
        
        # Validate required fields
        topic = body.get('topic')
        description = body.get('description', '')
        user_id = body.get('userId')
        
        if not topic:
            return res.json({
                'success': False,
                'error': 'Topic is required'
            }, 400)
        
        log(f"Received video generation request for topic: {topic}")
        
        # Initialize generator
        generator = AsyncVideoGenerator(context)
        
        # Create video record in database
        video_id = await generator.appwrite_manager.create_video_record(
            topic=topic,
            description=description,
            owner_id=user_id,
            session_id=str(uuid.uuid4())
        )
        
        if not video_id:
            return res.json({
                'success': False,
                'error': 'Failed to create video record'
            }, 500)
        
        # Start async video generation (non-blocking)
        asyncio.create_task(generator.process_video_generation(
            topic=topic,
            description=description,
            user_id=user_id,
            video_id=video_id
        ))
        
        # Return immediately with task ID
        return res.json({
            'success': True,
            'message': 'Video generation started',
            'videoId': video_id,
            'status': 'queued'
        })
        
    except Exception as e:
        error(f"Function error: {str(e)}")
        return res.json({
            'success': False,
            'error': str(e)
        }, 500)

# Appwrite function handler
def handler(context):
    """
    Appwrite function handler
    """
    return asyncio.run(main(context)) 