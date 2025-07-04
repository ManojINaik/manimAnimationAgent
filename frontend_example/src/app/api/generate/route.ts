import { NextRequest, NextResponse } from 'next/server';
import { Client, Databases, ID } from 'node-appwrite';

// GitHub dispatch helper
async function triggerGithubWorkflow(videoId: string) {
  const owner = process.env.GITHUB_REPO_OWNER!; // e.g. "ManojINaik"
  const repo = process.env.GITHUB_REPO_NAME!;   // e.g. "manimAnimationAgent"
  const workflow = process.env.GITHUB_WORKFLOW_FILENAME || 'video-renderer.yml';
  const ghPat = process.env.GH_PAT!; // Personal Access Token with 'workflow' permission

  console.log('Triggering GitHub workflow:', { owner, repo, workflow, videoId });
  console.log('GitHub PAT available:', !!ghPat);

  const maxRetries = 3;
  const baseDelay = 1000; // 1 second
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`GitHub dispatch attempt ${attempt}/${maxRetries}`);
      
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutMs = Number(process.env.GITHUB_API_TIMEOUT_MS || 30000); // default 30s if not set
      console.log(`GitHub fetch timeout set to ${timeoutMs} ms`);
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
      
      const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`, {
        method: 'POST',
        headers: {
          Authorization: `token ${ghPat}`,
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.github+json',
          'User-Agent': 'Manim-Animation-Agent/1.0',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: { video_id: videoId },
        }),
        signal: controller.signal,
      }).finally(() => clearTimeout(timeoutId));
      
      console.log('GitHub API response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('GitHub API error:', errorText);
        throw new Error(`GitHub API failed: ${response.status} - ${errorText}`);
      }
      
      console.log('✅ Successfully triggered GitHub workflow');
      return; // Success, exit retry loop
    } catch (err: any) {
      console.error(`❌ GitHub dispatch attempt ${attempt} failed:`, err);
      
      const isNetworkError = err.code === 'ETIMEDOUT' || 
                           err.code === 'ECONNRESET' || 
                           err.name === 'AbortError' ||
                           err.message?.includes('fetch failed') ||
                           err.message?.includes('network') ||
                           err.message?.includes('timeout');
      
      if (attempt === maxRetries || !isNetworkError) {
        // Last attempt or non-retryable error
        console.error('❌ All GitHub dispatch attempts failed or non-retryable error');
        return; // Exit without throwing to avoid blocking document creation
      }
      
      // Wait before retry with exponential backoff
      const delay = baseDelay * Math.pow(2, attempt - 1);
      console.log(`⏳ Waiting ${delay}ms before retry...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
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
  console.log('📥 API /generate POST request received at:', new Date().toISOString());
  
  // Check required environment variables
  const requiredEnvVars = ['GITHUB_REPO_OWNER', 'GITHUB_REPO_NAME', 'GH_PAT'];
  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missingVars.length > 0) {
    console.error('Missing environment variables:', missingVars);
  }

  try {
    const body = await request.json();
    const { topic, description } = body;
    
    console.log('📋 Request payload:', { topic, description });

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
        scene_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    );

    // Trigger GitHub Actions workflow *synchronously* so the serverless function
    // doesn't exit before the request completes, which caused intermittent
    // failures in production. We still swallow errors so the client receives a
    // successful response as long as the DB document was created.
    try {
      await triggerGithubWorkflow((videoDocument as any).$id);
    } catch (err) {
      console.error('❌ GitHub workflow trigger ultimately failed after all retries:', err);
      // Proceed without throwing – we don't want to block the response if the
      // GitHub API is temporarily unavailable.
    }

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