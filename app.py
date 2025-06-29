#!/usr/bin/env python3
"""
manimAnimationAgent - Hugging Face Spaces App
Generates educational videos using Gemini 2.0 Flash and Manim
"""

import os
import sys
import asyncio
import time
import random
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import gradio as gr

# Environment setup
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
video_generator = None
CAN_IMPORT_DEPENDENCIES = False
GRADIO_OUTPUT_DIR = "gradio_outputs"
DEPENDENCY_ERROR = None

def check_dependencies():
    """Check if required dependencies are available."""
    global CAN_IMPORT_DEPENDENCIES, DEPENDENCY_ERROR
    
    missing_deps = []
    
    try:
        import manim
    except ImportError:
        missing_deps.append("manim")
    
    try:
        from generate_video import VideoGenerator
    except ImportError as e:
        missing_deps.append("generate_video")
        DEPENDENCY_ERROR = str(e)
    
    try:
        from mllm_tools.litellm import LiteLLMWrapper
    except ImportError:
        missing_deps.append("mllm_tools")
    
    if missing_deps:
        CAN_IMPORT_DEPENDENCIES = False
        return f"Missing dependencies: {', '.join(missing_deps)}"
    else:
        CAN_IMPORT_DEPENDENCIES = True
        return "All dependencies available"

def setup_environment():
    """Setup environment for HF Spaces."""
    print("🚀 Setting up manimAnimationAgent...")
    
    # Create output directory
    os.makedirs(GRADIO_OUTPUT_DIR, exist_ok=True)
    
    # Check dependencies
    dep_status = check_dependencies()
    print(f"📦 Dependencies: {dep_status}")
    
    gemini_keys = os.getenv("GEMINI_API_KEY", "")
    if gemini_keys:
        key_count = len([k.strip() for k in gemini_keys.split(',') if k.strip()])
        print(f"✅ Found {key_count} Gemini API key(s)")
        return True
    else:
        print("⚠️ No Gemini API keys found")
        return False

def initialize_video_generator():
    """Initialize video generator with proper dependencies."""
    global video_generator, CAN_IMPORT_DEPENDENCIES, DEPENDENCY_ERROR
    
    try:
        if DEMO_MODE:
            return "⚠️ Demo mode enabled - No video generation"
        
        if not CAN_IMPORT_DEPENDENCIES:
            return f"⚠️ Missing dependencies - {DEPENDENCY_ERROR or 'Video generation not available'}"
        
        gemini_keys = os.getenv("GEMINI_API_KEY", "")
        if not gemini_keys:
            return "⚠️ No API keys found - Set GEMINI_API_KEY environment variable"
        
        # Import dependencies
        try:
            from generate_video import VideoGenerator
            from mllm_tools.litellm import LiteLLMWrapper
            print("✅ Successfully imported video generation dependencies")
        except ImportError as e:
            return f"⚠️ Import error: {str(e)}"
        
        # Initialize models with comma-separated API key support
        planner_model = LiteLLMWrapper(
            model_name="gemini/gemini-2.5-pro",
            temperature=0.7,
            print_cost=True,
            verbose=False,
            use_langfuse=False
        )
        
        # Initialize video generator
        video_generator = VideoGenerator(
            planner_model=planner_model,  
            helper_model=planner_model,
            scene_model=planner_model,
            output_dir=GRADIO_OUTPUT_DIR,
            use_rag=False,
            use_context_learning=False,
            use_visual_fix_code=False,
            verbose=True
        )
        
        return "✅ Video generator initialized successfully"
        
    except Exception as e:
        CAN_IMPORT_DEPENDENCIES = False
        print(f"❌ Error initializing video generator: {e}")
        return f"❌ Initialization failed: {str(e)}"

