import os
import re
import json
from typing import Union, List, Dict
from PIL import Image
import glob

from mllm_tools.utils import _prepare_text_inputs, _extract_code
from mllm_tools.gemini import GeminiWrapper
try:
    from mllm_tools.vertex_ai import VertexAIWrapper
except ImportError:
    VertexAIWrapper = None
from task_generator import (
    get_prompt_code_generation,
    get_prompt_fix_error,
    get_prompt_visual_fix_error,
    get_banned_reasonings,
    get_prompt_rag_query_generation_fix_error,
    get_prompt_context_learning_code,
    get_prompt_rag_query_generation_code
)
from task_generator.prompts_raw import (
    _code_font_size,
    _code_disable,
    _code_limit,
    _prompt_manim_cheatsheet
)
try:
    from src.rag.vector_store import RAGVectorStore # Import RAGVectorStore
    HAS_RAG = True
except ImportError:
    RAGVectorStore = None
    HAS_RAG = False

try:
    from src.core.agent_memory import AgentMemory
    HAS_AGENT_MEMORY = True
except ImportError:
    AgentMemory = None
    HAS_AGENT_MEMORY = False

class CodeGenerator:
    """A class for generating and managing Manim code."""

    def __init__(self, scene_model, helper_model, output_dir="output", print_response=False, use_rag=False, use_context_learning=False, context_learning_path="data/context_learning", chroma_db_path="rag/chroma_db", manim_docs_path="rag/manim_docs", embedding_model="gemini/text-embedding-004", use_visual_fix_code=False, use_langfuse=True, session_id=None, use_agent_memory=True):
        """Initialize the CodeGenerator.

        Args:
            scene_model: The model used for scene generation
            helper_model: The model used for helper tasks
            output_dir (str, optional): Directory for output files. Defaults to "output".
            print_response (bool, optional): Whether to print model responses. Defaults to False.
            use_rag (bool, optional): Whether to use RAG. Defaults to False.
            use_context_learning (bool, optional): Whether to use context learning. Defaults to False.
            context_learning_path (str, optional): Path to context learning examples. Defaults to "data/context_learning".
            chroma_db_path (str, optional): Path to ChromaDB. Defaults to "rag/chroma_db".
            manim_docs_path (str, optional): Path to Manim docs. Defaults to "rag/manim_docs".
            embedding_model (str, optional): Name of embedding model. Defaults to "gemini/text-embedding-004".
            use_visual_fix_code (bool, optional): Whether to use visual code fixing. Defaults to False.
            use_langfuse (bool, optional): Whether to use Langfuse logging. Defaults to True.
            session_id (str, optional): Session identifier. Defaults to None.
            use_agent_memory (bool, optional): Whether to use agent memory for learning. Defaults to True.
        """
        self.scene_model = scene_model
        self.helper_model = helper_model
        self.output_dir = output_dir
        self.print_response = print_response
        self.use_rag = use_rag
        self.use_context_learning = use_context_learning
        self.context_learning_path = context_learning_path
        self.context_examples = self._load_context_examples() if use_context_learning else None
        self.manim_docs_path = manim_docs_path

        self.use_visual_fix_code = use_visual_fix_code
        self.banned_reasonings = get_banned_reasonings()
        self.session_id = session_id # Use session_id passed from VideoGenerator

        # Initialize Agent Memory for self-improving capabilities
        self.use_agent_memory = use_agent_memory and HAS_AGENT_MEMORY
        if self.use_agent_memory:
            self.agent_memory = AgentMemory(agent_id=f"manimAnimationAgent-{session_id}" if session_id else "manimAnimationAgent")
        else:
            self.agent_memory = None
            if use_agent_memory:
                print("Warning: Agent memory requested but not available. Install mem0ai for self-improving capabilities.")

        if use_rag:
            try:
                self.vector_store = RAGVectorStore(
                    chroma_db_path=chroma_db_path,
                    manim_docs_path=manim_docs_path,
                    embedding_model=embedding_model,
                    session_id=self.session_id,
                    use_langfuse=use_langfuse
                )
                print("✅ RAG system initialized successfully")
            except Exception as e:
                print(f"⚠️ RAG initialization failed: {e}")
                print("🔄 Continuing without RAG - text embedding not available")
                self.vector_store = None
                self.use_rag = False  # Disable RAG functionality
        else:
            self.vector_store = None

    def _load_context_examples(self) -> str:
        """Load all context learning examples from the specified directory.

        Returns:
            str: Formatted context learning examples, or None if no examples found.
        """
        examples = []
        for example_file in glob.glob(f"{self.context_learning_path}/**/*.py", recursive=True):
            with open(example_file, 'r') as f:
                examples.append(f"# Example from {os.path.basename(example_file)}\n{f.read()}\n")

        # Format examples using get_prompt_context_learning_code instead of _prompt_context_learning
        if examples:
            formatted_examples = get_prompt_context_learning_code(
                examples="\n".join(examples)
            )
            return formatted_examples
        return None

    def _generate_rag_queries_code(self, implementation: str, scene_trace_id: str = None, topic: str = None, scene_number: int = None, session_id: str = None, relevant_plugins: List[str] = []) -> List[str]:
        """Generate RAG queries from the implementation plan.

        Args:
            implementation (str): The implementation plan text
            scene_trace_id (str, optional): Trace ID for the scene. Defaults to None.
            topic (str, optional): Topic of the scene. Defaults to None.
            scene_number (int, optional): Scene number. Defaults to None.
            session_id (str, optional): Session identifier. Defaults to None.
            relevant_plugins (List[str], optional): List of relevant plugins. Defaults to empty list.

        Returns:
            List[str]: List of generated RAG queries
        """
        # Create a cache key for this scene
        cache_key = f"{topic}_scene{scene_number}"

        # Check if we already have a cache file for this scene
        cache_dir = os.path.join(self.output_dir, re.sub(r'[^a-z0-9_]+', '_', topic.lower()), f"scene{scene_number}", "rag_cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, "rag_queries_code.json")

        # If cache file exists, load and return cached queries
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_queries = json.load(f)
                print(f"Using cached RAG queries for {cache_key}")
                return cached_queries

        # Generate new queries if not cached
        if relevant_plugins:
            prompt = get_prompt_rag_query_generation_code(implementation, ", ".join(relevant_plugins))
        else:
            prompt = get_prompt_rag_query_generation_code(implementation, "No plugins are relevant.")

        queries = self.helper_model(
            _prepare_text_inputs(prompt),
            metadata={"generation_name": "rag_query_generation", "trace_id": scene_trace_id, "tags": [topic, f"scene{scene_number}"], "session_id": session_id}
        )

        print(f"RAG queries: {queries}")
        # retreive json triple backticks
        
        try: # add try-except block to handle potential json decode errors
            queries = re.search(r'```json(.*)```', queries, re.DOTALL).group(1)
            queries = json.loads(queries)
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error when parsing RAG queries for storyboard: {e}")
            print(f"Response text was: {queries}")
            return [] # Return empty list in case of parsing error

        # Cache the queries
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(queries, f)

        return queries

    def _generate_rag_queries_error_fix(self, error: str, code: str, scene_trace_id: str = None, topic: str = None, scene_number: int = None, session_id: str = None, relevant_plugins: List[str] = []) -> List[str]:
        """Generate RAG queries for fixing code errors.

        Args:
            error (str): The error message to fix
            code (str): The code containing the error
            scene_trace_id (str, optional): Trace ID for the scene. Defaults to None.
            topic (str, optional): Topic of the scene. Defaults to None.
            scene_number (int, optional): Scene number. Defaults to None.
            session_id (str, optional): Session identifier. Defaults to None.
            relevant_plugins (List[str], optional): List of relevant plugins. Defaults to empty list.

        Returns:
            List[str]: List of generated RAG queries for error fixing
        """
        # Create a cache key for this scene and error
        cache_key = f"{topic}_scene{scene_number}_error_fix"

        # Check if we already have a cache file for error fix queries
        cache_dir = os.path.join(self.output_dir, re.sub(r'[^a-z0-9_]+', '_', topic.lower()), f"scene{scene_number}", "rag_cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, "rag_queries_error_fix.json")

        # If cache file exists, load and return cached queries
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_queries = json.load(f)
                print(f"Using cached RAG queries for error fix in {cache_key}")
                return cached_queries

        # Generate new queries for error fix if not cached
        prompt = get_prompt_rag_query_generation_fix_error(
            error=error,
            code=code,
            relevant_plugins=", ".join(relevant_plugins) if relevant_plugins else "No plugins are relevant."
        )

        queries = self.helper_model(
            _prepare_text_inputs(prompt),
            metadata={"generation_name": "rag-query-generation-fix-error", "trace_id": scene_trace_id, "tags": [topic, f"scene{scene_number}"], "session_id": session_id}
        )

        # remove json triple backticks
        queries = queries.replace("```json", "").replace("```", "")
        try: # add try-except block to handle potential json decode errors
            queries = json.loads(queries)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError when parsing RAG queries for error fix: {e}")
            print(f"Response text was: {queries}")
            return [] # Return empty list in case of parsing error

        # Cache the queries
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(queries, f)

        return queries

    def _extract_code_with_retries(self, response_text: str, pattern: str, generation_name: str = None, trace_id: str = None, session_id: str = None, max_retries: int = 10) -> str:
        """Extract code from response text with retry logic.

        Args:
            response_text (str): The text containing code to extract
            pattern (str): Regex pattern for extracting code
            generation_name (str, optional): Name of generation step. Defaults to None.
            trace_id (str, optional): Trace identifier. Defaults to None.
            session_id (str, optional): Session identifier. Defaults to None.
            max_retries (int, optional): Maximum number of retries. Defaults to 10.

        Returns:
            str: The extracted code

        Raises:
            ValueError: If code extraction fails after max retries
        """
        retry_prompt = """
        Please extract the Python code in the correct format using the pattern: {pattern}. 
        You MUST NOT include any other text or comments. 
        You MUST return the exact same code as in the previous response, NO CONTENT EDITING is allowed.
        Previous response: 
        {response_text}
        """

        for attempt in range(max_retries):
            code_match = re.search(pattern, response_text, re.DOTALL)
            if code_match:
                return code_match.group(1)
            
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}: Failed to extract code pattern. Retrying...")
                # Regenerate response with a more explicit prompt
                response_text = self.scene_model(
                    _prepare_text_inputs(retry_prompt.format(pattern=pattern, response_text=response_text)),
                    metadata={
                        "generation_name": f"{generation_name}_format_retry_{attempt + 1}",
                        "trace_id": trace_id,
                        "session_id": session_id
                    }
                )
        
        raise ValueError(f"Failed to extract code pattern after {max_retries} attempts. Pattern: {pattern}")

    def generate_manim_code(self,
                            topic: str,
                            description: str,                            
                            scene_outline: str,
                            scene_implementation: str,
                            scene_number: int,
                            additional_context: Union[str, List[str]] = None,
                            scene_trace_id: str = None,
                            session_id: str = None,
                            rag_queries_cache: Dict = None) -> str:
        """Generate Manim code from video plan.

        Args:
            topic (str): Topic of the scene
            description (str): Description of the scene
            scene_outline (str): Outline of the scene
            scene_implementation (str): Implementation details
            scene_number (int): Scene number
            additional_context (Union[str, List[str]], optional): Additional context. Defaults to None.
            scene_trace_id (str, optional): Trace identifier. Defaults to None.
            session_id (str, optional): Session identifier. Defaults to None.
            rag_queries_cache (Dict, optional): Cache for RAG queries. Defaults to None.

        Returns:
            Tuple[str, str]: Generated code and response text
        """
        if self.use_context_learning:
            # Add context examples to additional_context
            if additional_context is None:
                additional_context = []
            elif isinstance(additional_context, str):
                additional_context = [additional_context]
            
            # Now using the properly formatted code examples
            if self.context_examples:
                additional_context.append(self.context_examples)

        # Add preventive examples from agent memory to avoid common errors
        if self.use_agent_memory and self.agent_memory:
            scene_type = self._infer_scene_type(scene_implementation)
            task_description = scene_implementation[:200] if scene_implementation else "No description"
            preventive_examples = self.agent_memory.get_preventive_examples(
                task_description=task_description,  # First 200 chars as task description
                topic=topic,
                scene_type=scene_type,
                limit=3
            )
            
            if preventive_examples:
                if additional_context is None:
                    additional_context = []
                elif isinstance(additional_context, str):
                    additional_context = [additional_context]
                
                # Format preventive examples for inclusion in prompt
                examples_text = "# Previous successful patterns to avoid common errors:\n"
                for i, (problem, solution) in enumerate(preventive_examples, 1):
                    examples_text += f"# Example {i}: Avoided error '{problem[:100]}...'\n"
                    examples_text += f"# Successful approach:\n{solution[:300]}...\n\n"
                
                additional_context.append(examples_text)
                print(f"Added {len(preventive_examples)} preventive examples from agent memory")

        if self.use_rag:
            # Generate RAG queries (will use cache if available)
            rag_queries = self._generate_rag_queries_code(
                implementation=scene_implementation,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=scene_number,
                session_id=session_id
            )

            retrieved_docs = self.vector_store.find_relevant_docs(
                queries=rag_queries,
                k=2, # number of documents to retrieve
                trace_id=scene_trace_id,
                topic=topic,
                scene_number=scene_number
            )
            # Format the retrieved documents into a string
            if additional_context is None:
                additional_context = []
            additional_context.append(retrieved_docs)

        # Format code generation prompt with plan and retrieved context
        prompt = get_prompt_code_generation(
            scene_outline=scene_outline,
            scene_implementation=scene_implementation,
            topic=topic,
            description=description,
            scene_number=scene_number,
            additional_context=additional_context
        )

        # Generate code using model
        response_text = self.scene_model(
            _prepare_text_inputs(prompt),
            metadata={"generation_name": "code_generation", "trace_id": scene_trace_id, "tags": [topic, f"scene{scene_number}"], "session_id": session_id}
        )

        # Extract code with retries
        code = self._extract_code_with_retries(
            response_text,
            r"```python(.*)```",
            generation_name="code_generation",
            trace_id=scene_trace_id,
            session_id=session_id
        )
        # Store successful generation in agent memory
        if self.use_agent_memory and self.agent_memory:
            scene_type = self._infer_scene_type(scene_implementation)
            self.agent_memory.store_successful_generation(
                task_description=f"Scene {scene_number}: {scene_outline}",
                generated_code=code,
                topic=topic,
                scene_type=scene_type
            )

        return code, response_text

    def _infer_scene_type(self, scene_implementation: str) -> str:
        """
        Infer the type of scene from the implementation description.
        
        Args:
            scene_implementation: The scene implementation text
            
        Returns:
            str: Inferred scene type
        """
        if scene_implementation is None:
            return 'general'
        
        text = scene_implementation.lower()
        
        # Check for common scene types
        if any(word in text for word in ['graph', 'plot', 'chart', 'axis', 'coordinate']):
            return 'graph'
        elif any(word in text for word in ['formula', 'equation', 'math', 'expression']):
            return 'formula'
        elif any(word in text for word in ['animate', 'move', 'transform', 'transition']):
            return 'animation'
        elif any(word in text for word in ['text', 'title', 'label', 'write']):
            return 'text'
        elif any(word in text for word in ['shape', 'circle', 'square', 'rectangle']):
            return 'geometry'
        elif any(word in text for word in ['3d', 'three', 'dimensional', 'cube', 'sphere']):
            return '3d'
        else:
            return 'general'

    def fix_code_errors(self, implementation_plan: str, code: str, error: str, scene_trace_id: str, topic: str, scene_number: int, session_id: str, rag_queries_cache: Dict = None) -> str:
        """
        Fix errors in the generated code using the helper model.

        Args:
            implementation_plan (str): The implementation plan for context
            code (str): The original code with errors
            error (str): The error message to fix
            scene_trace_id (str): Trace ID for the scene
            topic (str): Topic of the scene
            scene_number (int): Scene number
            session_id (str): Session identifier
            rag_queries_cache (Dict, optional): Cache for RAG queries. Defaults to None.

        Returns:
            str: Fixed code
        """
        scene_type = self._infer_scene_type(implementation_plan)
        original_code = code  # Store original for memory
        
        # Check agent memory for similar errors first
        similar_fixes = []
        if self.use_agent_memory and self.agent_memory:
            similar_fixes = self.agent_memory.search_similar_fixes(
                error_message=error,
                code_context=code[:300],  # First 300 chars of code as context
                topic=topic,
                scene_type=scene_type,
                limit=3
            )
            
            if similar_fixes:
                print(f"Found {len(similar_fixes)} similar error patterns in memory")
        
        # First, try to fix common known issues automatically
        fixed_code = self._auto_fix_common_issues(code, error)
        auto_fix_applied = fixed_code != code
        
        if auto_fix_applied:
            # Store the auto-fix in memory for future reference
            if self.use_agent_memory and self.agent_memory:
                self.agent_memory.store_error_fix(
                    error_message=error,
                    original_code=original_code,
                    fixed_code=fixed_code,
                    topic=topic,
                    scene_type=scene_type,
                    fix_method="auto"
                )
            return fixed_code
        
        # If auto-fix didn't help, use LLM to fix the error
        context = ""
        
        # Add similar fixes from memory to context
        if similar_fixes:
            memory_context = "# Similar errors fixed previously:\n"
            for i, fix in enumerate(similar_fixes, 1):
                memory_context += f"# Fix {i}: {fix.get('memory', 'Previous fix')}\n"
            context += memory_context + "\n"
        
        if self.use_rag:
            rag_queries = self._generate_rag_queries_error_fix(
                error=error,
                code=code,
                scene_trace_id=scene_trace_id,
                topic=topic,
                scene_number=scene_number,
                session_id=session_id
            )
            rag_context = self.vector_store.query_documents(rag_queries, limit=5)
            context += rag_context

        # Generate fixed code using LLM
        prompt = get_prompt_fix_error(error, code, context)
        fixed_code = self.scene_model(
            _prepare_text_inputs(prompt),
            metadata={"generation_name": "fix-error", "trace_id": scene_trace_id, "tags": [topic, f"scene{scene_number}"], "session_id": session_id}
        )

        fixed_code = self._extract_code_with_retries(
            fixed_code, 
            pattern=r'```python\n(.*?)\n```',
            generation_name="fix-error",
            trace_id=scene_trace_id,
            session_id=session_id
        )

        # Store the LLM-based fix in memory for future reference
        if self.use_agent_memory and self.agent_memory and fixed_code != original_code:
            self.agent_memory.store_error_fix(
                error_message=error,
                original_code=original_code,
                fixed_code=fixed_code,
                topic=topic,
                scene_type=scene_type,
                fix_method="llm"
            )

        return fixed_code

    def _auto_fix_common_issues(self, code: str, error: str) -> str:
        """
        Automatically fix common recurring issues in generated code.
        
        Args:
            code (str): The original code with errors
            error (str): The error message
            
        Returns:
            str: Fixed code if auto-fix applied, otherwise original code
        """
        fixed_code = code
        
        # Fix 1: Config object attribute errors
        if "'ManimMLConfig' object has no attribute 'frame_x_radius'" in error or \
           "'ManimMLConfig' object is not subscriptable" in error:
            # Replace problematic config access with hardcoded constants
            fixed_code = fixed_code.replace(
                'FRAME_X_MIN = config["frame_x_radius"]',
                'FRAME_X_MIN = -7.0'
            ).replace(
                'FRAME_X_MAX = config["frame_x_radius"]', 
                'FRAME_X_MAX = 7.0'
            ).replace(
                'FRAME_Y_MIN = config["frame_y_radius"]',
                'FRAME_Y_MIN = -4.0'
            ).replace(
                'FRAME_Y_MAX = config["frame_y_radius"]',
                'FRAME_Y_MAX = 4.0'
            ).replace(
                'FRAME_X_MIN = config.frame_x_radius',
                'FRAME_X_MIN = -7.0'
            ).replace(
                'FRAME_X_MAX = config.frame_x_radius',
                'FRAME_X_MAX = 7.0'
            ).replace(
                'FRAME_Y_MIN = config.frame_y_radius',
                'FRAME_Y_MIN = -4.0'
            ).replace(
                'FRAME_Y_MAX = config.frame_y_radius',
                'FRAME_Y_MAX = 4.0'
            ).replace(
                'FRAME_X_MIN = global_config.frame_x_radius',
                'FRAME_X_MIN = -7.0'
            ).replace(
                'FRAME_X_MAX = global_config.frame_x_radius',
                'FRAME_X_MAX = 7.0'
            ).replace(
                'FRAME_Y_MIN = global_config.frame_y_radius',
                'FRAME_Y_MIN = -4.0'
            ).replace(
                'FRAME_Y_MAX = global_config.frame_y_radius',
                'FRAME_Y_MAX = 4.0'
            )
        
        # Fix 2: Arrow3D with buff parameter
        if "unexpected keyword argument 'buff'" in error and "Arrow3D" in code:
            import re
            # Remove buff parameter from Arrow3D calls
            arrow3d_pattern = r'Arrow3D\([^)]*buff=[^,)]*[,)]'
            def remove_buff(match):
                call = match.group(0)
                # Remove buff parameter and any trailing comma
                call = re.sub(r',?\s*buff=[^,)]*', '', call)
                # Fix any double commas
                call = call.replace(',,', ',').replace('(,', '(')
                return call
            fixed_code = re.sub(arrow3d_pattern, remove_buff, fixed_code)
        
        # Fix 3: Syntax errors with stray backticks
        if "invalid syntax" in error and "```" in code:
            fixed_code = fixed_code.replace('```', '')
        
        # Fix 4: UpdateFromFunc parameter issues
        if "missing 1 required positional argument" in error and "UpdateFromFunc" in code:
            # Fix update function signatures to match Manim's requirements
            fixed_code = re.sub(
                r'def update_ball\(self, obj, alpha\):',
                'def update_ball(obj):',
                fixed_code
            )
        
        # Fix 5: Array comparison ambiguity with get_bottom(), get_top(), etc.
        if "The truth value of an array with more than one element is ambiguous" in error:
            import re
            # Fix comparisons like obj.get_bottom() < value to use numpy array indexing
            patterns = [
                (r'(\w+)\.get_bottom\(\)\s*([<>]=?)\s*(-?\d+\.?\d*)', r'\1.get_bottom()[1] \2 \3'),
                (r'(\w+)\.get_top\(\)\s*([<>]=?)\s*(-?\d+\.?\d*)', r'\1.get_top()[1] \2 \3'),
                (r'(\w+)\.get_left\(\)\s*([<>]=?)\s*(-?\d+\.?\d*)', r'\1.get_left()[0] \2 \3'),
                (r'(\w+)\.get_right\(\)\s*([<>]=?)\s*(-?\d+\.?\d*)', r'\1.get_right()[0] \2 \3'),
            ]
            for pattern, replacement in patterns:
                fixed_code = re.sub(pattern, replacement, fixed_code)
        
        # Fix 6: Missing SVG files - replace with basic shapes
        if "could not find" in error and ".svg" in error:
            import re
            # Replace SVGMobject with Rectangle for missing SVG files
            svg_patterns = [
                (r'SVGMobject\("car\.svg"\)', 'Rectangle(height=0.5, width=1.0, color=BLUE)'),
                (r'SVGMobject\("arrow\.svg"\)', 'Arrow(start=ORIGIN, end=RIGHT, color=RED)'),
                (r'SVGMobject\("([^"]+\.svg)"\)', r'Rectangle(height=0.5, width=0.5, color=YELLOW)  # Replaced missing \1'),
            ]
            for pattern, replacement in svg_patterns:
                fixed_code = re.sub(pattern, replacement, fixed_code)
        
        # Fix 7: Non-existent Manim classes/functions
        if "is not defined" in error or "cannot import name" in error:
            import re
            # Replace non-existent Manim functions with working alternatives
            replacements = [
                (r'Surround\(([^)]+)\)', r'Circumscribe(\1)'),  # Surround doesn't exist, use Circumscribe
                (r'from manim import \*, Surround', 'from manim import *'),  # Remove invalid import
                (r'from manim import Surround[^\n]*\n', ''),  # Remove Surround import line
            ]
            for pattern, replacement in replacements:
                fixed_code = re.sub(pattern, replacement, fixed_code)
        
        # Fix 8: Config frame attribute errors  
        if "'ManimMLConfig' object has no attribute 'frame_width'" in error or \
           "'ManimMLConfig' object has no attribute 'frame_height'" in error:
            # Replace config frame access with hardcoded values
            fixed_code = fixed_code.replace(
                'config.frame_width', '14.0'
            ).replace(
                'config.frame_height', '8.0'
            ).replace(
                '-config.frame_width / 2', '-7.0'
            ).replace(
                'config.frame_width / 2', '7.0'
            ).replace(
                '-config.frame_height / 2', '-4.0'
            ).replace(
                'config.frame_height / 2', '4.0'
            )
        
        # Fix 9: Transform animation issues with function objects
        if "object of type 'function' has no len()" in error and "Transform" in code:
            import re
            # Fix Transform calls with .animate that should use the object directly
            fixed_code = re.sub(
                r'Transform\((\w+), \1\.animate\.([^)]+)\)',
                r'self.play(\1.animate.\2)',
                fixed_code
            )
            # Also fix incorrect Transform usage
            fixed_code = re.sub(
                r'self\.play\(Transform\(([^,]+), ([^)]+)\.animate\.([^)]+)\)\)',
                r'self.play(\2.animate.\3)',
                fixed_code
            )
        
        # Fix 10: Syntax errors with import statements
        if "invalid syntax" in error and "import" in error:
            import re
            # Fix malformed import statements
            fixed_code = re.sub(r'from manim import \*, (\w+)', r'from manim import *', fixed_code)
            fixed_code = re.sub(r'from manim import \*,', 'from manim import *', fixed_code)
        
        return fixed_code

    def visual_self_reflection(self, code: str, media_path: Union[str, Image.Image], scene_trace_id: str, topic: str, scene_number: int, session_id: str) -> str:
        """Use snapshot image or mp4 video to fix code.

        Args:
            code (str): Code to fix
            media_path (Union[str, Image.Image]): Path to media file or PIL Image
            scene_trace_id (str): Trace identifier
            topic (str): Topic of the scene
            scene_number (int): Scene number
            session_id (str): Session identifier

        Returns:
            Tuple[str, str]: Fixed code and response text
        """
        
        # Determine if we're dealing with video or image
        is_video = isinstance(media_path, str) and media_path.endswith('.mp4')
        
        # Load prompt template
        prompt = get_prompt_visual_fix_error(code=code)
        
        # Prepare input based on media type
        if is_video and isinstance(self.scene_model, (GeminiWrapper, VertexAIWrapper)):
            # For video with Gemini models
            messages = [
                {"type": "text", "content": prompt},
                {"type": "video", "content": media_path}
            ]
        else:
            # For images or non-Gemini models
            if isinstance(media_path, str):
                media = Image.open(media_path)
            else:
                media = media_path
            messages = [
                {"type": "text", "content": prompt},
                {"type": "image", "content": media}
            ]
        
        # Get model response
        response_text = self.scene_model(
            messages,
            metadata={
                "generation_name": "visual_self_reflection",
                "trace_id": scene_trace_id,
                "tags": [topic, f"scene{scene_number}"],
                "session_id": session_id
            }
        )
        
        # Extract code with retries
        fixed_code = self._extract_code_with_retries(
            response_text,
            r"```python(.*)```",
            generation_name="visual_self_reflection",
            trace_id=scene_trace_id,
            session_id=session_id
        )
        return fixed_code, response_text