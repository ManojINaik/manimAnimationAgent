import { Client, Databases, Functions, Account, Storage, RealtimeResponseEvent } from 'appwrite';

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
    status: 'queued' | 'planning' | 'rendering' | 'completed' | 'failed';
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
    // 1. Try hitting the internal Next.js API route – this handles
    // longer timeouts and avoids CORS issues when the FastAPI backend
    // runs locally.
    try {
        const apiRes = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, description })
        });

        const apiJson = await apiRes.json();
        if (apiRes.ok && apiJson.success) {
            return {
                success: true,
                videoId: apiJson.task_id || apiJson.videoId,
            };
        }

        // If the internal API returns an error, continue to fallback
        console.warn('Internal API call failed; attempting Appwrite function:', apiJson.error);
    } catch (err) {
        console.warn('Internal API call error; attempting Appwrite function:', err);
    }

    // 2. If internal API not working, and BACKEND URL is explicitly defined,
    // attempt direct backend call (useful for production deployments with
    // public FastAPI endpoint).
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

    if (backendUrl) {
        try {
            const res = await fetch(`${backendUrl}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, context: description })
            });

            const json = await res.json();
            if (!res.ok) throw new Error(json.message || 'Request failed');

            return {
                success: json.success,
                videoId: json.task_id || json.videoId,
                error: json.error
            };
        } catch (err) {
            console.warn('Direct backend call failed, falling back to Appwrite Function:', err);
            // fall through to function call
        }
    }

    // 3. Fallback: invoke the Appwrite cloud function
    try {
        const response = await functions.createExecution(
            VIDEO_FUNCTION_ID,
            JSON.stringify({ topic, description }),
            false // async execution
        );

        const rawResponse = (response as any).response; // response type from SDK is any

        let parsed: any = { success: false };
        try {
            parsed = rawResponse ? JSON.parse(rawResponse) : {};
        } catch (e) {
            console.warn('Unable to parse Appwrite function response, returning raw execution object');
        }

        return {
            success: parsed.success ?? false,
            videoId: parsed.videoId || parsed.task_id,
            error: parsed.error
        };
    } catch (error) {
        console.error('Failed to generate video:', error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Failed to generate video'
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
    return storage.getFileView(bucketId, fileId).toString();
} 