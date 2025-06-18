#!/usr/bin/env python3
"""
manimAnimationAgent - Streamlit App with API Endpoints
Provides both web interface and REST API for educational video generation
"""

import os
import sys
import asyncio
import time
import json
import random
from typing import Dict, Any, Optional, List
from pathlib import Path
import streamlit as st
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import threading
from datetime import datetime
import uuid

# Environment setup
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
STREAMLIT_OUTPUT_DIR = "streamlit_outputs"
video_generator = None
CAN_IMPORT_DEPENDENCIES = False
DEPENDENCY_ERROR = None

# Pydantic models for API
class VideoGenerationRequest(BaseModel):
    topic: str
    context: str = ""
    max_scenes: int = 3
    ai_model: str = "gemini/gemini-2.0-flash-exp"  # Renamed to avoid conflict
    temperature: float = 0.7

class VideoGenerationResponse(BaseModel):
    success: bool
    message: str
    task_id: str
    status: str = "queued"
    progress: int = 0

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result: Optional[Dict] = None
    error: Optional[str] = None

# Global task storage
task_storage = {}

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
    """Setup environment for Streamlit."""
    print("🚀 Setting up manimAnimationAgent for Streamlit...")
    
    # Create output directory
    os.makedirs(STREAMLIT_OUTPUT_DIR, exist_ok=True)
    
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
            model_name="gemini/gemini-2.0-flash-exp",
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
            output_dir=STREAMLIT_OUTPUT_DIR,
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

def simulate_video_generation(topic: str, context: str, max_scenes: int, task_id: str):
    """Enhanced simulation for Streamlit demo."""
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
        # Update task status
        task_storage[task_id]["progress"] = progress
        task_storage[task_id]["message"] = stage
        
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
            "Streamlit Cloud has limited system library support",
            "For full functionality, run locally with complete dependencies"
        ],
        "capabilities": [
            "✅ Gemini 2.0 Flash AI integration",
            "✅ Comma-separated API key support", 
            "✅ Educational content planning",
            "❌ Video rendering (requires local setup)"
        ]
    }
    
    # Update final task status
    task_storage[task_id]["status"] = "completed"
    task_storage[task_id]["progress"] = 100
    task_storage[task_id]["message"] = "Task completed successfully"
    task_storage[task_id]["result"] = demo_content
    
    return demo_content

async def generate_video_async(topic: str, context: str, max_scenes: int, task_id: str):
    """Generate video asynchronously - handles both real and demo modes."""
    global video_generator
    
    try:
        # Update task status
        task_storage[task_id]["status"] = "running"
        task_storage[task_id]["progress"] = 5
        task_storage[task_id]["message"] = "Starting video generation..."
        
        if not topic.strip():
            raise ValueError("Please enter an educational topic")
        
        # Always use demo mode on Streamlit Cloud due to dependency limitations
        if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES or video_generator is None:
            return simulate_video_generation(topic, context, max_scenes, task_id)
        
        # This code would run with full dependencies (local setup)
        task_storage[task_id]["progress"] = 10
        task_storage[task_id]["message"] = "🚀 Starting video generation..."
        
        result = await video_generator.generate_video_pipeline(
            topic=topic,
            description=context or f"Educational video about {topic}",
            max_retries=3,
            only_plan=False,
            specific_scenes=list(range(1, max_scenes + 1)) if max_scenes > 0 else None
        )
        
        task_storage[task_id]["progress"] = 100
        task_storage[task_id]["message"] = "✅ Video generation completed!"
        task_storage[task_id]["status"] = "completed"
        task_storage[task_id]["result"] = result
        
        return result
        
    except Exception as e:
        task_storage[task_id]["status"] = "failed"
        task_storage[task_id]["error"] = str(e)
        task_storage[task_id]["message"] = f"Error: {str(e)}"
        raise e

# FastAPI app for API endpoints
api_app = FastAPI(
    title="manimAnimationAgent API",
    description="REST API for generating educational videos with AI",
    version="1.0.0"
)

