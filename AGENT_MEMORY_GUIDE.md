# Self-Improving Agent with Mem0 Integration

## Overview

The TheoremExplainAgent now includes **self-improving capabilities** using Mem0 for learning from mistakes. This feature allows the agent to:

1. **Remember Error-Fix Patterns**: Store successful fixes for coding errors
2. **Prevent Repeated Mistakes**: Use past solutions to avoid similar errors
3. **Improve Code Generation**: Include successful patterns as examples in new generation

## Features

### 🧠 Agent Memory System
- **Persistent Memory**: Uses Mem0 cloud service to store long-term memory
- **Pattern Recognition**: Groups similar errors using intelligent hashing
- **Context-Aware**: Considers topic, scene type, and error context
- **Multiple Fix Methods**: Tracks auto-fixes, LLM fixes, and manual corrections

### 🔄 Self-Learning Loop
1. **Code Generation**: Generate Manim code with preventive examples
2. **Error Detection**: When errors occur, search memory for similar fixes
3. **Error Fixing**: Apply fixes and store successful patterns
4. **Memory Storage**: Save error-fix pairs for future reference
5. **Pattern Retrieval**: Use stored patterns in future generations

## Configuration

### Environment Setup
The agent memory system requires a Mem0 API key in your `.env` file:

```env
# Mem0 API key for agent memory
mem0_api_key=your_mem0_api_key_here
```

### Installation
```bash
pip install mem0ai
```

### CodeGenerator Configuration
```python
from src.core.code_generator import CodeGenerator

generator = CodeGenerator(
    scene_model=your_model,
    helper_model=your_helper_model,
    use_agent_memory=True,  # Enable self-improving capabilities
    session_id="your_session_id"  # Optional: for session-specific memory
)
```

## How It Works

### 1. Error Pattern Storage

When the `fix_code_errors` method is called, the system:

- **Detects Error Type**: Categorizes the error and code context
- **Applies Fix**: Uses auto-fix rules or LLM-based fixing
- **Stores Pattern**: Saves the error-fix pair in Mem0 with metadata:
  ```python
  {
      "error_message": "AttributeError: 'Circle' object has no attribute 'bad_method'",
      "original_code": "circle = Circle()\nself.play(circle.bad_method())",
      "fixed_code": "circle = Circle()\nself.play(Create(circle))",
      "topic": "geometry",
      "scene_type": "animation",
      "fix_method": "llm"
  }
  ```

### 2. Preventive Code Generation

Before generating new code, the system:

- **Infers Scene Type**: Determines if it's a graph, animation, formula, etc.
- **Searches Memory**: Looks for successful patterns for similar tasks
- **Includes Examples**: Adds preventive examples to the generation prompt

### 3. Smart Error Fixing

When fixing errors, the system:

- **Searches Similar Fixes**: Finds previously solved similar errors
- **Applies Best Practices**: Uses successful patterns from memory
- **Updates Memory**: Stores new successful fixes for future use

## Scene Type Classification

The system automatically classifies scenes based on implementation text:

- **Graph**: Keywords like "graph", "plot", "chart", "axis"
- **Formula**: Keywords like "formula", "equation", "math" 
- **Animation**: Keywords like "animate", "move", "transform"
- **Text**: Keywords like "text", "title", "label", "write"
- **Geometry**: Keywords like "shape", "circle", "square"
- **3D**: Keywords like "3d", "cube", "sphere"
- **General**: Default for unclassified scenes

## API Reference

### AgentMemory Class

#### `store_error_fix(error_message, original_code, fixed_code, topic, scene_type, fix_method)`
Store an error-fix pattern in memory.

**Parameters:**
- `error_message` (str): The error that occurred
- `original_code` (str): Code that caused the error
- `fixed_code` (str): The corrected code
- `topic` (str): Subject area (e.g., "calculus", "physics")
- `scene_type` (str): Type of scene (e.g., "graph", "animation")
- `fix_method` (str): How fix was applied ("auto", "llm", "manual")

#### `search_similar_fixes(error_message, code_context, topic, scene_type, limit)`
Search for similar error-fix patterns.

