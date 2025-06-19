import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { topic, description } = body;

    if (!topic) {
      return NextResponse.json(
        { success: false, error: 'Topic is required' },
        { status: 400 }
      );
    }

    // Get backend URL from environment or use default
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    
    // Video generation can take several minutes. Increase the default
    // timeout (Node fetch defaults to 5 min = 300 000 ms) so we don't run
    // into UND_ERR_HEADERS_TIMEOUT errors on long-running requests.
    // We use AbortController instead of relying on Node's internal limit.

    const controller = new AbortController();
    // 10 minutes should be enough for most educational videos. Adjust via
    // NEXT_PUBLIC_GENERATE_TIMEOUT_MS env var if you need more.
    const timeoutMs = Number(process.env.NEXT_PUBLIC_GENERATE_TIMEOUT_MS ?? 600_000);
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    const response = await fetch(`${backendUrl}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic, description }),
      signal: controller.signal,
    }).finally(() => clearTimeout(timeoutId));

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('Error in API route:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Internal server error' 
      },
      { status: 500 }
    );
  }
} 