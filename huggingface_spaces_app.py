#!/usr/bin/env python3
"""
manimAnimationAgent - Gradio Interface for Hugging Face Spaces
"""

import os
import sys
import json
import asyncio
import time
import random
from typing import Dict, Any, Tuple
from pathlib import Path
import gradio as gr

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Environment setup
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
video_generator = None
CAN_IMPORT_DEPENDENCIES = True

def setup_environment():
    """Setup environment for HF Spaces."""
    print("🚀 Setting up manimAnimationAgent...")
    
    gemini_keys = os.getenv("GEMINI_API_KEY", "")
    if gemini_keys:
        key_count = len([k.strip() for k in gemini_keys.split(',') if k.strip()])
        print(f"✅ Found {key_count} Gemini API key(s)")
        return True
    else:
        print("⚠️ No Gemini API keys found - running in demo mode")
        return False

def initialize_video_generator():
    """Initialize video generator."""
    global video_generator, CAN_IMPORT_DEPENDENCIES
    
    try:
        if DEMO_MODE:
            return "✅ Demo mode enabled - No heavy dependencies loaded"
        
        # Check if we have API keys before importing heavy dependencies
        gemini_keys = os.getenv("GEMINI_API_KEY", "")
        if not gemini_keys:
            return "⚠️ No API keys found - running in demo mode (prevents model downloads)"
        
        # Try to import but handle missing dependencies gracefully
        try:
            from generate_video import VideoGenerator
            from mllm_tools.litellm import LiteLLMWrapper
        except ImportError as import_err:
            print(f"Heavy dependencies not available: {import_err}")
            return "⚠️ Heavy dependencies not installed - using demo mode to prevent downloads"
        
        planner_model = LiteLLMWrapper(
            model_name="gemini/gemini-2.0-flash",
            temperature=0.7,
            print_cost=True,
            verbose=False,
            use_langfuse=False
        )
        
        video_generator = VideoGenerator(
            planner_model=planner_model,  
            helper_model=planner_model,
            scene_model=planner_model,
            output_dir="output",
            use_rag=False,
            use_context_learning=False,
            use_visual_fix_code=False,
            verbose=False
        )
        
        return "✅ Video generator initialized with full dependencies"
        
    except Exception as e:
        CAN_IMPORT_DEPENDENCIES = False
        print(f"Initialization error: {e}")
        return f"⚠️ Running in demo mode to prevent model downloads: {str(e)[:100]}..."

def simulate_video_generation(topic: str, context: str, max_scenes: int, progress_callback=None):
    """Simulate video generation."""
    stages = [
        ("🔍 Analyzing topic", 15),
        ("📝 Planning structure", 30),
        ("🎬 Generating scenes", 50),
        ("✨ Creating animations", 75),
        ("🎥 Rendering video", 90),
        ("✅ Finalizing", 100)
    ]
    
    results = []
    for stage, progress in stages:
        if progress_callback:
            progress_callback(progress, stage)
        time.sleep(random.uniform(0.3, 0.7))
        results.append(f"• {stage}")
    
    return {
        "success": True,
        "message": f"Demo video generated for: {topic}",
        "scenes_created": max_scenes,
        "processing_steps": results,
        "demo_note": "This is a simulation for demo purposes."
    }

async def generate_video_async(topic: str, context: str, max_scenes: int, progress_callback=None):
    """Generate video asynchronously."""
    global video_generator
    
    if not topic.strip():
        return {"success": False, "error": "Please enter a topic"}
    
    try:
        if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES:
            return simulate_video_generation(topic, context, max_scenes, progress_callback)
        
        if progress_callback:
            progress_callback(10, "🚀 Starting generation...")
        
        result = await video_generator.generate_video_pipeline(
            topic=topic,
            description=context,
            max_retries=3,
            only_plan=False,
            specific_scenes=list(range(1, max_scenes + 1))
        )
        
        if progress_callback:
            progress_callback(100, "✅ Completed!")
        
        return {"success": True, "message": f"Video generated for: {topic}", "result": result}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_video_gradio(topic: str, context: str, max_scenes: int, progress=gr.Progress()) -> Tuple[str, str]:
    """Main Gradio function."""
    def progress_callback(percent, message):
        progress(percent / 100, desc=message)
    
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

