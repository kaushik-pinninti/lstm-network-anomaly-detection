"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Activity, AlertTriangle, Network, Zap } from "lucide-react"

interface Stats {
  packetsProcessed: number
  anomaliesDetected: number
  avgThroughput: number
  modelAccuracy: number
}

export function StatsGrid() {
  const [stats, setStats] = useState<Stats>({
    packetsProcessed: 0,
    anomaliesDetected: 0,
    avgThroughput: 0,
    modelAccuracy: 0,
  })

  useEffect(() => {
    // Simulate real-time stats updates
    const interval = setInterval(async () => {
      try {
        const response = await fetch("/api/stats")
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error("Failed to fetch stats:", error)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const statCards = [
    {
      title: "Packets Processed",
      value: stats.packetsProcessed.toLocaleString(),
      icon: Network,
      color: "text-chart-1",
    },
    {
      title: "Anomalies Detected",
      value: stats.anomaliesDetected,
      icon: AlertTriangle,
      color: "text-chart-2",
    },
    {
      title: "Avg Throughput",
      value: `${stats.avgThroughput.toFixed(2)} Mbps`,
      icon: Zap,
      color: "text-chart-3",
    },
    {
      title: "Model Accuracy",
      value: `${(stats.modelAccuracy * 100).toFixed(1)}%`,
      icon: Activity,
      color: "text-chart-4",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {statCards.map((stat) => (
        <Card key={stat.title} className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
              <p className="mt-2 text-3xl font-bold text-foreground">{stat.value}</p>
            </div>
            <stat.icon className={`h-8 w-8 ${stat.color}`} />
          </div>
        </Card>
      ))}
    </div>
  )
}
