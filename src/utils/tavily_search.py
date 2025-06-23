"""
Tavily Search Integration for Advanced Error-Driven Development

This module implements the two-step strategy for error resolution:
1. Generate a concise search query from the full traceback
2. Use Tavily to search for solutions and apply them

Author: manimAnimationAgent
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


@dataclass
class ErrorAnalysis:
    """Structured representation of error analysis"""
    error_type: str
    key_components: List[str]
    search_query: str
    context_info: str


class TavilyErrorSearchEngine:
    """
    Advanced error-driven development engine using Tavily for intelligent error resolution.
    
    This class implements a two-step strategy:
    1. Analyze the full traceback and generate a concise search query (under 400 chars)
    2. Search for solutions using Tavily and provide structured results
    """
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize the Tavily Error Search Engine.
        
        Args:
            api_key: Tavily API key. If None, will try to get from TAVILY_API_KEY env var
            verbose: Whether to print detailed logs
        """
        self.verbose = verbose
        self.client = None
        
        if not TAVILY_AVAILABLE:
            if self.verbose:
                print("⚠️ Tavily not available. Install with: pip install tavily-python")
            return
            
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        
        if not self.api_key:
            if self.verbose:
                print("⚠️ No Tavily API key found. Set TAVILY_API_KEY environment variable or pass api_key parameter")
            return
            
        try:
            self.client = TavilyClient(api_key=self.api_key)
            if self.verbose:
                print("✅ Tavily client initialized successfully")
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to initialize Tavily client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Tavily is available and properly configured"""
        return TAVILY_AVAILABLE and self.client is not None

    def analyze_error_for_search(self, traceback: str, code_context: str = "") -> ErrorAnalysis:
        """
        Step 1: Analyze the full traceback and generate a concise search query using Gemini.
        
        This method uses Gemini to intelligently analyze the error and create
        an effective search query under 400 characters.
        
        Args:
            traceback: Full error traceback from Manim
            code_context: Additional code context (optional)
            
        Returns:
            ErrorAnalysis object with structured error information
        """
        if self.verbose:
            # print("🔍 Analyzing error for search query generation using Gemini...")
            pass  # Removed noisy Gemini analyzer log
            
        # Extract key error components for Gemini analysis
        error_type = self._extract_error_type(traceback)
        key_components = self._extract_key_components(traceback, code_context)
        context_info = self._extract_context_info(traceback, code_context)
        
        # Use fallback method instead of Gemini to reduce noise and duplicated analysis
        search_query = self._generate_search_query_fallback(error_type, key_components, traceback)
        
        analysis = ErrorAnalysis(
            error_type=error_type,
            key_components=key_components,
            search_query=search_query,
            context_info=context_info
        )
        
        if self.verbose:
            print(f"📋 Error Analysis:")
            print(f"   Type: {analysis.error_type}")
            print(f"   Key Components: {analysis.key_components}")
            print(f"   Search Query ({len(analysis.search_query)} chars): {analysis.search_query}")
            
        return analysis

    def search_for_solution(self, error_analysis: ErrorAnalysis, max_results: int = 5, extract_content: bool = True) -> Dict:
        """
        Step 2: Use Tavily to search for solutions based on the error analysis.
        
        Args:
            error_analysis: ErrorAnalysis object from analyze_error_for_search
            max_results: Maximum number of search results to return
            extract_content: Whether to extract full page content from URLs using Tavily Extract
            
        Returns:
            Dictionary containing search results and extracted solutions
        """
        if not self.is_available():
            return {
                "available": False,
                "error": "Tavily not available or not configured",
                "fallback_suggestions": self._get_fallback_suggestions(error_analysis)
            }
            
        try:
            if self.verbose:
                print(f"🔍 Searching Tavily for: {error_analysis.search_query}")
                
            # Perform the search with documentation priority
            response = self.client.search(
                query=error_analysis.search_query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_domains=[
                    "docs.manim.community",  # Highest priority - official docs
                    "github.com/ManimCommunity",  # Official GitHub
                    "github.com",  # Other GitHub repos
                    "stackoverflow.com"  # Community solutions as backup
                    # Removed reddit/discord to focus on authoritative sources
                ]
            )
            
            # Process and structure the results
            processed_results = self._process_search_results(response, error_analysis)
            
            # Step 3: Extract full content from TOP 3 URLs if requested
            if extract_content and processed_results.get("solutions"):
                processed_results = self._extract_full_content(processed_results, max_extractions=3)
            
            if self.verbose:
                print(f"✅ Found {len(processed_results.get('solutions', []))} potential solutions")
                if extract_content:
                    extracted_count = sum(1 for sol in processed_results.get('solutions', []) if sol.get('extracted_content'))
                    print(f"📄 Extracted full content from {extracted_count} URLs")
                
            return processed_results
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Tavily search failed: {e}")
            return {
                "available": True,
                "error": str(e),
                "fallback_suggestions": self._get_fallback_suggestions(error_analysis)
            }

    def get_error_resolution_suggestions(self, traceback: str, code_context: str = "", extract_content: bool = True) -> Dict:
        """
        Complete three-step error resolution process.
        
        This is the main method that combines all steps:
        1. Analyze error and generate search query
        2. Search for solutions using Tavily
        3. Extract full content from top URLs for deeper analysis
        
        Args:
            traceback: Full error traceback from Manim
            code_context: Additional code context (optional)
            extract_content: Whether to extract full page content from URLs
            
        Returns:
            Dictionary containing analysis, search results, extracted content, and actionable suggestions
        """
        # Step 1: Analyze error
        error_analysis = self.analyze_error_for_search(traceback, code_context)
        
        # Step 2: Search for solutions and extract content
        search_results = self.search_for_solution(error_analysis, extract_content=extract_content)
        
        # Combine results
        return {
            "error_analysis": error_analysis,
            "search_results": search_results,
            "actionable_suggestions": self._generate_actionable_suggestions(
                error_analysis, search_results
            ),
            "has_extracted_content": any(
                sol.get("extracted_content") for sol in search_results.get("solutions", [])
            ),
            "timestamp": self._get_timestamp()
        }

    def _extract_error_type(self, traceback: str) -> str:
        """Extract the type of error from traceback"""
        # Look for common Python exception types
        error_patterns = [
            r'(\w*Error): ',
            r'(\w*Exception): ',
            r'(\w*Warning): '
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, traceback)
            if match:
                return match.group(1)
                
        return "UnknownError"

    def _extract_key_components(self, traceback: str, code_context: str) -> List[str]:
        """Extract key components that should be included in search"""
        components = []
        
        # Extract Manim-specific components with better patterns
        manim_patterns = [
            r'(manim\.\w+)',
            r'(\w+\.animate\.\w+)',
            r'(self\.play\([^)]+\))',
            r'(\w+(?:Mobject|Animation|Scene)\w*)',
            r'(Polygon|Triangle|Square|Circle|Rectangle)', # Common shapes
            r'(get_\w+)', # Common getter methods
            r'(Angle|Line|Arrow|Text|MathTex)', # Common objects
        ]
        
        text_to_search = traceback + " " + code_context
        
        for pattern in manim_patterns:
            matches = re.findall(pattern, text_to_search, re.IGNORECASE)
            components.extend(matches)
        
        # Extract specific method names that failed
        method_pattern = r'AttributeError.*\'(\w+)\' object has no attribute \'(\w+)\''
        method_match = re.search(method_pattern, traceback)
        if method_match:
            obj_type, method_name = method_match.groups()
            components.extend([obj_type, method_name])
            
        # Extract specific TypeError patterns
        type_error_pattern = r'TypeError: (\w+)\.(\w+)\(\) (.*)'
        type_match = re.search(type_error_pattern, traceback)
        if type_match:
            class_name, method_name, error_detail = type_match.groups()
            components.extend([class_name, method_name])
            
        # Extract specific method calls from code context
        method_call_pattern = r'(\w+)\.(\w+)\('
        method_calls = re.findall(method_call_pattern, code_context)
        for obj_name, method_name in method_calls[-3:]:  # Last 3 method calls
            components.extend([obj_name, method_name])
        
        # Remove duplicates and limit length
        unique_components = list(set(components))
        return unique_components[:5]  # Limit to avoid query length issues

    def _extract_context_info(self, traceback: str, code_context: str) -> str:
        """Extract contextual information for better understanding"""
        context_parts = []
        
        # Extract file and line number
        file_pattern = r'File "([^"]+)", line (\d+)'
        file_match = re.search(file_pattern, traceback)
        if file_match:
            file_path, line_num = file_match.groups()
            context_parts.append(f"File: {os.path.basename(file_path)}:{line_num}")
        
        # Extract the actual error message
        error_msg_pattern = r'(\w+(?:Error|Exception)): (.+)$'
        error_match = re.search(error_msg_pattern, traceback, re.MULTILINE)
        if error_match:
            error_type, error_msg = error_match.groups()
            context_parts.append(f"Message: {error_msg.strip()}")
        
        return " | ".join(context_parts)

    def _process_search_results(self, response: Dict, error_analysis: ErrorAnalysis) -> Dict:
        """Process and structure Tavily search results"""
        results = {
            "available": True,
            "query_used": error_analysis.search_query,
            "answer": response.get("answer", ""),
            "solutions": [],
            "raw_results": response.get("results", [])
        }
        
        # Extract solutions from search results
        for result in response.get("results", [])[:5]:
            solution = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "relevance_score": result.get("score", 0),
                "source_type": self._classify_source(result.get("url", "")),
                "extracted_content": None  # Will be populated by _extract_full_content if enabled
            }
            results["solutions"].append(solution)
        
        return results

    def _extract_full_content(self, search_results: Dict, max_extractions: int = 3) -> Dict:
        """
        Step 3: Extract full page content from TOP 3 URLs using Tavily Extract API.
        
        Prioritizes URLs by:
        1. Official docs (docs.manim.community) - highest priority
        2. GitHub repos - second priority  
        3. Stack Overflow - third priority
        
        Args:
            search_results: Dictionary containing search results with URLs
            max_extractions: Maximum number of URLs to extract content from (default: 3)
            
        Returns:
            Updated search results with extracted content from top 3 prioritized URLs
        """
        if not self.is_available() or not search_results.get("solutions"):
            return search_results
            
        # Get top URLs based on relevance score and source type priority
        solutions = search_results["solutions"]
        prioritized_solutions = self._prioritize_urls_for_extraction(solutions, max_extractions)
        
        urls_to_extract = [sol["url"] for sol in prioritized_solutions if sol["url"]]
        
        if not urls_to_extract:
            if self.verbose:
                print("⚠️ No valid URLs found for content extraction")
            return search_results
        
        try:
            if self.verbose:
                print(f"📄 Extracting content from TOP {len(urls_to_extract)} URLs (max 3)...")
                for i, url in enumerate(urls_to_extract, 1):
                    print(f"   {i}. {url}")
                
            # Use Tavily Extract API to get full page content
            extract_response = self.client.extract(
                urls=urls_to_extract,
                include_images=False,  # Focus on text content for error resolution
                extract_depth="basic",  # Basic extraction is sufficient for most cases
                format="markdown"  # Markdown format for better LLM processing
            )
            
            # Process extraction results
            extraction_results = {}
            for result in extract_response.get("results", []):
                url = result.get("url", "")
                raw_content = result.get("raw_content", "")
                if url and raw_content:
                    # Clean and truncate content for LLM processing
                    cleaned_content = self._clean_extracted_content(raw_content)
                    extraction_results[url] = cleaned_content
            
            # Add extracted content back to solutions
            for solution in solutions:
                url = solution["url"]
                if url in extraction_results:
                    solution["extracted_content"] = extraction_results[url]
                    if self.verbose:
                        content_length = len(extraction_results[url])
                        print(f"✅ Extracted {content_length} characters from {solution['source_type']}: {solution['title'][:50]}...")
            
            # Handle failed extractions
            failed_results = extract_response.get("failed_results", [])
            if failed_results and self.verbose:
                print(f"⚠️ Failed to extract content from {len(failed_results)} URLs")
                
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Content extraction failed: {e}")
        
        return search_results

    def _prioritize_urls_for_extraction(self, solutions: List[Dict], max_extractions: int) -> List[Dict]:
        """Prioritize which URLs to extract content from based on source type and relevance"""
        # Define priority order for source types
        source_priority = {
            "official_docs": 1,
            "github": 2,
            "stackoverflow": 3,
            "reddit": 4,
            "other": 5
        }
        
        # Sort by source priority first, then by relevance score
        prioritized = sorted(
            solutions,
            key=lambda x: (
                source_priority.get(x.get("source_type", "other"), 5),
                -x.get("relevance_score", 0)
            )
        )
        
        return prioritized[:max_extractions]

    def _clean_extracted_content(self, raw_content: str, max_length: int = 8000) -> str:
        """Clean and truncate extracted content for LLM processing"""
        if not raw_content:
            return ""
        
        # Remove excessive whitespace and clean up formatting
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', raw_content)  # Reduce multiple newlines
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Normalize spaces
        cleaned = cleaned.strip()
        
        # Truncate if too long (keep within token limits)
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "\n\n[Content truncated for processing...]"
        
        return cleaned

    def _classify_source(self, url: str) -> str:
        """Classify the type of source"""
        if "docs.manim.community" in url:
            return "official_docs"
        elif "github.com" in url:
            return "github"
        elif "stackoverflow.com" in url:
            return "stackoverflow"
        elif "reddit.com" in url:
            return "reddit"
        else:
            return "other"

    def _generate_actionable_suggestions(self, error_analysis: ErrorAnalysis, search_results: Dict) -> List[str]:
        """Generate actionable suggestions based on error analysis and search results"""
        suggestions = []
        
        if not search_results.get("available", False):
            return [
                "Tavily search not available. Try manual documentation lookup.",
                f"Search for: {error_analysis.search_query}",
                "Check Manim Community documentation",
                "Review similar code examples online"
            ]
        
        # Extract suggestions from Tavily answer
        answer = search_results.get("answer", "")
        if answer:
            suggestions.append(f"Quick Answer: {answer}")
        
        # Extract suggestions from high-scoring results
        for solution in search_results.get("solutions", [])[:3]:
            if solution.get("relevance_score", 0) > 0.7:
                source_type = solution.get("source_type", "")
                title = solution.get("title", "")
                
                if source_type == "official_docs":
                    suggestions.append(f"📚 Official Docs: {title}")
                elif source_type == "stackoverflow":
                    suggestions.append(f"💡 Stack Overflow: {title}")
                elif source_type == "github":
                    suggestions.append(f"🔧 GitHub: {title}")
        
        # Add generic suggestions based on error type
        error_type = error_analysis.error_type.lower()
        if "attributeerror" in error_type:
            suggestions.append("🔍 Check method/attribute names in latest Manim docs")
        elif "importerror" in error_type or "modulenotfounderror" in error_type:
            suggestions.append("📦 Verify Manim installation and imports")
        elif "typeerror" in error_type:
            suggestions.append("🔧 Check function parameters and data types")
        
        return suggestions[:6]  # Limit to 6 suggestions

    def _get_fallback_suggestions(self, error_analysis: ErrorAnalysis) -> List[str]:
        """Get fallback suggestions when Tavily is not available"""
        suggestions = [
            f"Manual search recommended: {error_analysis.search_query}",
            "Check Manim Community documentation at docs.manim.community"
        ]
        
        # Add specific suggestions based on error type
        if "get_side_length" in error_analysis.search_query:
            suggestions.extend([
                "Use: np.linalg.norm(vertex2 - vertex1) to calculate side length",
                "Or use get_vertices() and calculate distances manually",
                "Polygon objects don't have get_side_length() method"
            ])
        elif "Angle" in error_analysis.search_query and "radius" in error_analysis.search_query:
            suggestions.extend([
                "Use: Angle(line1, line2, radius=0.5) instead of Angle(vertex1, vertex2, vertex3)",
                "Angle requires Line objects, not vertex coordinates",
                "Check Angle documentation for correct parameters"
            ])
        elif "Point" in error_analysis.search_query:
            suggestions.extend([
                "Use numpy arrays: np.array([x, y, z]) instead of Point(x, y, z)",
                "Manim uses numpy arrays for coordinates, not Point objects",
                "Use [x, y, z] for vertex coordinates in Polygon"
            ])
        else:
            suggestions.extend([
                "Search GitHub issues for similar problems",
                "Ask on Manim Discord or Reddit community",
                "Review Manim examples and tutorials"
            ])
            
        return suggestions

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _generate_search_query_fallback(self, error_type: str, key_components: List[str], traceback: str) -> str:
        """
        Generate a documentation-targeted search query when Gemini is not available.
        
        Strategy: Focus on official documentation with specific error messages and objects.
        Format: manim [Object] [ErrorType]: [key error phrase] site:docs.manim.community
        """
        # Extract the main Manim object/class involved
        main_object = self._extract_main_manim_object(traceback, key_components)
        
        # Extract key error phrase from the actual error message
        error_phrase = self._extract_key_error_phrase(traceback)
        
        # Build documentation-targeted query
        query_parts = ["manim"]
        
        # Add the main object if found
        if main_object:
            query_parts.append(main_object)
        
        # Add error type
        query_parts.append(error_type)
        
        # Add key error phrase if found and space allows
        if error_phrase:
            test_query = " ".join(query_parts + [error_phrase])
            if len(test_query) < 350:  # Leave room for site: operator
                query_parts.append(error_phrase)
        
        # Always target official documentation first
        base_query = " ".join(query_parts)
        final_query = f"{base_query} site:docs.manim.community"
        
        # If too long, remove error phrase and try again
        if len(final_query) > 400:
            base_query = " ".join(query_parts[:-1]) if error_phrase else base_query
            final_query = f"{base_query} site:docs.manim.community"
        
        # Last resort - just basic query
        if len(final_query) > 400:
            final_query = f"manim {error_type} {main_object or ''} site:docs.manim.community".strip()
            
        return final_query

    def _extract_main_manim_object(self, traceback: str, key_components: List[str]) -> str:
        """Extract the main Manim object/class that's causing the error"""
        # Priority order for Manim objects (most specific first)
        manim_objects = [
            # Geometry objects
            'Polygon', 'Triangle', 'Square', 'Circle', 'Rectangle', 'RegularPolygon', 'Ellipse',
            'Line', 'Arrow', 'Vector', 'Angle', 'Arc', 'Sector', 'Annulus',
            
            # Text and Math
            'Text', 'MathTex', 'Tex', 'MarkupText', 'Code',
            
            # 3D objects
            'Sphere', 'Cube', 'Cylinder', 'Cone', 'Torus', 'Surface', 'ParametricSurface',
            
            # Animations
            'Transform', 'ReplacementTransform', 'TransformMatchingTex', 'FadeIn', 'FadeOut',
            'Create', 'Write', 'DrawBorderThenFill', 'ShowCreation', 'GrowFromCenter',
            'Indicate', 'Flash', 'Circumscribe', 'Wiggle', 'Rotate', 'Move', 'Shift',
            
            # Scene and groups
            'Scene', 'VGroup', 'Group', 'VMobject', 'Mobject',
            
            # Number line and graphs
            'NumberLine', 'Axes', 'Graph', 'BarChart', 'PieChart'
        ]
        
        # Search in traceback and key components
        text_to_search = (traceback + " " + " ".join(key_components)).lower()
        
        for obj in manim_objects:
            if obj.lower() in text_to_search:
                return obj
        
        # Fallback to first component that looks like a class (capitalized)
        for component in key_components:
            if component and component[0].isupper() and len(component) > 2:
                return component
                
        return ""

    def _extract_key_error_phrase(self, traceback: str) -> str:
        """Extract the most descriptive part of the error message"""
        # Look for the actual error message line
        error_message_patterns = [
            # ValueError patterns
            r'ValueError: (.+?)(?:\n|$)',
            # TypeError patterns  
            r'TypeError: (.+?)(?:\n|$)',
            # AttributeError patterns
            r'AttributeError: (.+?)(?:\n|$)',
            # ImportError patterns
            r'ImportError: (.+?)(?:\n|$)',
            r'ModuleNotFoundError: (.+?)(?:\n|$)',
            # Generic error patterns
            r'(\w+Error: .+?)(?:\n|$)',
            r'(\w+Exception: .+?)(?:\n|$)'
        ]
        
        for pattern in error_message_patterns:
            match = re.search(pattern, traceback, re.MULTILINE | re.IGNORECASE)
            if match:
                error_msg = match.group(1).strip()
                
                # Clean up and shorten the error message for search
                # Remove file paths and line numbers
                error_msg = re.sub(r'/[\w/.-]+\.py:\d+', '', error_msg)
                error_msg = re.sub(r'File "[^"]+", line \d+', '', error_msg)
                
                # Remove excessive technical details but keep key phrases
                if "same number of dimensions" in error_msg:
                    return "all input arrays must have same number of dimensions"
                elif "takes" in error_msg and "argument" in error_msg:
                    return "takes positional argument"
                elif "has no attribute" in error_msg:
                    # Extract the attribute name
                    attr_match = re.search(r"has no attribute '(\w+)'", error_msg)
                    if attr_match:
                        return f"has no attribute {attr_match.group(1)}"
                elif "unexpected keyword argument" in error_msg:
                    return "unexpected keyword argument"
                elif "missing" in error_msg and "required" in error_msg:
                    return "missing required argument"
                else:
                    # Return first 50 characters of cleaned error message
                    return error_msg[:50].strip()
        
        return ""


# Helper function for easy integration
def search_error_solution(traceback: str, code_context: str = "", api_key: Optional[str] = None, extract_content: bool = True) -> Dict:
    """
    Convenient function to search for error solutions using Tavily with content extraction.
    
    Args:
        traceback: Full error traceback
        code_context: Additional code context
        api_key: Tavily API key (optional)
        extract_content: Whether to extract full page content from URLs (default: True)
        
    Returns:
        Dictionary with error analysis, solution suggestions, and extracted content
    """
    engine = TavilyErrorSearchEngine(api_key=api_key, verbose=True)
    return engine.get_error_resolution_suggestions(traceback, code_context, extract_content=extract_content) 