def simulate_video_generation(topic: str, context: str, max_scenes: int, progress_callback=None):
    """Enhanced simulation for HF Spaces demo."""
    stages = [
        ("🔍 Analyzing educational topic", 15),
        ("📚 Planning curriculum structure", 30),
        ("🎯 Designing learning objectives", 45),
        ("📝 Creating content outline", 60),
        ("🎨 Generating visual concepts", 75),
        ("🎬 Simulating video production", 90),
        ("✅ Demo completed", 100)
    ]
    
    results = []
    for stage, progress in stages:
        if progress_callback:
            progress_callback(progress, stage)
        time.sleep(random.uniform(0.8, 1.5))
        results.append(f"• {stage}")
    
    # Create demo information
    demo_content = {
        "success": True,
        "message": f"Demo simulation completed for educational topic: {topic}",
        "scenes_planned": max_scenes,
        "processing_steps": results,
        "demo_note": "🎮 This is a demonstration mode",
        "limitations": [
            "Real video generation requires Manim system dependencies",
            "HF Spaces has limited system library support",
            "For full functionality, run locally with complete dependencies"
        ],
        "capabilities": [
            "✅ Gemini 2.0 Flash AI integration",
            "✅ Comma-separated API key support", 
            "✅ Educational content planning",
            "❌ Video rendering (requires local setup)"
        ]
    }
    
    return demo_content

async def generate_video_async(topic: str, context: str, max_scenes: int, progress_callback=None):
    """Generate video asynchronously - handles both real and demo modes."""
    global video_generator
    
    if not topic.strip():
        return {"success": False, "error": "Please enter an educational topic"}
    
    try:
        # Always use demo mode on HF Spaces due to dependency limitations
        if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES or video_generator is None:
            return simulate_video_generation(topic, context, max_scenes, progress_callback)
        
        # This code would run with full dependencies (local setup)
        if progress_callback:
            progress_callback(10, "🚀 Starting video generation...")
        
        result = await video_generator.generate_video_pipeline(
            topic=topic,
            description=context or f"Educational video about {topic}",
            max_retries=3,
            only_plan=False,
            specific_scenes=list(range(1, max_scenes + 1)) if max_scenes > 0 else None
        )
        
        if progress_callback:
            progress_callback(100, "✅ Video generation completed!")
        
        # Check for generated video files
        file_prefix = topic.lower().replace(' ', '_')
        file_prefix = ''.join(c for c in file_prefix if c.isalnum() or c == '_')
        
        output_folder = os.path.join(GRADIO_OUTPUT_DIR, file_prefix)
        video_files = []
        
        if os.path.exists(output_folder):
            combined_video = os.path.join(output_folder, f"{file_prefix}_combined.mp4")
            if os.path.exists(combined_video):
                video_files.append(combined_video)
            
            for i in range(1, max_scenes + 1):
                scene_video = os.path.join(output_folder, f"scene{i}", f"{file_prefix}_scene{i}.mp4")
                if os.path.exists(scene_video):
                    video_files.append(scene_video)
        
        return {
            "success": True, 
            "message": f"Video generated successfully for: {topic}",
            "video_files": video_files,
            "output_folder": output_folder,
            "result": result
        }
        
    except Exception as e:
        print(f"❌ Error in video generation: {e}")
        return {"success": False, "error": str(e)}

