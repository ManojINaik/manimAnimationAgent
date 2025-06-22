import os
import json
import random
from typing import Union, List, Dict, Optional
import subprocess
import argparse
import glob
from PIL import Image
import re
from dotenv import load_dotenv
import asyncio
import uuid # Import uuid for generating trace_id
import warnings
from pydantic import ConfigDict

from mllm_tools.litellm import LiteLLMWrapper
from mllm_tools.utils import _prepare_text_inputs # Keep _prepare_text_inputs if still used directly in main

# Import new modules
from src.core.video_planner import VideoPlanner
from src.core.code_generator import CodeGenerator
from src.core.video_renderer import VideoRenderer
from src.utils.utils import _print_response, _extract_code, extract_xml, extract_xml_tag # Import utility functions
from src.config.config import Config # Import Config class

# Appwrite integration for metadata management
from src.core.appwrite_integration import AppwriteVideoManager
# Removed AppwriteAgentMemory import - using Mem0-based AgentMemory instead

# Video parsing
from src.core.parse_video import (
    get_images_from_video,
    image_with_most_non_black_space
)
from task_generator import get_banned_reasonings
from task_generator.prompts_raw import (_code_font_size, _code_disable, _code_limit, _prompt_manim_cheatsheet)

# Suppress Pydantic serialization warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
# Suppress mem0 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="mem0")

# Load allowed models list from JSON file
allowed_models_path = os.path.join(os.path.dirname(__file__), 'src', 'utils', 'allowed_models.json')
with open(allowed_models_path, 'r') as f:
    allowed_models = json.load(f).get("allowed_models", [])

load_dotenv(override=True)

