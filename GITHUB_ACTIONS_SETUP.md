# GitHub Actions Video Rendering Setup

This guide shows how to set up free cloud video rendering using GitHub Actions.

## Overview

The system works in two parts:
1. **Appwrite Function**: Handles requests and queues videos (no heavy dependencies)
2. **GitHub Actions**: Renders videos using manim in the cloud (free)

## Setup Steps

### 1. GitHub Repository Setup

Make sure your repository is public or has GitHub Actions minutes available.

### 2. GitHub Repository Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
APPWRITE_ENDPOINT=https://your-appwrite-endpoint
APPWRITE_PROJECT_ID=your-project-id
APPWRITE_API_KEY=your-api-key
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key (optional)
```

### 3. Appwrite Function Environment Variables

Add these to your Appwrite Function environment:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx (Personal Access Token)
GITHUB_REPO=username/repository-name
```

#### Creating GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` and `actions`
4. Copy the token and add to Appwrite Function

### 4. Database Setup

Your Appwrite database should have:

**Database ID**: `video_metadata`

**Collections**:
- `videos` - stores video metadata and status
- `scenes` - stores scene information

**Videos Collection Attributes**:
```json
{
  "topic": "string",
  "description": "string", 
  "owner_id": "string",
  "session_id": "string",
  "status": "string",
  "progress": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "error_message": "string"
}
```

### 5. How It Works

1. **User Request**: Frontend calls Appwrite Function with video topic
2. **Queue Video**: Function creates database record with status "queued"
3. **Trigger Workflow**: Function triggers GitHub Actions workflow
4. **Render Video**: GitHub Actions runs manim and generates video
5. **Upload Results**: Video is uploaded back to Appwrite Storage
6. **Update Status**: Database is updated with "completed" status

### 6. Monitoring

- Check GitHub Actions tab for workflow runs
- Monitor Appwrite database for video status
- View logs in GitHub Actions for debugging

### 7. Triggering Options

**Automatic**: Videos are processed every 5 minutes by scheduled workflow

**Manual**: Trigger specific video by workflow dispatch

**Immediate**: When GitHub token is configured, videos trigger immediately

### 8. Cost

- **GitHub Actions**: Free for public repos, 2000 minutes/month for private
- **Appwrite**: Based on your plan
- **Storage**: Appwrite storage costs for video files

### 9. Scaling

- Process up to 5 videos per workflow run
- Runs can process videos concurrently
- Total workflow time limited to 6 hours per run

### 10. Troubleshooting

**Videos stuck in queue**: Check GitHub Actions logs
**Workflow not triggering**: Verify GitHub token and repo name
**Build failures**: Check Python dependencies in workflow
**Upload failures**: Verify Appwrite credentials

## Example API Usage

```javascript
// Call Appwrite Function to queue video
const response = await functions.createExecution(
  'video-generation-function-id',
  JSON.stringify({
    topic: "Pythagorean Theorem",
    description: "Explain the mathematical proof",
    userId: "user123"
  })
);

// Response includes video ID for tracking
const videoId = response.response.videoId;
```

## Status Flow

```
queued → processing → planning → ready_for_render → queued_for_render → rendering → completed
                                                                                  ↓
                                                                               failed
```

This setup gives you free, scalable video rendering without managing servers! 