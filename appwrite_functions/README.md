# Appwrite Functions for Asynchronous Video Generation

This implementation transforms the synchronous video generation pipeline into an asynchronous, serverless architecture using Appwrite Functions with real-time status updates.

## Architecture Overview

### 1. Asynchronous Execution
- **Non-blocking**: The video generation runs in the background on Appwrite's servers
- **Immediate Response**: Returns a task ID immediately, allowing users to close their browser
- **Scalable**: Multiple videos can be generated concurrently

### 2. Real-time Updates
- **Live Status**: Users receive instant updates on video generation progress
- **Scene Progress**: Track individual scene rendering status
- **Error Handling**: Real-time error notifications if generation fails

## Implementation Components

### Backend: Appwrite Function

#### `appwrite_functions/video_generation/`
- **main.py**: The serverless function handler
  - Receives video generation requests
  - Creates database records
  - Spawns async video generation task
  - Updates status in real-time

#### Key Features:
1. **Progress Tracking**: Updates progress percentage (0-100%)
2. **Scene Status**: Tracks which scene is currently being rendered
3. **Error Recovery**: Graceful error handling with detailed messages
4. **File Management**: Automatic upload of generated videos to Appwrite Storage

### Frontend: Next.js with TypeScript

#### `frontend_example/`
- **VideoGenerator.tsx**: React component with real-time updates
- **appwrite.ts**: Service layer for Appwrite integration

#### Features:
1. **Real-time Subscriptions**: Automatic updates without polling
2. **Progress Bar**: Visual representation of generation progress
3. **Scene Tracking**: Live status for each scene
4. **Download Link**: Automatic display when video is ready

## Database Schema

### Videos Collection
```typescript
{
  topic: string,
  description?: string,
  status: 'queued' | 'planning' | 'rendering' | 'completed' | 'failed',
  progress?: number,              // 0-100
  current_scene?: number,         // Currently rendering scene
  scene_count: number,
  combined_video_url?: string,
  error_message?: string,
  created_at: datetime,
  updated_at: datetime
}
```

### Scenes Collection
```typescript
{
  video_id: string,
  scene_number: number,
  status: 'planned' | 'coded' | 'rendered' | 'failed',
  video_url?: string,
  code_url?: string,
  error_message?: string,
  created_at: datetime,
  updated_at: datetime
}
```

## Deployment

### 1. Deploy Appwrite Function

```bash
# From the project root
appwrite functions createDeployment \
    --functionId=video_generation \
    --entrypoint='main.py' \
    --code='./appwrite_functions/video_generation' \
    --activate=true
```

### 2. Set Environment Variables

In Appwrite Console, configure these variables for the function:
- `APPWRITE_API_KEY`
- `APPWRITE_PROJECT_ID`
- `APPWRITE_ENDPOINT`
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `mem0_api_key`

### 3. Setup Database

Run the setup script to create collections:
```python
python scripts/setup_appwrite_db.py
```

### 4. Configure Frontend

```bash
cd frontend_example
cp .env.example .env.local
# Edit .env.local with your Appwrite project details
npm install
npm run dev
```

## Usage Flow

1. **User submits request**: Topic and description sent to Appwrite Function
2. **Function returns immediately**: Video ID returned for tracking
3. **Background processing**: Function generates video asynchronously
4. **Real-time updates**: Frontend receives live status updates
5. **Completion**: Download link appears when video is ready

## Benefits

### For Users
- No waiting for long-running processes
- Can close browser and return later
- Real-time progress visibility
- Multiple videos can be generated simultaneously

### For Developers
- Scalable architecture
- Separation of concerns
- Easy monitoring and debugging
- Built-in error recovery

## Example Usage

```typescript
// Frontend code
const result = await generateVideo("Newton's Laws", "Explain all three laws");
// Returns immediately with videoId

// Subscribe to updates
subscribeToVideo(result.videoId, (video) => {
  console.log(`Status: ${video.status}, Progress: ${video.progress}%`);
});
```

## Monitoring

- **Appwrite Console**: View function logs and execution history
- **Database**: Track all video generation attempts
- **Real-time Dashboard**: Build custom monitoring using subscriptions

## Error Handling

The system handles errors gracefully:
- Failed scenes can be retried
- Partial videos can be recovered
- Error messages are stored for debugging
- Users are notified in real-time

## Future Enhancements

1. **Queue Management**: Priority queues for premium users
2. **Webhooks**: Notify external systems on completion
3. **Batch Processing**: Generate multiple videos in one request
4. **Resume Capability**: Continue from failed scenes
5. **Cost Estimation**: Predict generation time and resources 