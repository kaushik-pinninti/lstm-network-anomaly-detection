import { NextResponse } from "next/server"

export async function GET() {
  const now = Date.now()

  // Generate traffic data for last 60 seconds
  const traffic = Array.from({ length: 60 }, (_, i) => ({
    time: new Date(now - (59 - i) * 1000).toLocaleTimeString(),
    packets: Math.floor(Math.random() * 500) + 200,
  }))

  // Generate anomaly scores
  const anomalies = Array.from({ length: 60 }, (_, i) => ({
    time: new Date(now - (59 - i) * 1000).toLocaleTimeString(),
    score: Math.random() * 0.3 + (Math.random() > 0.9 ? 0.5 : 0),
    threshold: 0.5,
  }))

  return NextResponse.json({ traffic, anomalies })
}
