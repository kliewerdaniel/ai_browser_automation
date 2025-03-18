import { NextResponse } from 'next/server';

// Fetch Ollama models
export async function GET() {
  try {
    const response = await fetch('http://localhost:11434/api/tags', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json({ 
      models: data.models || [],
      success: true 
    });
  } catch (error) {
    console.error('Error fetching models:', error);
    return NextResponse.json({ 
      models: [{ name: 'mistral' }], // Fallback to mistral
      success: false,
      error: error instanceof Error ? error.message : 'An unknown error occurred'
    }, { status: 500 });
  }
}
