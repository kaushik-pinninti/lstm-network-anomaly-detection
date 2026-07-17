"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, CheckCircle2, Info } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Anomaly {
  id: string
  timestamp: string
  severity: "high" | "medium" | "low"
  type: string
  description: string
  score: number
}

export function AnomalyFeed() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        const response = await fetch("/api/anomalies")
        const data = await response.json()
        setAnomalies(data)
      } catch (error) {
        console.error("Failed to fetch anomalies:", error)
      }
    }

    fetchAnomalies()
    const interval = setInterval(fetchAnomalies, 5000)
    return () => clearInterval(interval)
  }, [])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive"
      case "medium":
        return "default"
      case "low":
        return "secondary"
      default:
        return "secondary"
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "high":
        return AlertTriangle
      case "medium":
        return Info
      case "low":
        return CheckCircle2
      default:
        return Info
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Anomaly Detection Feed</CardTitle>
        <CardDescription>Real-time threat detection events</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {anomalies.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <CheckCircle2 className="h-12 w-12 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground">No anomalies detected</p>
                <p className="text-xs text-muted-foreground mt-1">System monitoring normally</p>
              </div>
            ) : (
              anomalies.map((anomaly) => {
                const Icon = getSeverityIcon(anomaly.severity)
                return (
                  <div
                    key={anomaly.id}
                    className="flex gap-4 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-accent"
                  >
                    <Icon
                      className={`h-5 w-5 mt-0.5 flex-shrink-0 ${
                        anomaly.severity === "high"
                          ? "text-destructive"
                          : anomaly.severity === "medium"
                            ? "text-chart-2"
                            : "text-muted-foreground"
                      }`}
                    />
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-sm font-medium text-foreground">{anomaly.type}</p>
                        <Badge variant={getSeverityColor(anomaly.severity)} className="text-xs">
                          {anomaly.severity}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{anomaly.description}</p>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>{anomaly.timestamp}</span>
                        <span>Score: {anomaly.score.toFixed(3)}</span>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