**Returns:** List of similar error patterns from memory

#### `get_preventive_examples(task_description, topic, scene_type, limit)`
Get successful code examples for preventing errors.

**Returns:** List of (problem_description, solution_code) tuples

#### `store_successful_generation(task_description, generated_code, topic, scene_type)`
Store a successful code generation pattern.

#### `get_memory_stats()`
Get statistics about stored memories.

**Returns:** Dictionary with memory statistics

## Testing

Run the test script to verify functionality:

```bash
python test_agent_memory.py
```

This will test:
- Basic memory operations
- Error-fix storage and retrieval
- Integration with CodeGenerator
- Memory statistics

## Benefits

### 🚀 Improved Code Quality
- **Fewer Repeated Errors**: Learns from past mistakes
- **Better Code Patterns**: Uses proven successful approaches
- **Faster Error Resolution**: Applies known fixes automatically

### 📈 Performance Enhancement
- **Reduced Generation Time**: Prevents errors before they occur
- **Higher Success Rate**: Uses battle-tested code patterns
- **Intelligent Fixes**: Context-aware error resolution

### 🎯 Domain Adaptation
- **Subject-Specific Learning**: Remembers patterns for different topics
- **Scene-Type Optimization**: Tailored fixes for different scene types
- **Progressive Improvement**: Gets better with more usage

## Example Usage

```python
# Initialize with memory enabled
generator = CodeGenerator(
    scene_model=gemini_model,
    helper_model=gemini_helper,
    use_agent_memory=True,
    session_id="math_tutorial_session"
)

# Generate code (automatically includes preventive examples)
code, response = generator.generate_manim_code(
    topic="calculus",
    description="Show derivative visualization",
    scene_outline="Graph function and its derivative",
    scene_implementation="Create function graph with tangent line animation",
    scene_number=1
)

# If errors occur, they'll be fixed and stored for future reference
if error_detected:
    fixed_code = generator.fix_code_errors(
        implementation_plan=scene_implementation,
        code=problematic_code,
        error=error_message,
        scene_trace_id="scene_1",
        topic="calculus",
        scene_number=1,
        session_id="math_tutorial_session"
    )
```

## Monitoring and Analytics

### Memory Statistics
Check memory usage and effectiveness:

```python
stats = generator.agent_memory.get_memory_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"Error fixes: {stats['error_fixes']}")
print(f"Successful generations: {stats['successful_generations']}")
```

### Mem0 Dashboard
Monitor memory operations on the Mem0 platform dashboard to track:
- Memory creation patterns
- Search frequency
- Error fix success rates
- Agent learning progress

## Troubleshooting

### Common Issues

1. **Memory Not Enabled**
   - Check Mem0 API key in `.env` file
   - Verify `mem0ai` package installation
   - Ensure `use_agent_memory=True` in CodeGenerator

2. **No Similar Fixes Found**
   - This is normal for new error types
   - System will improve as it encounters more errors
   - Consider manually adding common patterns

3. **Memory Storage Failures**
   - Check internet connection (Mem0 is cloud-based)
   - Verify API key validity
   - Check Mem0 service status

4. **Metadata Size Errors (Fixed in v1.1)**
   - **Issue**: "Metadata size is too large" errors when storing code
   - **Solution**: Implemented automatic code truncation to fit Mem0's 2000 character limit
   - **Details**: Long code snippets are automatically truncated while preserving essential patterns

### Best Practices

1. **Use Descriptive Topics**: Helps with pattern matching
2. **Consistent Scene Types**: Improves classification accuracy
3. **Regular Testing**: Run test script to verify functionality
4. **Monitor Memory Growth**: Check stats periodically

## Future Enhancements

Planned improvements include:
- **Confidence Scoring**: Rate fix reliability
- **Collaborative Learning**: Share patterns across agents
- **Advanced Analytics**: Detailed performance metrics
- **Custom Memory Models**: Domain-specific memory optimization

---

**Note**: This feature requires an active Mem0 API key and internet connection. The system gracefully degrades to standard functionality if memory is unavailable. 