#!/usr/bin/env python3
"""
manimAnimationAgent - Gradio Interface for Hugging Face Spaces
A web interface for generating educational videos explaining mathematical theorems and concepts.
"""

import os
import sys
import json
import traceback
import tempfile
import shutil
import asyncio
import threading
import time
import random
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import gradio as gr
import zipfile

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Environment setup for Hugging Face Spaces
SPACE_ID = os.getenv("SPACE_ID", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Global variables
video_generator = None
generation_status = {}
CAN_IMPORT_DEPENDENCIES = True

def setup_environment():
    """Setup environment variables and dependencies for Hugging Face Spaces."""
    print("🚀 Setting up manimAnimationAgent...")
    
    # Check for API keys
    gemini_keys = os.getenv("GEMINI_API_KEY", "")
    if gemini_keys:
        key_count = len([k.strip() for k in gemini_keys.split(',') if k.strip()])
        print(f"✅ Found {key_count} Gemini API key(s)")
    else:
        print("⚠️ No Gemini API keys found - running in demo mode")
    
    # Check for optional environment variables
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
    if elevenlabs_key:
        print("✅ ElevenLabs API key found")
    else:
        print("⚠️ No ElevenLabs API key found - TTS will be disabled")
    
    return True

def initialize_video_generator():
    """Initialize the video generator with error handling."""
    global video_generator, CAN_IMPORT_DEPENDENCIES
    
    try:
        if DEMO_MODE:
            return "✅ Demo mode enabled - Video generation will be simulated"
        
        # Try importing dependencies
        from generate_video import VideoGenerator
        from mllm_tools.litellm import LiteLLMWrapper
        
        # Initialize models
        planner_model = LiteLLMWrapper(
            model_name="gemini/gemini-2.0-flash",
            temperature=0.7,
            print_cost=True,
            verbose=False,
            use_langfuse=False
        )
        
        helper_model = LiteLLMWrapper(
            model_name="gemini/gemini-2.0-flash",
            temperature=0.7,
            print_cost=True,
            verbose=False,
            use_langfuse=False
        )
        
        video_generator = VideoGenerator(
            planner_model=planner_model,
            helper_model=helper_model,
            scene_model=helper_model,
            output_dir="output",
            use_rag=False,
            use_context_learning=False,
            use_visual_fix_code=False,
            verbose=False
        )
        
        return "✅ Video generator initialized successfully with Gemini models"
        
    except ImportError as e:
        CAN_IMPORT_DEPENDENCIES = False
        print(f"Import error: {e}")
        return f"⚠️ Missing dependencies - running in demo mode: {str(e)}"
    except Exception as e:
        CAN_IMPORT_DEPENDENCIES = False
        print(f"Initialization error: {e}")
        return f"⚠️ Failed to initialize - running in demo mode: {str(e)}"

def simulate_video_generation(topic: str, context: str, max_scenes: int, progress_callback=None) -> Dict[str, Any]:
    """Simulate video generation for demo purposes with progress updates."""
    stages = [
        ("🔍 Analyzing topic and context", 10),
        ("📝 Planning video structure", 25),
        ("🎬 Generating scene outlines", 45),
        ("✨ Creating animations", 70),
        ("🎥 Rendering videos", 85),
        ("🔗 Combining scenes", 95),
        ("✅ Finalizing output", 100)
    ]
    
    results = []
    for stage, progress in stages:
        if progress_callback:
            progress_callback(progress, stage)
        time.sleep(random.uniform(0.2, 0.8))  # Simulate processing time
        results.append(f"• {stage}")
    
    return {
        "success": True,
        "message": f"Demo video generated for topic: {topic}",
        "scenes_created": max_scenes,
        "total_duration": f"{max_scenes * 45} seconds",
        "processing_steps": results,
        "output_files": [
            f"scene_{i+1}.mp4" for i in range(max_scenes)
        ] + ["combined_video.mp4"],
        "demo_note": "This is a simulated result for demonstration purposes."
    }

async def generate_video_async(topic: str, context: str, max_scenes: int, progress_callback=None):
    """Asynchronously generate video with progress updates."""
    global video_generator
    
    if not topic.strip():
        return {"success": False, "error": "Please enter a topic to explain"}
    
    try:
        if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES:
            return simulate_video_generation(topic, context, max_scenes, progress_callback)
        
        # Real video generation
        if progress_callback:
            progress_callback(10, "🚀 Starting video generation...")
        
        result = await video_generator.generate_video_pipeline(
            topic=topic,
            description=context,
            max_retries=3,
            only_plan=False,
            specific_scenes=list(range(1, max_scenes + 1)),
            only_render=False,
            only_combine=False
        )
        
        if progress_callback:
            progress_callback(100, "✅ Video generation completed!")
        
        return {
            "success": True,
            "message": f"Video generated successfully for topic: {topic}",
            "result": result
        }
        
    except Exception as e:
        error_msg = f"Error during generation: {str(e)}"
        print(f"Generation error: {traceback.format_exc()}")
        return {"success": False, "error": error_msg}

def generate_video_gradio(topic: str, context: str, max_scenes: int, progress=gr.Progress()) -> Tuple[str, str]:
    """Main function called by Gradio interface."""
    def progress_callback(percent, message):
        progress(percent / 100, desc=message)
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            generate_video_async(topic, context, max_scenes, progress_callback)
        )
    finally:
        loop.close()
    
    if result["success"]:
        output = f"""# 🎓 Video Generation Complete!

## 📋 Generation Details
- **Topic:** {topic}
- **Context:** {context if context else "None provided"}
- **Max Scenes:** {max_scenes}

## ✅ Results
{result["message"]}

"""
        
        if "processing_steps" in result:
            output += "## 🔄 Processing Steps\n"
            for step in result["processing_steps"]:
                output += f"{step}\n"
            output += "\n"
        
        if "output_files" in result:
            output += "## 📁 Generated Files\n"
            for file in result["output_files"]:
                output += f"• {file}\n"
            output += "\n"
        
        if "demo_note" in result:
            output += f"## ⚠️ Demo Mode\n{result['demo_note']}\n\n"
        
        status = "🎮 Demo mode - Simulation completed successfully" if DEMO_MODE else "✅ Video generation completed successfully"
        
        return output, status
    
    else:
        error_output = f"""# ❌ Generation Failed

## Error Details
{result.get("error", "Unknown error occurred")}

## 💡 Troubleshooting Tips
1. **Check your topic**: Make sure it's a valid mathematical or scientific concept
2. **Verify API keys**: Ensure your Gemini API keys are properly set
3. **Try simpler topics**: Start with basic concepts like "velocity" or "pythagorean theorem"
4. **Check context**: Make sure additional context is relevant and not too complex

## 🔧 Common Issues
- **API Rate Limits**: If using multiple API keys, the system will automatically rotate between them
- **Complex Topics**: Very advanced topics might require more specific context
- **Long Context**: Try shortening the additional context if it's very long
"""
        return error_output, "❌ Generation failed - Check the output for details"

