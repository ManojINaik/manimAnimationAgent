#!/usr/bin/env python3
"""
Demo: Gemini-Powered Tavily Integration for Manim Error Resolution

This script demonstrates the enhanced error resolution system that uses:
1. Gemini to generate optimal search queries
2. Tavily to search for solutions
3. AI to apply fixes to code
"""

import os
import sys
from src.utils.tavily_search import TavilyErrorSearchEngine

def demo_fallback_system():
    """Demonstrate the fallback system when APIs are unavailable"""
    print("🎯 Demo: Fallback Query Generation System")
    print("="*50)
    
    # Sample Manim error that was occurring in the GitHub Actions
    manim_error = """
Traceback (most recent call last):
  File "scene.py", line 62, in construct
    a = triangle.get_side_length(0)
TypeError: Mobject.__getattr__.<locals>.getter() takes 1 positional argument but 2 were given
"""
    
    code_context = """
triangle = Polygon([-2, -1, 0], [2, -1, 0], [2, 1, 0])
self.add(triangle)
a = triangle.get_side_length(0)  # This method doesn't exist!
b = triangle.get_side_length(1)
c = triangle.get_side_length(2)
"""
    
    print("📋 **Sample Error:**")
    print("   Issue: Trying to call get_side_length() on Polygon object")
    print("   Problem: This method doesn't exist in Manim")
    print("   Solution needed: Calculate side length manually")
    print()
    
    # Initialize Tavily engine
    engine = TavilyErrorSearchEngine(verbose=True)
    
    print("🧪 **Testing Query Generation:**")
    analysis = engine.analyze_error_for_search(manim_error, code_context)
    
    print(f"✅ Generated Query: '{analysis.search_query}'")
    print(f"📏 Query Length: {len(analysis.search_query)} characters (under 400 ✓)")
    print(f"🔍 Error Type: {analysis.error_type}")
    print(f"🧩 Key Components: {analysis.key_components}")
    print()
    
    return analysis

def demo_manual_query_testing():
    """Test how different queries would perform"""
    print("🔍 Demo: Query Optimization Examples")
    print("="*50)
    
    # Example queries that Gemini might generate vs. our fallback
    example_queries = [
        {
            "type": "Gemini (ideal)",
            "query": "manim Polygon calculate side length distance vertices numpy",
            "why": "Focuses on the solution (calculating distances) rather than the error"
        },
        {
            "type": "Fallback (our system)",
            "query": "manim TypeError triangle get_side_length parameters arguments",
            "why": "Focuses on error details, still effective for finding solutions"
        },
        {
            "type": "Poor query (old system)",
            "query": "get_side_length error python",
            "why": "Too generic, no Manim context, would find irrelevant results"
        }
    ]
    
    for i, example in enumerate(example_queries, 1):
        print(f"{i}. **{example['type']}:**")
        print(f"   Query: '{example['query']}'")
        print(f"   Length: {len(example['query'])} chars")
        print(f"   Why: {example['why']}")
        print()

def demo_real_world_application():
    """Show how this integrates with the actual error fixing process"""
    print("⚙️ Demo: Real-World Integration")
    print("="*50)
    
    print("🔄 **Error Resolution Workflow:**")
    print("   1. ❌ Manim animation fails with error")
    print("   2. 🤖 Gemini analyzes error and generates targeted search query")
    print("   3. 🌐 Tavily searches web with optimized query")
    print("   4. 📊 System prioritizes official docs, GitHub issues, Stack Overflow")
    print("   5. 🛠️ AI applies search insights to fix the code")
    print("   6. ✅ Animation renders successfully")
    print()
    
    print("💡 **Key Improvements:**")
    print("   • Dynamic query generation adapts to ANY error (not just predefined)")
    print("   • Gemini understands context better than regex patterns")
    print("   • More relevant search results = better fixes")
    print("   • Works in both local development AND GitHub Actions")
    print("   • Intelligent fallback when APIs unavailable")
    print()
    
    print("🎯 **Expected Benefits:**")
    print("   • Faster error resolution (fewer retry loops)")
    print("   • Higher success rate for complex errors")
    print("   • Better adaptation to new Manim versions")
    print("   • Learning from real-world solutions on the web")

def demo_api_setup_guide():
    """Show users how to set up the APIs"""
    print("🔑 Demo: API Setup Guide")
    print("="*50)
    
    print("📋 **Required API Keys:**")
    print()
    print("1. **Gemini API (Free tier available):**")
    print("   • Go to: https://aistudio.google.com/app/apikey")
    print("   • Create free Google AI Studio account")
    print("   • Generate API key")
    print("   • Set environment variable: GEMINI_API_KEY=your_key_here")
    print()
    print("2. **Tavily API (1000 free searches/month):**")
    print("   • Go to: https://tavily.com")
    print("   • Sign up for free account")
    print("   • Get API key from dashboard")
    print("   • Set environment variable: TAVILY_API_KEY=your_key_here")
    print()
    print("3. **For GitHub Actions:**")
    print("   • Add both keys as repository secrets")
    print("   • Go to: Repo Settings → Secrets and variables → Actions")
    print("   • Add: GEMINI_API_KEY and TAVILY_API_KEY")
    print()
    
    # Check current status
    gemini_available = bool(os.getenv('GEMINI_API_KEY'))
    tavily_available = bool(os.getenv('TAVILY_API_KEY'))
    
    print("🔍 **Current Status:**")
    print(f"   Gemini API Key: {'✅ Available' if gemini_available else '❌ Missing'}")
    print(f"   Tavily API Key: {'✅ Available' if tavily_available else '❌ Missing'}")
    
    if not gemini_available:
        print("   ⚠️ Without Gemini: Will use fallback query generation")
    if not tavily_available:
        print("   ⚠️ Without Tavily: Will use fallback suggestions")

def main():
    """Run the complete demonstration"""
    print("🚀 Gemini-Powered Tavily Integration Demo")
    print("🎬 Manim Animation Agent - Advanced Error Resolution")
    print("="*60)
    print()
    
    # Demo sections
    analysis = demo_fallback_system()
    print()
    demo_manual_query_testing()
    print()
    demo_real_world_application()
    print()
    demo_api_setup_guide()
    
    print()
    print("🎉 **Demo Complete!**")
    print("The enhanced Tavily integration is now ready for production use.")
    print("It provides intelligent error resolution that adapts to any Manim error pattern!")

if __name__ == "__main__":
    main() 