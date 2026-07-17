"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-2 shadow-sm">
        <div className="grid gap-2">
          <div className="flex flex-col">
            <span className="text-[0.70rem] uppercase text-muted-foreground">{label}</span>
            {payload.map((entry: any, index: number) => (
              <span key={index} className="font-bold text-foreground" style={{ color: entry.color }}>
                {entry.name}: {typeof entry.value === "number" ? entry.value.toFixed(2) : entry.value}
              </span>
            ))}
          </div>
        </div>
      </div>
    )
  }
  return null
}

const initialTrafficData = Array.from({ length: 20 }, (_, i) => ({
  time: `${i}s`,
  packets: 0,
}))

const initialAnomalyData = Array.from({ length: 20 }, (_, i) => ({
  time: `${i}s`,
  score: 0,
  threshold: 0.5,
}))

export function TrafficCharts() {
  const [trafficData, setTrafficData] = useState(initialTrafficData)
  const [anomalyData, setAnomalyData] = useState(initialAnomalyData)

  useEffect(() => {
    console.log("[v0] TrafficCharts mounted, starting data fetch")

    const fetchData = async () => {
      try {
        console.log("[v0] Fetching chart data...")
        const response = await fetch("/api/charts")

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`)
        }

        const data = await response.json()
        console.log("[v0] Chart data received:", {
          trafficLength: data.traffic?.length,
          anomaliesLength: data.anomalies?.length,
        })

        if (data.traffic && Array.isArray(data.traffic) && data.traffic.length > 0) {
          setTrafficData(data.traffic)
        }
        if (data.anomalies && Array.isArray(data.anomalies) && data.anomalies.length > 0) {
          setAnomalyData(data.anomalies)
        }
      } catch (error) {
        console.error("[v0] Failed to fetch chart data:", error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 3000)

    return () => {
      console.log("[v0] TrafficCharts cleanup")
      clearInterval(interval)
    }
  }, [])

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Network Traffic</CardTitle>
          <CardDescription>Real-time packet flow (last 60 seconds)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trafficData}>
                <defs>
                  <linearGradient id="trafficGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(210 100% 50%)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(210 100% 50%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(240 5% 26%)" />
                <XAxis dataKey="time" stroke="hsl(240 5% 64%)" fontSize={12} tick={{ fill: "hsl(240 5% 64%)" }} />
                <YAxis stroke="hsl(240 5% 64%)" fontSize={12} tick={{ fill: "hsl(240 5% 64%)" }} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="packets"
                  name="Packets/sec"
                  stroke="hsl(210 100% 50%)"
                  fill="url(#trafficGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Anomaly Score</CardTitle>
          <CardDescription>LSTM prediction confidence (threshold: 0.5)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={anomalyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(240 5% 26%)" />
                <XAxis dataKey="time" stroke="hsl(240 5% 64%)" fontSize={12} tick={{ fill: "hsl(240 5% 64%)" }} />
                <YAxis domain={[0, 1]} stroke="hsl(240 5% 64%)" fontSize={12} tick={{ fill: "hsl(240 5% 64%)" }} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="score"
                  name="Score"
                  stroke="hsl(173 80% 40%)"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="threshold"
                  name="Threshold"
                  stroke="hsl(0 84% 60%)"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
