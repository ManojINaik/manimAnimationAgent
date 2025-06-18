"""
Agent Memory Management using Mem0 for Self-Improving Code Generation.

This module provides functionality to store and retrieve error-fix patterns,
allowing the agent to learn from past mistakes and improve code generation.
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime

try:
    from mem0 import MemoryClient
    HAS_MEM0 = True
except ImportError:
    MemoryClient = None
    HAS_MEM0 = False

class AgentMemory:
    """
    Manages agent memory for learning from coding errors and successful fixes.
    Uses Mem0 to store and retrieve patterns that help improve code generation.
    """
    
    def __init__(self, api_key: Optional[str] = None, agent_id: str = "theorem-explain-agent"):
        """
        Initialize the agent memory system.
        
        Args:
            api_key: Mem0 API key. If None, tries to get from environment
            agent_id: Unique identifier for this agent
        """
        self.agent_id = agent_id
        self.enabled = HAS_MEM0
        
        if not self.enabled:
            print("Warning: mem0ai not available. Agent memory features disabled.")
            return
            
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv('MEM0_API_KEY') or os.getenv('mem0_api_key')
            
        if not api_key:
            print("Warning: No Mem0 API key found. Agent memory features disabled.")
            self.enabled = False
            return
            
        try:
            self.client = MemoryClient(api_key=api_key)
            print(f"Agent memory initialized for agent: {self.agent_id}")
        except Exception as e:
            print(f"Failed to initialize Mem0 client: {e}")
            self.enabled = False

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

    def store_error_fix(self, 
                       error_message: str, 
                       original_code: str, 
                       fixed_code: str, 
                       topic: str = None,
                       scene_type: str = None,
                       fix_method: str = "llm") -> bool:
        """
        Store an error-fix pair in agent memory.
        
        Args:
            error_message: The error that occurred
            original_code: Code that caused the error
            fixed_code: The corrected code
            topic: Topic/subject of the code (e.g., "calculus", "physics")
            scene_type: Type of scene (e.g., "graph", "animation", "formula")
            fix_method: How the fix was applied ("auto", "llm", "manual")
            
        Returns:
            bool: True if successfully stored, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            # Create a structured memory entry
            timestamp = datetime.now().isoformat()
            error_hash = self._create_error_hash(error_message, original_code)
            
            # Truncate code to fit within metadata limits (Mem0 has 2000 char limit)
            max_code_length = 300  # Leave room for other metadata
            truncated_original = original_code[:max_code_length] + "..." if len(original_code) > max_code_length else original_code
            truncated_fixed = fixed_code[:max_code_length] + "..." if len(fixed_code) > max_code_length else fixed_code
            
            # Create a descriptive message for Mem0
            messages = [
                {
                    "role": "assistant", 
                    "content": f"I encountered an error '{error_message[:100]}...' in {topic or 'unknown'} code generation. "
                              f"I successfully fixed it by modifying the code. The original issue was in code that "
                              f"involved {scene_type or 'general'} elements. The fix method was {fix_method}. "
                              f"This pattern should be remembered for similar future errors."
                }
            ]
            
            # Store in Mem0 with metadata (keeping under 2000 chars total)
            metadata = {
                "type": "error_fix",
                "error_hash": error_hash,
                "topic": (topic or "general")[:50],  # Limit topic length
                "scene_type": (scene_type or "general")[:50],  # Limit scene type length
                "fix_method": fix_method[:20],  # Limit fix method length
                "timestamp": timestamp,
                "error_snippet": error_message[:200],  # Store error snippet
                "original_snippet": truncated_original,
                "fixed_snippet": truncated_fixed
            }
            
            # Ensure metadata doesn't exceed limit
            metadata_str = str(metadata)
            if len(metadata_str) > 1900:  # Leave some buffer
                # Further truncate code snippets
                metadata["original_snippet"] = original_code[:100] + "..."
                metadata["fixed_snippet"] = fixed_code[:100] + "..."
            
            result = self.client.add(
                messages=messages,
                agent_id=self.agent_id,
                metadata=metadata
            )
            
            print(f"Stored error-fix pattern: {error_hash} for topic: {topic}")
            return True
            
        except Exception as e:
            print(f"Failed to store error-fix pattern: {e}")
            return False

    def search_similar_fixes(self, 
                           error_message: str, 
                           code_context: str, 
                           topic: str = None,
                           scene_type: str = None,
                           limit: int = 5) -> List[Dict]:
        """
        Search for similar error-fix patterns in memory.
        
        Args:
            error_message: Current error message
            code_context: Current code context
            topic: Current topic/subject
            scene_type: Current scene type
            limit: Maximum number of results
            
        Returns:
            List of similar error-fix patterns
        """
        if not self.enabled:
            return []
            
        try:
            # Create search query
            query = f"error fix pattern similar to '{error_message[:100]}' in {topic or 'general'} code"
            
            # Search with filters
            filters = {
                "type": "error_fix"
            }
            
            if topic:
                filters["topic"] = topic
            if scene_type:
                filters["scene_type"] = scene_type
                
            results = self.client.search(
                query=query,
                agent_id=self.agent_id,
                filters=filters,
                limit=limit
            )
            
            print(f"Found {len(results)} similar error patterns")
            return results
            
        except Exception as e:
            print(f"Failed to search for similar fixes: {e}")
            return []

    def get_preventive_examples(self, 
                              task_description: str, 
                              topic: str = None,
                              scene_type: str = None,
                              limit: int = 3) -> List[Tuple[str, str]]:
        """
        Get successful code examples that can prevent common errors.
        
        Args:
            task_description: Description of the current task
            topic: Current topic/subject
            scene_type: Current scene type
            limit: Maximum number of examples
            
        Returns:
            List of (problem_description, solution_code) tuples
        """
        if not self.enabled:
            return []
            
        try:
            # Search for successful patterns
            query = f"successful {scene_type or 'general'} code examples for {topic or 'general'} {task_description}"
            
            filters = {
                "type": "error_fix",
                "success": True
            }
            
            if topic:
                filters["topic"] = topic
            if scene_type:
                filters["scene_type"] = scene_type
                
            results = self.client.search(
                query=query,
                agent_id=self.agent_id,
                filters=filters,
                limit=limit
            )
            
            examples = []
            for result in results:
                if 'metadata' in result:
                    meta = result['metadata']
                    # Handle both old and new metadata structures
                    problem = meta.get('error_snippet', meta.get('error_message', 'Unknown error'))
                    solution = meta.get('fixed_snippet', meta.get('fixed_code', meta.get('code_snippet', '')))
                    if solution:
                        examples.append((problem, solution))
            
            print(f"Retrieved {len(examples)} preventive examples")
            return examples
            
        except Exception as e:
            print(f"Failed to get preventive examples: {e}")
            return []

    def store_successful_generation(self, 
                                  task_description: str, 
                                  generated_code: str, 
                                  topic: str = None,
                                  scene_type: str = None) -> bool:
        """
        Store a successful code generation pattern.
        
        Args:
            task_description: Description of what the code does
            generated_code: The successful code
            topic: Topic/subject of the code
            scene_type: Type of scene
            
        Returns:
            bool: True if successfully stored
        """
        if not self.enabled:
            return False
            
        try:
            timestamp = datetime.now().isoformat()
            
            # Truncate large content to fit Mem0's 2000 char metadata limit
            max_desc_length = 200
            max_code_length = 500
            
            truncated_description = task_description[:max_desc_length] + "..." if len(task_description) > max_desc_length else task_description
            truncated_code = generated_code[:max_code_length] + "..." if len(generated_code) > max_code_length else generated_code
            
            messages = [
                {
                    "role": "assistant",
                    "content": f"I successfully generated code for {truncated_description} in {topic or 'general'} domain. "
                              f"The code works correctly for {scene_type or 'general'} type scenes. "
                              f"This is a good pattern to reference for similar tasks."
                }
            ]
            
            # Create metadata within size limits
            metadata = {
                "type": "successful_generation",
                "task_description": truncated_description,
                "code_snippet": truncated_code,
                "topic": (topic or "general")[:50],
                "scene_type": (scene_type or "general")[:50],
                "timestamp": timestamp
            }
            
            # Double-check metadata size
            metadata_str = str(metadata)
            if len(metadata_str) > 1900:  # Leave buffer
                # Further reduce code snippet
                metadata["code_snippet"] = generated_code[:200] + "..."
                metadata["task_description"] = task_description[:100] + "..."
            
            result = self.client.add(
                messages=messages,
                agent_id=self.agent_id,
                metadata=metadata
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to store successful generation: {e}")
            return False

    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories."""
        if not self.enabled:
            return {"enabled": False, "total_memories": 0}
            
        try:
            # Get all memories for this agent
            all_memories = self.client.get_all(agent_id=self.agent_id)
            
            error_fixes = len([m for m in all_memories if m.get('metadata', {}).get('type') == 'error_fix'])
            successful_gens = len([m for m in all_memories if m.get('metadata', {}).get('type') == 'successful_generation'])
            
            return {
                "enabled": True,
                "total_memories": len(all_memories),
                "error_fixes": error_fixes,
                "successful_generations": successful_gens,
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            print(f"Failed to get memory stats: {e}")
            return {"enabled": True, "error": str(e)}

    def clear_memory(self, confirm: bool = False) -> bool:
        """
        Clear all memories for this agent.
        
        Args:
            confirm: Must be True to actually clear memories
            
        Returns:
            bool: True if cleared successfully
        """
        if not self.enabled or not confirm:
            return False
            
        try:
            # This is a destructive operation - require explicit confirmation
            all_memories = self.client.get_all(agent_id=self.agent_id)
            
            for memory in all_memories:
                self.client.delete(memory_id=memory['id'])
                
            print(f"Cleared {len(all_memories)} memories for agent {self.agent_id}")
            return True
            
        except Exception as e:
            print(f"Failed to clear memories: {e}")
            return False 