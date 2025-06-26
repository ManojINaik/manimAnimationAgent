import { Client, Databases, Functions, Account, Storage, RealtimeResponseEvent, Query } from 'appwrite';

// Initialize Appwrite client
const client = new Client()
    .setEndpoint(process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT || 'https://cloud.appwrite.io/v1')
    .setProject(process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID || '');

// Initialize services
export const databases = new Databases(client);
export const functions = new Functions(client);
export const account = new Account(client);
export const storage = new Storage(client);

// Database and collection IDs
export const DATABASE_ID = 'video_metadata';
export const VIDEOS_COLLECTION_ID = 'videos';
export const SCENES_COLLECTION_ID = 'scenes';
export const VIDEO_FUNCTION_ID = 'video_generation';

// Storage bucket IDs
export const FINAL_VIDEOS_BUCKET_ID = 'final_videos';
export const SCENE_VIDEOS_BUCKET_ID = 'scene_videos';

// Types
export interface VideoDocument {
    $id: string;
    topic: string;
    description?: string;
    status: 'queued' | 'planning' | 'rendering' | 'completed' | 'failed' | 'queued_for_render';
    progress?: number;
    current_scene?: number;
    scene_count: number;
    owner_id?: string;
    session_id?: string;
    combined_video_url?: string;
    subtitles_url?: string;
    error_message?: string;
    total_duration?: number;
    created_at: string;
    updated_at: string;
}

export interface SceneDocument {
    $id: string;
    video_id: string;
    scene_number: number;
    status: 'planned' | 'coded' | 'rendered' | 'failed';
    scene_plan?: string;
    storyboard?: string;
    technical_plan?: string;
    generated_code?: string;
    video_url?: string;
    code_url?: string;
    duration?: number;
    error_message?: string;
    created_at: string;
    updated_at: string;
}

// Subscribe to realtime updates for a video
export function subscribeToVideo(
    videoId: string, 
    onUpdate: (video: VideoDocument) => void
): () => void {
    const channel = `databases.${DATABASE_ID}.collections.${VIDEOS_COLLECTION_ID}.documents.${videoId}`;
    
    const unsubscribe = client.subscribe(channel, (response: RealtimeResponseEvent<VideoDocument>) => {
        if (response.events.includes('databases.*.collections.*.documents.*.update')) {
            onUpdate(response.payload);
        }
    });

    return unsubscribe;
}

// Subscribe to realtime updates for video scenes
export function subscribeToVideoScenes(
    videoId: string,
    onUpdate: (scene: SceneDocument) => void
): () => void {
    const channel = `databases.${DATABASE_ID}.collections.${SCENES_COLLECTION_ID}.documents`;
    
    const unsubscribe = client.subscribe(channel, (response: RealtimeResponseEvent<SceneDocument>) => {
        if (response.payload.video_id === videoId) {
            onUpdate(response.payload);
        }
    });

    return unsubscribe;
}

// Generate video using Appwrite Function
export async function generateVideo(topic: string, description: string): Promise<{
    success: boolean;
    videoId?: string;
    error?: string;
}> {
    try {
        console.log('🚀 generateVideo called with:', { topic, description, timestamp: new Date().toISOString() });
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, description }),
        });

        const json = await response.json();

        if (!response.ok || !json.success) {
            throw new Error(json.error || 'Failed to queue video generation.');
        }

        return {
            success: true,
            videoId: json.videoId,
        };
    } catch (error) {
        console.error('Error in generateVideo service:', error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'An unknown error occurred.',
        };
    }
}

// Poll for task status and extract video_id when available
export async function getTaskStatus(taskId: string): Promise<{
    success: boolean;
    status?: string;
    progress?: number;
    message?: string;
    video_id?: string;
    error?: string;
}> {
    try {
        const response = await fetch(`/api/status/${taskId}`);
        if (!response.ok) {
            throw new Error('Failed to get task status');
        }
        
        const data = await response.json();
        return {
            success: true,
            status: data.status,
            progress: data.progress,
            message: data.message,
            video_id: data.video_id,
            error: data.error
        };
    } catch (error) {
        console.error('Failed to get task status:', error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Failed to get task status'
        };
    }
}

