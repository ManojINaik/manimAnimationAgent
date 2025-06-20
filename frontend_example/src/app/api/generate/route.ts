import { NextRequest, NextResponse } from 'next/server';
import { Client, Databases, ID } from 'node-appwrite';

// GitHub dispatch helper
async function triggerGithubWorkflow(videoId: string) {
  const owner = process.env.GITHUB_REPO_OWNER!; // e.g. "ManojINaik"
  const repo = process.env.GITHUB_REPO_NAME!;   // e.g. "manimAnimationAgent"
  const workflow = process.env.GITHUB_WORKFLOW_FILENAME || 'video-renderer.yml';
  const ghPat = process.env.GH_PAT!; // Personal Access Token with 'workflow' permission

  try {
    await fetch(`https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`, {
      method: 'POST',
      headers: {
        Authorization: `token ${ghPat}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json',
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: { video_id: videoId },
      }),
    });
  } catch (err) {
    console.error('Failed to dispatch GitHub workflow', err);
  }
}

// Initialize Appwrite client with server-side API key (never exposed to the browser)
const client = new Client()
  .setEndpoint(process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT!)
  .setProject(process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID!)
  .setKey(process.env.APPWRITE_API_KEY!);

const databases = new Databases(client);

// Database and collection identifiers
const DATABASE_ID = 'video_metadata';
const VIDEOS_COLLECTION_ID = 'videos';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { topic, description } = body;

    if (!topic) {
      return NextResponse.json(
        { success: false, error: 'Topic is required' },
        { status: 400 },
      );
    }

    // Create a new video document with status queued_for_render for the worker to pick up
    const videoDocument = await databases.createDocument(
      DATABASE_ID,
      VIDEOS_COLLECTION_ID,
      ID.unique(),
      {
        topic,
        description: description || `Educational video about ${topic}`,
        status: 'queued_for_render',
      },
    );

    // Fire GitHub Actions workflow asynchronously (do not await)
    triggerGithubWorkflow((videoDocument as any).$id);

    return NextResponse.json({
      success: true,
      videoId: (videoDocument as any).$id,
      message: 'Video generation task has been successfully queued.',
    });
  } catch (error: any) {
    console.error('Error creating video document in Appwrite:', error);
    return NextResponse.json(
      {
        success: false,
        error: error?.message || 'Failed to create video task in the database.',
      },
      { status: 500 },
    );
  }
} 