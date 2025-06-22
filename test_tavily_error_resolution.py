#!/usr/bin/env python3
"""
Test script for Gemini-powered Tavily Error Resolution

This script tests the enhanced Tavily integration that uses Gemini to 
generate optimal search queries for Manim errors.
"""

import os
import sys
from src.utils.tavily_search import TavilyErrorSearchEngine, search_error_solution

def test_gemini_query_generation():
    """Test Gemini-based search query generation"""
    print("🧪 Testing Gemini-powered Search Query Generation\n")
    
    # Initialize Tavily engine
    engine = TavilyErrorSearchEngine(verbose=True)
    
    # Test cases - common Manim errors
    test_cases = [
        {
            "name": "get_side_length AttributeError",
            "traceback": """
Traceback (most recent call last):
  File "scene.py", line 62, in construct
    a = triangle.get_side_length(0)
TypeError: Mobject.__getattr__.<locals>.getter() takes 1 positional argument but 2 were given
            """,
            "code_context": "triangle = Polygon([-2, -1, 0], [2, -1, 0], [2, 1, 0])\na = triangle.get_side_length(0)"
        },
        {
            "name": "Angle constructor error", 
            "traceback": """
Traceback (most recent call last):
  File "scene.py", line 71, in construct
    angle = Angle(triangle.get_vertices()[0], triangle.get_vertices()[1], triangle.get_vertices()[2], radius=0.5)
TypeError: Angle.__init__() got multiple values for argument 'radius'
            """,
            "code_context": "angle = Angle(triangle.get_vertices()[0], triangle.get_vertices()[1], triangle.get_vertices()[2], radius=0.5)"
        },
        {
            "name": "Point constructor error",
            "traceback": """
Traceback (most recent call last):
  File "scene.py", line 65, in construct  
    triangle = Polygon(Point(-2, -1, 0), Point(2, -1, 0), Point(2, 1, 0))
TypeError: Point.__init__() takes from 1 to 3 positional arguments but 4 were given
            """,
            "code_context": "triangle = Polygon(Point(-2, -1, 0), Point(2, -1, 0), Point(2, 1, 0))"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Test Case {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            # Analyze error and generate search query with Gemini
            analysis = engine.analyze_error_for_search(
                test_case["traceback"], 
                test_case["code_context"]
            )
            
            print(f"✅ Generated Query: {analysis.search_query}")
            print(f"📏 Query Length: {len(analysis.search_query)} chars")
            print(f"🔍 Error Type: {analysis.error_type}")
            print(f"🧩 Key Components: {analysis.key_components}")
            
            # Test Tavily search with generated query
            if engine.is_available():
                print("\n🌐 Testing Tavily search...")
                search_results = engine.search_for_solution(analysis)
                
                if search_results.get("available", False):
                    solutions = search_results.get("solutions", [])
                    print(f"📊 Found {len(solutions)} solutions")
                    
                    for j, solution in enumerate(solutions[:2], 1):
                        print(f"   {j}. {solution.get('title', 'No title')}")
                        print(f"      Source: {solution.get('source_type', 'unknown')}")
                        print(f"      Score: {solution.get('relevance_score', 0):.2f}")
                else:
                    print("❌ Tavily search failed")
            else:
                print("⚠️ Tavily not available - testing query generation only")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("\n" + "="*50 + "\n")

def test_complete_workflow():
    """Test the complete error resolution workflow"""
    print("🔄 Testing Complete Error Resolution Workflow\n")
    
    sample_error = """
Traceback (most recent call last):
  File "/path/to/scene.py", line 40, in construct
    triangle = Polygon([-2, -1, 0], [2, -1, 0], [2, 1, 0])
    a = triangle.get_side_length(0)
TypeError: Mobject.__getattr__.<locals>.getter() takes 1 positional argument but 2 were given
    """
    
    sample_code = """
triangle = Polygon([-2, -1, 0], [2, -1, 0], [2, 1, 0])
self.add(triangle)
a = triangle.get_side_length(0)  # This line causes the error
"""
    
    try:
        print("🚀 Running complete error resolution...")
        result = search_error_solution(sample_error, sample_code)
        
        print("📊 Resolution Results:")
        print(f"   Error Type: {result['error_analysis'].error_type}")
        print(f"   Search Query: {result['error_analysis'].search_query}")
        print(f"   Solutions Found: {len(result['search_results'].get('solutions', []))}")
        print(f"   Actionable Suggestions: {len(result['actionable_suggestions'])}")
        
        print("\n💡 Top Suggestions:")
        for i, suggestion in enumerate(result['actionable_suggestions'][:3], 1):
            print(f"   {i}. {suggestion}")
            
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")

def test_api_keys():
    """Test API key availability"""
    print("🔑 Testing API Key Configuration\n")
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')
    
    print(f"Gemini API Key: {'✅ Available' if gemini_key else '❌ Missing'}")
    print(f"Tavily API Key: {'✅ Available' if tavily_key else '❌ Missing'}")
    
    if not gemini_key:
        print("⚠️ Set GEMINI_API_KEY environment variable for Gemini search query generation")
    if not tavily_key:
        print("⚠️ Set TAVILY_API_KEY environment variable for web search")
    
    return bool(gemini_key), bool(tavily_key)

def main():
    """Run all tests"""
    print("🎯 Gemini-Powered Tavily Error Resolution Test Suite")
    print("=" * 60)
    
    # Test API keys first
    has_gemini, has_tavily = test_api_keys()
    print()
    
    if has_gemini:
        # Test Gemini query generation
        test_gemini_query_generation()
        
        # Test complete workflow
        test_complete_workflow()
    else:
        print("⚠️ Skipping tests - Gemini API key required for dynamic query generation")
        print("💡 The system will fall back to static query generation without Gemini")
    
    print("🏁 Test suite completed!")
    print("\n📝 Summary:")
    print("- Gemini generates optimal search queries dynamically")
    print("- Tavily searches with Gemini-optimized queries")
    print("- System provides intelligent fallback when APIs unavailable")
    print("- Error resolution now adapts to any Manim error pattern")

if __name__ == "__main__":
    main() 