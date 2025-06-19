"""
Appwrite Function for Video Generation Coordination
Handles video generation coordination and database operations without heavy dependencies
"""

import os
import sys
import json
import asyncio
import uuid
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.exception import AppwriteException
from appwrite.id import ID

# Simple LLM wrapper without heavy dependencies
try:
    from mllm_tools.litellm import LiteLLMWrapper
except ImportError:
    print("Warning: LiteLLMWrapper not available, using mock")
    class LiteLLMWrapper:
        def __init__(self, model):
            self.model = model

class VideoCoordinator:
    """
    Handles video generation coordination and database operations
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the video coordinator with Appwrite context
        
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
        
        # Database IDs
        self.database_id = "video_metadata"
        self.videos_collection_id = "videos"
        self.scenes_collection_id = "scenes"
        
    async def trigger_github_workflow(self, video_id: str) -> bool:
        """
        Trigger GitHub Actions workflow to render video
        
        Args:
            video_id: Video ID to render
            
        Returns:
            True if trigger was successful
        """
        try:
            github_token = os.getenv('GITHUB_TOKEN')
            github_repo = os.getenv('GITHUB_REPO')  # format: "username/repo"
            
            if not github_token or not github_repo:
                self.log("GitHub token or repo not configured - videos will be processed on schedule")
                return False
            
            # Trigger repository dispatch event
            url = f"https://api.github.com/repos/{github_repo}/dispatches"
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            data = {
                "event_type": "render_video",
                "client_payload": {
                    "video_id": video_id
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 204:
                self.log(f"Successfully triggered GitHub workflow for video {video_id}")
                return True
            else:
                self.log(f"Failed to trigger GitHub workflow: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Error triggering GitHub workflow: {str(e)}")
            return False
        
    async def create_video_record(self, topic: str, description: str, owner_id: str, session_id: str) -> Optional[str]:
        """
        Create a video record in the database
        
        Args:
            topic: Video topic
            description: Video description  
            owner_id: User ID
            session_id: Session ID
            
        Returns:
            Video document ID if successful, None otherwise
        """
        try:
            document = await self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                document_id=ID.unique(),
                data={
                    "topic": topic,
                    "description": description,
                    "owner_id": owner_id,
                    "session_id": session_id,
                    "status": "queued",
                    "progress": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            return document['$id']
        except Exception as e:
            self.error(f"Failed to create video record: {str(e)}")
            return None
        
    async def update_video_status(self, 
                                  video_id: str, 
                                  status: str, 
                                  progress: int = None,
                                  error_message: str = None):
        """
        Update video status in database
        
        Args:
            video_id: Video document ID
            status: Current status
            progress: Progress percentage (0-100)
            error_message: Error message if failed
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if progress is not None:
                update_data["progress"] = progress
                
            if error_message:
                update_data["error_message"] = error_message
            
            await self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                document_id=video_id,
                data=update_data
            )
            
            self.log(f"Updated video {video_id} status to: {status}")
            
        except Exception as e:
            self.error(f"Failed to update video status: {str(e)}")
    
    async def process_video_request(self, 
                                   topic: str, 
                                   description: str,
                                   user_id: str,
                                   video_id: str):
        """
        Process a video generation request (coordination only)
        
        Args:
            topic: Video topic
            description: Video description
            user_id: User ID making the request
            video_id: Pre-created video document ID
        """
        try:
            # Update status to processing
            await self.update_video_status(video_id, "processing", progress=10)
            
            self.log(f"Processing video request for topic: {topic}")
            
            # Simulate planning phase
            await self.update_video_status(video_id, "planning", progress=30)
            await asyncio.sleep(1)  # Simulate processing time
            
            # Mark as ready for external processing
            await self.update_video_status(video_id, "ready_for_render", progress=50)
            
            self.log(f"Video {video_id} ready for external rendering")
            
            # Try to trigger GitHub Actions workflow
            workflow_triggered = await self.trigger_github_workflow(video_id)
            
            if workflow_triggered:
                await self.update_video_status(video_id, "queued_for_render", progress=100)
                self.log(f"Video {video_id} queued for GitHub Actions rendering")
            else:
                # Fallback - mark for scheduled processing
                await self.update_video_status(video_id, "queued_for_render", progress=100)
                self.log(f"Video {video_id} queued for scheduled processing")
                
        except Exception as e:
            self.error(f"Video request processing failed: {str(e)}")
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
        
        log(f"Received video request for topic: {topic}")
        
        # Initialize coordinator
        coordinator = VideoCoordinator(context)
        
        # Create video record in database
        video_id = await coordinator.create_video_record(
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
        
        # Start async processing (non-blocking)
        asyncio.create_task(coordinator.process_video_request(
            topic=topic,
            description=description,
            user_id=user_id,
            video_id=video_id
        ))
        
        # Return immediately with task ID
        return res.json({
            'success': True,
            'message': 'Video request received and queued',
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