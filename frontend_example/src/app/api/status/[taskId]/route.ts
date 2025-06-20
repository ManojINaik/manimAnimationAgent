import { NextRequest, NextResponse } from 'next/server';

export async function GET(
    request: NextRequest,
    { params }: { params: { taskId: string } }
) {
    try {
        const taskId = params.taskId;
        
        // Get the backend URL from environment or default to localhost:8000
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        
        // Forward the request to the FastAPI backend
        const response = await fetch(`${backendUrl}/api/status/${taskId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error(`Backend responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        return NextResponse.json(data);
        
    } catch (error) {
        console.error('Error fetching task status:', error);
        return NextResponse.json(
            { error: 'Failed to fetch task status' },
            { status: 500 }
        );
    }
} 