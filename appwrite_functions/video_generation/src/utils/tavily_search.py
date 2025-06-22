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
            print("🔍 Analyzing error for search query generation using Gemini...")
            
        # Extract key error components for Gemini analysis
        error_type = self._extract_error_type(traceback)
        key_components = self._extract_key_components(traceback, code_context)
        context_info = self._extract_context_info(traceback, code_context)
        
        # Use Gemini to generate optimal search query
        search_query = self._generate_search_query_with_gemini(traceback, code_context, error_type, key_components)
        
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

    def search_for_solution(self, error_analysis: ErrorAnalysis, max_results: int = 5) -> Dict:
        """
        Step 2: Use Tavily to search for solutions based on the error analysis.
        
        Args:
            error_analysis: ErrorAnalysis object from analyze_error_for_search
            max_results: Maximum number of search results to return
            
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
                
            # Perform the search
            response = self.client.search(
                query=error_analysis.search_query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_domains=[
                    "docs.manim.community",
                    "github.com",
                    "stackoverflow.com",
                    "reddit.com",
                    "discord.com"
                ]
            )
            
            # Process and structure the results
            processed_results = self._process_search_results(response, error_analysis)
            
            if self.verbose:
                print(f"✅ Found {len(processed_results.get('solutions', []))} potential solutions")
                
            return processed_results
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Tavily search failed: {e}")
            return {
                "available": True,
                "error": str(e),
                "fallback_suggestions": self._get_fallback_suggestions(error_analysis)
            }

    def get_error_resolution_suggestions(self, traceback: str, code_context: str = "") -> Dict:
        """
        Complete two-step error resolution process.
        
        This is the main method that combines both steps:
        1. Analyze error and generate search query
        2. Search for solutions using Tavily
        
        Args:
            traceback: Full error traceback from Manim
            code_context: Additional code context (optional)
            
        Returns:
            Dictionary containing analysis, search results, and actionable suggestions
        """
        # Step 1: Analyze error
        error_analysis = self.analyze_error_for_search(traceback, code_context)
        
        # Step 2: Search for solutions
        search_results = self.search_for_solution(error_analysis)
        
        # Combine results
        return {
            "error_analysis": error_analysis,
            "search_results": search_results,
            "actionable_suggestions": self._generate_actionable_suggestions(
                error_analysis, search_results
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

    def _generate_search_query_with_gemini(self, traceback: str, code_context: str, error_type: str, key_components: List[str]) -> str:
        """
        Use Gemini to generate an optimal search query for the error.
        
        Args:
            traceback: Full error traceback
            code_context: Code context around the error
            error_type: Type of error (e.g., TypeError, AttributeError)
            key_components: Key components extracted from the error
            
        Returns:
            Optimized search query under 400 characters
        """
        try:
            # Import Gemini client
            import google.generativeai as genai
            import os
            
            # Configure Gemini
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                if self.verbose:
                    print("⚠️ No Gemini API key found, using fallback query generation")
                return self._generate_search_query_fallback(error_type, key_components, traceback)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Create prompt for Gemini
            prompt = f"""You are an expert in Manim (Python animation library) error analysis. Your task is to generate the most effective search query for finding solutions to this specific error.

ERROR DETAILS:
Error Type: {error_type}
Key Components: {key_components}

TRACEBACK:
{traceback[:1000]}  # Limit traceback to avoid token limits

CODE CONTEXT:
{code_context[:500]}  # Limit context to avoid token limits

REQUIREMENTS:
1. Generate a search query that is EXACTLY under 400 characters
2. Focus on the most important keywords for finding solutions
3. Include "manim" as the first word
4. Prioritize: error type, object names, method names, and the specific issue
5. Avoid generic terms, focus on specific Manim terminology
6. Consider common Manim documentation sources and community discussions

EXAMPLES:
- For Polygon vertex errors: "manim Polygon vertices numpy array coordinates"
- For Angle constructor errors: "manim Angle Line objects constructor parameters"
- For missing methods: "manim [ObjectType] [methodname] alternative solution"

Generate ONLY the search query (no explanation):"""

            # Generate query with Gemini
            response = model.generate_content(prompt)
            search_query = response.text.strip()
            
            # Ensure it's under 400 characters
            if len(search_query) > 400:
                search_query = search_query[:397] + "..."
            
            # Ensure it starts with "manim" for relevance
            if not search_query.lower().startswith('manim'):
                search_query = f"manim {search_query}"
                if len(search_query) > 400:
                    search_query = search_query[:397] + "..."
            
            if self.verbose:
                print(f"🤖 Gemini generated search query: {search_query}")
            
            return search_query
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Gemini query generation failed: {e}, using fallback")
            return self._generate_search_query_fallback(error_type, key_components, traceback)

    def _generate_search_query_fallback(self, error_type: str, key_components: List[str], traceback: str) -> str:
        """Generate a fallback search query when Gemini is not available"""
        base_query = f"manim {error_type}"
        
        # Add key components in order of importance
        query_parts = [base_query]
        
        # Add most relevant components
        for component in key_components[:3]:  # Limit to top 3 components
            test_query = " ".join(query_parts + [component])
            if len(test_query) < 350:  # Leave room for additional context
                query_parts.append(component)
            else:
                break
        
        # Add specific context if space allows
        if "attribute" in traceback.lower() and len(" ".join(query_parts)) < 300:
            query_parts.append("method attribute")
        elif "import" in traceback.lower() and len(" ".join(query_parts)) < 300:
            query_parts.append("import error")
        elif "argument" in traceback.lower() and len(" ".join(query_parts)) < 300:
            query_parts.append("parameters arguments")
        
        final_query = " ".join(query_parts)
        
        # Ensure we're under the limit
        if len(final_query) > 400:
            final_query = final_query[:397] + "..."
            
        return final_query

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
                "source_type": self._classify_source(result.get("url", ""))
            }
            results["solutions"].append(solution)
        
        return results

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


# Helper function for easy integration
def search_error_solution(traceback: str, code_context: str = "", api_key: Optional[str] = None) -> Dict:
    """
    Convenient function to search for error solutions using Tavily.
    
    Args:
        traceback: Full error traceback
        code_context: Additional code context
        api_key: Tavily API key (optional)
        
    Returns:
        Dictionary with error analysis and solution suggestions
    """
    engine = TavilyErrorSearchEngine(api_key=api_key, verbose=True)
    return engine.get_error_resolution_suggestions(traceback, code_context) 