#!/usr/bin/env python3
"""
manimAnimationAgent - Gradio Interface
A web interface for generating educational videos explaining mathematical theorems and concepts.
"""

import os
import sys
import json
import traceback
import tempfile
import shutil
from typing import Optional, List, Dict, Any
import gradio as gr
from pathlib import Path
import asyncio
import threading
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Demo mode flag - set to True for deployment environments with limited resources
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"  # Default to demo mode for HF Spaces

# Global variables for managing video generation
video_generator = None
generation_status = {}

# Flag to track if we can import all dependencies
CAN_IMPORT_DEPENDENCIES = True

def initialize_video_generator():
    """Initialize the video generator with default settings."""
    global video_generator, CAN_IMPORT_DEPENDENCIES
    try:
        if DEMO_MODE:
            return "✅ Demo mode - Video generator simulation enabled"
        
        if not CAN_IMPORT_DEPENDENCIES:
            return "⚠️ Running in fallback mode due to missing dependencies"
        
        from generate_video import VideoGenerator
        from src.config.config import Config
        
        video_generator = VideoGenerator(
            planner_model=Config.DEFAULT_PLANNER_MODEL,
            helper_model=Config.DEFAULT_HELPER_MODEL,
            scene_model=Config.DEFAULT_SCENE_MODEL,
            output_dir="output",
            verbose=Config.MODEL_VERBOSE
        )
        return "✅ Video generator initialized successfully"
    except Exception as e:
        CAN_IMPORT_DEPENDENCIES = False
        return f"❌ Failed to initialize video generator: {str(e)}\n\n🔧 Running in demo mode"

def simulate_video_generation(topic: str, context: str, max_scenes: int) -> Dict[str, Any]:
    """Simulate video generation for demo purposes."""
    import time
    import random
    
    # Simulate different stages
    stages = [
        ("Planning video structure", 20),
        ("Generating scene outlines", 40),
        ("Creating animations", 60),
        ("Rendering videos", 80),
        ("Finalizing output", 100)
    ]
    
    for stage, progress in stages:
        time.sleep(random.uniform(0.1, 0.3))  # Faster for demo
    
    return {
        "success": True,
        "message": f"Demo video generated for topic: {topic}",
        "scenes_created": max_scenes,
        "total_duration": "2.5 minutes",
        "demo_note": "This is a simulated result. In production, actual Manim videos would be generated."
    }

def generate_video_demo(topic: str, context: str = "", max_scenes: int = 3) -> str:
    """Generate a video explanation for the given topic (demo version)."""
    if not topic.strip():
        return "❌ Please enter a topic to explain"
    
    try:
        # Simulate video generation
        result = simulate_video_generation(topic, context, max_scenes)
        
        output = f"""🎓 **manimAnimationAgent**

**Topic:** {topic}
**Context:** {context if context else "None provided"}
**Max Scenes:** {max_scenes}

**✅ Demo Generation Complete!**

📊 **Results:**
- Scenes Created: {result['scenes_created']}
- Total Duration: {result['total_duration']}
- Status: {result['message']}

⚠️ **Demo Mode Note:**
{result['demo_note']}

🚀 **To enable full video generation:**
1. Set up API keys (GEMINI_API_KEY, etc.)
2. Install full dependencies (Manim, FFmpeg, etc.)
3. Set DEMO_MODE=false

📝 **Example topics to try:**
- Pythagorean Theorem
- Velocity in Physics
- Derivatives in Calculus
- Newton's Laws of Motion
"""
        return output
        
    except Exception as e:
        return f"❌ Error during generation: {str(e)}\n\nPlease try with a simpler topic."

def get_example_topics() -> List[List[str]]:
    """Get example topics for the interface."""
    return [
        ["Pythagorean Theorem", "Explain with visual proof and real-world applications"],
        ["Velocity", "Explain velocity in physics with detailed examples"],
        ["Derivatives", "Explain derivatives in calculus with geometric interpretation"],
        ["Newton's Laws", "Explain Newton's three laws of motion with examples"],
        ["Quadratic Formula", "Derive and explain the quadratic formula step by step"],
        ["Logarithms", "Explain logarithms and their properties with examples"],
        ["Probability", "Explain basic probability concepts with practical examples"],
        ["Trigonometry", "Explain basic trigonometric functions and their uses"]
    ]

# Create the main interface
with gr.Blocks(
    title="🎓 manimAnimationAgent",
    theme=gr.themes.Soft(),
    css="""
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .demo-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #856404;
    }
    """
) as demo:
    
    # Header
    gr.HTML(f"""
    <div class="main-header">
        <h1>🎓 manimAnimationAgent</h1>
        <p>Generate educational videos explaining mathematical theorems and concepts using AI</p>
        {'<div class="demo-warning">⚠️ <strong>Demo Mode Active</strong> - This is a simulation for demonstration purposes.</div>' if DEMO_MODE else ''}
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.HTML("<h3>📝 Video Generation Settings</h3>")
            
            # Topic input
            topic_input = gr.Textbox(
                label="Topic to Explain",
                placeholder="Enter the topic you want to explain (e.g., 'velocity', 'pythagorean theorem')",
                lines=1
            )
            
            # Context input
            context_input = gr.Textbox(
                label="Additional Context (Optional)",
                placeholder="Provide additional context or specific requirements for the explanation",
                lines=3
            )
            
            # Max scenes
            max_scenes_slider = gr.Slider(
                label="Maximum Number of Scenes",
                minimum=1,
                maximum=5,
                value=3,
                step=1
            )
            
            # Example topics
            gr.HTML("<h4>💡 Example Topics</h4>")
            examples = gr.Examples(
                examples=get_example_topics(),
                inputs=[topic_input, context_input]
            )
            
            # Generate button
            generate_btn = gr.Button(
                "🚀 Generate Educational Video",
                variant="primary",
                size="lg"
            )
    
        with gr.Column(scale=1):
            gr.HTML("<h3>📊 System Status</h3>")
            
            # Initialization status
            init_status = gr.Textbox(
                label="System Status",
                value="Click 'Initialize System' to check status",
                interactive=False,
                lines=3
            )
            init_btn = gr.Button("🔧 Initialize System")
            
            # Generation result
            gr.HTML("<h3>📋 Generation Results</h3>")
            result_display = gr.Textbox(
                label="Generation Output",
                lines=15,
                interactive=False
            )
    
    # Event handlers
    init_btn.click(
        fn=initialize_video_generator,
        outputs=init_status
    )
    
    generate_btn.click(
        fn=generate_video_demo,
        inputs=[topic_input, context_input, max_scenes_slider],
        outputs=result_display
    )

# Launch the interface if run directly
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 