def generate_video_gradio(topic: str, context: str, max_scenes: int, progress=gr.Progress()) -> Tuple[str, str, Optional[str]]:
    """Main Gradio function that handles video generation and returns results."""
    def progress_callback(percent, message):
        progress(percent / 100, desc=message)
    
    # Create new event loop for this generation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            generate_video_async(topic, context, max_scenes, progress_callback)
        )
    finally:
        loop.close()
    
    if result["success"]:
        output = f"""# 🎓 Educational Content Generation

**Topic:** {topic}
**Context:** {context if context else "General educational content"}
**Planned Scenes:** {max_scenes}

## ✅ Generation Results
{result["message"]}
"""
        
        # Add processing steps if available
        if "processing_steps" in result:
            output += "\n## 🔄 Processing Steps\n"
            for step in result["processing_steps"]:
                output += f"{step}\n"
        
        # Add capabilities info
        if "capabilities" in result:
            output += "\n## 🛠️ System Capabilities\n"
            for cap in result["capabilities"]:
                output += f"{cap}\n"
        
        # Add limitations for demo mode
        if "limitations" in result:
            output += "\n## ⚠️ Current Limitations\n"
            for limit in result["limitations"]:
                output += f"• {limit}\n"
        
        # Add demo note if present
        if "demo_note" in result:
            output += f"\n## {result['demo_note']}\n"
            output += "For full video generation capabilities, set up the system locally with all dependencies."
        
        # Add video file information for real generation
        video_path = None
        if "video_files" in result and result["video_files"]:
            output += f"\n## 🎥 Generated Videos\n"
            for video_file in result["video_files"]:
                output += f"• {os.path.basename(video_file)}\n"
            video_path = result["video_files"][0]
        elif "output_folder" in result:
            output += f"\n📁 **Output folder:** {result['output_folder']}\n"
        
        status = "🎮 Demo mode active" if (DEMO_MODE or not CAN_IMPORT_DEPENDENCIES) else "✅ Generation completed"
        return output, status, video_path
    
    else:
        error_output = f"""# ❌ Generation Failed

**Error:** {result.get("error", "Unknown error")}

## 💡 Troubleshooting Tips

### For Demo Mode Issues:
1. **Topic Clarity:** Use specific educational topics
2. **Context:** Provide clear learning objectives
3. **Scope:** Keep scenes reasonable (2-4 for demos)

### For Full Video Generation:
1. **Local Setup:** Clone the repository locally
2. **Dependencies:** Install all required packages including Manim
3. **API Keys:** Set GEMINI_API_KEY with valid keys
4. **System Requirements:** Ensure Manim system dependencies are installed

## 🔧 Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd TheoremExplainAgent

# Install full dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-key-1,your-key-2"
export DEMO_MODE=false

# Run locally
python app.py
```
"""
        return error_output, "❌ Failed", None

def get_examples():
    """Educational example topics optimized for AI processing."""
    return [
        ["Pythagorean Theorem", "Visual proof with geometric demonstrations for high school students"],
        ["Newton's Second Law", "F=ma explained with real-world examples and mathematical derivations"],
        ["Calculus Derivatives", "Rate of change concept with graphical interpretations and applications"],
        ["DNA Structure", "Double helix model with chemical bonds and biological significance"],
        ["Photosynthesis Process", "Step-by-step biochemical pathway with energy transformations"],
        ["Quadratic Formula", "Derivation, applications, and graphical representation"],
        ["Electromagnetic Waves", "Properties, spectrum, and everyday applications"],
        ["Cellular Respiration", "ATP production pathway with molecular details"]
    ]

# Initialize the system with error handling
try:
    print("🔧 Initializing system...")
    has_api_keys = setup_environment()
    init_status = initialize_video_generator()
    print(f"✅ System initialization completed: {init_status}")
except Exception as e:
    print(f"❌ System initialization failed: {e}")
    has_api_keys = False
    init_status = f"❌ Initialization error: {str(e)}"

