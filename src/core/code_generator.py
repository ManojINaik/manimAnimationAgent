import os
import re
import json
from typing import Union, List, Dict, Optional
from PIL import Image
import glob
import math

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
    get_prompt_rag_query_generation_code,
    get_prompt_tavily_search_query_generation,
    get_prompt_tavily_assisted_fix_error
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

# Import Tavily search functionality
try:
    from src.utils.tavily_search import TavilyErrorSearchEngine, search_error_solution
    HAS_TAVILY = True
except ImportError:
    TavilyErrorSearchEngine = None
    search_error_solution = None
    HAS_TAVILY = False

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
        Fix errors in the generated code using dynamic error resolution with LLM, Memory, and Tavily.

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
        original_code = code
        
        print("🔧 Starting dynamic error resolution with LLM, Memory, and Tavily integration...")
        
        # Check agent memory for similar errors first
        similar_fixes = []
        if self.use_agent_memory and self.agent_memory:
            similar_fixes = self.agent_memory.search_similar_fixes(
                error_message=error,
                code_context=code[:300],
                topic=topic,
                scene_type=scene_type,
                limit=3
            )
            
            if similar_fixes:
                print(f"Found {len(similar_fixes)} similar error patterns in memory")
        
        # Try Tavily-enhanced error resolution if available
        tavily_result = None
        if HAS_TAVILY:
            try:
                print("🌐 Attempting Tavily-enhanced error resolution...")
                tavily_result = self._fix_error_with_tavily(
                    implementation_plan=implementation_plan,
                    code=code,
                    error=error,
                    scene_trace_id=scene_trace_id,
                    topic=topic,
                    scene_number=scene_number,
                    session_id=session_id
                )
                
                if tavily_result and tavily_result != code:
                    print("✅ Tavily-enhanced fix applied successfully")
                    # Store fix metadata for later storage after successful rendering
                    self._last_fix_metadata = {
                        "error_message": error,
                        "original_code": original_code,
                        "fixed_code": tavily_result,
                        "topic": topic,
                        "scene_type": scene_type,
                        "fix_method": "tavily"
                    }
                    return tavily_result
            except Exception as e:
                print(f"⚠️ Tavily error resolution failed: {e}")
        
        # Fallback to LLM with memory and RAG context
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

        # Generate fixed code using LLM with context
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

        # Store fix metadata for later storage after successful rendering (only if fix was actually applied)
        if fixed_code != original_code:
            self._last_fix_metadata = {
                "error_message": error,
                "original_code": original_code,
                "fixed_code": fixed_code,
                "topic": topic,
                "scene_type": scene_type,
                "fix_method": "llm"
            }
        else:
            self._last_fix_metadata = None

        return fixed_code

    def _fix_error_with_tavily(self, implementation_plan: str, code: str, error: str, 
                              scene_trace_id: str, topic: str, scene_number: int, session_id: str) -> Optional[str]:
        """
        Implement the two-step Tavily-enhanced error resolution strategy.
        
        Step 1: Generate targeted search query using LLM
        Step 2: Use Tavily to search for solutions and apply them with LLM assistance
        
        Args:
            implementation_plan: Implementation plan for context
            code: Code with errors
            error: Error message
            scene_trace_id: Trace ID for logging
            topic: Topic name
            scene_number: Scene number
            session_id: Session ID
            
        Returns:
            Fixed code string or None if Tavily fix failed
        """
        try:
            # Step 1: Generate targeted search query using LLM
            print("🎯 Step 1: Generating optimized search query...")
            query_prompt = get_prompt_tavily_search_query_generation(
                traceback=error,
                code_context=code[:500],
                implementation_plan=implementation_plan[:200]
            )
            
            query_response = self.helper_model(
                _prepare_text_inputs(query_prompt),
                metadata={
                    "generation_name": "tavily-query-generation", 
                    "trace_id": scene_trace_id, 
                    "tags": [topic, f"scene{scene_number}"], 
                    "session_id": session_id
                }
            )
            
            search_query = self._extract_search_query_from_response(query_response)
            if not search_query:
                print("⚠️ Failed to generate search query")
                return None
                
            print(f"📝 Generated search query: {search_query}")
            
            # Step 2: Use Tavily to search for solutions
            print("🌐 Step 2: Searching for solutions with Tavily...")
            tavily_engine = TavilyErrorSearchEngine(verbose=True)
            
            if not tavily_engine.is_available():
                print("⚠️ Tavily not available - skipping Tavily-enhanced fix")
                return None
                
            # Analyze error and search for solutions
            error_analysis = tavily_engine.analyze_error_for_search(error, code[:500])
            error_analysis.search_query = search_query  # Use LLM-generated query
            
            search_results = tavily_engine.search_for_solution(error_analysis, max_results=5)
            
            if not search_results or not search_results.get('available'):
                print("⚠️ Tavily search failed or not available")
                return None
                
            # Format results for LLM
            formatted_results = self._format_tavily_results_for_llm(search_results)
            
            print("📋 Tavily search completed, applying insights...")
            
            # Step 3: Use LLM with Tavily results to fix the code
            print("🛠️ Step 3: Applying Tavily insights to fix the code...")
            fix_prompt = get_prompt_tavily_assisted_fix_error(
                implementation_plan=implementation_plan,
                manim_code=code,
                error_message=error,
                tavily_search_results=formatted_results,
                search_query=search_query
            )
            
            # Generate fixed code using LLM with Tavily insights
            fixed_response = self.scene_model(
                _prepare_text_inputs(fix_prompt),
                metadata={
                    "generation_name": "tavily-assisted-fix", 
                    "trace_id": scene_trace_id, 
                    "tags": [topic, f"scene{scene_number}"], 
                    "session_id": session_id
                }
            )
            
            # Extract fixed code
            fixed_code = self._extract_code_with_retries(
                fixed_response,
                r"```python(.*)```",
                generation_name="tavily-assisted-fix",
                trace_id=scene_trace_id,
                session_id=session_id
            )
            
            if fixed_code != code:
                print("✅ Tavily-assisted fix completed successfully")
                return fixed_code
            else:
                print("⚠️ Tavily-assisted fix did not produce different code")
                return None
                
        except Exception as e:
            print(f"❌ Error in Tavily-enhanced fix: {e}")
            return None

    def _extract_search_query_from_response(self, response: str) -> Optional[str]:
        """
        Extract search query from LLM response.
        
        Args:
            response: LLM response containing search query
            
        Returns:
            Extracted search query or None if not found
        """
        # Try to extract from JSON format first
        json_match = re.search(r'```json\s*\{[^}]*"query":\s*"([^"]+)"[^}]*\}\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Try to extract from quotes
        quote_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'Query:\s*(.+?)(?:\n|$)',
            r'Search:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in quote_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                if len(query) > 10:  # Reasonable query length
                    return query
                    
        # Fallback: take first meaningful line
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        for line in lines:
            if len(line) > 10 and not line.startswith('#'):
                return line
                
        return None

    def _format_tavily_results_for_llm(self, search_results: dict) -> str:
        """
        Format Tavily search results for LLM consumption.
        
        Args:
            search_results: Results from Tavily search
            
        Returns:
            Formatted string for LLM
        """
        formatted = "=== TAVILY SEARCH RESULTS ===\n\n"
        
        # Add query information
        if 'query' in search_results:
            formatted += f"Search Query: {search_results['query']}\n\n"
        
        # Add answer if available
        if 'answer' in search_results and search_results['answer']:
            formatted += f"AI Answer: {search_results['answer']}\n\n"
        
        # Add search results
        if 'results' in search_results:
            formatted += "Relevant Solutions:\n"
            for i, result in enumerate(search_results['results'][:3], 1):
                formatted += f"{i}. {result.get('title', 'No title')}\n"
                formatted += f"   URL: {result.get('url', 'No URL')}\n"
                if 'content' in result:
                    content = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
                    formatted += f"   Content: {content}\n"
            formatted += "\n"
        
        # Add extracted content if available
        if 'extracted_content' in search_results:
            formatted += "Detailed Solutions:\n"
            for i, content in enumerate(search_results['extracted_content'][:2], 1):
                truncated = content[:500] + "..." if len(content) > 500 else content
                formatted += f"{i}. {truncated}\n\n"
                
        return formatted

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

    def store_successful_fix(self):
        """
        Store the last fix in memory only after successful video rendering.
        This method should be called after confirming that the video was rendered successfully.
        """
        if (self.use_agent_memory and self.agent_memory and 
            hasattr(self, '_last_fix_metadata') and self._last_fix_metadata):
            
            fix_metadata = self._last_fix_metadata
            print(f"✅ Storing successful fix in memory: {fix_metadata['fix_method']} method")
            
            self.agent_memory.store_error_fix(
                error_message=fix_metadata["error_message"],
                original_code=fix_metadata["original_code"],
                fixed_code=fix_metadata["fixed_code"],
                topic=fix_metadata["topic"],
                scene_type=fix_metadata["scene_type"],
                fix_method=fix_metadata["fix_method"]
            )
            
            # Clear the metadata after storing
            self._last_fix_metadata = None
        else:
            print("No fix metadata to store or memory not available")

    def clear_fix_metadata(self):
        """
        Clear the last fix metadata without storing it.
        This method should be called when video rendering fails.
        """
        if hasattr(self, '_last_fix_metadata'):
            if self._last_fix_metadata:
                print("❌ Clearing unsuccessful fix metadata (video rendering failed)")
            self._last_fix_metadata = None