class VideoGenerator:
    """
    A class for generating manim videos using AI models.

    This class coordinates the video generation pipeline by managing scene planning,
    code generation, and video rendering. It supports concurrent scene processing,
    visual code fixing, and RAG (Retrieval Augmented Generation).

    Args:
        planner_model: Model used for scene planning and high-level decisions
        scene_model: Model used specifically for scene generation (defaults to planner_model)
        helper_model: Helper model for additional tasks (defaults to planner_model)
        output_dir (str): Directory to store generated files and videos
        verbose (bool): Whether to print detailed output
        use_rag (bool): Whether to use Retrieval Augmented Generation
        use_context_learning (bool): Whether to use context learning with example code
        context_learning_path (str): Path to context learning examples
        chroma_db_path (str): Path to ChromaDB for RAG
        manim_docs_path (str): Path to Manim documentation for RAG
        embedding_model (str): Model to use for embeddings
        use_visual_fix_code (bool): Whether to use visual feedback for code fixing
        use_langfuse (bool): Whether to enable Langfuse logging
        trace_id (str, optional): Trace ID for logging
        max_scene_concurrency (int): Maximum number of scenes to process concurrently

    Attributes:
        output_dir (str): Directory for output files
        verbose (bool): Verbosity flag
        use_visual_fix_code (bool): Visual code fixing flag
        session_id (str): Unique session identifier
        scene_semaphore (asyncio.Semaphore): Controls concurrent scene processing
        banned_reasonings (list): List of banned reasoning patterns
        planner (VideoPlanner): Handles scene planning
        code_generator (CodeGenerator): Handles code generation
        video_renderer (VideoRenderer): Handles video rendering
    """

    def __init__(self,
                 planner_model,
                 scene_model=None,
                 helper_model=None,
                 output_dir="output",
                 verbose=False,
                 use_rag=False,
                 use_context_learning=False,
                 context_learning_path="data/context_learning",
                 chroma_db_path="data/rag/chroma_db",
                 manim_docs_path="data/rag/manim_docs",
                 embedding_model="gemini/text-embedding-004",
                 use_visual_fix_code=False,
                 use_langfuse=True,
                 trace_id=None,
                 max_scene_concurrency: int = 5,
                 use_appwrite=True):
        self.output_dir = output_dir
        self.verbose = verbose
        self.use_visual_fix_code = use_visual_fix_code
        self.session_id = self._load_or_create_session_id()  # Modified to load existing or create new
        self.scene_semaphore = asyncio.Semaphore(max_scene_concurrency)
        self.banned_reasonings = get_banned_reasonings()

        # Agent memory will be initialized by CodeGenerator when use_agent_memory=True
        # This uses Mem0 for error patterns and learning

        # Initialize Appwrite for file uploads and video/scene records
        self.appwrite_manager = None
        if use_appwrite:
            try:
                from src.core.appwrite_integration import AppwriteVideoManager
                self.appwrite_manager = AppwriteVideoManager()
                print("✅ Appwrite initialized for file uploads and database records")
            except Exception as e:
                print(f"⚠️ Appwrite initialization failed: {e}")
                use_appwrite = False

        self.use_appwrite = use_appwrite

        # Initialize the planner with the model instance, not a string
        self.planner_model = planner_model

        # Initialize separate modules
        self.planner = VideoPlanner(
            planner_model=self.planner_model, # Pass the initialized model
            helper_model=helper_model,
            output_dir=output_dir,
            print_response=verbose,
            use_context_learning=use_context_learning,
            context_learning_path=context_learning_path,
            use_rag=use_rag,
            session_id=self.session_id,
            chroma_db_path=chroma_db_path,
            manim_docs_path=manim_docs_path,
            embedding_model=embedding_model,
            use_langfuse=use_langfuse
        )
        self.code_generator = CodeGenerator(
            scene_model=scene_model if scene_model is not None else self.planner_model, # Pass the model
            helper_model=helper_model if helper_model is not None else self.planner_model, # Pass the model
            output_dir=output_dir,
            print_response=verbose,
            use_rag=use_rag,
            use_context_learning=use_context_learning,
            context_learning_path=context_learning_path,
            chroma_db_path=chroma_db_path,
            manim_docs_path=manim_docs_path,
            embedding_model=embedding_model,
            use_visual_fix_code=use_visual_fix_code,
            use_langfuse=use_langfuse,
            session_id=self.session_id,
            use_agent_memory=True  # Enable agent memory for error learning
        )
        self.video_renderer = VideoRenderer(
            output_dir=output_dir,
            print_response=verbose,
            use_visual_fix_code=use_visual_fix_code
        )

    def _load_or_create_session_id(self) -> str:
        """
        Load existing session ID from file or create a new one.

        Returns:
            str: The session ID either loaded from file or newly created.
        """
        session_file = os.path.join(self.output_dir, "session_id.txt")

        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session_id = f.read().strip()
                print(f"Loaded existing session ID: {session_id}")
                return session_id

        # Create new session ID if none exists
        session_id = str(uuid.uuid4())
        os.makedirs(self.output_dir, exist_ok=True)
        with open(session_file, 'w') as f:
            f.write(session_id)
        print(f"Created new session ID: {session_id}")
        return session_id

    def _save_topic_session_id(self, topic: str, session_id: str) -> None:
        """
        Save session ID for a specific topic.

        Args:
            topic (str): The topic to save the session ID for
            session_id (str): The session ID to save
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        topic_dir = os.path.join(self.output_dir, file_prefix)
        os.makedirs(topic_dir, exist_ok=True)

        session_file = os.path.join(topic_dir, "session_id.txt")
        with open(session_file, 'w') as f:
            f.write(session_id)

    def _load_topic_session_id(self, topic: str) -> Optional[str]:
        """
        Load session ID for a specific topic if it exists.

        Args:
            topic (str): The topic to load the session ID for

        Returns:
            Optional[str]: The session ID if found, None otherwise
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        session_file = os.path.join(self.output_dir, file_prefix, "session_id.txt")

        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return f.read().strip()
        return None

    def generate_scene_outline(self,
                            topic: str,
                            description: str,
                            session_id: str) -> str:
        """
        Generate scene outline using VideoPlanner.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            session_id (str): Session identifier

        Returns:
            str: Generated and extracted scene outline
        """
        scene_outline = self.planner.generate_scene_outline(topic, description, session_id)
        return scene_outline

    async def generate_scene_implementation(self,
                                      topic: str,
                                      description: str,
                                      plan: str,
                                      session_id: str) -> List[str]:
        """
        Generate scene implementations using VideoPlanner.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            plan (str): The scene plan to implement
            session_id (str): Session identifier for tracking

        Returns:
            List[str]: List of generated scene implementations
        """
        return await self.planner.generate_scene_implementation(topic, description, plan, session_id)

    async def generate_scene_implementation_concurrently(self,
                                              topic: str,
                                              description: str,
                                              plan: str,
                                              session_id: str) -> List[str]:
        """
        Generate scene implementations concurrently using VideoPlanner.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            plan (str): The scene plan to implement
            session_id (str): Session identifier for tracking

        Returns:
            List[str]: List of generated scene implementations
        """
        return await self.planner.generate_scene_implementation_concurrently(topic, description, plan, session_id, self.scene_semaphore) # Pass semaphore

    def load_implementation_plans(self, topic: str) -> Dict[int, Optional[str]]:
        """
        Load implementation plans for each scene.

        Args:
            topic (str): The topic to load implementation plans for

        Returns:
            Dict[int, Optional[str]]: Dictionary mapping scene numbers to their plans.
                                    If a scene's plan is missing, its value will be None.
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)

        # Load scene outline from file
        scene_outline_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_scene_outline.txt")
        if not os.path.exists(scene_outline_path):
            return {}
        
        with open(scene_outline_path, "r") as f:
            scene_outline = f.read()

        # Extract scene outline to get number of scenes
        scene_outline_content = extract_xml(scene_outline)
        scene_number = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline_content))
        print(f"Number of scenes: {scene_number}")

        implementation_plans = {}

        # Check each scene's implementation plan
        for i in range(1, scene_number + 1):
            plan_path = os.path.join(self.output_dir, file_prefix, f"scene{i}", f"{file_prefix}_scene{i}_implementation_plan.txt")
            if os.path.exists(plan_path):
                with open(plan_path, "r") as f:
                    implementation_plans[i] = f.read()
                print(f"Found existing implementation plan for scene {i}")
            else:
                implementation_plans[i] = None
                print(f"Missing implementation plan for scene {i}")

        return implementation_plans

    async def render_video_fix_code(self,
                              topic: str,
                              description: str,
                              scene_outline: str,
                              implementation_plans: List,
                              max_retries=3,
                              session_id: str = None,
                              scene_ids: List[Optional[str]] = None) -> None:
        """
        Render the video for all scenes with code fixing capability.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            scene_outline (str): The overall scene outline
            implementation_plans (List): List of implementation plans for each scene
            max_retries (int, optional): Maximum number of code fix attempts. Defaults to 3.
            session_id (str, optional): Session identifier for tracking
            scene_ids (List[Optional[str]], optional): List of scene IDs for database tracking
            
        Raises:
            Exception: When any scene fails after max retries, aborting the entire video generation
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)

        # Ensure scene_ids has the same length as implementation_plans
        if scene_ids is None:
            scene_ids = [None] * len(implementation_plans)
        elif len(scene_ids) < len(implementation_plans):
            scene_ids.extend([None] * (len(implementation_plans) - len(scene_ids)))

        # Create tasks for each scene
        tasks = []
        for i, implementation_plan in enumerate(implementation_plans):
            # Try to load scene trace id, or generate new one if it doesn't exist
            scene_dir = os.path.join(self.output_dir, file_prefix, f"scene{i+1}")
            subplan_dir = os.path.join(scene_dir, "subplans")
            os.makedirs(subplan_dir, exist_ok=True)  # Create directories if they don't exist
            
            scene_trace_id_path = os.path.join(subplan_dir, "scene_trace_id.txt")
            try:
                with open(scene_trace_id_path, 'r') as f:
                    scene_trace_id = f.read().strip()
            except FileNotFoundError:
                scene_trace_id = str(uuid.uuid4())
                with open(scene_trace_id_path, 'w') as f:
                    f.write(scene_trace_id)

            # Get the scene ID for this scene
            scene_id = scene_ids[i] if i < len(scene_ids) else None
            
            task = self.process_scene(i, scene_outline, implementation_plan, topic, description, max_retries, file_prefix, session_id, scene_trace_id, scene_id)
            tasks.append(task)

        # Execute all tasks concurrently - if any scene fails after max retries, it will raise an exception
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            # If any scene failed after max retries, abort the entire video generation
            error_msg = f"Video generation aborted: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Re-raise the exception to propagate the failure up the call stack
            raise Exception(error_msg)

    async def process_scene(self, i: int, scene_outline: str, scene_implementation: str, topic: str, description: str, max_retries: int, file_prefix: str, session_id: str, scene_trace_id: str, scene_id: str = None): # added scene_trace_id and scene_id
        """
        Process a single scene using CodeGenerator and VideoRenderer.

        Args:
            i (int): Scene index
            scene_outline (str): Overall scene outline
            scene_implementation (str): Implementation plan for this scene
            topic (str): The topic of the video
            description (str): Description of the video content
            max_retries (int): Maximum number of code fix attempts
            file_prefix (str): Prefix for file naming
            session_id (str): Session identifier for tracking
            scene_trace_id (str): Trace identifier for this scene
            scene_id (str, optional): Scene ID for database tracking
            
        Raises:
            Exception: When max retries are reached for this scene
        """
        curr_scene = i + 1
        curr_version = 0
        # scene_trace_id = str(uuid.uuid4()) # Remove uuid generation
        rag_queries_cache = {}  # Initialize RAG queries cache

        # Create necessary directories
        code_dir = os.path.join(self.output_dir, file_prefix, f"scene{curr_scene}", "code")
        os.makedirs(code_dir, exist_ok=True)
        media_dir = os.path.join(self.output_dir, file_prefix, "media") # Define media_dir here

        # Define scene upload callback
        async def upload_scene_callback(scene_num: int, file_path: str, scene_dir: str):
            """Upload scene video and update scene record."""
            if not self.use_appwrite or not self.appwrite_manager or not scene_id:
                return
                
            try:
                # Find the generated video file in the media directory
                media_base = os.path.join(self.output_dir, file_prefix, "media", "videos")
                video_folder = None
                
                # Look for the video folder - extract version from file_path to ensure we get the right version
                file_name = os.path.basename(file_path)
                version_match = re.search(r'_v(\d+)\.py$', file_name)
                current_version = int(version_match.group(1)) if version_match else curr_version
                
                # Look for the video folder - start with the version from the file path
                for version in range(current_version, -1, -1):  # Check from current version down to 0
                    potential_folder = os.path.join(media_base, f"{file_prefix}_scene{scene_num}_v{version}", "1080p60")
                    if os.path.exists(potential_folder):
                        video_folder = potential_folder
                        break
                
                if not video_folder:
                    # Fallback: look for any scene folder matching this scene number
                    if os.path.exists(media_base):
                        for folder in os.listdir(media_base):
                            if folder.startswith(f"{file_prefix}_scene{scene_num}_v"):
                                potential_folder = os.path.join(media_base, folder, "1080p60")
                                if os.path.exists(potential_folder):
                                    video_folder = potential_folder
                                    break
                
                video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')] if video_folder and os.path.exists(video_folder) else []
                
                if video_files:
                    video_path = os.path.join(video_folder, video_files[0])
                    # Upload scene video
                    scene_file_id = await self.appwrite_manager.upload_scene_video(video_path, scene_id)
                    
                    if scene_file_id:
                        # Get video URL
                        video_url = self.appwrite_manager._get_file_url(
                            self.appwrite_manager.scene_videos_bucket_id, 
                            scene_file_id
                        )
                        
                        # Upload source code
                        code_file_id = await self.appwrite_manager.upload_source_code(file_path, scene_id)
                        code_url = None
                        if code_file_id:
                            code_url = self.appwrite_manager._get_file_url(
                                self.appwrite_manager.source_code_bucket_id, 
                                code_file_id
                            )
                        
                        # Update scene record
                        await self.update_scene_record(
                            scene_id,
                            status="rendered",
                            video_url=video_url,
                            code_url=code_url
                        )
                        print(f"✅ Scene {scene_num} uploaded successfully")

                        # NOTE: DO NOT DELETE LOCAL FILES - they are needed for video combination later
                        # The combination step happens after all scenes are uploaded
                        # Clean up will happen after final video is generated
                        
                    else:
                        print(f"⚠️ Failed to upload scene {scene_num} video")
                else:
                    print(f"⚠️ No video file found for scene {scene_num} in {video_folder}")
                    
            except Exception as e:
                print(f"⚠️ Scene {scene_num} upload failed: {e}")

        async with self.scene_semaphore:
            # Step 3A: Generate initial manim code
            code, log = self.code_generator.generate_manim_code(
                topic=topic,
                description=description,
                scene_outline=scene_outline,
                scene_implementation=scene_implementation,
                scene_number=curr_scene,
                additional_context=[_prompt_manim_cheatsheet, _code_font_size, _code_limit, _code_disable],
                scene_trace_id=scene_trace_id, # Use passed scene_trace_id
                session_id=session_id,
                rag_queries_cache=rag_queries_cache  # Pass the cache
            )

            # Save initial code and log (file operations can be offloaded if needed)
            with open(os.path.join(code_dir, f"{file_prefix}_scene{curr_scene}_v{curr_version}_init_log.txt"), "w", encoding='utf-8') as f:
                f.write(log)
            with open(os.path.join(code_dir, f"{file_prefix}_scene{curr_scene}_v{curr_version}.py"), "w", encoding='utf-8') as f:
                f.write(code)
            print(f"Code saved to {code_dir}/{file_prefix}_scene{curr_scene}_v{curr_version}.py")

            # Step 3B: Compile and fix code if needed
            error_message = None
            while True: # Retry loop controlled by break statements
                code, error_message = await self.video_renderer.render_scene(
                    code=code,
                    file_prefix=file_prefix,
                    curr_scene=curr_scene,
                    curr_version=curr_version,
                    code_dir=code_dir,
                    media_dir=media_dir,
                    max_retries=max_retries, # Pass max_retries here if needed in render_scene
                    use_visual_fix_code=self.use_visual_fix_code,
                    visual_self_reflection_func=self.code_generator.visual_self_reflection, # Pass visual_self_reflection function
                    banned_reasonings=self.banned_reasonings, # Pass banned reasonings
                    scene_trace_id=scene_trace_id,
                    topic=topic,
                    session_id=session_id,
                    on_success_callback=upload_scene_callback  # Add the upload callback
                )
                if error_message is None: # Render success if error_message is None
                    break

                if curr_version >= max_retries: # Max retries reached
                    error_msg = f"Max retries ({max_retries}) reached for scene {curr_scene}, error: {error_message}"
                    print(f"❌ {error_msg}")
                    
                    # Update scene record with failure status if using Appwrite
                    if scene_id and self.use_appwrite and self.appwrite_manager:
                        try:
                            await self.update_scene_record(
                                scene_id,
                                status="failed",
                                error_message=error_message
                            )
                        except Exception as e:
                            print(f"⚠️ Failed to update scene record: {e}")
                    
                    # Raise exception to abort entire video generation process
                    raise Exception(error_msg)

                curr_version += 1
                # if program runs this, it means that the code is not rendered successfully
                code = self.code_generator.fix_code_errors(
                    implementation_plan=scene_implementation,
                    code=code,
                    error=error_message,
                    scene_trace_id=scene_trace_id,
                    topic=topic,
                    scene_number=curr_scene,
                    session_id=session_id,
                    rag_queries_cache=rag_queries_cache
                )

                with open(os.path.join(code_dir, f"{file_prefix}_scene{curr_scene}_v{curr_version}_fix_log.txt"), "w", encoding='utf-8') as f:
                    f.write(error_message)
                with open(os.path.join(code_dir, f"{file_prefix}_scene{curr_scene}_v{curr_version}.py"), "w", encoding='utf-8') as f:
                    f.write(code)

                print(f"Code saved to {code_dir}/{file_prefix}_scene{curr_scene}_v{curr_version}.py")

    def run_manim_process(self,
                          topic: str):
        """
        Run manim on all generated manim code for a specific topic using VideoRenderer.

        Args:
            topic (str): The topic to render videos for
        """
        return self.video_renderer.run_manim_process(topic)

    def create_snapshot_scene(self, topic: str, scene_number: int, version_number: int, return_type: str = "image"):
        """
        Create a snapshot of the video for a specific topic and scene using VideoRenderer.

        Args:
            topic (str): The topic of the video
            scene_number (int): Scene number to snapshot
            version_number (int): Version number to snapshot
            return_type (str, optional): Type of snapshot to return. Defaults to "image".

        Returns:
            The snapshot in the specified format
        """
        return self.video_renderer.create_snapshot_scene(topic, scene_number, version_number, return_type)

    def combine_videos(self, topic: str):
        """
        Combine all videos and subtitle files for a specific topic using VideoRenderer.

        Args:
            topic (str): The topic to combine videos for
        """
        self.video_renderer.combine_videos(topic)

    async def _generate_scene_implementation_single(self, topic: str, description: str, scene_outline_i: str, i: int, file_prefix: str, session_id: str, scene_trace_id: str) -> str:
        """
        Generate detailed implementation plan for a single scene using VideoPlanner.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            scene_outline_i (str): Outline for this specific scene
            i (int): Scene index
            file_prefix (str): Prefix for file naming
            session_id (str): Session identifier for tracking
            scene_trace_id (str): Trace identifier for this scene

        Returns:
            str: Generated implementation plan
        """
        return await self.planner._generate_scene_implementation_single(topic, description, scene_outline_i, i, file_prefix, session_id, scene_trace_id)

    async def create_video_record(self, topic: str, description: str, scene_count: int, session_id: str = None) -> Optional[str]:
        """Create a video record in Appwrite database."""
        if not self.use_appwrite or not self.appwrite_manager:
            return None
            
        try:
            video_id = await self.appwrite_manager.create_video_record(
                topic=topic,
                description=description,
                scene_count=scene_count,
                session_id=session_id
            )
            if self.verbose and video_id:
                print(f"📝 Created video record: {video_id}")
            return video_id
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to create video record: {e}")
            return None

    async def update_video_status(self, video_id: str, status: str, error_message: str = None, 
                                 combined_video_url: str = None, subtitles_url: str = None) -> bool:
        """Update video status in Appwrite database."""
        if not self.use_appwrite or not self.appwrite_manager or not video_id:
            return False
            
        try:
            success = await self.appwrite_manager.update_video_status(
                video_id=video_id,
                status=status,
                error_message=error_message,
                combined_video_url=combined_video_url,
                subtitles_url=subtitles_url
            )
            if self.verbose and success:
                print(f"📝 Updated video {video_id} status to: {status}")
            return success
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to update video status: {e}")
            return False

    async def create_scene_records(self, video_id: str, scene_plans: List[str]) -> List[Optional[str]]:
        """Create scene records in Appwrite database."""
        if not self.use_appwrite or not self.appwrite_manager or not video_id:
            return [None] * len(scene_plans)
            
        scene_ids = []
        for i, plan in enumerate(scene_plans):
            try:
                scene_id = await self.appwrite_manager.create_scene_record(
                    video_id=video_id,
                    scene_number=i + 1,
                    scene_plan=plan
                )
                scene_ids.append(scene_id)
                if self.verbose and scene_id:
                    print(f"📝 Created scene {i + 1} record: {scene_id}")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Failed to create scene {i + 1} record: {e}")
                scene_ids.append(None)
        
        return scene_ids

    async def update_scene_record(self, scene_id: str, status: str = None, generated_code: str = None,
                                 video_url: str = None, code_url: str = None, error_message: str = None) -> bool:
        """Update scene record in Appwrite database."""
        if not self.use_appwrite or not self.appwrite_manager or not scene_id:
            return False
            
        try:
            success = await self.appwrite_manager.update_scene_record(
                scene_id=scene_id,
                status=status,
                generated_code=generated_code,
                video_url=video_url,
                code_url=code_url,
                error_message=error_message
            )
            if self.verbose and success:
                print(f"📝 Updated scene {scene_id} record")
            return success
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to update scene record: {e}")
            return False

    async def generate_video_pipeline(self, topic: str, description: str, max_retries: int, only_plan: bool = False, specific_scenes: List[int] = None, only_render: bool = False, only_combine: bool = False):
        """
        Modified pipeline to handle partial scene completions and option to only generate plans for specific scenes.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            max_retries (int): Maximum number of code fix attempts
            only_plan (bool, optional): Whether to only generate plans without rendering. Defaults to False.
            specific_scenes (List[int], optional): List of specific scenes to process. Defaults to None.
            only_render (bool, optional): Whether to only render scenes without combining videos. Defaults to False.
            only_combine (bool, optional): Whether to only combine videos. Defaults to False.
        """
        session_id = self._load_or_create_session_id()
        self._save_topic_session_id(topic, session_id)
        
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)

        # Initialize database record for this video
        video_id = None
        scene_ids = []  # Initialize scene_ids at the beginning
        try:
            # Get initial scene count estimate (will be updated after planning)
            estimated_scene_count = 4  # Default estimate
            video_id = await self.create_video_record(topic, description, estimated_scene_count, session_id)
            if video_id:
                await self.update_video_status(video_id, "planning")
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Database initialization failed: {e}")
            video_id = None
        
        # Load or generate scene outline
        scene_outline_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_scene_outline.txt")
        if not os.path.exists(scene_outline_path):
            scene_outline = self.planner.generate_scene_outline(topic, description, session_id)
            if not scene_outline or not extract_xml(scene_outline):
                print(f"❌ Failed to generate a valid scene outline for topic: {topic}. Aborting.")
                raise ValueError("Failed to generate a valid scene outline from the AI model. Please try a different topic or model.")
            
            os.makedirs(os.path.join(self.output_dir, file_prefix), exist_ok=True)
            with open(scene_outline_path, "w", encoding='utf-8') as f:
                f.write(scene_outline)
        else:
            print(f"Loaded existing scene outline for topic: {topic}")
            with open(scene_outline_path, "r", encoding='utf-8') as f:
                scene_outline = f.read()

        # After loading or generating, verify the outline has content
        scene_outline_content = extract_xml(scene_outline)
        if not scene_outline_content or len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline_content)) == 0:
            print(f"❌ Scene outline for '{topic}' is empty or invalid. Deleting and aborting.")
            if os.path.exists(scene_outline_path):
                os.remove(scene_outline_path)
            raise ValueError(f"The generated scene outline for '{topic}' was empty or invalid. The process cannot continue.")

        # Load or generate implementation plans
        implementation_plans_dict = self.load_implementation_plans(topic)
        if not implementation_plans_dict:
            scene_outline_content = extract_xml(scene_outline)
            scene_numbers = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline_content))
            implementation_plans_dict = {i: None for i in range(1, scene_numbers + 1)}

        # Create scene records in database after scene outline is generated
        try:
            if video_id and not scene_ids:  # Only create if scene_ids is empty
                scene_outline_content = extract_xml(scene_outline)
                scene_count = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline_content))
                
                # Update video with actual scene count
                await self.update_video_status(video_id, "planning")
                
                # Create scene records
                scene_plans = []
                for i in range(1, scene_count + 1):
                    scene_match = re.search(f'<SCENE_{i}>(.*?)</SCENE_{i}>', scene_outline_content, re.DOTALL)
                    scene_plan = scene_match.group(1).strip() if scene_match else f"Scene {i} plan"
                    scene_plans.append(scene_plan)
                
                scene_ids = await self.create_scene_records(video_id, scene_plans)
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to create scene records: {e}")

        # Generate missing implementation plans for specified scenes or all missing scenes
        missing_scenes = []
        for scene_num, plan in implementation_plans_dict.items():
            if plan is None and (specific_scenes is None or scene_num in specific_scenes):
                missing_scenes.append(scene_num)

        if missing_scenes:
            print(f"Generating implementation plans for missing scenes: {missing_scenes}")
            for scene_num in missing_scenes:
                scene_outline_content = extract_xml(scene_outline)
                scene_match = re.search(f'<SCENE_{scene_num}>(.*?)</SCENE_{scene_num}>', scene_outline_content, re.DOTALL)
                if scene_match:
                    scene_outline_i = scene_match.group(1)
                    scene_trace_id = str(uuid.uuid4())
                    implementation_plan = await self._generate_scene_implementation_single(
                        topic, description, scene_outline_i, scene_num, file_prefix, session_id, scene_trace_id)
                    implementation_plans_dict[scene_num] = implementation_plan
                    
                    # Update scene record with implementation plan
                    if scene_ids and len(scene_ids) >= scene_num and scene_ids[scene_num - 1]:
                        await self.update_scene_record(
                            scene_ids[scene_num - 1], 
                            status="planned",
                            generated_code=implementation_plan
                        )

        if only_plan:
            print(f"Only generating plans - skipping code generation and video rendering for topic: {topic}")
            return

        # Convert dictionary to list maintaining scene order
        sorted_scene_numbers = sorted(implementation_plans_dict.keys())
        implementation_plans = [implementation_plans_dict[i] for i in sorted_scene_numbers]
        
        # Render scenes
        print(f"Starting video rendering for topic: {topic}")
        
        # Update video status to rendering
        if video_id:
            await self.update_video_status(video_id, "rendering")
        
        # Check which scenes need processing
        scenes_to_process = []
        for i, implementation_plan in enumerate(implementation_plans):
            scene_dir = os.path.join(self.output_dir, file_prefix, f"scene{i+1}")
            code_dir = os.path.join(scene_dir, "code")
            
            # Check if scene has any code files
            has_code = False
            if os.path.exists(code_dir):
                if any(f.endswith('.py') for f in os.listdir(code_dir)):
                    has_code = True
            
            # For only_render mode, only process scenes without code
            if only_render:
                if not has_code:
                    scenes_to_process.append((i+1, implementation_plan))
                    print(f"Scene {i+1} has no code, will process")
            # For normal mode, process scenes that haven't been successfully rendered
            elif not os.path.exists(os.path.join(scene_dir, "succ_rendered.txt")):
                scenes_to_process.append((i+1, implementation_plan))
        
        if not scenes_to_process:
            print(f"No scenes need processing for topic '{topic}'.")
        else:
            print(f"Rendering {len(scenes_to_process)} scenes that need processing...")
            # Create a list of tuples with scene numbers and plans
            scene_plans = [(scene_num, plan) for scene_num, plan in scenes_to_process]
            # Sort by scene number to ensure correct order
            scene_plans.sort(key=lambda x: x[0])
            
            # Extract just the plans in the correct order and matching scene IDs
            filtered_implementation_plans = [plan for _, plan in scene_plans]
            
            # Filter scene_ids to match the scenes being processed
            filtered_scene_ids = []
            for scene_num, _ in scene_plans:
                if scene_ids and len(scene_ids) >= scene_num:
                    filtered_scene_ids.append(scene_ids[scene_num - 1])
                else:
                    filtered_scene_ids.append(None)
            
            try:
                await self.render_video_fix_code(topic, description, scene_outline, filtered_implementation_plans,
                                               max_retries=max_retries, session_id=session_id, scene_ids=filtered_scene_ids)
            except Exception as e:
                # Scene rendering failed after max retries - update video status and abort
                if video_id:
                    await self.update_video_status(video_id, "failed", str(e))
                
                # Re-raise the exception to abort the entire pipeline
                raise e
        
        if not only_render:  # Skip video combination in only_render mode
            print(f"Video rendering completed for topic '{topic}'.")
            # Combine videos after rendering is complete
            print(f"Starting video combination for topic '{topic}'...")
            self.combine_videos(topic)
            
            # Upload files to Appwrite storage and update video status
            if video_id:
                combined_video_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_combined.mp4")
                combined_srt_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_combined.srt")
                
                if os.path.exists(combined_video_path):
                    print(f"📤 Uploading video and files to Appwrite storage...")
                    
                    # Upload combined video
                    video_file_id = None
                    subtitles_file_id = None
                    
                    if self.use_appwrite and self.appwrite_manager:
                        try:
                            # Upload video file
                            video_file_id = await self.appwrite_manager.upload_video_file(combined_video_path, video_id)
                            print(f"✅ Uploaded video file: {video_file_id}")
                            
                            # Upload subtitles if they exist
                            if os.path.exists(combined_srt_path):
                                subtitles_file_id = await self.appwrite_manager.upload_subtitles(combined_srt_path, video_id)
                                print(f"✅ Uploaded subtitles file: {subtitles_file_id}")
                        except Exception as e:
                            print(f"⚠️ File upload failed: {e}")
                    
                    # Now that combination is complete, we can clean up individual scene files
                    print("🧹 Cleaning up individual scene files after successful combination...")
                    media_base = os.path.join(self.output_dir, file_prefix, "media", "videos")
                    if os.path.exists(media_base):
                        for folder in os.listdir(media_base):
                            if folder.startswith(f"{file_prefix}_scene"):
                                folder_path = os.path.join(media_base, folder, "1080p60")
                                if os.path.exists(folder_path):
                                    for filename in os.listdir(folder_path):
                                        if filename.endswith('.mp4'):
                                            file_path = os.path.join(folder_path, filename)
                                            try:
                                                os.remove(file_path)
                                                print(f"🗑️ Cleaned up: {filename}")
                                            except OSError as e:
                                                print(f"⚠️ Could not clean up {filename}: {e}")
                else:
                    print(f"⚠️ Combined video not found at {combined_video_path}")

    def check_theorem_status(self, theorem: Dict) -> Dict[str, bool]:
        """
        Check if a theorem has its plan, code files, and rendered videos with detailed scene status.

        Args:
            theorem (Dict): Dictionary containing theorem information

        Returns:
            Dict[str, bool]: Dictionary containing status information for the theorem
        """
        topic = theorem['theorem']
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        
        # Check scene outline
        scene_outline_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_scene_outline.txt")
        has_scene_outline = os.path.exists(scene_outline_path)
        
        # Get number of scenes if outline exists
        num_scenes = 0
        if has_scene_outline:
            with open(scene_outline_path, "r") as f:
                scene_outline = f.read()
            scene_outline_content = extract_xml(scene_outline)
            num_scenes = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline_content))
        
        # Check implementation plans, code files, and rendered videos
        implementation_plans = 0
        code_files = 0
        rendered_scenes = 0
        
        # Track status of individual scenes
        scene_status = []
        for i in range(1, num_scenes + 1):
            scene_dir = os.path.join(self.output_dir, file_prefix, f"scene{i}")
            
            # Check implementation plan
            plan_path = os.path.join(scene_dir, f"{file_prefix}_scene{i}_implementation_plan.txt")
            has_plan = os.path.exists(plan_path)
            if has_plan:
                implementation_plans += 1
            
            # Check code files
            code_dir = os.path.join(scene_dir, "code")
            has_code = False
            if os.path.exists(code_dir):
                if any(f.endswith('.py') for f in os.listdir(code_dir)):
                    has_code = True
                    code_files += 1
            
            # Check rendered scene video
            has_render = False
            if os.path.exists(scene_dir):
                succ_rendered_path = os.path.join(scene_dir, "succ_rendered.txt")
                if os.path.exists(succ_rendered_path):
                    has_render = True
                    rendered_scenes += 1
            
            scene_status.append({
                'scene_number': i,
                'has_plan': has_plan,
                'has_code': has_code,
                'has_render': has_render
            })

        # Check combined video
        combined_video_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_combined.mp4")
        has_combined_video = os.path.exists(combined_video_path)
        
        return {
            'topic': topic,
            'has_scene_outline': has_scene_outline,
            'total_scenes': num_scenes,
            'implementation_plans': implementation_plans,
            'code_files': code_files,
            'rendered_scenes': rendered_scenes,
            'has_combined_video': has_combined_video,
            'scene_status': scene_status
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Manim videos using AI')
    parser.add_argument('--model', type=str, choices=allowed_models,
                      default='gemini/gemini-1.5-pro-002', help='Select the AI model to use')
    parser.add_argument('--topic', type=str, default=None, help='Topic to generate videos for')
    parser.add_argument('--context', type=str, default=None, help='Context of the topic')
    parser.add_argument('--helper_model', type=str, choices=allowed_models,
                      default=None, help='Select the helper model to use')
    parser.add_argument('--only_gen_vid', action='store_true', help='Only generate videos to existing plans')
    parser.add_argument('--only_combine', action='store_true', help='Only combine videos')
    parser.add_argument('--peek_existing_videos', '--peek', action='store_true', help='Peek at existing videos')
    parser.add_argument('--output_dir', type=str, default=Config.OUTPUT_DIR, help='Output directory') # Use Config
    parser.add_argument('--theorems_path', type=str, default=None, help='Path to theorems json file')
    parser.add_argument('--sample_size', '--sample', type=int, default=None, help='Number of theorems to sample')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--max_retries', type=int, default=5, help='Maximum number of retries for code generation')
    parser.add_argument('--use_rag', '--rag', action='store_true', help='Use Retrieval Augmented Generation (requires working embedding services)')
    parser.add_argument('--use_visual_fix_code','--visual_fix_code', action='store_true', help='Use VLM to fix code with rendered visuals')
    parser.add_argument('--chroma_db_path', type=str, default=Config.CHROMA_DB_PATH, help="Path to Chroma DB") # Use Config
    parser.add_argument('--manim_docs_path', type=str, default=Config.MANIM_DOCS_PATH, help="Path to manim docs") # Use Config
    parser.add_argument('--embedding_model', type=str,
                       default=Config.EMBEDDING_MODEL, # Use Config
                       choices=["gemini/text-embedding-004", "vertex_ai/text-embedding-005"],
                       help='Select the embedding model to use')
    parser.add_argument('--use_context_learning', action='store_true',
                       help='Use context learning with example Manim code')
    parser.add_argument('--context_learning_path', type=str,
                       default=Config.CONTEXT_LEARNING_PATH, # Use Config
                       help='Path to context learning examples')
    parser.add_argument('--use_langfuse', action='store_true',
                       help='Enable Langfuse logging')
    parser.add_argument('--max_scene_concurrency', type=int, default=1, help='Maximum number of scenes to process concurrently')
    parser.add_argument('--max_topic_concurrency', type=int, default=1,
                       help='Maximum number of topics to process concurrently')
    parser.add_argument('--debug_combine_topic', type=str, help='Debug combine videos', default=None)
    parser.add_argument('--only_plan', action='store_true', help='Only generate scene outline and implementation plans')
    parser.add_argument('--check_status', action='store_true', 
                       help='Check planning and code status for all theorems')
    parser.add_argument('--only_render', action='store_true', help='Only render scenes without combining videos')
    parser.add_argument('--scenes', nargs='+', type=int, help='Specific scenes to process (if theorems_path is provided)')
    args = parser.parse_args()

    # Initialize planner model using LiteLLM
    if args.verbose:
        verbose = True
    else:
        verbose = False
    planner_model = LiteLLMWrapper(
        model_name=args.model,
        temperature=0.7,
        print_cost=True,
        verbose=verbose,
        use_langfuse=args.use_langfuse
    )
    helper_model = LiteLLMWrapper(
        model_name=args.helper_model if args.helper_model else args.model, # Use helper_model if provided, else planner_model
        temperature=0.7,
        print_cost=True,
        verbose=verbose,
        use_langfuse=args.use_langfuse
    )
    scene_model = LiteLLMWrapper( # Initialize scene_model separately
        model_name=args.model,
        temperature=0.7,
        print_cost=True,
        verbose=verbose,
        use_langfuse=args.use_langfuse
    )
    print(f"Planner model: {args.model}, Helper model: {args.helper_model if args.helper_model else args.model}, Scene model: {args.model}") # Print all models


    if args.theorems_path:
        # Load the sample theorems
        with open(args.theorems_path, "r") as f:
            theorems = json.load(f)

        if args.sample_size:
            theorems = theorems[:args.sample_size]

        if args.peek_existing_videos:
            print(f"Here's the results of checking whether videos are rendered successfully in {args.output_dir}:")
            # in output_dir, find all combined.mp4 files and print number of successful rendered videos out of total number of folders
            successful_rendered_videos = 0
            total_folders = 0
            for item in os.listdir(args.output_dir):
                if os.path.isdir(os.path.join(args.output_dir, item)):
                    total_folders += 1
                    if os.path.exists(os.path.join(args.output_dir, item, f"{item}_combined.mp4")):
                        successful_rendered_videos += 1
            print(f"Number of successful rendered videos: {successful_rendered_videos}/{total_folders}")

            # also check whether any succ_rendered.txt in scene{i} folder, and then add up the number of successful rendered videos
            successful_rendered_videos = 0
            total_scenes = 0
            for item in os.listdir(args.output_dir):
                if os.path.isdir(os.path.join(args.output_dir, item)):
                    for scene_folder in os.listdir(os.path.join(args.output_dir, item)):
                        if "scene" in scene_folder and os.path.isdir(os.path.join(args.output_dir, item, scene_folder)):
                            total_scenes += 1
                            if os.path.exists(os.path.join(args.output_dir, item, scene_folder, "succ_rendered.txt")):
                                successful_rendered_videos += 1
            print(f"Number of successful rendered scenes: {successful_rendered_videos}/{total_scenes}")
            exit()

        video_generator = VideoGenerator(
            planner_model=planner_model,
            scene_model=scene_model, # Pass scene_model
            helper_model=helper_model, # Pass helper_model
            output_dir=args.output_dir,
            verbose=args.verbose,
            use_rag=args.use_rag,
            use_context_learning=args.use_context_learning,
            context_learning_path=args.context_learning_path,
            chroma_db_path=args.chroma_db_path,
            manim_docs_path=args.manim_docs_path,
            embedding_model=args.embedding_model,
            use_visual_fix_code=args.use_visual_fix_code,
            use_langfuse=args.use_langfuse,
            max_scene_concurrency=args.max_scene_concurrency
        )

        if args.debug_combine_topic is not None:
            video_generator.combine_videos(args.debug_combine_topic)
            exit()

        if args.only_gen_vid:
            # Generate videos for existing plans
            print("Generating videos for existing plans...")

            async def process_theorem(theorem, topic_semaphore):
                async with topic_semaphore:
                    topic = theorem['theorem']
                    print(f"Processing topic: {topic}")
                    await video_generator.render_video_fix_code(topic, theorem['description'], max_retries=args.max_retries)

            async def main():
                # Use the command-line argument for topic concurrency
                topic_semaphore = asyncio.Semaphore(args.max_topic_concurrency)
                tasks = [process_theorem(theorem, topic_semaphore) for theorem in theorems]
                await asyncio.gather(*tasks)

            asyncio.run(main())

        elif args.check_status:
            print("\nChecking theorem status...")
            video_generator = VideoGenerator(
                planner_model=planner_model,
                scene_model=scene_model,
                helper_model=helper_model,
                output_dir=args.output_dir,
                verbose=args.verbose,
                use_rag=args.use_rag,
                use_context_learning=args.use_context_learning,
                context_learning_path=args.context_learning_path,
                chroma_db_path=args.chroma_db_path,
                manim_docs_path=args.manim_docs_path,
                embedding_model=args.embedding_model,
                use_visual_fix_code=args.use_visual_fix_code,
                use_langfuse=args.use_langfuse,
                max_scene_concurrency=args.max_scene_concurrency
            )
            
            all_statuses = [video_generator.check_theorem_status(theorem) for theorem in theorems]
            
            # Print combined status table
            print("\nTheorem Status:")
            print("-" * 160)
            print(f"{'Topic':<40} {'Outline':<8} {'Total':<8} {'Status (Plan/Code/Render)':<50} {'Combined':<10} {'Missing Components':<40}")
            print("-" * 160)
            for status in all_statuses:
                # Create status string showing plan/code/render completion for each scene
                scene_status_str = ""
                for scene in status['scene_status']:
                    scene_str = (
                        ("P" if scene['has_plan'] else "-") +
                        ("C" if scene['has_code'] else "-") +
                        ("R" if scene['has_render'] else "-") + " "
                    )
                    scene_status_str += scene_str
                
                # Collect missing components
                missing_plans = []
                missing_code = []
                missing_renders = []
                for scene in status['scene_status']:
                    if not scene['has_plan']:
                        missing_plans.append(str(scene['scene_number']))
                    if not scene['has_code']:
                        missing_code.append(str(scene['scene_number']))
                    if not scene['has_render']:
                        missing_renders.append(str(scene['scene_number']))
                
                # Format missing components string
                missing_str = []
                if missing_plans:
                    missing_str.append(f"P:{','.join(missing_plans)}")
                if missing_code:
                    missing_str.append(f"C:{','.join(missing_code)}")
                if missing_renders:
                    missing_str.append(f"R:{','.join(missing_renders)}")
                missing_str = ' '.join(missing_str)
                
                print(f"{status['topic'][:37]+'...' if len(status['topic'])>37 else status['topic']:<40} "
                    f"{'✓' if status['has_scene_outline'] else '✗':<8} "
                    f"{status['total_scenes']:<8} "
                    f"{scene_status_str[:47]+'...' if len(scene_status_str)>47 else scene_status_str:<50} "
                    f"{'✓' if status['has_combined_video'] else '✗':<10} "
                    f"{missing_str[:37]+'...' if len(missing_str)>37 else missing_str:<40}")

            # Print summary
            print("\nSummary:")
            print(f"Total theorems: {len(theorems)}")
            print(f"Total scenes: {sum(status['total_scenes'] for status in all_statuses)}")
            print(f"Scene completion status:")
            print(f"  Plans: {sum(status['implementation_plans'] for status in all_statuses)} scenes")
            print(f"  Code: {sum(status['code_files'] for status in all_statuses)} scenes")
            print(f"  Renders: {sum(status['rendered_scenes'] for status in all_statuses)} scenes")
            print(f"Combined videos: {sum(1 for status in all_statuses if status['has_combined_video'])}/{len(theorems)}")
            exit()

        else:
            # Generate video pipeline from scratch
            print("Generating video pipeline from scratch...")

            async def process_theorem(theorem, topic_semaphore):
                async with topic_semaphore:
                    topic = theorem['theorem']
                    description = theorem['description']
                    print(f"Processing topic: {topic}")
                    if args.only_combine:
                        video_generator.combine_videos(topic)
                    else:
                        await video_generator.generate_video_pipeline(
                            topic, 
                            description, 
                            max_retries=args.max_retries,
                            only_plan=args.only_plan,
                            specific_scenes=args.scenes,
                            only_render=args.only_render,
                            only_combine=args.only_combine
                        )
                        if not args.only_plan and not args.only_render:  # Add condition for only_render
                            video_generator.combine_videos(topic)

            async def main():
                # Use the command-line argument for topic concurrency
                topic_semaphore = asyncio.Semaphore(args.max_topic_concurrency)
                tasks = [process_theorem(theorem, topic_semaphore) for theorem in theorems]
                await asyncio.gather(*tasks)

            asyncio.run(main())

    elif args.topic and args.context:
        video_generator = VideoGenerator(
            planner_model=planner_model,
            scene_model=scene_model, # Pass scene_model
            helper_model=helper_model, # Pass helper_model
            output_dir=args.output_dir,
            verbose=args.verbose,
            use_rag=args.use_rag,
            use_context_learning=args.use_context_learning,
            context_learning_path=args.context_learning_path,
            chroma_db_path=args.chroma_db_path,
            manim_docs_path=args.manim_docs_path,
            embedding_model=args.embedding_model,
            use_visual_fix_code=args.use_visual_fix_code,
            use_langfuse=args.use_langfuse,
            max_scene_concurrency=args.max_scene_concurrency
        )
        # Process single topic with context
        print(f"Processing topic: {args.topic}")

        if args.only_gen_vid:
            video_generator.render_video_fix_code(args.topic, args.context, max_retries=args.max_retries)
            exit()

        if args.only_combine:
            video_generator.combine_videos(args.topic)
        else:
            asyncio.run(video_generator.generate_video_pipeline(
                args.topic,
                args.context,
                max_retries=args.max_retries,
                only_plan=args.only_plan,
                only_render=args.only_render,
                only_combine=args.only_combine
            ))
            if not args.only_plan and not args.only_render:
                video_generator.combine_videos(args.topic)
    else:
        print("Please provide either (--theorems_path) or (--topic and --context)")
        exit()
