import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    groq_api: process.env.GROQ_API_KEY ? 'configured' : 'unconfigured',
    database: 'connected',
    environment: 'vercel_edge_serverless'
  });
}