**Topic:** {topic}
**Context:** {context if context else "None"}
**Scenes:** {max_scenes}

## ✅ Result
{result["message"]}

"""
        if "processing_steps" in result:
            output += "## 🔄 Steps\n"
            for step in result["processing_steps"]:
                output += f"{step}\n"
        
        if "demo_note" in result:
            output += f"\n⚠️ **{result['demo_note']}**"
        
        status = "🎮 Demo completed" if DEMO_MODE else "✅ Generation completed"
        return output, status
    
    else:
        error_output = f"""# ❌ Generation Failed

{result.get("error", "Unknown error")}

## 💡 Tips
- Check topic validity
- Verify API keys
- Try simpler topics
"""
        return error_output, "❌ Failed"

def get_examples():
    """Example topics."""
    return [
        ["Velocity", "Physics concept with real-world examples"],
        ["Pythagorean Theorem", "Mathematical proof with applications"],
        ["Derivatives", "Calculus concept with geometric interpretation"],
        ["Newton's Laws", "Three laws of motion with demonstrations"],
        ["Quadratic Formula", "Step-by-step derivation and usage"]
    ]

def create_interface():
    """Create Gradio interface."""
    setup_environment()
    init_status = initialize_video_generator()
    
    with gr.Blocks(
        title="🎓 manimAnimationAgent",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
            <h1>🎓 manimAnimationAgent</h1>
            <p>Generate educational videos using AI</p>
        </div>
        """)
        
        if DEMO_MODE:
            gr.HTML("""
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>⚠️ Demo Mode - Preventing Model Downloads</h3>
                <p>This prevents automatic downloading of Kokoro and other heavy models.</p>
                <p>To enable full functionality:</p>
                <ul>
                    <li>Set <code>GEMINI_API_KEY</code> (supports comma-separated keys)</li>
                    <li>Set <code>DEMO_MODE=false</code></li>
                    <li>Install full dependencies (manim, manim-voiceover, etc.)</li>
                </ul>
                <p><strong>Note:</strong> Full mode requires ~2GB of model downloads.</p>
            </div>
            """)
        
        with gr.Row():
            with gr.Column():
                topic_input = gr.Textbox(
                    label="Topic",
                    placeholder="e.g., velocity, pythagorean theorem"
                )
                
                context_input = gr.Textbox(
                    label="Context (Optional)",
                    placeholder="Additional details or requirements",
                    lines=3
                )
                
                max_scenes_slider = gr.Slider(
                    label="Max Scenes",
                    minimum=1,
                    maximum=6,
                    value=3,
                    step=1
                )
                
                generate_btn = gr.Button("🚀 Generate Video", variant="primary")
                
            with gr.Column():
                status_display = gr.Textbox(
                    label="Status",
                    value=init_status,
                    interactive=False
                )
                
                gr.HTML("""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <h4>🔑 API Setup</h4>
                    <p><strong>Multiple keys:</strong></p>
                    <code>GEMINI_API_KEY=key1,key2,key3</code>
                    <p><strong>Single key:</strong></p>
                    <code>GEMINI_API_KEY=your_key</code>
                </div>
                """)
        
        examples = gr.Examples(
            examples=get_examples(),
            inputs=[topic_input, context_input]
        )
        
        output_display = gr.Markdown(
            value="Ready to generate! Enter a topic and click Generate."
        )
        
        generate_btn.click(
            fn=generate_video_gradio,
            inputs=[topic_input, context_input, max_scenes_slider],
            outputs=[output_display, status_display],
            show_progress=True
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    ) 