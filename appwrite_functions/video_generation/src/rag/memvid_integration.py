"""
Memvid integration for video-based RAG system using QR code encoding.
This module provides a wrapper around the memvid library to integrate
with the Manim Animation Agent's existing RAG infrastructure.
"""

import os
import sys
from typing import List, Dict, Optional, Union, Tuple
import logging
from pathlib import Path

try:
    from memvid import MemvidRetriever, MemvidChat
    HAS_MEMVID = True
except ImportError:
    MemvidRetriever = None
    MemvidChat = None
    HAS_MEMVID = False

logger = logging.getLogger(__name__)

class MemvidRAGIntegration:
    """
    Integration class for using memvid video-based memory as a RAG system.
    
    This class provides compatibility with the existing RAG interface
    while using video-based QR code memory for documentation retrieval.
    """

    def __init__(self, 
                 video_file: str = "manim_memory.mp4", 
                 index_file: str = "manim_memory_index.json",
                 session_id: Optional[str] = None,
                 use_langfuse: bool = False):
        """
        Initialize the memvid RAG integration.
        
        Args:
            video_file (str): Path to the memory video file
            index_file (str): Path to the memory index file  
            session_id (str, optional): Session identifier for tracking
            use_langfuse (bool): Whether to use Langfuse for tracking (compatibility)
        """
        self.video_file = video_file
        self.index_file = index_file
        self.session_id = session_id
        self.use_langfuse = use_langfuse
        
        if not HAS_MEMVID:
            raise ImportError(
                "memvid library not found. Please install with: pip install memvid"
            )
            
        # Check if memory files exist
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Memory video file not found: {video_file}")
        if not os.path.exists(index_file):
            raise FileNotFoundError(f"Memory index file not found: {index_file}")
            
        # Initialize memvid retriever
        try:
            self.retriever = MemvidRetriever(video_file, index_file)
            logger.info(f"✅ Memvid RAG initialized with {video_file}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize memvid retriever: {e}")
            raise
            
    def search_documents(self, 
                        queries: List[str], 
                        top_k: int = 5) -> List[Dict[str, Union[str, float]]]:
        """
        Search the video memory for relevant documentation.
        
        This method provides compatibility with the existing RAG interface
        by accepting multiple queries and returning formatted results.
        
        Args:
            queries (List[str]): List of search queries
            top_k (int): Maximum number of results per query
            
        Returns:
            List[Dict]: List of search results with content and scores
        """
        if not self.retriever:
            logger.warning("Memvid retriever not initialized")
            return []
            
        all_results = []
        
        for query in queries:
            try:
                # Search using memvid retriever
                results = self.retriever.search(query, top_k=top_k)
                
                # Format results to match expected interface
                # Handle different return formats from memvid
                for result in results:
                    try:
                        # Try to unpack as (chunk, score) first
                        if isinstance(result, (tuple, list)) and len(result) == 2:
                            chunk, score = result
                        elif isinstance(result, (tuple, list)) and len(result) > 2:
                            # If more than 2 values, take first two as chunk and score
                            chunk, score = result[0], result[1]
                        elif isinstance(result, dict):
                            # If result is a dict, extract content and score
                            chunk = result.get('content', result.get('text', str(result)))
                            score = result.get('score', 0.0)
                        else:
                            # Fallback: treat as string with default score
                            chunk = str(result)
                            score = 0.0
                            
                        all_results.append({
                            "content": chunk,
                            "score": float(score),
                            "query": query,
                            "source": "memvid_memory"
                        })
                    except Exception as unpack_error:
                        logger.error(f"Error unpacking result {result}: {unpack_error}")
                        continue
                    
            except Exception as e:
                logger.error(f"Error searching for query '{query}': {e}")
                continue
                
        # Sort by score and return top results
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k * len(queries)]
        
    def get_context(self, 
                    query: str, 
                    max_tokens: int = 2000) -> str:
        """
        Get context for a specific query with token limit.
        
        Args:
            query (str): Search query
            max_tokens (int): Maximum tokens in response
            
        Returns:
            str: Formatted context string
        """
        if not self.retriever:
            logger.warning("Memvid retriever not initialized")
            return ""
            
        try:
            # Use memvid's get_context method if available
            if hasattr(self.retriever, 'get_context'):
                context = self.retriever.get_context(query, max_tokens=max_tokens)
            else:
                # Fallback to search method
                results = self.retriever.search(query, top_k=5)
                context_parts = []
                current_tokens = 0
                
                for result in results:
                    try:
                        # Handle different return formats from memvid
                        if isinstance(result, (tuple, list)) and len(result) == 2:
                            chunk, score = result
                        elif isinstance(result, (tuple, list)) and len(result) > 2:
                            # If more than 2 values, take first two as chunk and score
                            chunk, score = result[0], result[1]
                        elif isinstance(result, dict):
                            # If result is a dict, extract content and score
                            chunk = result.get('content', result.get('text', str(result)))
                            score = result.get('score', 0.0)
                        else:
                            # Fallback: treat as string with default score
                            chunk = str(result)
                            score = 0.0
                            
                        # Rough token estimation (4 chars ≈ 1 token)
                        estimated_tokens = len(chunk) // 4
                        if current_tokens + estimated_tokens > max_tokens:
                            break
                        context_parts.append(f"[Score: {score:.3f}] {chunk}")
                        current_tokens += estimated_tokens
                    except Exception as unpack_error:
                        logger.error(f"Error unpacking result {result} in get_context: {unpack_error}")
                        continue
                    
                context = "\n\n".join(context_parts)
                
            return context
            
        except Exception as e:
            logger.error(f"Error getting context for query '{query}': {e}")
            return ""
            
    def format_rag_context(self, 
                          search_results: List[Dict[str, Union[str, float]]]) -> str:
        """
        Format search results into a context string for LLM consumption.
        
        Args:
            search_results (List[Dict]): Search results from search_documents
            
        Returns:
            str: Formatted context string
        """
        if not search_results:
            return "No relevant documentation found in memory."
            
        context_parts = [
            "=== MANIM DOCUMENTATION (from video memory) ===",
            ""
        ]
        
        for i, result in enumerate(search_results[:10], 1):  # Limit to top 10
            score = result.get("score", 0.0)
            content = result.get("content", "")
            query = result.get("query", "unknown")
            
            context_parts.extend([
                f"[Result {i} - Score: {score:.3f} - Query: '{query}']",
                content.strip(),
                ""
            ])
            
        context_parts.append("=== END DOCUMENTATION ===")
        return "\n".join(context_parts)
        
    def is_available(self) -> bool:
        """Check if memvid RAG system is available and functional."""
        return HAS_MEMVID and self.retriever is not None
        
    def get_stats(self) -> Dict[str, Union[str, int]]:
        """Get statistics about the memory system."""
        if not self.retriever:
            return {"status": "unavailable"}
            
        return {
            "status": "available",
            "video_file": self.video_file,
            "index_file": self.index_file,
            "video_size": os.path.getsize(self.video_file) if os.path.exists(self.video_file) else 0,
            "index_size": os.path.getsize(self.index_file) if os.path.exists(self.index_file) else 0,
            "session_id": self.session_id
        }

