# Connect Any Next.js Frontend to Manim Video Generation Backend

This guide explains how to connect any Next.js frontend application to the Manim video generation backend API endpoints.

## Table of Contents
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [API Endpoints](#api-endpoints)
- [Frontend Integration](#frontend-integration)
- [Real-time Updates](#real-time-updates)
- [Error Handling](#error-handling)
- [Complete Examples](#complete-examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies

```bash
npm install appwrite
# For TypeScript projects
npm install --save-dev @types/node
```

### 2. Environment Variables

Create `.env.local` in your Next.js project root:

```env
# Appwrite Configuration (Required)
NEXT_PUBLIC_APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
NEXT_PUBLIC_APPWRITE_PROJECT_ID=your_project_id_here

# Server-side API Key (Required for API routes)
APPWRITE_API_KEY=your_server_api_key_here

# GitHub Integration (Required for video generation)
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=your_repo_name
GH_PAT=your_github_personal_access_token
GITHUB_WORKFLOW_FILENAME=video-renderer.yml

# Optional: Backend URL for status checking
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Optional: GitHub API timeout (default: 30000ms)
GITHUB_API_TIMEOUT_MS=30000
```

### 3. Appwrite Setup

Ensure your Appwrite project has:
- Database: `video_metadata`
- Collections: `videos`, `scenes`
- Storage buckets: `final_videos`, `scene_videos`

## Environment Setup

### Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_APPWRITE_ENDPOINT` | Appwrite server endpoint | ✅ | `https://cloud.appwrite.io/v1` |
| `NEXT_PUBLIC_APPWRITE_PROJECT_ID` | Your Appwrite project ID | ✅ | `64f2a8b4c123456789` |
| `APPWRITE_API_KEY` | Server-side API key | ✅ | `your_secret_api_key` |
| `GITHUB_REPO_OWNER` | GitHub repository owner | ✅ | `username` |
| `GITHUB_REPO_NAME` | GitHub repository name | ✅ | `manimAnimationAgent` |
| `GH_PAT` | GitHub Personal Access Token | ✅ | `ghp_xxxxx` |
| `GITHUB_WORKFLOW_FILENAME` | Workflow file name | ❌ | `video-renderer.yml` |
| `NEXT_PUBLIC_BACKEND_URL` | Backend service URL | ❌ | `http://localhost:8000` |
| `GITHUB_API_TIMEOUT_MS` | GitHub API timeout | ❌ | `30000` |

### GitHub Personal Access Token Setup

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token with `workflow` and `repo` permissions
3. Copy the token to `GH_PAT` environment variable

## API Endpoints

### 1. Generate Video - `POST /api/generate`

Triggers video generation by creating an Appwrite document and starting GitHub workflow.

**Request:**
```typescript
interface GenerateRequest {
  topic: string;        // Required: Video topic
  description?: string; // Optional: Additional context
}
```

**Response:**
```typescript
interface GenerateResponse {
  success: boolean;
  videoId?: string;     // Appwrite document ID
  message?: string;     // Success message
  error?: string;       // Error message if failed
}
```

**Example:**
```typescript
const response = await fetch('/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: "Newton's Laws of Motion",
    description: "Explain with visual demonstrations"
  })
});

const result = await response.json();
if (result.success) {
  console.log('Video ID:', result.videoId);
}
```

### 2. Check Status - `GET /api/status/[taskId]`

Checks the status of a video generation task (proxy to backend).

**Response:**
```typescript
interface StatusResponse {
  status?: string;      // Current status
  progress?: number;    // Progress percentage
  message?: string;     // Status message
  video_id?: string;    // Video ID when available
  error?: string;       // Error if failed
}
```

**Example:**
```typescript
const response = await fetch(`/api/status/${taskId}`);
const status = await response.json();
console.log('Current status:', status.status);
```

## Frontend Integration

### 1. Create Appwrite Client Service

Create `lib/appwrite.ts`:

```typescript
import { Client, Databases, Storage, Query } from 'appwrite';

// Initialize client
const client = new Client()
  .setEndpoint(process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT!)
  .setProject(process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID!);

export const databases = new Databases(client);
export const storage = new Storage(client);

// Constants
export const DATABASE_ID = 'video_metadata';
export const VIDEOS_COLLECTION_ID = 'videos';
export const SCENES_COLLECTION_ID = 'scenes';
export const FINAL_VIDEOS_BUCKET_ID = 'final_videos';
export const SCENE_VIDEOS_BUCKET_ID = 'scene_videos';

// Types
export interface VideoDocument {
  $id: string;
  topic: string;
  description?: string;
  status: 'queued' | 'planning' | 'rendering' | 'completed' | 'failed';
  progress?: number;
  scene_count: number;
  combined_video_url?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface SceneDocument {
  $id: string;
  video_id: string;
  scene_number: number;
  status: 'planned' | 'coded' | 'rendered' | 'failed';
  video_url?: string;
  duration?: number;
  created_at: string;
  updated_at: string;
}
```

### 2. Generate Video Function

```typescript
// lib/api.ts
export async function generateVideo(topic: string, description: string = '') {
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, description })
    });

    const result = await response.json();
    
    if (!response.ok || !result.success) {
      throw new Error(result.error || 'Failed to generate video');
    }

    return result;
  } catch (error) {
    console.error('Video generation failed:', error);
    throw error;
  }
}
```

### 3. Get Video Document

```typescript
// lib/appwrite.ts
export async function getVideo(videoId: string): Promise<VideoDocument | null> {
  try {
    const response = await databases.getDocument(
      DATABASE_ID,
      VIDEOS_COLLECTION_ID,
      videoId
    );
    return response as unknown as VideoDocument;
  } catch (error) {
    console.error('Failed to get video:', error);
    return null;
  }
}
```

### 4. Get Video Scenes

```typescript
// lib/appwrite.ts
export async function getVideoScenes(videoId: string): Promise<SceneDocument[]> {
  try {
    const response = await databases.listDocuments(
      DATABASE_ID,
      SCENES_COLLECTION_ID,
      [Query.equal('video_id', videoId)]
    );
    return response.documents as unknown as SceneDocument[];
  } catch (error) {
    console.error('Failed to get scenes:', error);
    return [];
  }
}
```

### 5. Get Storage File URL

```typescript
// lib/appwrite.ts
export function getFileUrl(bucketId: string, fileId: string): string {
  try {
    return storage.getFileView(bucketId, fileId).toString();
  } catch (error) {
    console.error('Failed to generate file URL:', error);
    return '';
  }
}
```

## Real-time Updates

### Setup Real-time Subscriptions

```typescript
// lib/realtime.ts
import { RealtimeResponseEvent } from 'appwrite';

export function subscribeToVideo(
  videoId: string,
  onUpdate: (video: VideoDocument) => void
): () => void {
  const channel = `databases.${DATABASE_ID}.collections.${VIDEOS_COLLECTION_ID}.documents.${videoId}`;
  
  const unsubscribe = client.subscribe(
    channel,
    (response: RealtimeResponseEvent<VideoDocument>) => {
      if (response.events.includes('databases.*.collections.*.documents.*.update')) {
        onUpdate(response.payload);
      }
    }
  );

  return unsubscribe;
}

export function subscribeToVideoScenes(
  videoId: string,
  onUpdate: (scene: SceneDocument) => void
): () => void {
  const channel = `databases.${DATABASE_ID}.collections.${SCENES_COLLECTION_ID}.documents`;
  
  const unsubscribe = client.subscribe(
    channel,
    (response: RealtimeResponseEvent<SceneDocument>) => {
      if (response.payload.video_id === videoId) {
        onUpdate(response.payload);
      }
    }
  );

  return unsubscribe;
}
```

### React Hook for Video Status

```typescript
// hooks/useVideoStatus.ts
import { useState, useEffect } from 'react';
import { VideoDocument, SceneDocument } from '../lib/appwrite';
import { subscribeToVideo, subscribeToVideoScenes } from '../lib/realtime';

export function useVideoStatus(videoId: string | null) {
  const [video, setVideo] = useState<VideoDocument | null>(null);
  const [scenes, setScenes] = useState<SceneDocument[]>([]);

  useEffect(() => {
    if (!videoId) return;

    // Subscribe to video updates
    const unsubscribeVideo = subscribeToVideo(videoId, (updatedVideo) => {
      setVideo(updatedVideo);
    });

    // Subscribe to scene updates
    const unsubscribeScenes = subscribeToVideoScenes(videoId, (updatedScene) => {
      setScenes(prev => {
        const existingIndex = prev.findIndex(s => s.$id === updatedScene.$id);
        if (existingIndex >= 0) {
          const newScenes = [...prev];
          newScenes[existingIndex] = updatedScene;
          return newScenes;
        }
        return [...prev, updatedScene].sort((a, b) => a.scene_number - b.scene_number);
      });
    });

    return () => {
      unsubscribeVideo();
      unsubscribeScenes();
    };
  }, [videoId]);

  return { video, scenes };
}
```

## Error Handling

### Connection Testing

```typescript
// lib/appwrite.ts
export async function testConnection(): Promise<{
  success: boolean;
  error?: string;
  endpoint?: string;
  projectId?: string;
}> {
  try {
    const endpoint = process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT;
    const projectId = process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID;
    
    if (!endpoint || !projectId) {
      throw new Error('Missing Appwrite configuration');
    }
    
    return { success: true, endpoint, projectId };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Configuration error',
      endpoint: process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT,
      projectId: process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID
    };
  }
}
```

### Error Boundary Component

```tsx
// components/ErrorBoundary.tsx
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-lg font-semibold text-red-800">Something went wrong</h2>
          <p className="mt-2 text-red-600">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Complete Examples

### 1. Video Generator Component

```tsx
// components/VideoGenerator.tsx
import React, { useState } from 'react';
import { generateVideo } from '../lib/api';
import { useVideoStatus } from '../hooks/useVideoStatus';

export default function VideoGenerator() {
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { video, scenes } = useVideoStatus(videoId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isGenerating || !topic) return;

    setError(null);
    setIsGenerating(true);

    try {
      const result = await generateVideo(topic, description);
      setVideoId(result.videoId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Topic</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Newton's Laws of Motion"
            className="w-full p-3 border rounded-lg"
            required
            disabled={isGenerating}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Description (Optional)</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Additional context..."
            className="w-full p-3 border rounded-lg"
            rows={3}
            disabled={isGenerating}
          />
        </div>

        <button
          type="submit"
          disabled={isGenerating || !topic}
          className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg disabled:opacity-50"
        >
          {isGenerating ? 'Generating...' : 'Generate Video'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {video && (
        <div className="mt-6 space-y-4">
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold">{video.topic}</h3>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                {video.status}
              </span>
              {video.progress && (
                <span className="text-sm text-gray-600">{video.progress}%</span>
              )}
            </div>
          </div>

          {scenes.length > 0 && (
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-2">Scenes ({scenes.length})</h4>
              <div className="grid gap-2">
                {scenes.map((scene) => (
                  <div key={scene.$id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span>Scene {scene.scene_number}</span>
                    <span className="text-xs px-2 py-1 rounded bg-gray-200">
                      {scene.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {video.status === 'completed' && video.combined_video_url && (
            <div className="p-4 border-2 border-green-200 rounded-lg bg-green-50">
              <h4 className="font-medium text-green-800 mb-2">Video Ready!</h4>
              <video controls className="w-full rounded">
                <source src={getFileUrl(FINAL_VIDEOS_BUCKET_ID, video.combined_video_url)} type="video/mp4" />
              </video>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 2. Video History Component

```tsx
// components/VideoHistory.tsx
import React, { useState, useEffect } from 'react';
import { storage, FINAL_VIDEOS_BUCKET_ID, getFileUrl } from '../lib/appwrite';

interface VideoFile {
  $id: string;
  name: string;
  sizeOriginal: number;
  $createdAt: string;
}

export default function VideoHistory() {
  const [files, setFiles] = useState<VideoFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await storage.listFiles(FINAL_VIDEOS_BUCKET_ID);
      setFiles(response.files as VideoFile[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading videos...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">{error}</p>
        <button onClick={loadFiles} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Video History ({files.length})</h2>
      
      {files.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No videos found. Create your first video!
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {files.map((file) => (
            <div key={file.$id} className="border rounded-lg p-4">
              <h3 className="font-medium mb-2">{file.name}</h3>
              <p className="text-sm text-gray-600 mb-4">
                {(file.sizeOriginal / 1024 / 1024).toFixed(2)} MB
              </p>
              <p className="text-xs text-gray-500 mb-4">
                {new Date(file.$createdAt).toLocaleDateString()}
              </p>
              
              <div className="space-y-2">
                <a
                  href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, file.$id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full text-center py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Watch
                </a>
                <a
                  href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, file.$id)}
                  download={file.name}
                  className="block w-full text-center py-2 px-4 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Download
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 3. Main App Integration

```tsx
// pages/index.tsx or app/page.tsx
import React, { useState } from 'react';
import VideoGenerator from '../components/VideoGenerator';
import VideoHistory from '../components/VideoHistory';
import { ErrorBoundary } from '../components/ErrorBoundary';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generator' | 'history'>('generator');

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold">AI Video Generator</h1>
            <p className="text-gray-600 mt-2">Create educational videos with AI</p>
          </div>

          <div className="flex justify-center mb-8">
            <div className="flex rounded-lg border bg-white p-1">
              <button
                onClick={() => setActiveTab('generator')}
                className={`px-6 py-2 rounded-md transition-colors ${
                  activeTab === 'generator'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Create Video
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-6 py-2 rounded-md transition-colors ${
                  activeTab === 'history'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                History
              </button>
            </div>
          </div>

          {activeTab === 'generator' ? <VideoGenerator /> : <VideoHistory />}
        </div>
      </div>
    </ErrorBoundary>
  );
}
```

## Troubleshooting

### Common Issues

1. **"Missing Appwrite configuration"**
   - Verify `.env.local` file exists and contains required variables
   - Check variable names match exactly (including `NEXT_PUBLIC_` prefix)

2. **"GitHub workflow trigger failed"**
   - Verify GitHub Personal Access Token has correct permissions
   - Check repository owner/name are correct
   - Ensure workflow file exists in `.github/workflows/`

3. **"Failed to get video files"**
   - Verify Appwrite project has `final_videos` storage bucket
   - Check bucket permissions allow read access

4. **Real-time updates not working**
   - Verify Appwrite project has realtime enabled
   - Check browser console for connection errors
   - Ensure database/collection names match exactly

### Debug Mode

Add this to your component for debugging:

```typescript
const [debug, setDebug] = useState(false);

// Add this button to toggle debug info
<button onClick={() => setDebug(!debug)}>
  {debug ? 'Hide' : 'Show'} Debug Info
</button>

{debug && (
  <pre className="mt-4 p-4 bg-gray-100 rounded text-xs overflow-auto">
    {JSON.stringify({
      endpoint: process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT,
      projectId: process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID,
      video,
      scenes
    }, null, 2)}
  </pre>
)}
```

### Environment Validation

Create a validation utility:

```typescript
// lib/validateEnv.ts
export function validateEnvironment(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  const required = [
    'NEXT_PUBLIC_APPWRITE_ENDPOINT',
    'NEXT_PUBLIC_APPWRITE_PROJECT_ID'
  ];

  required.forEach(key => {
    if (!process.env[key]) {
      errors.push(`Missing required environment variable: ${key}`);
    }
  });

  return { valid: errors.length === 0, errors };
}
```

## Support

For additional help:
1. Check the [Appwrite documentation](https://appwrite.io/docs)
2. Verify your GitHub Actions workflow configuration
3. Test environment variables in browser console
4. Check network tab for API call errors

## Next Steps

After integration:
1. Customize the UI components to match your design
2. Add authentication if needed
3. Implement additional features like video sharing
4. Add analytics and monitoring
5. Deploy to your preferred hosting platform

---

This integration guide provides everything needed to connect any Next.js frontend to the Manim video generation backend. The modular approach allows you to customize components while maintaining core functionality. 