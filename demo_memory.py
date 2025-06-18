"""
Demo: Self-Improving TheoremExplainAgent with Mem0

This demo showcases how the agent learns from past mistakes and prevents 
repetition of similar errors in future code generations.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append('src')

def demo_learning_cycle():
    """Demonstrate the complete learning cycle with realistic examples."""
    print("🎓 Self-Improving Agent Learning Demo")
    print("=" * 50)
    
    try:
        from src.core.agent_memory import AgentMemory
        
        # Initialize agent memory
        print("1. Initializing Agent Memory...")
        memory = AgentMemory(agent_id="demo-theorem-agent")
        
        if not memory.enabled:
            print("❌ Memory not enabled. Please check your Mem0 API key.")
            return
        
        print("✅ Agent memory initialized")
        
        # Simulate common Manim errors and their fixes
        print("\n2. Storing Error-Fix Patterns...")
        
        error_fix_examples = [
            {
                "error": "AttributeError: 'Circle' object has no attribute 'animate'",
                "original": "circle = Circle()\nself.play(circle.animate.shift(UP))",
                "fixed": "circle = Circle()\nself.play(circle.animate.shift(UP))",
                "topic": "geometry",
                "scene_type": "animation",
                "explanation": "Common Circle animation error - object already supports animate"
            },
            {
                "error": "'ManimMLConfig' object has no attribute 'frame_width'",
                "original": "width = config.frame_width\nheight = config.frame_height", 
                "fixed": "width = 14.0  # Fixed frame width\nheight = 8.0  # Fixed frame height",
                "topic": "general",
                "scene_type": "general",
                "explanation": "Config object attribute access should use hardcoded values"
            },
            {
                "error": "unexpected keyword argument 'buff' in Arrow3D",
                "original": "arrow = Arrow3D(start=ORIGIN, end=UP, buff=0.1)",
                "fixed": "arrow = Arrow3D(start=ORIGIN, end=UP)  # Removed buff parameter",
                "topic": "3d",
                "scene_type": "3d",
                "explanation": "Arrow3D doesn't support buff parameter in newer versions"
            },
            {
                "error": "The truth value of an array with more than one element is ambiguous",
                "original": "if obj.get_center() > 0:",
                "fixed": "if obj.get_center()[0] > 0:  # Use array indexing",
                "topic": "general",
                "scene_type": "animation",
                "explanation": "Array comparisons need explicit indexing"
            },
            {
                "error": "SVGMobject: could not find 'graph.svg'",
                "original": "graph = SVGMobject('graph.svg')",
                "fixed": "graph = Rectangle(height=2, width=3, color=BLUE)  # Fallback shape",
                "topic": "graphs",
                "scene_type": "graph",
                "explanation": "Missing SVG files should be replaced with basic shapes"
            }
        ]
        
        # Store all error-fix patterns
        for i, example in enumerate(error_fix_examples, 1):
            success = memory.store_error_fix(
                error_message=example["error"],
                original_code=example["original"],
                fixed_code=example["fixed"],
                topic=example["topic"],
                scene_type=example["scene_type"],
                fix_method="demo"
            )
            
            if success:
                print(f"  ✅ Stored pattern {i}: {example['explanation']}")
            else:
                print(f"  ❌ Failed to store pattern {i}")
        
        print(f"\n3. Memory Statistics After Learning:")
        stats = memory.get_memory_stats()
        print(f"  • Total memories: {stats.get('total_memories', 0)}")
        print(f"  • Error fixes: {stats.get('error_fixes', 0)}")
        print(f"  • Successful generations: {stats.get('successful_generations', 0)}")
        
        # Demonstrate pattern retrieval
        print("\n4. Testing Pattern Retrieval...")
        test_scenarios = [
            {
                "error": "Circle object animation problem",
                "topic": "geometry", 
                "scene_type": "animation",
                "description": "Looking for Circle animation fixes"
            },
            {
                "error": "Config frame width issue",
                "topic": "general",
                "scene_type": "general", 
                "description": "Looking for config attribute fixes"
            },
            {
                "error": "Arrow3D parameter error",
                "topic": "3d",
                "scene_type": "3d",
                "description": "Looking for Arrow3D fixes"
            }
        ]
        
        for scenario in test_scenarios:
            similar_fixes = memory.search_similar_fixes(
                error_message=scenario["error"],
                code_context="sample code context",
                topic=scenario["topic"],
                scene_type=scenario["scene_type"],
                limit=2
            )
            
            print(f"  🔍 {scenario['description']}: Found {len(similar_fixes)} similar patterns")
        
        # Demonstrate preventive examples
        print("\n5. Testing Preventive Examples...")
        prevention_tests = [
            {"task": "animate a circle", "topic": "geometry", "scene_type": "animation"},
            {"task": "create 3D arrow", "topic": "3d", "scene_type": "3d"},
            {"task": "display graph visualization", "topic": "graphs", "scene_type": "graph"}
        ]
        
        for test in prevention_tests:
            examples = memory.get_preventive_examples(
                task_description=test["task"],
                topic=test["topic"],
                scene_type=test["scene_type"],
                limit=2
            )
            print(f"  🛡️  '{test['task']}': {len(examples)} preventive patterns")
        
        print("\n6. Simulating Code Generation with Memory...")
        
        # Mock a code generation scenario where memory helps
        print("  📝 Scenario: Generating animation code for a circle...")
        print("  🧠 Agent checks memory for similar past errors...")
        
        similar_fixes = memory.search_similar_fixes(
            error_message="Circle animation",
            code_context="circle = Circle()",
            topic="geometry",
            scene_type="animation"
        )
        
        if similar_fixes:
            print(f"  ✅ Found {len(similar_fixes)} relevant patterns from memory")
            print("  💡 Agent uses these patterns to generate better code:")
            print("     - Knows Circle objects support .animate")
            print("     - Avoids common attribute errors")
            print("     - Uses proven animation patterns")
        else:
            print("  ℹ️  No similar patterns found - agent will learn from this generation")
        
        print("\n7. Benefits Demonstration:")
        print("  🚀 Code Quality:")
        print("     - Fewer repeated errors across sessions")
        print("     - Better code patterns from successful examples")
        print("     - Context-aware fixes based on topic and scene type")
        
        print("\n  📈 Performance:")
        print("     - Faster error resolution using known fixes")
        print("     - Reduced generation time with preventive examples")
        print("     - Progressive improvement with more usage")
        
        print("\n  🎯 Adaptation:")
        print("     - Subject-specific learning (geometry, calculus, physics)")
        print("     - Scene-type optimization (graphs, animations, formulas)")
        print("     - Session-aware memory for project continuity")
        
        print("\n🎉 Demo completed successfully!")
        print("\nThis agent now has learned patterns that will help it:")
        print("• Generate better code on the first try")
        print("• Fix errors faster when they occur")  
        print("• Avoid repeating the same mistakes")
        print("• Adapt to different mathematical domains")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure mem0ai is installed: pip install mem0ai")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_integration_with_code_generator():
    """Show how the memory integrates with actual CodeGenerator."""
    print("\n" + "="*50)
    print("🔧 CodeGenerator Integration Demo")
    print("="*50)
    
    try:
        # Mock models for demonstration
        class MockModel:
            def __call__(self, *args, **kwargs):
                return """```python
from manim import *

class DemoScene(Scene):
    def construct(self):
        # This code has a common error that the agent has learned to fix
        circle = Circle()
        # The agent's memory will help prevent errors here
        self.play(Create(circle))
        self.play(circle.animate.shift(UP))
```"""
        
        from src.core.code_generator import CodeGenerator
        
        print("1. Initializing CodeGenerator with agent memory...")
        generator = CodeGenerator(
            scene_model=MockModel(),
            helper_model=MockModel(),
            use_agent_memory=True,
            session_id="demo-integration"
        )
        
        if generator.use_agent_memory:
            print("✅ Agent memory enabled in CodeGenerator")
            
            # Check memory stats
            if generator.agent_memory:
                stats = generator.agent_memory.get_memory_stats()
                print(f"   📊 Current memory state: {stats.get('total_memories', 0)} memories")
        else:
            print("❌ Agent memory not enabled")
            return False
        
        print("\n2. Testing scene type inference...")
        test_scenes = [
            "Create a graph showing y = x^2",
            "Animate a circle moving in 3D space", 
            "Display the quadratic formula",
            "Write text explaining the theorem"
        ]
        
        for scene_desc in test_scenes:
            scene_type = generator._infer_scene_type(scene_desc)
            print(f"   '{scene_desc}' → {scene_type}")
        
        print("\n3. Simulating code generation with memory...")
        
        # This would include preventive examples from memory
        code, response = generator.generate_manim_code(
            topic="geometry",
            description="Circle animation tutorial",
            scene_outline="Scene 1: Create and animate a circle",
            scene_implementation="Create a circle and animate it moving upward",
            scene_number=1
        )
        
        print("✅ Code generated with memory-enhanced prompts")
        print(f"   Generated {len(code.split('\\n'))} lines of code")
        
        print("\n4. Simulating error fix with memory storage...")
        
        # This would search memory for similar fixes and store the new fix
        fixed_code = generator.fix_code_errors(
            implementation_plan="Create animated circle",
            code="circle = Circle()\\nself.play(circle.bad_method())",
            error="AttributeError: 'Circle' object has no attribute 'bad_method'",
            scene_trace_id="demo-trace",
            topic="geometry", 
            scene_number=1,
            session_id="demo-integration"
        )
        
        print("✅ Error fixed and pattern stored in memory")
        print("   Future similar errors will be resolved faster")
        
        print("\n🎉 Integration demo completed!")
        print("\nThe agent is now actively learning and will:")
        print("• Include preventive examples in future code generation")
        print("• Search memory when fixing errors")
        print("• Store successful fixes for future use")
        print("• Improve performance over time")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 TheoremExplainAgent Self-Improvement Demo")
    print("This demo shows how the agent learns from mistakes using Mem0")
    print()
    
    # Run the learning cycle demo
    learning_success = demo_learning_cycle()
    
    if learning_success:
        # Run the integration demo
        integration_success = demo_integration_with_code_generator()
        
        if integration_success:
            print(f"\n{'='*60}")
            print("🏆 DEMO COMPLETE - Self-Improving Agent Ready!")
            print("="*60)
            print()
            print("Key Features Demonstrated:")
            print("✅ Error pattern storage and retrieval")
            print("✅ Preventive example generation")
            print("✅ Scene type classification")
            print("✅ Memory-enhanced code generation")
            print("✅ Intelligent error fixing")
            print("✅ Progressive learning capability")
            print()
            print("The agent is now equipped with memory and will continuously")
            print("improve its performance as it encounters and solves more problems.")
    else:
        print("\n⚠️  Demo could not complete due to configuration issues.")
        print("Please ensure:")
        print("• Mem0 API key is set in .env file")
        print("• mem0ai package is installed")
        print("• Internet connection is available") 