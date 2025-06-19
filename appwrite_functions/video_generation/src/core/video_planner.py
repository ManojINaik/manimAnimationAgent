import os
import re
import json
import glob
from typing import List, Optional
import uuid
import asyncio

from mllm_tools.utils import _prepare_text_inputs
from src.utils.utils import extract_xml, extract_xml_tag
from task_generator import (
    get_prompt_scene_plan,
    get_prompt_scene_vision_storyboard,
    get_prompt_scene_technical_implementation,
    get_prompt_scene_animation_narration,
    get_prompt_context_learning_scene_plan,
    get_prompt_context_learning_vision_storyboard,
    get_prompt_context_learning_technical_implementation,
    get_prompt_context_learning_animation_narration,
    get_prompt_context_learning_code
)
from src.rag.rag_integration import RAGIntegration

class VideoPlanner:
    """A class for planning and generating video content.

    This class handles the planning and generation of video content including scene outlines,
    vision storyboards, technical implementations, and animation narrations.

    Args:
        planner_model: The model used for planning tasks
        helper_model: Optional helper model, defaults to planner_model if None
        output_dir (str): Directory for output files. Defaults to "output"
        print_response (bool): Whether to print model responses. Defaults to False
        use_context_learning (bool): Whether to use context learning. Defaults to False
        context_learning_path (str): Path to context learning examples. Defaults to "data/context_learning"
        use_rag (bool): Whether to use RAG. Defaults to False
        session_id (str): Session identifier. Defaults to None
        chroma_db_path (str): Path to ChromaDB. Defaults to "data/rag/chroma_db"
        manim_docs_path (str): Path to Manim docs. Defaults to "data/rag/manim_docs"
        embedding_model (str): Name of embedding model. Defaults to "text-embedding-ada-002"
        use_langfuse (bool): Whether to use Langfuse logging. Defaults to True
    """

    def __init__(self, planner_model, helper_model=None, output_dir="output", print_response=False, use_context_learning=False, context_learning_path="data/context_learning", use_rag=False, session_id=None, chroma_db_path="data/rag/chroma_db", manim_docs_path="data/rag/manim_docs", embedding_model="text-embedding-ada-002", use_langfuse=True):
        self.planner_model = planner_model
        self.helper_model = helper_model if helper_model is not None else planner_model
        self.output_dir = output_dir
        self.print_response = print_response
        self.use_context_learning = use_context_learning
        self.context_learning_path = context_learning_path
        # Initialize different types of context examples
        self.scene_plan_examples = self._load_context_examples('scene_plan') if use_context_learning else None
        self.vision_storyboard_examples = self._load_context_examples('scene_vision_storyboard') if use_context_learning else None
        self.technical_implementation_examples = self._load_context_examples('technical_implementation') if use_context_learning else None
        self.animation_narration_examples = self._load_context_examples('scene_animation_narration') if use_context_learning else None
        self.code_examples = self._load_context_examples('code') if use_context_learning else None
        self.use_rag = use_rag
        self.rag_integration = None
        if use_rag:
            self.rag_integration = RAGIntegration(
                helper_model=helper_model,
                output_dir=output_dir,
                chroma_db_path=chroma_db_path,
                manim_docs_path=manim_docs_path,
                embedding_model=embedding_model,
                use_langfuse=use_langfuse,
                session_id=session_id
            )
        self.relevant_plugins = []  # Initialize as an empty list

    def _load_context_examples(self, example_type: str) -> str:
        """Load context learning examples of a specific type from files.

        Args:
            example_type (str): Type of examples to load ('scene_plan', 'scene_vision_storyboard', etc.)

        Returns:
            str: Formatted string containing the loaded examples, or None if no examples found
        """
        examples = []
        
        # Define file patterns for different types
        file_patterns = {
            'scene_plan': '*_scene_plan.txt',
            'scene_vision_storyboard': '*_scene_vision_storyboard.txt',
            'technical_implementation': '*_technical_implementation.txt',
            'scene_animation_narration': '*_scene_animation_narration.txt',
            'code': '*.py'
        }
        
        pattern = file_patterns.get(example_type)
        if not pattern:
            return None

        # Search in subdirectories of context_learning_path
        for root, _, _ in os.walk(self.context_learning_path):
            for example_file in glob.glob(os.path.join(root, pattern)):
                with open(example_file, 'r') as f:
                    content = f.read()
                    if example_type == 'code':
                        examples.append(f"# Example from {os.path.basename(example_file)}\n{content}\n")
                    else:
                        examples.append(f"# Example from {os.path.basename(example_file)}\n{content}\n")

        # Format examples using appropriate template
        if examples:
            formatted_examples = self._format_examples(example_type, examples)
            return formatted_examples
        return None

    def _format_examples(self, example_type: str, examples: List[str]) -> str:
        """Format examples using the appropriate template based on their type.

        Args:
            example_type (str): Type of examples to format
            examples (List[str]): List of example strings to format

        Returns:
            str: Formatted examples string, or None if no template found
        """
        templates = {
            'scene_plan': get_prompt_context_learning_scene_plan,
            'scene_vision_storyboard': get_prompt_context_learning_vision_storyboard,
            'technical_implementation': get_prompt_context_learning_technical_implementation,
            'scene_animation_narration': get_prompt_context_learning_animation_narration,
            'code': get_prompt_context_learning_code
        }
        
        template = templates.get(example_type)
        if template:
            return template(examples="\n".join(examples))
        return None

    def generate_scene_outline(self,
                            topic: str,
                            description: str,
                            session_id: str) -> str:
        """Generate a scene outline based on the topic and description.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            session_id (str): Session identifier

        Returns:
            str: Generated scene outline
        """
        # Detect relevant plugins upfront if RAG is enabled
        if self.use_rag:
            self.relevant_plugins = self.rag_integration.detect_relevant_plugins(topic, description) or []
            self.rag_integration.set_relevant_plugins(self.relevant_plugins)
            print(f"Detected relevant plugins: {self.relevant_plugins}")

        prompt = get_prompt_scene_plan(topic, description)
        
        if self.use_context_learning and self.scene_plan_examples:
            prompt += f"\n\nHere are some example scene plans for reference:\n{self.scene_plan_examples}"

        # Generate plan using planner model
        response_text = self.planner_model(
            _prepare_text_inputs(prompt),
            metadata={"generation_name": "scene_outline", "tags": [topic, "scene-outline"], "session_id": session_id}
        )
        
        # Extract scene outline <SCENE_OUTLINE> ... </SCENE_OUTLINE>
        scene_outline = extract_xml_tag(response_text, "SCENE_OUTLINE")
        if not scene_outline:
            print("⚠️  Warning: Could not find <SCENE_OUTLINE> tags. Returning full response.")
            # Fallback to returning the full text if tags are missing, after logging a warning.
            scene_outline = response_text

        # Create a file-safe prefix for the topic
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        
        # Ensure the directory exists
        topic_dir = os.path.join(self.output_dir, file_prefix)
        os.makedirs(topic_dir, exist_ok=True)
        
        outline_path = os.path.join(topic_dir, "scene_outline.txt")

        # Save the processed (extracted) scene outline to a file
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(scene_outline)

        return scene_outline

    async def _generate_scene_implementation_single(self, topic: str, description: str, scene_outline_i: str, i: int, file_prefix: str, session_id: str, scene_trace_id: str) -> str:
        """Generate implementation plan for a single scene.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            scene_outline_i (str): Outline for this specific scene
            i (int): Scene number
            file_prefix (str): Prefix for output files
            session_id (str): Session identifier
            scene_trace_id (str): Unique trace ID for this scene

        Returns:
            str: Generated implementation plan for the scene
        """
        # Initialize empty implementation plan
        implementation_plan = ""
        scene_dir = os.path.join(self.output_dir, file_prefix, f"scene{i}")
        subplan_dir = os.path.join(scene_dir, "subplans")
        os.makedirs(scene_dir, exist_ok=True)
        os.makedirs(subplan_dir, exist_ok=True)

        # Save scene_trace_id to file
        trace_id_file = os.path.join(subplan_dir, "scene_trace_id.txt")
        with open(trace_id_file, 'w') as f:
            f.write(scene_trace_id)
        print(f"Scene trace ID saved to {trace_id_file}")

        # ===== Step 1: Generate Scene Vision and Storyboard =====
        # ===================================================
        prompt_vision_storyboard = get_prompt_scene_vision_storyboard(i, topic, description, scene_outline_i, self.relevant_plugins)

        # Add vision storyboard examples only for this stage if available
        if self.use_context_learning and self.vision_storyboard_examples:
            prompt_vision_storyboard += f"\n\nHere are some example storyboards:\n{self.vision_storyboard_examples}"
        
        if self.rag_integration:
            # Use the already detected plugins instead of detecting again
            # relevant_plugins = self.relevant_plugins # Removed redundant variable
            # print(f"Using detected plugins: {relevant_plugins}") # Removed redundant print

            # Generate RAG queries
            rag_queries = self.rag_integration._generate_rag_queries_storyboard(
                scene_plan=scene_outline_i,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=i,
                session_id=session_id,
                relevant_plugins=self.relevant_plugins # Use self.relevant_plugins directly
            )

            retrieved_docs = self.rag_integration.get_relevant_docs(
                rag_queries=rag_queries,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=i
            )
            
            # Add documentation to prompt
            prompt_vision_storyboard += f"\n\n{retrieved_docs}"

        vision_storyboard_plan = self.planner_model(
            _prepare_text_inputs(prompt_vision_storyboard),
            metadata={"generation_name": "scene_vision_storyboard", "trace_id": scene_trace_id, "tags": [topic, f"scene{i}"], "session_id": session_id}
        )
        # extract vision storyboard plan <SCENE_VISION_STORYBOARD_PLAN> ... </SCENE_VISION_STORYBOARD_PLAN>
        vision_match = re.search(r'(<SCENE_VISION_STORYBOARD_PLAN>.*?</SCENE_VISION_STORYBOARD_PLAN>)', vision_storyboard_plan, re.DOTALL)
        vision_storyboard_plan = vision_match.group(1) if vision_match else vision_storyboard_plan
        implementation_plan += vision_storyboard_plan + "\n\n"
        # Save the vision and storyboard plan to a file
        storyboard_plan_path = os.path.join(subplan_dir, f"{file_prefix}_scene{i}_vision_storyboard_plan.txt")
        with open(storyboard_plan_path, 'w', encoding='utf-8') as f:
            f.write(vision_storyboard_plan)
        print(f"Scene {i} Vision and Storyboard Plan saved to {storyboard_plan_path}")

        # ===== Step 2: Generate Technical Implementation Plan =====
        # =========================================================
        prompt_technical_implementation = get_prompt_scene_technical_implementation(i, topic, description, scene_outline_i, vision_storyboard_plan, self.relevant_plugins)

        # Add technical implementation examples only for this stage if available
        if self.use_context_learning and self.technical_implementation_examples:
            prompt_technical_implementation += f"\n\nHere are some example technical implementations:\n{self.technical_implementation_examples}"

        if self.rag_integration:
            # Use the already detected plugins instead of detecting again
            # relevant_plugins = self.relevant_plugins # Removed redundant variable
            # print(f"Using detected plugins: {relevant_plugins}") # Removed redundant print

            # Generate RAG queries
            rag_queries = self.rag_integration._generate_rag_queries_technical(
                storyboard=vision_storyboard_plan,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=i,
                session_id=session_id,
                relevant_plugins=self.relevant_plugins # Use self.relevant_plugins directly
            )

            retrieved_docs = self.rag_integration.get_relevant_docs(
                rag_queries=rag_queries,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=i
            )

            # Add documentation to prompt
            prompt_technical_implementation += f"\n\n{retrieved_docs}"

        technical_implementation_plan = self.planner_model(
            _prepare_text_inputs(prompt_technical_implementation),
            metadata={"generation_name": "scene_technical_implementation", "trace_id": scene_trace_id, "tags": [topic, f"scene{i}"], "session_id": session_id}
        )
        # extract technical implementation plan <SCENE_TECHNICAL_IMPLEMENTATION_PLAN> ... </SCENE_TECHNICAL_IMPLEMENTATION_PLAN>
        technical_match = re.search(r'(<SCENE_TECHNICAL_IMPLEMENTATION_PLAN>.*?</SCENE_TECHNICAL_IMPLEMENTATION_PLAN>)', technical_implementation_plan, re.DOTALL)
        technical_implementation_plan = technical_match.group(1) if technical_match else technical_implementation_plan
        implementation_plan += technical_implementation_plan + "\n\n"
        # Save the technical implementation plan to a file
        technical_plan_path = os.path.join(subplan_dir, f"{file_prefix}_scene{i}_technical_implementation_plan.txt")
        with open(technical_plan_path, 'w', encoding='utf-8') as f:
            f.write(technical_implementation_plan)
        print(f"Scene {i} Technical Implementation Plan saved to {technical_plan_path}")
       
        # ===== Step 3: Generate Animation and Narration Plan =====
        # =========================================================
        prompt_animation_narration = get_prompt_scene_animation_narration(i, topic, description, scene_outline_i, vision_storyboard_plan, technical_implementation_plan, self.relevant_plugins)
        
        # Add animation narration examples only for this stage if available
        if self.use_context_learning and self.animation_narration_examples:
            prompt_animation_narration += f"\n\nHere are some example animation and narration plans:\n{self.animation_narration_examples}"
        
        if self.rag_integration:
            rag_queries = self.rag_integration._generate_rag_queries_narration(
                storyboard=vision_storyboard_plan,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=i,
                session_id=session_id,
                relevant_plugins=self.relevant_plugins # Use self.relevant_plugins directly
            )
            retrieved_docs = self.rag_integration.get_relevant_docs(
                rag_queries=rag_queries,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=i
            )
            prompt_animation_narration += f"\n\n{retrieved_docs}"

        animation_narration_plan = self.planner_model(
            _prepare_text_inputs(prompt_animation_narration),
            metadata={"generation_name": "scene_animation_narration", "trace_id": scene_trace_id, "tags": [topic, f"scene{i}"], "session_id": session_id}
        )
        # extract animation narration plan <SCENE_ANIMATION_NARRATION_PLAN> ... </SCENE_ANIMATION_NARRATION_PLAN>
        animation_match = re.search(r'(<SCENE_ANIMATION_NARRATION_PLAN>.*?</SCENE_ANIMATION_NARRATION_PLAN>)', animation_narration_plan, re.DOTALL)
        animation_narration_plan = animation_match.group(1) if animation_match else animation_narration_plan
        implementation_plan += animation_narration_plan + "\n\n"
        # Save the animation and narration plan to a file
        animation_narration_plan_path = os.path.join(subplan_dir, f"{file_prefix}_scene{i}_animation_narration_plan.txt")
        with open(animation_narration_plan_path, 'w', encoding='utf-8') as f:
            f.write(animation_narration_plan)
        print(f"Scene {i} Animation and Narration Plan saved to {animation_narration_plan_path}")

        # ===== Step 4: Save Implementation Plan =====
        # ==========================================
        # save the overall implementation plan to file
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        plan_path = os.path.join(self.output_dir, file_prefix, f"scene{i}", "implementation_plan.txt")

        # Save the scene implementation to a file
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(f"# Scene {i} Implementation Plan\n\n")
            f.write(implementation_plan)
        print(f"Scene {i} Implementation Plan saved to {plan_path}")

        return implementation_plan

    async def generate_scene_implementation(self,
                                      topic: str,
                                      description: str,
                                      plan: str,
                                      session_id: str) -> List[str]:
        """Generate detailed implementation plans for all scenes.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            plan (str): Overall scene plan
            session_id (str): Session identifier

        Returns:
            List[str]: List of implementation plans for each scene
        """
        # extract scene outline <SCENE_OUTLINE> ... </SCENE_OUTLINE>
        scene_outline = re.search(r'(<SCENE_OUTLINE>.*?</SCENE_OUTLINE>)', plan, re.DOTALL).group(1)
        # check the number of scenes in the outline
        scene_number = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline))
        # replace all spaces and special characters with underscores for file path compatibility
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        # generate implementation plan for each scene
        all_scene_implementation_plans = []

        tasks = []
        for i in range(1, scene_number):
            print(f"Generating implementation plan for scene {i} in topic {topic}")
            scene_outline_i = re.search(r'(<SCENE_{i}>.*?</SCENE_{i}>)'.format(i=i), scene_outline, re.DOTALL).group(1)
            scene_trace_id = str(uuid.uuid4())
            task = asyncio.create_task(self._generate_scene_implementation_single(topic, description, scene_outline_i, i, file_prefix, session_id, scene_trace_id))
            tasks.append(task)

        all_scene_implementation_plans = await asyncio.gather(*tasks)
        return all_scene_implementation_plans

    async def generate_scene_implementation_concurrently(self,
                                              topic: str,
                                              description: str,
                                              plan: str,
                                              session_id: str,
                                              scene_semaphore) -> List[str]:
        """Generate detailed implementation plans for all scenes concurrently with controlled concurrency.

        Args:
            topic (str): The topic of the video
            description (str): Description of the video content
            plan (str): Overall scene plan
            session_id (str): Session identifier
            scene_semaphore: Semaphore to control concurrent scene generation

        Returns:
            List[str]: List of implementation plans for each scene
        """
        scene_outline = extract_xml(plan)
        scene_number = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline))
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', topic.lower())
        all_scene_implementation_plans = []

        async def generate_single_scene_implementation(i):
            async with scene_semaphore:  # controls parallelism
                print(f"Generating implementation plan for scene {i} in topic {topic}")
                scene_outline_i = re.search(r'(<SCENE_{i}>.*?</SCENE_{i}>)'.format(i=i), scene_outline, re.DOTALL).group(1)
                scene_trace_id = str(uuid.uuid4())  # Generate UUID here
                return await self._generate_scene_implementation_single(topic, description, scene_outline_i, i, file_prefix, session_id, scene_trace_id)

        tasks = [generate_single_scene_implementation(i + 1) for i in range(scene_number)]
        all_scene_implementation_plans = await asyncio.gather(*tasks)
        return all_scene_implementation_plans 