// Get video document
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

// Get video scenes
export async function getVideoScenes(videoId: string): Promise<SceneDocument[]> {
    try {
        const response = await databases.listDocuments(
            DATABASE_ID,
            SCENES_COLLECTION_ID,
            [`video_id="${videoId}"`]
        );
        return response.documents as unknown as SceneDocument[];
    } catch (error) {
        console.error('Failed to get video scenes:', error);
        return [];
    }
}

// Get file URL from storage
export function getFileUrl(bucketId: string, fileId: string): string {
    try {
        console.log('🎬 Getting file URL for:', { bucketId, fileId });
        const url = storage.getFileView(bucketId, fileId).toString();
        console.log('✅ Generated URL:', url);
        return url;
    } catch (error) {
        console.error('❌ Failed to generate file URL:', { bucketId, fileId, error });
        return '';
    }
}

// Check if file exists in storage
export async function checkFileExists(bucketId: string, fileId: string): Promise<boolean> {
    try {
        await storage.getFile(bucketId, fileId);
        console.log('✅ File exists:', { bucketId, fileId });
        return true;
    } catch (error) {
        console.error('❌ File does not exist or access denied:', { bucketId, fileId, error });
        return false;
    }
}

// Test connection to Appwrite
export async function testConnection(): Promise<{
    success: boolean;
    error?: string;
    endpoint?: string;
    projectId?: string;
}> {
    try {
        console.log('🔌 Testing Appwrite connection...');
        console.log('Endpoint:', process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT);
        console.log('Project ID:', process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID);
        
        // Just return the configuration for now
        const endpoint = process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT;
        const projectId = process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID;
        
        if (!endpoint || !projectId) {
            throw new Error('Missing Appwrite configuration');
        }
        
        console.log('✅ Configuration looks good');
        
        return {
            success: true,
            endpoint,
            projectId
        };
    } catch (error) {
        console.error('❌ Configuration check failed:', error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown configuration error',
            endpoint: process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT,
            projectId: process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID
        };
    }
}

// Get all videos for history
export async function getAllVideos(): Promise<VideoDocument[]> {
    try {
        console.log('🔍 Fetching all videos from database...');
        console.log('Database ID:', DATABASE_ID);
        console.log('Collection ID:', VIDEOS_COLLECTION_ID);
        
        // Test connection first
        const connectionTest = await testConnection();
        if (!connectionTest.success) {
            throw new Error(`Connection failed: ${connectionTest.error}`);
        }
        
        const response = await databases.listDocuments(
            DATABASE_ID,
            VIDEOS_COLLECTION_ID,
            [Query.orderDesc('$createdAt')] // Use proper Query object
        );
        
        console.log('✅ Successfully fetched videos:', response.documents.length);
        console.log('Videos:', response.documents);
        
        return response.documents as unknown as VideoDocument[];
    } catch (error) {
        console.error('❌ Failed to get all videos:', error);
        console.error('Error details:', {
            message: error instanceof Error ? error.message : 'Unknown error',
            name: error instanceof Error ? error.name : 'Unknown',
            stack: error instanceof Error ? error.stack : 'No stack trace'
        });
        
        // Return empty array instead of throwing to prevent loading loop
        return [];
    }
}

// Get all files from final_videos storage bucket
export async function getAllVideoFiles(): Promise<any[]> {
    try {
        console.log('📁 Fetching all files from final_videos bucket...');
        
        const response = await storage.listFiles(FINAL_VIDEOS_BUCKET_ID);
        
        console.log('✅ Successfully fetched files from storage:', response.files.length);
        console.log('Files:', response.files);
        
        return response.files;
    } catch (error) {
        console.error('❌ Failed to get files from storage:', error);
        console.error('Error details:', {
            message: error instanceof Error ? error.message : 'Unknown error',
            name: error instanceof Error ? error.name : 'Unknown',
            stack: error instanceof Error ? error.stack : 'No stack trace'
        });
        
        return [];
    }
} 