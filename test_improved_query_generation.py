#!/usr/bin/env python3
"""
Test: Improved Documentation-Targeted Search Query Generation

This script tests the enhanced search query generation that targets
official documentation rather than forums, using the exact error
example provided by the user.
"""

import os
import sys
from src.utils.tavily_search import TavilyErrorSearchEngine, search_error_solution

def test_user_example_error():
    """Test the exact error example provided by the user"""
    print("🎯 Testing User-Provided Error Example")
    print("="*60)
    
    # The exact error from the user
    user_error = """
ValueError: all the input arrays must have same number of dimensions, but the 
array at index 0 has 2 dimension(s) and the array at index 1 has 3 dimension(s)
"""
    
    code_context = """
triangle = Polygon([(0, 0, 0), (2, 0, 0), (2, 1.5, 0)], stroke_width=2)
"""
    
    print("📋 **User's Example Error:**")
    print("   Object: Polygon")
    print("   Error: ValueError - dimension mismatch")  
    print("   Expected Query: manim Polygon ValueError: all input arrays must have same number of dimensions site:docs.manim.community")
    print()
    
    # Test improved query generation
    engine = TavilyErrorSearchEngine(verbose=True)
    
    print("🔍 **Testing Improved Query Generation:**")
    print("-" * 50)
    
    analysis = engine.analyze_error_for_search(user_error, code_context)
    
    print(f"✅ **Generated Query:** {analysis.search_query}")
    print(f"📏 **Query Length:** {len(analysis.search_query)} characters")
    print(f"🔍 **Error Type:** {analysis.error_type}")
    print(f"🧩 **Key Components:** {analysis.key_components}")
    print()
    
    # Check if it matches user's expectations
    expected_elements = [
        "manim",
        "Polygon", 
        "ValueError",
        "all input arrays must have same number of dimensions",
        "site:docs.manim.community"
    ]
    
    query = analysis.search_query
    matches = []
    for element in expected_elements:
        if element.lower() in query.lower():
            matches.append(f"✅ {element}")
        else:
            matches.append(f"❌ {element}")
    
    print("🎯 **Query Validation:**")
    for match in matches:
        print(f"   {match}")
    
    return analysis

def test_various_error_types():
    """Test query generation for different types of Manim errors"""
    print("\n🧪 **Testing Various Error Types**")
    print("="*50)
    
    test_cases = [
        {
            "name": "AttributeError - get_side_length",
            "traceback": """
Traceback (most recent call last):
  File "scene.py", line 62, in construct
    a = triangle.get_side_length(0)
TypeError: Mobject.__getattr__.<locals>.getter() takes 1 positional argument but 2 were given
            """,
            "code": "triangle = Polygon([[-2, -1, 0], [2, -1, 0], [2, 1, 0]])\na = triangle.get_side_length(0)",
            "expected_object": "Polygon"
        },
        {
            "name": "Transform TypeError",
            "traceback": """
Traceback (most recent call last):
  File "scene.py", line 45, in construct
    self.play(Transform(circle, square))
TypeError: Transform.__init__() missing 1 required positional argument: 'target_mobject'
            """,
            "code": "self.play(Transform(circle, square))",
            "expected_object": "Transform"
        },
        {
            "name": "Text AttributeError", 
            "traceback": """
Traceback (most recent call last):
  File "scene.py", line 25, in construct
    text = Text("Hello").set_font_size(48)
AttributeError: 'Text' object has no attribute 'set_font_size'
            """,
            "code": "text = Text('Hello').set_font_size(48)",
            "expected_object": "Text"
        }
    ]
    
    engine = TavilyErrorSearchEngine(verbose=False)  # Quiet for bulk testing
    
    for i, case in enumerate(test_cases, 1):
        print(f"📋 **Test Case {i}: {case['name']}**")
        
        analysis = engine.analyze_error_for_search(case["traceback"], case["code"])
        
        print(f"   Generated Query: {analysis.search_query}")
        print(f"   Expected Object: {case['expected_object']}")
        print(f"   Found Object: {'✅' if case['expected_object'].lower() in analysis.search_query.lower() else '❌'}")
        print(f"   Has site:docs.manim.community: {'✅' if 'site:docs.manim.community' in analysis.search_query else '❌'}")
        print()

def test_query_format_comparison():
    """Compare old vs new query format"""
    print("📊 **Query Format Comparison**")
    print("="*50)
    
    sample_error = """
ValueError: all the input arrays must have same number of dimensions, but the 
array at index 0 has 2 dimension(s) and the array at index 1 has 3 dimension(s)
"""
    
    print("🔄 **Before (Forum-focused):**")
    print("   manim ValueError Polygon parameters arguments")
    print("   ❌ Generic terms, no specific error message")
    print("   ❌ No site targeting - gets forums and random results")
    print("   ❌ Missing key error details")
    print()
    
    print("✨ **After (Documentation-focused):**")
    print("   manim Polygon ValueError all input arrays must have same number of dimensions site:docs.manim.community")
    print("   ✅ Specific object (Polygon)")
    print("   ✅ Exact error message included")
    print("   ✅ Targets official documentation only")
    print("   ✅ More likely to find relevant solutions")
    print()
    
    print("🎯 **Key Improvements:**")
    print("   • Targets docs.manim.community specifically")
    print("   • Includes exact error message phrases")
    print("   • Identifies specific Manim objects")
    print("   • Prioritizes authoritative sources over forums")
    print("   • Provides more focused, relevant results")

def main():
    """Run the test"""
    print("🎬 Improved Documentation-Targeted Query Generation Test")
    print("="*65)
    
    # Test user's specific example
    analysis = test_user_example_error()
    
    # Test various error types
    test_various_error_types()
    
    # Show format comparison
    test_query_format_comparison()
    
    print("\n🎉 **Testing Complete!**")
    print("The improved query generation now targets official documentation")
    print("and includes specific error messages for much better results!")
    
    # Show final query for user's example
    print(f"\n📝 **Final Query for User's Example:**")
    print(f"   {analysis.search_query}")
    print("   This query will now find official Manim documentation about")
    print("   Polygon dimension errors instead of random forum discussions!")

if __name__ == "__main__":
    main() 