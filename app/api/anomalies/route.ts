import { NextResponse } from "next/server"

const anomalyTypes = [
  "Port Scan Detected",
  "DDoS Attack Pattern",
  "Unusual Traffic Volume",
  "Suspicious Connection",
  "Protocol Anomaly",
  "Data Exfiltration Attempt",
]

const descriptions = [
  "Multiple connection attempts from single source",
  "Traffic volume exceeds normal threshold",
  "Unusual packet size distribution detected",
  "Connection to known malicious IP",
  "Abnormal protocol behavior observed",
  "Large data transfer to external host",
]

export async function GET() {
  // Generate random anomalies (20% chance)
  const anomalies =
    Math.random() > 0.8
      ? Array.from({ length: Math.floor(Math.random() * 3) + 1 }, (_, i) => ({
          id: `anomaly-${Date.now()}-${i}`,
          timestamp: new Date().toLocaleTimeString(),
          severity: ["high", "medium", "low"][Math.floor(Math.random() * 3)] as "high" | "medium" | "low",
          type: anomalyTypes[Math.floor(Math.random() * anomalyTypes.length)],
          description: descriptions[Math.floor(Math.random() * descriptions.length)],
          score: Math.random() * 0.5 + 0.5,
        }))
      : []

  return NextResponse.json(anomalies)
}
