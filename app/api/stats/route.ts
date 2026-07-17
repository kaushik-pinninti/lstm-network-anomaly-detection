import { NextResponse } from "next/server"

export async function GET() {
  // Simulate real-time stats
  const stats = {
    packetsProcessed: Math.floor(Math.random() * 100000) + 50000,
    anomaliesDetected: Math.floor(Math.random() * 50),
    avgThroughput: Math.random() * 100 + 50,
    modelAccuracy: 0.92 + Math.random() * 0.05,
  }

  return NextResponse.json(stats)
}
