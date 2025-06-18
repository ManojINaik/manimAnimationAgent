#!/usr/bin/env python3
"""
manimAnimationAgent - FastAPI Backend Server
Provides REST API endpoints for educational video generation
"""

import os
import sys
import asyncio
import time
import json
import random
from typing import Dict, Any, Optional, List
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment setup
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
API_OUTPUT_DIR = "api_outputs"
video_generator = None
CAN_IMPORT_DEPENDENCIES = False
DEPENDENCY_ERROR = None

# Global task storage (in production, use Redis or database)
task_storage = {}

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
    created_at: str

class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    dependencies_available: bool
    timestamp: str
    version: str = "1.0.0"

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
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        return False
    else:
        CAN_IMPORT_DEPENDENCIES = True
        logger.info("All dependencies available")
        return True

def setup_environment():
    """Setup environment for API server."""
    logger.info("🚀 Setting up manimAnimationAgent API Server...")
    
    # Create output directory
    os.makedirs(API_OUTPUT_DIR, exist_ok=True)
    
    # Check dependencies
    dep_status = check_dependencies()
    
    gemini_keys = os.getenv("GEMINI_API_KEY", "")
    if gemini_keys:
        key_count = len([k.strip() for k in gemini_keys.split(',') if k.strip()])
        logger.info(f"✅ Found {key_count} Gemini API key(s)")
        return True
    else:
        logger.warning("⚠️ No Gemini API keys found")
        return False

def initialize_video_generator():
    """Initialize video generator with proper dependencies."""
    global video_generator, CAN_IMPORT_DEPENDENCIES, DEPENDENCY_ERROR
    
    try:
        if DEMO_MODE:
            logger.info("⚠️ Demo mode enabled - No video generation")
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
            logger.info("✅ Successfully imported video generation dependencies")
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
            output_dir=API_OUTPUT_DIR,
            use_rag=False,
            use_context_learning=False,
            use_visual_fix_code=False,
            verbose=True
        )
        
        logger.info("✅ Video generator initialized successfully")
        return "✅ Video generator initialized successfully"
        
    except Exception as e:
        CAN_IMPORT_DEPENDENCIES = False
        logger.error(f"❌ Error initializing video generator: {e}")
        return f"❌ Initialization failed: {str(e)}"

def simulate_video_generation(topic: str, context: str, max_scenes: int, task_id: str):
    """Enhanced simulation for API demo."""
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
        if task_id in task_storage:
            task_storage[task_id]["progress"] = progress
            task_storage[task_id]["message"] = stage
        
        time.sleep(random.uniform(0.5, 1.0))  # Faster for API
        results.append(f"• {stage}")
    
    # Create demo information
    demo_content = {
        "success": True,
        "message": f"Demo simulation completed for educational topic: {topic}",
        "topic": topic,
        "context": context,
        "scenes_planned": max_scenes,
        "processing_steps": results,
        "demo_note": "🎮 This is a demonstration mode",
        "limitations": [
            "Real video generation requires Manim system dependencies",
            "Production deployment needs complete dependencies",
            "For full functionality, run locally with complete setup"
        ],
        "capabilities": [
            "✅ Gemini 2.0 Flash AI integration",
            "✅ Comma-separated API key support", 
            "✅ Educational content planning",
            "✅ RESTful API endpoints",
            "❌ Video rendering (requires local setup)"
        ],
        "generated_at": datetime.now().isoformat()
    }
    
    # Update final task status
    if task_id in task_storage:
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
        if task_id in task_storage:
            task_storage[task_id]["status"] = "running"
            task_storage[task_id]["progress"] = 5
            task_storage[task_id]["message"] = "Starting video generation..."
        
        if not topic.strip():
            raise ValueError("Please provide an educational topic")
        
        # Always use demo mode if dependencies not available
        if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES or video_generator is None:
            logger.info(f"Running demo generation for topic: {topic}")
            return simulate_video_generation(topic, context, max_scenes, task_id)
        
        # This code would run with full dependencies (local setup)
        if task_id in task_storage:
            task_storage[task_id]["progress"] = 10
            task_storage[task_id]["message"] = "🚀 Starting video generation..."
        
        result = await video_generator.generate_video_pipeline(
            topic=topic,
            description=context or f"Educational video about {topic}",
            max_retries=3,
            only_plan=False,
            specific_scenes=list(range(1, max_scenes + 1)) if max_scenes > 0 else None
        )
        
        if task_id in task_storage:
            task_storage[task_id]["progress"] = 100
            task_storage[task_id]["message"] = "✅ Video generation completed!"
            task_storage[task_id]["status"] = "completed"
            task_storage[task_id]["result"] = result
        
        return result
        
    except Exception as e:
        logger.error(f"Error in video generation: {e}")
        if task_id in task_storage:
            task_storage[task_id]["status"] = "failed"
            task_storage[task_id]["error"] = str(e)
            task_storage[task_id]["message"] = f"Error: {str(e)}"
        raise e

# Create FastAPI app
app = FastAPI(
    title="manimAnimationAgent API",
    description="REST API for generating educational videos with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    logger.info("Starting manimAnimationAgent API...")
    setup_environment()
    init_status = initialize_video_generator()
    logger.info(f"Initialization status: {init_status}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "manimAnimationAgent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.post("/api/generate", response_model=VideoGenerationResponse)
async def generate_video_api(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate educational video via API"""
    task_id = str(uuid.uuid4())
    
    logger.info(f"New video generation request: {request.topic} (Task ID: {task_id})")
    
    # Initialize task
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "message": "Task queued",
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "request": request.dict()
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
        message="Video generation task queued successfully",
        task_id=task_id,
        status="queued"
    )

@app.get("/api/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a video generation task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    return TaskStatus(**task)

@app.get("/api/tasks")
async def list_tasks(limit: int = 10, status: Optional[str] = None):
    """List tasks with optional filtering"""
    tasks = list(task_storage.values())
    
    # Filter by status if provided
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    # Sort by creation time (newest first)
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    tasks = tasks[:limit]
    
    return {
        "tasks": tasks,
        "total": len(task_storage),
        "filtered": len(tasks)
    }

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a specific task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del task_storage[task_id]
    return {"message": f"Task {task_id} deleted successfully"}

@app.delete("/api/tasks")
async def clear_all_tasks():
    """Clear all tasks"""
    count = len(task_storage)
    task_storage.clear()
    return {"message": f"Cleared {count} tasks"}

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        demo_mode=DEMO_MODE,
        dependencies_available=CAN_IMPORT_DEPENDENCIES,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/stats")
async def get_stats():
    """Get API statistics"""
    status_counts = {}
    for task in task_storage.values():
        status = task["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_tasks": len(task_storage),
        "status_breakdown": status_counts,
        "demo_mode": DEMO_MODE,
        "dependencies_available": CAN_IMPORT_DEPENDENCIES,
        "uptime": "API running"
    }

# Example usage endpoint
@app.get("/api/example")
async def get_example_usage():
    """Get example API usage"""
    return {
        "example_request": {
            "method": "POST",
            "url": "/api/generate",
            "body": {
                "topic": "Pythagorean Theorem",
                "context": "High school mathematics level",
                "max_scenes": 3
            }
        },
        "example_response": {
            "success": True,
            "message": "Video generation task queued successfully",
            "task_id": "example-task-id",
            "status": "queued"
        },
        "status_check": {
            "method": "GET",
            "url": "/api/status/example-task-id"
        }
    }

if __name__ == "__main__":
    # Setup environment
    setup_environment()
    
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    ) 