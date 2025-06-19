"""
Appwrite-based Agent Memory Management

This module provides agent memory functionality using Appwrite database
for storing and retrieving error-fix patterns, replacing the Mem0 integration.
"""

import os
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .appwrite_integration import AppwriteVideoManager

class AppwriteAgentMemory:
    """
    Manages agent memory for learning from coding errors and successful fixes.
    Uses Appwrite database to store and retrieve patterns that help improve code generation.
    """
    
    def __init__(self, appwrite_manager: AppwriteVideoManager, agent_id: str = "manimAnimationAgent"):
        """
        Initialize the agent memory system.
        
        Args:
            appwrite_manager: Appwrite manager instance
            agent_id: Unique identifier for this agent
        """
        self.agent_id = agent_id
        self.appwrite_manager = appwrite_manager
        self.enabled = appwrite_manager.enabled
        
        if not self.enabled:
            print("Warning: Appwrite not available. Agent memory features disabled.")
        else:
            print(f"Agent memory initialized for agent: {self.agent_id}")

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

    async def store_error_fix(self, 
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
            # Store using Appwrite manager
            success = await self.appwrite_manager.store_agent_memory(
                error_message=error_message,
                original_code=original_code,
                fixed_code=fixed_code,
                topic=topic,
                scene_type=scene_type,
                fix_method=fix_method
            )
            
            if success:
                print(f"Stored error-fix pattern for topic: {topic}")
            
            return success
            
        except Exception as e:
            print(f"Failed to store error-fix pattern: {e}")
            return False

    async def search_similar_fixes(self, 
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
            # Search using Appwrite manager
            results = await self.appwrite_manager.search_agent_memory(
                topic=topic,
                scene_type=scene_type,
                limit=limit
            )
            
            print(f"Found {len(results)} similar error patterns")
            return results
            
        except Exception as e:
            print(f"Failed to search for similar fixes: {e}")
            return []

    async def get_preventive_examples(self, 
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
            results = await self.appwrite_manager.search_agent_memory(
                topic=topic,
                scene_type=scene_type,
                limit=limit
            )
            
            examples = []
            for result in results:
                problem = result.get('error_message', 'Unknown error')
                solution = result.get('fixed_code', '')
                if solution:
                    examples.append((problem, solution))
            
            print(f"Retrieved {len(examples)} preventive examples")
            return examples
            
        except Exception as e:
            print(f"Failed to get preventive examples: {e}")
            return []

    async def store_successful_generation(self, 
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
            # Store as a successful pattern (no error, just good code)
            success = await self.appwrite_manager.store_agent_memory(
                error_message=f"Successful generation: {task_description}",
                original_code="# Previous attempt",
                fixed_code=generated_code,
                topic=topic,
                scene_type=scene_type,
                fix_method="llm"
            )
            
            return success
            
        except Exception as e:
            print(f"Failed to store successful generation: {e}")
            return False

    async def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories."""
        if not self.enabled:
            return {"enabled": False, "total_memories": 0}
            
        try:
            # Get memory statistics from Appwrite
            stats = await self.appwrite_manager.get_video_statistics()
            
            return {
                "enabled": True,
                "total_memories": stats.get("memory_patterns", 0),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            print(f"Failed to get memory stats: {e}")
            return {"enabled": True, "error": str(e)}

    async def clear_memory(self, confirm: bool = False) -> bool:
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
            # Note: This would require implementing a delete all method in AppwriteVideoManager
            # For now, return False as a safety measure
            print("Clear memory not implemented for Appwrite backend for safety")
            return False
            
        except Exception as e:
            print(f"Failed to clear memories: {e}")
            return False 