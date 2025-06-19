# Appwrite Database Integration for Video Metadata Management

## Overview

This guide documents the implementation of Appwrite database and storage integration to replace the text file-based metadata system with a scalable, searchable, and structured database solution.

## 🎯 Problem Statement

The current system stores video metadata in scattered text files across the output directory, which leads to:

- **Scalability Issues**: File-based storage doesn't scale well with large numbers of videos
- **Search Limitations**: No efficient way to search or filter videos by topic, status, or other criteria
- **Data Integrity**: No structured validation or relationships between data
- **Collaboration Challenges**: Difficult to share and manage data across multiple users
- **Analytics Gaps**: No centralized way to track video generation statistics

## 🏗️ Architecture Overview

### Database Collections

#### 1. Videos Collection
Stores metadata for each video generation task with fields for topic, description, status, scene count, owner, and file URLs.

#### 2. Scenes Collection  
Stores individual scene data linked to videos including plans, storyboards, generated code, and rendered videos.

#### 3. Agent Memory Collection
Stores error-fix patterns for machine learning with structured data for pattern matching and success tracking.

### Storage Buckets

- **Final Videos**: Combined .mp4 files (500MB max)
- **Scene Videos**: Individual scene videos (100MB max)  
- **Subtitles**: Subtitle files (1MB max)
- **Source Code**: Python code for reproducibility (10MB max)

## 🚀 Setup Instructions

### 1. Environment Configuration

Add these variables to your `.env` file:

```env
APPWRITE_API_KEY=your_api_key_here
APPWRITE_PROJECT_ID=your_project_id_here
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
```

### 2. Install Dependencies

```bash
pip install appwrite>=6.0.0
```

### 3. Initialize Database Structure

```python
python test_appwrite_integration.py
```

## 📝 Implementation Guide

### Basic Usage

```python
from src.core.appwrite_integration import AppwriteVideoManager

# Initialize manager
manager = AppwriteVideoManager()

# Create video record
video_id = await manager.create_video_record(
    topic="Linear Algebra: Eigenvalues",
    description="Educational video about eigenvalues",
    scene_count=4
)

# Update status
await manager.update_video_status(video_id, "planning")
```

### Agent Memory Integration

```python
from src.core.appwrite_agent_memory import AppwriteAgentMemory

memory = AppwriteAgentMemory(manager)

# Store error-fix patterns
await memory.store_error_fix(
    error_message="AttributeError: 'Text' object error",
    original_code="problematic_code",
    fixed_code="working_code",
    topic="text_rendering"
)
```

## 🔄 Migration from File-Based System

The system includes automatic migration:

```python
# Migrate existing data
success = await manager.migrate_existing_data("output/")
```

## 📊 Analytics and Monitoring

```python
# Get statistics
stats = await manager.get_video_statistics()
print(f"Total videos: {stats['completed_videos']}")
```

## 🧪 Testing

Run the test suite:

```bash
python test_appwrite_integration.py
```

This comprehensive system provides structured data management, global access, real-time collaboration capabilities, and advanced analytics while maintaining compatibility with existing workflows. 