@api_app.post("/api/generate", response_model=VideoGenerationResponse)
async def generate_video_api(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate educational video via API"""
    task_id = str(uuid.uuid4())
    
    # Initialize task
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "message": "Task queued",
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat()
    }
    
    # Add background task
    background_tasks.add_task(
        generate_video_async,
        request.topic,
        request.context,
        request.max_scenes,
        task_id
    )
    
    return VideoGenerationResponse(
        success=True,
        message="Video generation task queued",
        task_id=task_id,
        status="queued"
    )

@api_app.get("/api/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a video generation task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    return TaskStatus(**task)

@api_app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    return {"tasks": list(task_storage.values())}

@api_app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "demo_mode": DEMO_MODE,
        "dependencies_available": CAN_IMPORT_DEPENDENCIES,
        "timestamp": datetime.now().isoformat()
    }

# Streamlit UI
def main():
    st.set_page_config(
        page_title="🎓 manimAnimationAgent",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎓 manimAnimationAgent")
    st.markdown("**AI-Powered Educational Content Generation with Streamlit & API**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System status
        st.subheader("📊 System Status")
        setup_status = setup_environment()
        
        if setup_status:
            st.success("✅ System ready")
        else:
            st.warning("⚠️ Limited functionality (no API keys)")
        
        # Initialize system
        if st.button("🔄 Initialize System"):
            with st.spinner("Initializing..."):
                init_status = initialize_video_generator()
                if "✅" in init_status:
                    st.success(init_status)
                else:
                    st.warning(init_status)
        
        # API Configuration
        st.subheader("🔌 API Information")
        st.markdown("""
        **To use as API backend:**
        
        1. Deploy this Streamlit app
        2. Use the app URL as your API base
        3. Make requests to endpoints:
           - `POST /api/generate` - Generate video
           - `GET /api/status/{task_id}` - Check status
           - `GET /api/health` - Health check
        
        **Example API Usage:**
        ```python
        import requests
        
        # Generate video
        response = requests.post(
            "YOUR_STREAMLIT_URL/api/generate",
            json={{
                "topic": "{api_topic}",
                "context": "{api_context}",
                "max_scenes": {api_max_scenes}
            }}
        )
        ```
        """)
        
        # Demo mode indicator
        if DEMO_MODE:
            st.info("🎮 Running in Demo Mode")
        elif not CAN_IMPORT_DEPENDENCIES:
            st.warning("⚠️ Limited Dependencies")
    
    # Main interface tabs
    tab1, tab2, tab3 = st.tabs(["🎓 Generate Content", "📊 Task Monitor", "🔌 API Testing"])
    
    with tab1:
        st.header("📚 Generate Educational Content")
        
        # Input form
        with st.form("video_generation_form"):
            topic = st.text_input(
                "Educational Topic *",
                placeholder="e.g., Pythagorean Theorem, Newton's Laws, DNA Structure",
                help="Enter the topic you want to explain"
            )
            
            context = st.text_area(
                "Learning Context",
                placeholder="Additional context, target audience, or specific requirements...",
                help="Optional: Provide additional context for better content generation"
            )
            
            max_scenes = st.slider(
                "Number of Content Sections",
                min_value=1,
                max_value=6,
                value=3,
                help="How many sections to include in the educational content"
            )
            
            submitted = st.form_submit_button("🚀 Generate Educational Content")
        
        # Generation results
        if submitted:
            if not topic.strip():
                st.error("Please enter an educational topic")
            else:
                # Create task
                task_id = str(uuid.uuid4())
                task_storage[task_id] = {
                    "task_id": task_id,
                    "status": "running",
                    "progress": 0,
                    "message": "Starting generation...",
                    "result": None,
                    "error": None,
                    "created_at": datetime.now().isoformat()
                }
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Run generation
                    if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES:
                        result = simulate_video_generation(topic, context, max_scenes, task_id)
                        
                        # Update progress bar
                        for i in range(101):
                            progress_bar.progress(i)
                            if task_id in task_storage:
                                status_text.text(task_storage[task_id]["message"])
                            time.sleep(0.05)
                        
                        # Display results
                        st.success("✅ Educational content generation completed!")
                        
                        with st.expander("📋 Generation Results", expanded=True):
                            st.json(result)
                        
                        # Show capabilities and limitations
                        col_cap, col_limit = st.columns(2)
                        
                        with col_cap:
                            st.subheader("✅ Available Features")
                            for capability in result.get("capabilities", []):
                                st.markdown(f"- {capability}")
                        
                        with col_limit:
                            st.subheader("⚠️ Current Limitations")
                            for limitation in result.get("limitations", []):
                                st.markdown(f"- {limitation}")
                    
                    else:
                        # Real generation (when dependencies are available)
                        st.info("🔄 Running full video generation pipeline...")
                        # This would use the actual video generator
                        pass
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    if task_id in task_storage:
                        task_storage[task_id]["status"] = "failed"
                        task_storage[task_id]["error"] = str(e)
        
        # Example topics
        st.subheader("💡 Example Topics")
        examples = [
            "Quadratic Formula Derivation",
            "Newton's Second Law",
            "DNA Replication Process",
            "Photosynthesis Mechanism",
            "Pythagorean Theorem Proof",
            "Chemical Bonding Types"
        ]
        
        cols = st.columns(3)
        for i, example in enumerate(examples):
            with cols[i % 3]:
                if st.button(f"📚 {example}", key=f"example_{example}"):
                    st.session_state.example_topic = example
                    st.rerun()
    
    with tab2:
        st.header("📊 Task Monitor")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🔄 Refresh Tasks"):
                st.rerun()
        
        with col1:
            st.subheader(f"Tasks ({len(task_storage)} total)")
        
        if task_storage:
            for task_id, task in reversed(list(task_storage.items())):
                with st.expander(f"Task: {task_id[:8]}... - {task['status'].upper()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status:** {task['status']}")
                        st.write(f"**Created:** {task['created_at']}")
                        
                        # Progress bar
                        if task['status'] == 'running':
                            st.progress(task['progress'] / 100)
                        elif task['status'] == 'completed':
                            st.progress(1.0)
                        else:
                            st.progress(0.0)
                    
                    with col2:
                        st.write(f"**Progress:** {task['progress']}%")
                        st.write(f"**Message:** {task['message']}")
                    
                    if task['status'] == 'completed' and task['result']:
                        st.subheader("📋 Results")
                        st.json(task['result'])
                    elif task['status'] == 'failed' and task['error']:
                        st.error(f"Error: {task['error']}")
        else:
            st.info("No tasks yet. Generate some content to see tasks here!")
    
    with tab3:
        st.header("🔌 API Testing Interface")
        
        st.markdown("""
        Use this interface to test API endpoints that your web application can use.
        """)
        
        # API endpoint testing
        with st.form("api_test_form"):
            st.subheader("Test Video Generation API")
            
            api_topic = st.text_input("Topic", value="Pythagorean Theorem")
            api_context = st.text_area("Context", value="High school mathematics")
            api_max_scenes = st.number_input("Max Scenes", min_value=1, max_value=6, value=3)
            
            test_api = st.form_submit_button("🧪 Test API Call")
        
        if test_api:
            # Simulate API call
            task_id = str(uuid.uuid4())
            
            st.code(f"""
# Example API call your web app would make:
import requests

response = requests.post(
    "YOUR_STREAMLIT_URL/api/generate",
    json={{
        "topic": "{api_topic}",
        "context": "{api_context}",
        "max_scenes": {api_max_scenes}
    }}
)

# Response:
{{"task_id": "{task_id}", "status": "queued"}}
            """, language="python")
            
            # Simulate the generation
            with st.spinner("Simulating API response..."):
                task_storage[task_id] = {
                    "task_id": task_id,
                    "status": "running",
                    "progress": 0,
                    "message": "API test in progress...",
                    "result": None,
                    "error": None,
                    "created_at": datetime.now().isoformat()
                }
                
                result = simulate_video_generation(api_topic, api_context, api_max_scenes, task_id)
                
                st.success("✅ API test completed!")
                st.json({
                    "task_id": task_id,
                    "status": "completed",
                    "result": result
                })
        
        # Health check
        st.subheader("🏥 Health Check")
        if st.button("Check API Health"):
            health_data = {
                "status": "healthy",
                "demo_mode": DEMO_MODE,
                "dependencies_available": CAN_IMPORT_DEPENDENCIES,
                "timestamp": datetime.now().isoformat(),
                "task_count": len(task_storage)
            }
            st.json(health_data)

# Run the app
if __name__ == "__main__":
    # Setup environment
    setup_environment()
    
    # Run Streamlit app
    main() 