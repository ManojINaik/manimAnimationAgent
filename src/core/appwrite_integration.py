"""
Appwrite Integration for Metadata Management

This module provides structured data storage and file management using Appwrite,
replacing the text file-based metadata system with a scalable database solution.
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import asyncio

try:
    from appwrite.client import Client
    from appwrite.services.databases import Databases
    from appwrite.services.storage import Storage
    from appwrite.services.users import Users
    from appwrite.exception import AppwriteException
    from appwrite.id import ID
    from appwrite.query import Query
    from appwrite.input_file import InputFile
    HAS_APPWRITE = True
except ImportError:
    Client = None
    Databases = None
    Storage = None 
    Users = None
    AppwriteException = None
    ID = None
    Query = None
    InputFile = None
    HAS_APPWRITE = False

class AppwriteVideoManager:
    """
    Manages video metadata and file storage using Appwrite.
    Provides structured data management for video generation pipeline.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 project_id: Optional[str] = None,
                 endpoint: Optional[str] = None):
        """
        Initialize Appwrite client and services.
        
        Args:
            api_key: Appwrite API key
            project_id: Appwrite project ID
            endpoint: Appwrite endpoint URL
        """
        self.enabled = HAS_APPWRITE
        
        if not self.enabled:
            print("Warning: Appwrite SDK not available. Database features disabled.")
            return
            
        # Get credentials from environment if not provided
        self.api_key = api_key or os.getenv('APPWRITE_API_KEY')
        self.project_id = project_id or os.getenv('APPWRITE_PROJECT_ID')
        self.endpoint = endpoint or os.getenv('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1')
        
        if not all([self.api_key, self.project_id]):
            print("Warning: Missing Appwrite credentials. Database features disabled.")
            self.enabled = False
            return
            
        try:
            # Initialize Appwrite client
            self.client = Client()
            self.client.set_endpoint(self.endpoint)
            self.client.set_project(self.project_id)
            self.client.set_key(self.api_key)
            
            # Initialize services
            self.databases = Databases(self.client)
            self.storage = Storage(self.client)
            self.users = Users(self.client)
            
            # Database and collection IDs
            self.database_id = "video_metadata"
            self.videos_collection_id = "videos"
            self.scenes_collection_id = "scenes"
            self.agent_memory_collection_id = "agent_memory"
            
            # Storage bucket IDs
            self.final_videos_bucket_id = "final_videos"
            self.scene_videos_bucket_id = "scene_videos"
            self.subtitles_bucket_id = "subtitles"
            self.source_code_bucket_id = "source_code"
            
            print("✅ Appwrite client initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Appwrite client: {e}")
            self.enabled = False

    async def setup_database_structure(self) -> bool:
        """
        Setup database collections and storage buckets.
        This should be run once during initial setup.
        
        Returns:
            bool: True if setup successful
        """
        if not self.enabled:
            return False
            
        try:
            # Create database
            try:
                self.databases.create(
                    database_id=self.database_id,
                    name="Video Metadata Database"
                )
                print("✅ Created video metadata database")
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating database: {e}")
                    return False
                print("Database already exists")
            
            # Create collections
            await self._create_videos_collection()
            await self._create_scenes_collection()
            await self._create_agent_memory_collection()
            
            # Create storage buckets
            await self._create_storage_buckets()
            
            print("✅ Database structure setup completed")
            return True
            
        except Exception as e:
            print(f"Failed to setup database structure: {e}")
            return False

    async def _create_videos_collection(self):
        """Create videos collection with proper attributes."""
        try:
            # Create videos collection
            self.databases.create_collection(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                name="Videos"
            )
            
            # Add string attributes
            string_attrs = [
                {"key": "topic", "size": 255, "required": True},
                {"key": "description", "size": 1000, "required": False},
                {"key": "owner_id", "size": 36, "required": False},
                {"key": "session_id", "size": 100, "required": False},
                {"key": "combined_video_url", "size": 500, "required": False},
                {"key": "subtitles_url", "size": 500, "required": False},
                {"key": "error_message", "size": 1000, "required": False}
            ]
            
            for attr in string_attrs:
                try:
                    self.databases.create_string_attribute(
                        database_id=self.database_id,
                        collection_id=self.videos_collection_id,
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"]
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating attribute {attr['key']}: {e}")

            # Add enum attribute for status
            try:
                self.databases.create_enum_attribute(
                    database_id=self.database_id,
                    collection_id=self.videos_collection_id,
                    key="status",
                    elements=["queued", "planning", "ready_for_render", "queued_for_render", "rendering", "completed", "failed"],
                    required=True
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating status attribute: {e}")

            # Add integer attributes
            integer_attrs = [
                {"key": "scene_count", "required": True},
                {"key": "progress", "required": False, "min": 0, "max": 100, "default": 0},
                {"key": "current_scene", "required": False, "min": 0}
            ]
            
            for attr in integer_attrs:
                try:
                    self.databases.create_integer_attribute(
                        database_id=self.database_id,
                        collection_id=self.videos_collection_id,
                        key=attr["key"],
                        required=attr["required"],
                        min=attr.get("min"),
                        max=attr.get("max"),
                        default=attr.get("default")
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating {attr['key']} attribute: {e}")

            # Add float attribute
            try:
                self.databases.create_float_attribute(
                    database_id=self.database_id,
                    collection_id=self.videos_collection_id,
                    key="total_duration",
                    required=False
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating total_duration attribute: {e}")

            # Add datetime attributes
            datetime_attrs = ["created_at", "updated_at"]
            for attr in datetime_attrs:
                try:
                    self.databases.create_datetime_attribute(
                        database_id=self.database_id,
                        collection_id=self.videos_collection_id,
                        key=attr,
                        required=True
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating {attr} attribute: {e}")
            
            print("✅ Created videos collection")
            
        except AppwriteException as e:
            if "already exists" not in str(e).lower():
                print(f"Error creating videos collection: {e}")
            else:
                print("Videos collection already exists")

    async def _create_scenes_collection(self):
        """Create scenes collection with proper attributes."""
        try:
            # Create scenes collection
            self.databases.create_collection(
                database_id=self.database_id,
                collection_id=self.scenes_collection_id,
                name="Scenes"
            )
            
            # Add string attributes (optimized sizes due to Appwrite limits)
            string_attrs = [
                {"key": "video_id", "size": 36, "required": True},
                {"key": "scene_plan", "size": 2000, "required": False},
                {"key": "storyboard", "size": 2000, "required": False},
                {"key": "technical_plan", "size": 2000, "required": False},
                {"key": "generated_code", "size": 5000, "required": False},
                {"key": "video_url", "size": 500, "required": False},
                {"key": "code_url", "size": 500, "required": False},
                {"key": "error_message", "size": 1000, "required": False}
            ]
            
            for attr in string_attrs:
                try:
                    self.databases.create_string_attribute(
                        database_id=self.database_id,
                        collection_id=self.scenes_collection_id,
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"]
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating attribute {attr['key']}: {e}")

            # Add integer attribute for scene number
            try:
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.scenes_collection_id,
                    key="scene_number",
                    required=True
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating scene_number attribute: {e}")

            # Add float attribute for duration
            try:
                self.databases.create_float_attribute(
                    database_id=self.database_id,
                    collection_id=self.scenes_collection_id,
                    key="duration",
                    required=False
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating duration attribute: {e}")

            # Add enum attribute for status
            try:
                self.databases.create_enum_attribute(
                    database_id=self.database_id,
                    collection_id=self.scenes_collection_id,
                    key="status",
                    elements=["planned", "coded", "rendered", "failed"],
                    required=True
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating status attribute: {e}")

            # Add datetime attributes
            datetime_attrs = ["created_at", "updated_at"]
            for attr in datetime_attrs:
                try:
                    self.databases.create_datetime_attribute(
                        database_id=self.database_id,
                        collection_id=self.scenes_collection_id,
                        key=attr,
                        required=True
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating {attr} attribute: {e}")
            
            print("✅ Created scenes collection")
            
        except AppwriteException as e:
            if "already exists" not in str(e).lower():
                print(f"Error creating scenes collection: {e}")
            else:
                print("Scenes collection already exists")

    async def _create_agent_memory_collection(self):
        """Create agent memory collection for structured error-fix patterns."""
        try:
            # Create agent memory collection
            self.databases.create_collection(
                database_id=self.database_id,
                collection_id=self.agent_memory_collection_id,
                name="Agent Memory"
            )
            
            # Add string attributes (optimized sizes due to Appwrite limits)
            string_attrs = [
                {"key": "error_hash", "size": 32, "required": True},
                {"key": "error_message", "size": 1000, "required": True},
                {"key": "original_code", "size": 3000, "required": True},
                {"key": "fixed_code", "size": 3000, "required": True},
                {"key": "topic", "size": 100, "required": False},
                {"key": "scene_type", "size": 50, "required": False}
            ]
            
            for attr in string_attrs:
                try:
                    self.databases.create_string_attribute(
                        database_id=self.database_id,
                        collection_id=self.agent_memory_collection_id,
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"]
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating attribute {attr['key']}: {e}")

            # Add enum attribute for fix method
            try:
                self.databases.create_enum_attribute(
                    database_id=self.database_id,
                    collection_id=self.agent_memory_collection_id,
                    key="fix_method",
                    elements=["auto", "llm", "manual"],
                    required=True
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating fix_method attribute: {e}")

            # Add integer attributes
            integer_attrs = [
                {"key": "success_count", "required": True, "min": 0},
                {"key": "failure_count", "required": True, "min": 0}
            ]
            
            for attr in integer_attrs:
                try:
                    self.databases.create_integer_attribute(
                        database_id=self.database_id,
                        collection_id=self.agent_memory_collection_id,
                        key=attr["key"],
                        required=attr["required"]
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating {attr['key']} attribute: {e}")

            # Add float attribute for confidence score
            try:
                self.databases.create_float_attribute(
                    database_id=self.database_id,
                    collection_id=self.agent_memory_collection_id,
                    key="confidence_score",
                    required=False
                )
                await asyncio.sleep(0.1)
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating confidence_score attribute: {e}")

            # Add datetime attributes
            datetime_attrs = ["created_at", "updated_at"]
            for attr in datetime_attrs:
                try:
                    self.databases.create_datetime_attribute(
                        database_id=self.database_id,
                        collection_id=self.agent_memory_collection_id,
                        key=attr,
                        required=True
                    )
                    await asyncio.sleep(0.1)
                except AppwriteException as e:
                    if "already exists" not in str(e).lower():
                        print(f"Error creating {attr} attribute: {e}")
            
            print("✅ Created agent memory collection")
            
        except AppwriteException as e:
            if "already exists" not in str(e).lower():
                print(f"Error creating agent memory collection: {e}")
            else:
                print("Agent memory collection already exists")

    async def _create_storage_buckets(self):
        """Create storage buckets for video assets."""
        buckets = [
            {
                "id": self.final_videos_bucket_id,
                "name": "Final Videos",
                "file_security": True,
                "permissions": ["read(\"any\")", "write(\"users\")"],
                "file_extensions": ["mp4", "mkv", "avi"],
                "max_file_size": 500 * 1024 * 1024  # 500MB
            },
            {
                "id": self.scene_videos_bucket_id,
                "name": "Scene Videos",
                "file_security": True,
                "permissions": ["read(\"any\")", "write(\"users\")"],
                "file_extensions": ["mp4", "mkv", "avi"],
                "max_file_size": 100 * 1024 * 1024  # 100MB
            },
            {
                "id": self.subtitles_bucket_id,
                "name": "Subtitles",
                "file_security": True,
                "permissions": ["read(\"any\")", "write(\"users\")"],
                "file_extensions": ["srt", "vtt", "ass"],
                "max_file_size": 1 * 1024 * 1024  # 1MB
            },
            {
                "id": self.source_code_bucket_id,
                "name": "Source Code",
                "file_security": True,
                "permissions": ["read(\"any\")", "write(\"users\")"],
                "file_extensions": ["py", "txt", "json"],
                "max_file_size": 10 * 1024 * 1024  # 10MB
            }
        ]
        
        for bucket in buckets:
            try:
                self.storage.create_bucket(
                    bucket_id=bucket["id"],
                    name=bucket["name"],
                    permissions=bucket["permissions"],
                    file_security=bucket["file_security"],
                    enabled=True,
                    maximum_file_size=bucket["max_file_size"],
                    allowed_file_extensions=bucket["file_extensions"]
                )
                print(f"✅ Created bucket: {bucket['name']}")
                
            except AppwriteException as e:
                if "already exists" not in str(e).lower():
                    print(f"Error creating bucket {bucket['name']}: {e}")
                else:
                    print(f"Bucket {bucket['name']} already exists")

    # Video Management Methods
    
    async def create_video_record(self, 
                                topic: str, 
                                description: str = None,
                                scene_count: int = 1,
                                owner_id: str = None,
                                session_id: str = None) -> Optional[str]:
        """
        Create a new video record in the database.
        
        Args:
            topic: Video topic
            description: Video description
            scene_count: Number of scenes
            owner_id: User ID who owns this video
            session_id: Session identifier
            
        Returns:
            str: Video ID if successful, None otherwise
        """
        if not self.enabled:
            return None
            
        try:
            video_id = ID.unique()
            current_time = datetime.now(timezone.utc).isoformat()
            
            result = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                document_id=video_id,
                data={
                    "topic": topic,
                    "description": description or f"Educational video about {topic}",
                    "status": "queued",
                    "scene_count": scene_count,
                    "owner_id": owner_id,
                    "session_id": session_id,
                    "created_at": current_time,
                    "updated_at": current_time
                }
            )
            
            print(f"✅ Created video record: {video_id} for topic: {topic}")
            return video_id
            
        except Exception as e:
            print(f"Failed to create video record: {e}")
            return None

    async def update_video_status(self, 
                                video_id: str, 
                                status: str,
                                error_message: str = None,
                                combined_video_url: str = None,
                                subtitles_url: str = None,
                                total_duration: float = None) -> bool:
        """
        Update video status and metadata.
        
        Args:
            video_id: Video ID
            status: New status (queued, planning, rendering, completed, failed)
            error_message: Error message if failed
            combined_video_url: URL to combined video file
            subtitles_url: URL to subtitles file
            total_duration: Total video duration in seconds
            
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            return False
            
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            if combined_video_url:
                update_data["combined_video_url"] = combined_video_url
            if subtitles_url:
                update_data["subtitles_url"] = subtitles_url
            if total_duration:
                update_data["total_duration"] = total_duration
            
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                document_id=video_id,
                data=update_data
            )
            
            print(f"✅ Updated video {video_id} status to: {status}")
            return True
            
        except Exception as e:
            print(f"Failed to update video status: {e}")
            return False

    async def get_video_record(self, video_id: str) -> Optional[Dict]:
        """
        Get video record by ID.
        
        Args:
            video_id: Video ID
            
        Returns:
            Dict: Video record or None
        """
        if not self.enabled:
            return None
            
        try:
            result = self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                document_id=video_id
            )
            
            return result
            
        except Exception as e:
            print(f"Failed to get video record: {e}")
            return None

    async def list_videos(self, 
                         owner_id: str = None,
                         status: str = None,
                         limit: int = 25,
                         offset: int = 0) -> List[Dict]:
        """
        List videos with optional filtering.
        
        Args:
            owner_id: Filter by owner ID
            status: Filter by status
            limit: Maximum number of results
            offset: Results offset
            
        Returns:
            List of video records
        """
        if not self.enabled:
            return []
            
        try:
            queries = [Query.limit(limit), Query.offset(offset)]
            
            if owner_id:
                queries.append(Query.equal("owner_id", owner_id))
            if status:
                queries.append(Query.equal("status", status))
            
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                queries=queries
            )
            
            return result.get("documents", [])
            
        except Exception as e:
            print(f"Failed to list videos: {e}")
            return []

    # Scene Management Methods
    
    async def create_scene_record(self,
                                video_id: str,
                                scene_number: int,
                                scene_plan: str = None,
                                storyboard: str = None,
                                technical_plan: str = None) -> Optional[str]:
        """
        Create a new scene record.
        
        Args:
            video_id: Parent video ID
            scene_number: Scene number
            scene_plan: Scene plan text
            storyboard: Storyboard description
            technical_plan: Technical implementation plan
            
        Returns:
            str: Scene ID if successful
        """
        if not self.enabled:
            return None
            
        try:
            scene_id = ID.unique()
            current_time = datetime.now(timezone.utc).isoformat()
            
            result = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.scenes_collection_id,
                document_id=scene_id,
                data={
                    "video_id": video_id,
                    "scene_number": scene_number,
                    "scene_plan": scene_plan,
                    "storyboard": storyboard,
                    "technical_plan": technical_plan,
                    "status": "planned",
                    "created_at": current_time,
                    "updated_at": current_time
                }
            )
            
            print(f"✅ Created scene record: {scene_id} for video: {video_id}")
            return scene_id
            
        except Exception as e:
            print(f"Failed to create scene record: {e}")
            return None

    async def update_scene_record(self,
                                scene_id: str,
                                status: str = None,
                                generated_code: str = None,
                                video_url: str = None,
                                code_url: str = None,
                                duration: float = None,
                                error_message: str = None) -> bool:
        """
        Update scene record with new data.
        
        Args:
            scene_id: Scene ID
            status: New status
            generated_code: Generated Manim code
            video_url: URL to rendered video
            code_url: URL to source code file
            duration: Scene duration in seconds
            error_message: Error message if failed
            
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            return False
            
        try:
            update_data = {
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if status:
                update_data["status"] = status
            if generated_code:
                # Ensure generated_code is a string and within Appwrite field size limit (5000 chars)
                if not isinstance(generated_code, str):
                    generated_code = str(generated_code)
                if len(generated_code) > 5000:
                    generated_code = generated_code[:4970] + "... (truncated)"
                update_data["generated_code"] = generated_code
            if video_url:
                update_data["video_url"] = video_url
            if code_url:
                update_data["code_url"] = code_url
            if duration:
                update_data["duration"] = duration
            if error_message:
                update_data["error_message"] = error_message
            
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.scenes_collection_id,
                document_id=scene_id,
                data=update_data
            )
            
            print(f"✅ Updated scene {scene_id}")
            return True
            
        except Exception as e:
            print(f"Failed to update scene record: {e}")
            return False

    async def get_video_scenes(self, video_id: str) -> List[Dict]:
        """
        Get all scenes for a video.
        
        Args:
            video_id: Video ID
            
        Returns:
            List of scene records
        """
        if not self.enabled:
            return []
            
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.scenes_collection_id,
                queries=[
                    Query.equal("video_id", video_id),
                    Query.order_asc("scene_number")
                ]
            )
            
            return result.get("documents", [])
            
        except Exception as e:
            print(f"Failed to get video scenes: {e}")
            return []

    # Agent Memory Management
    
    def _create_error_hash(self, error_message: str, code_context: str) -> str:
        """Create a hash for similar error patterns."""
        # Normalize error message to capture similar patterns
        error_normalized = error_message.lower()
        # Remove specific variable names and line numbers
        import re
        error_normalized = re.sub(r'\b\w*\d+\w*\b', '<VAR>', error_normalized)
        error_normalized = re.sub(r'line \d+', 'line <NUM>', error_normalized)
        
        # Include code context for better pattern matching
        combined = f"{error_normalized}:{code_context[:200]}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    async def store_agent_memory(self,
                               error_message: str,
                               original_code: str,
                               fixed_code: str,
                               topic: str = None,
                               scene_type: str = None,
                               fix_method: str = "llm") -> bool:
        """
        Store or update agent memory pattern.
        
        Args:
            error_message: Error message
            original_code: Original problematic code
            fixed_code: Fixed code
            topic: Topic/subject
            scene_type: Type of scene
            fix_method: How the fix was applied
            
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            return False
            
        try:
            error_hash = self._create_error_hash(error_message, original_code)
            
            # Check if pattern already exists
            existing = await self.search_agent_memory(error_hash=error_hash)
            current_time = datetime.now(timezone.utc).isoformat()
            
            if existing:
                # Update existing pattern
                memory_id = existing[0]["$id"]
                success_count = existing[0].get("success_count", 0) + 1
                
                self.databases.update_document(
                    database_id=self.database_id,
                    collection_id=self.agent_memory_collection_id,
                    document_id=memory_id,
                    data={
                        "success_count": success_count,
                        "updated_at": current_time,
                        "fix_method": fix_method
                    }
                )
                print(f"✅ Updated agent memory pattern: {error_hash}")
            else:
                # Create new pattern
                memory_id = ID.unique()
                self.databases.create_document(
                    database_id=self.database_id,
                    collection_id=self.agent_memory_collection_id,
                    document_id=memory_id,
                    data={
                        "error_hash": error_hash,
                        "error_message": error_message,
                        "original_code": original_code,
                        "fixed_code": fixed_code,
                        "topic": topic or "general",
                        "scene_type": scene_type or "general",
                        "fix_method": fix_method,
                        "success_count": 1,
                        "failure_count": 0,
                        "created_at": current_time,
                        "updated_at": current_time
                    }
                )
                print(f"✅ Created agent memory pattern: {error_hash}")
            
            return True
            
        except Exception as e:
            print(f"Failed to store agent memory: {e}")
            return False

    async def search_agent_memory(self,
                                error_hash: str = None,
                                topic: str = None,
                                scene_type: str = None,
                                fix_method: str = None,
                                limit: int = 10) -> List[Dict]:
        """
        Search agent memory patterns.
        
        Args:
            error_hash: Specific error hash
            topic: Filter by topic
            scene_type: Filter by scene type
            fix_method: Filter by fix method
            limit: Maximum results
            
        Returns:
            List of matching memory patterns
        """
        if not self.enabled:
            return []
            
        try:
            queries = [Query.limit(limit), Query.order_desc("success_count")]
            
            if error_hash:
                queries.append(Query.equal("error_hash", error_hash))
            if topic:
                queries.append(Query.equal("topic", topic))
            if scene_type:
                queries.append(Query.equal("scene_type", scene_type))
            if fix_method:
                queries.append(Query.equal("fix_method", fix_method))
            
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.agent_memory_collection_id,
                queries=queries
            )
            
            return result.get("documents", [])
            
        except Exception as e:
            print(f"Failed to search agent memory: {e}")
            return []

    # File Management Methods
    
    async def upload_file(self,
                         bucket_id: str,
                         file_path: str,
                         file_id: str = None,
                         permissions: List[str] = None) -> Optional[str]:
        """
        Upload a file to Appwrite storage.
        
        Args:
            bucket_id: Storage bucket ID
            file_path: Local file path
            file_id: Custom file ID (optional)
            permissions: File permissions
            
        Returns:
            str: File ID if successful
        """
        if not self.enabled or not os.path.exists(file_path):
            return None
            
        try:
            file_id = file_id or ID.unique()
            permissions = permissions or ["read(\"any\")"]
            
            result = self.storage.create_file(
                bucket_id=bucket_id,
                file_id=file_id,
                file=InputFile.from_path(file_path),
                permissions=permissions
            )
            
            # Get file URL
            file_url = self._get_file_url(bucket_id, file_id)
            print(f"✅ Uploaded file: {file_path} -> {file_url}")
            
            return file_id
            
        except Exception as e:
            print(f"Failed to upload file {file_path}: {e}")
            return None

    def _get_file_url(self, bucket_id: str, file_id: str) -> str:
        """Get public URL for a file."""
        return f"{self.endpoint}/storage/buckets/{bucket_id}/files/{file_id}/view?project={self.project_id}"

    async def upload_video_file(self, file_path: str, video_id: str) -> Optional[str]:
        """Upload a final video file."""
        file_id = f"video_{video_id}"
        return await self.upload_file(self.final_videos_bucket_id, file_path, file_id)

    async def upload_scene_video(self, file_path: str, scene_id: str) -> Optional[str]:
        """Upload a scene video file."""
        file_id = f"scene_{scene_id}"
        return await self.upload_file(self.scene_videos_bucket_id, file_path, file_id)

    async def upload_subtitles(self, file_path: str, video_id: str) -> Optional[str]:
        """Upload a subtitles file."""
        file_id = f"subs_{video_id}"
        return await self.upload_file(self.subtitles_bucket_id, file_path, file_id)

    async def upload_source_code(self, file_path: str, scene_id: str) -> Optional[str]:
        """Upload source code file."""
        file_id = f"code_{scene_id}"
        return await self.upload_file(self.source_code_bucket_id, file_path, file_id)

    # Statistics and Analytics
    
    async def get_video_statistics(self) -> Dict[str, Any]:
        """Get video generation statistics."""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            # Get video counts by status
            video_stats = {}
            for status in ["queued", "planning", "rendering", "completed", "failed"]:
                result = self.databases.list_documents(
                    database_id=self.database_id,
                    collection_id=self.videos_collection_id,
                    queries=[Query.equal("status", status), Query.limit(1)]
                )
                video_stats[f"{status}_videos"] = result.get("total", 0)
            
            # Get scene stats
            scene_result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.scenes_collection_id,
                queries=[Query.limit(1)]
            )
            total_scenes = scene_result.get("total", 0)
            
            # Get memory stats
            memory_result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.agent_memory_collection_id,
                queries=[Query.limit(1)]
            )
            total_memory_patterns = memory_result.get("total", 0)
            
            return {
                "enabled": True,
                **video_stats,
                "total_scenes": total_scenes,
                "memory_patterns": total_memory_patterns
            }
            
        except Exception as e:
            print(f"Failed to get statistics: {e}")
            return {"enabled": True, "error": str(e)}

    # Migration helpers for existing data
    
    async def migrate_existing_data(self, output_dir: str) -> bool:
        """
        Migrate existing file-based data to Appwrite database.
        
        Args:
            output_dir: Directory containing existing video data
            
        Returns:
            bool: True if migration successful
        """
        if not self.enabled or not os.path.exists(output_dir):
            return False
            
        try:
            migrated_videos = 0
            migrated_scenes = 0
            
            # Process each topic folder
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if not os.path.isdir(item_path):
                    continue
                    
                # Extract topic from folder name
                topic = item.replace('_', ' ').title()
                
                # Create video record
                video_id = await self.create_video_record(
                    topic=topic,
                    description=f"Migrated video about {topic}",
                    scene_count=self._count_scenes(item_path),
                    session_id="migration"
                )
                
                if video_id:
                    migrated_videos += 1
                    
                    # Process scenes
                    scenes_migrated = await self._migrate_video_scenes(item_path, video_id)
                    migrated_scenes += scenes_migrated
                    
                    # Update video status based on files
                    status = self._determine_video_status(item_path)
                    await self.update_video_status(video_id, status)
            
            print(f"✅ Migration completed: {migrated_videos} videos, {migrated_scenes} scenes")
            return True
            
        except Exception as e:
            print(f"Failed to migrate existing data: {e}")
            return False

    def _count_scenes(self, video_dir: str) -> int:
        """Count scenes in a video directory."""
        scene_count = 0
        for item in os.listdir(video_dir):
            if item.startswith('scene') and os.path.isdir(os.path.join(video_dir, item)):
                scene_count += 1
        return max(scene_count, 1)

    async def _migrate_video_scenes(self, video_dir: str, video_id: str) -> int:
        """Migrate scenes for a specific video."""
        migrated_count = 0
        
        for item in os.listdir(video_dir):
            if not item.startswith('scene'):
                continue
                
            scene_dir = os.path.join(video_dir, item)
            if not os.path.isdir(scene_dir):
                continue
                
            scene_number = int(item.replace('scene', ''))
            
            # Load scene data
            scene_plan = self._load_file_content(scene_dir, 'implementation_plan.txt')
            generated_code = self._load_scene_code(scene_dir)
            
            # Create scene record
            scene_id = await self.create_scene_record(
                video_id=video_id,
                scene_number=scene_number,
                scene_plan=scene_plan,
                generated_code=generated_code
            )
            
            if scene_id:
                migrated_count += 1
                
                # Update scene status
                status = "rendered" if os.path.exists(os.path.join(scene_dir, "succ_rendered.txt")) else "coded"
                await self.update_scene_record(scene_id, status=status)
        
        return migrated_count

    def _load_file_content(self, directory: str, filename: str) -> Optional[str]:
        """Load content from a file if it exists."""
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return None

    def _load_scene_code(self, scene_dir: str) -> Optional[str]:
        """Load generated code from scene directory."""
        code_dir = os.path.join(scene_dir, "code")
        if os.path.exists(code_dir):
            for file in os.listdir(code_dir):
                if file.endswith('.py'):
                    return self._load_file_content(code_dir, file)
        return None

    def _determine_video_status(self, video_dir: str) -> str:
        """Determine video status based on files."""
        combined_video = os.path.join(video_dir, f"{os.path.basename(video_dir)}_combined.mp4")
        if os.path.exists(combined_video):
            return "completed"
        
        # Check if any scenes are rendered
        for item in os.listdir(video_dir):
            if item.startswith('scene'):
                scene_dir = os.path.join(video_dir, item)
                if os.path.exists(os.path.join(scene_dir, "succ_rendered.txt")):
                    return "rendering"
        
        return "planning" 