# Create Gradio interface
with gr.Blocks(
    title="🎓 manimAnimationAgent",
    theme=gr.themes.Soft(),
    css="footer {visibility: hidden}"
) as demo:
    
    gr.HTML("""
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 2.5em;">🎓 manimAnimationAgent</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">AI-Powered Educational Content Generation</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">Powered by Gemini 2.0 Flash</p>
    </div>
    """)
    
    # System status section
    with gr.Row():
        with gr.Column():
            gr.HTML(f"""
            <div style="background: {'#d4edda' if has_api_keys else '#fff3cd'}; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid {'#28a745' if has_api_keys else '#ffc107'};">
                <h4 style="margin: 0 0 8px 0;">🔐 API Configuration</h4>
                <p style="margin: 0;"><strong>Status:</strong> {"✅ API keys configured" if has_api_keys else "⚠️ No API keys found"}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">{"Ready for content generation" if has_api_keys else "Limited to demo capabilities"}</p>
            </div>
            """)
            
        with gr.Column():
            system_status = gr.Textbox(
                label="🔧 System Status",
                value=init_status,
                interactive=False,
                lines=2
            )
    
    # Dependency information
    if not CAN_IMPORT_DEPENDENCIES:
        gr.HTML("""
        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 15px 0; border: 1px solid #2196f3;">
            <h4 style="color: #1976d2; margin-top: 0;">🎮 Demo Mode Active</h4>
            <p>This HF Spaces instance runs in demonstration mode due to system dependency limitations.</p>
            
            <div style="background: #fff; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h5 style="color: #333; margin-top: 0;">✅ Available Features:</h5>
                <ul style="margin: 10px 0; color: #666;">
                    <li>🤖 Gemini 2.0 Flash AI integration</li>
                    <li>🔄 Comma-separated API key rotation</li>
                    <li>📚 Educational content planning</li>
                    <li>🎯 Learning objective design</li>
                </ul>
                
                <h5 style="color: #333; margin-top: 15px;">❌ Not Available:</h5>
                <ul style="margin: 10px 0; color: #666;">
                    <li>🎥 Actual video rendering (requires Manim system libraries)</li>
                    <li>📹 MP4 file generation</li>
                    <li>🎨 Visual animations</li>
                </ul>
            </div>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 0.9em;">
                <strong>For Full Video Generation:</strong><br>
                1. Clone repository locally<br>
                2. Install system dependencies (pangocairo, manim)<br>
                3. Set GEMINI_API_KEY environment variable<br>
                4. Run: python app.py
            </div>
        </div>
        """)
    
    # Main interface
    with gr.Row():
        with gr.Column(scale=2):
            topic_input = gr.Textbox(
                label="📚 Educational Topic",
                placeholder="e.g., Pythagorean Theorem, Newton's Laws, DNA Structure...",
                lines=1
            )
            
            context_input = gr.Textbox(
                label="📝 Learning Context (Optional)",
                placeholder="Specify target audience, learning objectives, or focus areas...",
                lines=3
            )
            
            max_scenes_slider = gr.Slider(
                label="🎬 Content Sections",
                minimum=1,
                maximum=6,
                value=3,
                step=1,
                info="Number of content sections to plan"
            )
            
            generate_btn = gr.Button(
                "🚀 Generate Educational Content", 
                variant="primary", 
                size="lg"
            )
            
        with gr.Column(scale=1):
            gr.HTML("""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; height: fit-content;">
                <h4 style="color: #495057; margin-top: 0;">💡 Tips for Best Results</h4>
                <ul style="color: #6c757d; font-size: 0.9em; line-height: 1.6;">
                    <li><strong>Be Specific:</strong> "Quadratic formula derivation" vs "Math"</li>
                    <li><strong>Educational Focus:</strong> Include learning objectives</li>
                    <li><strong>Target Audience:</strong> Specify grade level or background</li>
                    <li><strong>Clear Context:</strong> Mention key concepts to cover</li>
                </ul>
            </div>
            """)
    
    # Examples
    examples = gr.Examples(
        examples=get_examples(),
        inputs=[topic_input, context_input],
        label="📖 Example Educational Topics"
    )
    
    # Output section
    with gr.Row():
        with gr.Column(scale=2):
            output_display = gr.Markdown(
                value="👋 **Ready to generate educational content!** Enter a topic above and click 'Generate' to begin planning.",
                label="📋 Generation Results"
            )
        
        with gr.Column(scale=1):
            video_output = gr.Video(
                label="🎥 Generated Video",
                visible=True
            )
    
    # Wire up the interface
    generate_btn.click(
        fn=generate_video_gradio,
        inputs=[topic_input, context_input, max_scenes_slider],
        outputs=[output_display, system_status, video_output],
        show_progress=True
    )

# Launch configuration for HF Spaces compatibility
if __name__ == "__main__":
    print("🚀 Starting manimAnimationAgent...")
    print(f"📦 Dependencies check: {check_dependencies()}")
    print(f"🔑 API keys configured: {setup_environment()}")
    
    # HF Spaces compatible launch
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
        max_threads=4,  # Limit threads for zero GPU
        enable_queue=True,
        show_tips=True
    ) 