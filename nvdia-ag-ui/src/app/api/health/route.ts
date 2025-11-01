import { NextResponse } from 'next/server';

/**
 * Health check endpoint for Kubernetes liveness/readiness probes
 * Returns 200 OK if the application is healthy
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'nvidia-retail-ai-ui',
    },
    { status: 200 }
  );
}