def get_example_topics():
    """Get example topics with contexts for the interface.""" 
    return [
        ["Velocity", "Explain velocity in physics with detailed examples and real-world applications"],
        ["Pythagorean Theorem", "Explain with visual proof and practical applications in construction and navigation"],
        ["Derivatives", "Explain derivatives in calculus with geometric interpretation and rate of change examples"],
        ["Newton's Laws", "Explain Newton's three laws of motion with everyday examples and demonstrations"],
        ["Quadratic Formula", "Derive the quadratic formula step by step and show how to apply it"],
        ["Logarithms", "Explain logarithms, their properties, and applications in science and engineering"],
        ["Probability", "Explain basic probability concepts with coin flips, dice, and card examples"],
        ["Trigonometry", "Explain sine, cosine, and tangent functions with unit circle visualization"],
        ["Limits", "Explain the concept of limits in calculus with graphical examples"],
        ["Chemical Bonding", "Explain ionic, covalent, and metallic bonding with molecular examples"]
    ]

def create_interface():
    """Create and configure the Gradio interface."""
    
    setup_status = setup_environment()
    init_status = initialize_video_generator()
    
    custom_css = """
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .status-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #007bff;
        background-color: #f8f9fa;
    }
    .demo-warning {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        border: none;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        color: #2d3436;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    """
    
    with gr.Blocks(
        title="🎓 manimAnimationAgent",
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="purple"),
        css=custom_css
    ) as demo:
        
        gr.HTML(f"""
        <div class="main-header">
            <h1>🎓 manimAnimationAgent</h1>
            <p style="font-size: 18px; margin: 10px 0;">Generate educational videos explaining mathematical theorems and concepts using AI</p>
            <p style="font-size: 14px; opacity: 0.9;">Powered by Gemini 2.0 Flash with automatic API key rotation</p>
        </div>
        """)
        
        if DEMO_MODE:
            gr.HTML("""
            <div class="demo-warning">
                <h3>⚠️ Demo Mode Active</h3>
                <p>This is a demonstration version. To enable full video generation:</p>
                <ul>
                    <li>Set your <code>GEMINI_API_KEY</code> in the Secrets tab (supports comma-separated multiple keys)</li>
                    <li>Optionally set <code>ELEVENLABS_API_KEY</code> for voice narration</li>
                    <li>Set <code>DEMO_MODE=false</code> in environment variables</li>
                </ul>
            </div>
            """)
        
        with gr.Row():
            with gr.Column(scale=3):
                gr.HTML("<h3>📝 Video Generation Settings</h3>")
                
                topic_input = gr.Textbox(
                    label="🎯 Topic to Explain",
                    placeholder="Enter the topic you want to explain (e.g., 'velocity', 'pythagorean theorem')",
                    lines=1,
                    max_lines=2
                )
                
                context_input = gr.Textbox(
                    label="📝 Additional Context (Optional)",
                    placeholder="Provide specific requirements, difficulty level, or focus areas for the explanation",
                    lines=3,
                    max_lines=5
                )
                
                max_scenes_slider = gr.Slider(
                    label="🎬 Maximum Number of Scenes",
                    minimum=1,
                    maximum=6,
                    value=3,
                    step=1,
                    info="More scenes = longer video but higher cost"
                )
                
                generate_btn = gr.Button(
                    "🚀 Generate Video",
                    variant="primary",
                    size="lg"
                )
                
            with gr.Column(scale=2):
                gr.HTML("<h3>📊 Status & Information</h3>")
                
                status_display = gr.Textbox(
                    label="🔄 Current Status",
                    value=init_status,
                    interactive=False,
                    lines=2
                )
                
                gr.HTML("""
                <div class="status-box">
                    <h4>🔑 API Key Setup for Hugging Face Spaces</h4>
                    <p><strong>Multiple Gemini Keys (Recommended):</strong></p>
                    <code>GEMINI_API_KEY=key1,key2,key3,key4</code>
                    <p><strong>Single Key:</strong></p>
                    <code>GEMINI_API_KEY=your_single_api_key</code>
                    <p><strong>Optional TTS:</strong></p>
                    <code>ELEVENLABS_API_KEY=your_elevenlabs_key</code>
                    <br><br>
                    <small>💡 The system automatically rotates between multiple keys to avoid rate limits</small>
                </div>
                """)
        
        examples = gr.Examples(
            examples=get_example_topics(),
            inputs=[topic_input, context_input],
            label="📚 Example Topics & Contexts"
        )
        
        output_display = gr.Markdown(
            label="📋 Generation Results",
            value="Ready to generate your first video! Enter a topic above and click 'Generate Video'."
        )
        
        generate_btn.click(
            fn=generate_video_gradio,
            inputs=[topic_input, context_input, max_scenes_slider],
            outputs=[output_display, status_display],
            show_progress=True
        )
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid #eee;">
            <p>🎓 <strong>manimAnimationAgent</strong></p>
            <p>Built with ❤️ using Gradio, Gemini 2.0 Flash, and Manim</p>
            <p style="font-size: 12px; color: #666;">
                For support and updates, visit the project repository • 
                Rate limits automatically managed with multi-key rotation
            </p>
        </div>
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_tips=True,
        enable_queue=True,
        max_threads=10
    ) 