class MemvidChatIntegration:
    """
    Integration class for conversational interface with memvid memory.
    """

    def __init__(self, 
                 video_file: str = "manim_memory.mp4",
                 index_file: str = "manim_memory_index.json",
                 llm_api_key: Optional[str] = None,
                 llm_provider: str = "openai",
                 session_id: Optional[str] = None):
        """
        Initialize the memvid chat integration.
        
        Args:
            video_file (str): Path to the memory video file
            index_file (str): Path to the memory index file
            llm_api_key (str, optional): API key for LLM provider
            llm_provider (str): LLM provider ("openai" or "google")
            session_id (str, optional): Session identifier
        """
        self.video_file = video_file
        self.index_file = index_file
        self.llm_api_key = llm_api_key
        self.llm_provider = llm_provider
        self.session_id = session_id
        
        if not HAS_MEMVID:
            raise ImportError(
                "memvid library not found. Please install with: pip install memvid"
            )
            
        # Check if memory files exist
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Memory video file not found: {video_file}")
        if not os.path.exists(index_file):
            raise FileNotFoundError(f"Memory index file not found: {index_file}")
            
        # Get API key from environment if not provided
        if not llm_api_key:
            if llm_provider == "openai":
                llm_api_key = os.getenv("OPENAI_API_KEY")
            elif llm_provider == "google":
                llm_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                
        if not llm_api_key:
            logger.warning(f"No API key found for {llm_provider} provider")
            
        # Initialize memvid chat
        try:
            self.chat = MemvidChat(
                video_file=video_file,
                index_file=index_file,
                llm_api_key=llm_api_key,
                llm_provider=llm_provider
            )
            self.chat.start_session()
            logger.info(f"✅ Memvid chat initialized with {llm_provider} provider")
        except Exception as e:
            logger.error(f"❌ Failed to initialize memvid chat: {e}")
            raise
            
    def ask_question(self, question: str) -> str:
        """
        Ask a question to the memvid chat system.
        
        Args:
            question (str): Question to ask
            
        Returns:
            str: Answer from the chat system
        """
        if not self.chat:
            return "Chat system not available"
            
        try:
            response = self.chat.chat(question)
            return response
        except Exception as e:
            logger.error(f"Error asking question '{question}': {e}")
            return f"Error: {e}"

def get_memvid_integration(video_file: str = "manim_memory.mp4",
                          index_file: str = "manim_memory_index.json",
                          session_id: Optional[str] = None,
                          use_langfuse: bool = False) -> Optional[MemvidRAGIntegration]:
    """
    Factory function to get a memvid RAG integration instance.
    
    Args:
        video_file (str): Path to memory video file
        index_file (str): Path to memory index file  
        session_id (str, optional): Session identifier
        use_langfuse (bool): Whether to use Langfuse tracking
        
    Returns:
        MemvidRAGIntegration or None: Integration instance or None if unavailable
    """
    try:
        return MemvidRAGIntegration(
            video_file=video_file,
            index_file=index_file,
            session_id=session_id,
            use_langfuse=use_langfuse
        )
    except Exception as e:
        logger.error(f"Failed to create memvid integration: {e}")
        return None 