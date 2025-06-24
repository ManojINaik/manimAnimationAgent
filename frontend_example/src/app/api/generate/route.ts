import { NextRequest, NextResponse } from 'next/server';
import { Client, Databases, ID } from 'node-appwrite';

// CircleCI dispatch helper
async function triggerCircleCIWorkflow(videoId: string) {
  const token = process.env.CIRCLECI_TOKEN;
  const org = process.env.CIRCLECI_ORG || 'gh/your-username'; // e.g., 'gh/ManojINaik'
  const project = process.env.CIRCLECI_PROJECT || 'manimAnimationAgent';
  const branch = process.env.CIRCLECI_BRANCH || 'main';

  if (!token) {
    throw new Error('CircleCI token not configured');
  }

  console.log('Triggering CircleCI workflow:', { org, project, videoId });

  const maxRetries = 3;
  const baseDelay = 1000; // 1 second
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`CircleCI dispatch attempt ${attempt}/${maxRetries}`);
      
      const controller = new AbortController();
      const timeoutMs = Number(process.env.CIRCLECI_API_TIMEOUT_MS || 30000);
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
      
      const response = await fetch(`https://circleci.com/api/v2/project/${org}/${project}/pipeline`, {
        method: 'POST',
        headers: {
          'Circle-Token': token,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          branch: branch,
          parameters: {
            workflow: 'video-rendering',
            video_id: videoId
          }
        }),
        signal: controller.signal,
      }).finally(() => clearTimeout(timeoutId));
      
      console.log('CircleCI API response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('CircleCI API error:', errorText);
        throw new Error(`CircleCI API failed: ${response.status} - ${errorText}`);
      }
      
      const result = await response.json();
      console.log('✅ Successfully triggered CircleCI workflow');
      console.log(`   Pipeline ID: ${result.id}`);
      console.log(`   Pipeline Number: ${result.number}`);
      console.log(`   Dashboard: https://app.circleci.com/pipelines/${org}/${project}/${result.number}`);
      return result;
    } catch (err: any) {
      console.error(`❌ CircleCI dispatch attempt ${attempt} failed:`, err);
      
      const isNetworkError = err.code === 'ETIMEDOUT' || 
                           err.code === 'ECONNRESET' || 
                           err.name === 'AbortError' ||
                           err.message?.includes('fetch failed') ||
                           err.message?.includes('network') ||
                           err.message?.includes('timeout');
      
      if (attempt === maxRetries || !isNetworkError) {
        throw new Error(`CircleCI workflow trigger failed: ${err.message}`);
      }
      
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
        platform: 'circleci',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    );

    const videoId = (videoDocument as any).$id;
    console.log(`📹 Created video document: ${videoId} for CircleCI processing`);

    // Trigger CircleCI workflow
    try {
      const result = await triggerCircleCIWorkflow(videoId);
      console.log('🎯 CircleCI workflow triggered successfully:', result);
    } catch (triggerError: any) {
      console.error('❌ CircleCI workflow trigger failed:', triggerError);
      // Update video status to failed if trigger fails
      await databases.updateDocument(
        DATABASE_ID,
        VIDEOS_COLLECTION_ID,
        videoId,
        {
          status: 'failed',
          error_message: `Failed to trigger CircleCI: ${triggerError.message}`,
          updated_at: new Date().toISOString(),
        }
      );
      
      return NextResponse.json(
        {
          success: false,
          error: `Failed to trigger video rendering: ${triggerError.message}`,
        },
        { status: 500 },
      );
    }

    return NextResponse.json({
      success: true,
      videoId: videoId,
      platform: 'circleci',
      message: 'Video generation task has been successfully queued for CircleCI processing.',
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