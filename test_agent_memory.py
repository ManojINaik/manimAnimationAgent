"""
Test script for Agent Memory functionality using Mem0.

This script tests the self-improving capabilities of the TheoremExplainAgent
by simulating error-fix cycles and verifying memory storage/retrieval.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append('src')

def test_agent_memory():
    """Test the basic agent memory functionality."""
    print("Testing Agent Memory Functionality...")
    
    try:
        from src.core.agent_memory import AgentMemory
        
        # Initialize agent memory
        print("Initializing agent memory...")
        memory = AgentMemory(agent_id="test-agent")
        
        if not memory.enabled:
            print("❌ Agent memory not enabled. Check Mem0 API key.")
            return False
        
        print("✅ Agent memory initialized successfully")
        
        # Test storing an error-fix pattern
        print("\nTesting error-fix storage...")
        success = memory.store_error_fix(
            error_message="'Circle' object has no attribute 'animate'",
            original_code="circle = Circle()\nself.play(circle.animate.shift(UP))",
            fixed_code="circle = Circle()\nself.play(circle.animate.shift(UP))",
            topic="geometry",
            scene_type="animation",
            fix_method="test"
        )
        
        if success:
            print("✅ Successfully stored error-fix pattern")
        else:
            print("❌ Failed to store error-fix pattern")
            return False
        
        # Test searching for similar fixes
        print("\nTesting similar fixes search...")
        similar_fixes = memory.search_similar_fixes(
            error_message="Circle object attribute error",
            code_context="circle = Circle()",
            topic="geometry",
            scene_type="animation"
        )
        
        print(f"✅ Found {len(similar_fixes)} similar fixes")
        
        # Test storing successful generation
        print("\nTesting successful generation storage...")
        success = memory.store_successful_generation(
            task_description="Create animated circle",
            generated_code="circle = Circle()\nself.play(Create(circle))",
            topic="geometry",
            scene_type="animation"
        )
        
        if success:
            print("✅ Successfully stored successful generation")
        else:
            print("❌ Failed to store successful generation")
            return False
        
        # Test getting preventive examples
        print("\nTesting preventive examples retrieval...")
        examples = memory.get_preventive_examples(
            task_description="animate geometric shapes",
            topic="geometry",
            scene_type="animation"
        )
        
        print(f"✅ Retrieved {len(examples)} preventive examples")
        
        # Test memory stats
        print("\nTesting memory statistics...")
        stats = memory.get_memory_stats()
        print(f"✅ Memory stats: {stats}")
        
        print("\n🎉 All agent memory tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure mem0ai is installed: pip install mem0ai")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_code_generator_integration():
    """Test the integration with CodeGenerator."""
    print("\n" + "="*50)
    print("Testing CodeGenerator Integration...")
    
    try:
        # Mock the required components
        class MockModel:
            def __call__(self, *args, **kwargs):
                return "```python\nfrom manim import *\nclass TestScene(Scene):\n    def construct(self):\n        pass\n```"
        
        from src.core.code_generator import CodeGenerator
        
        # Initialize CodeGenerator with agent memory
        print("Initializing CodeGenerator with agent memory...")
        generator = CodeGenerator(
            scene_model=MockModel(),
            helper_model=MockModel(),
            use_agent_memory=True,
            session_id="test-session"
        )
        
        if generator.use_agent_memory:
            print("✅ CodeGenerator initialized with agent memory")
        else:
            print("❌ CodeGenerator agent memory not enabled")
            return False
        
        # Test scene type inference
        print("\nTesting scene type inference...")
        scene_type = generator._infer_scene_type("Create a graph showing a function")
        print(f"✅ Inferred scene type: {scene_type}")
        
        # Test error fixing with memory
        print("\nTesting error fixing with memory integration...")
        fixed_code = generator.fix_code_errors(
            implementation_plan="Create a simple animation",
            code="from manim import *\nclass TestScene(Scene):\n    def construct(self):\n        circle = Circle()\n        self.play(circle.bad_method())",
            error="AttributeError: 'Circle' object has no attribute 'bad_method'",
            scene_trace_id="test-trace",
            topic="geometry",
            scene_number=1,
            session_id="test-session"
        )
        
        if fixed_code:
            print("✅ Successfully fixed code with memory integration")
        else:
            print("❌ Failed to fix code")
            return False
        
        print("\n🎉 CodeGenerator integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Agent Memory Tests...")
    print("="*50)
    
    # Test basic memory functionality
    memory_test_passed = test_agent_memory()
    
    # Test integration with CodeGenerator
    integration_test_passed = test_code_generator_integration()
    
    print("\n" + "="*50)
    print("🏁 Test Results Summary:")
    print(f"Memory Tests: {'✅ PASSED' if memory_test_passed else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")
    
    if memory_test_passed and integration_test_passed:
        print("\n🎉 All tests passed! Self-improving agent is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.") 