"use client"

import { Activity, Bell, Settings, Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-card">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <Shield className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">Network Anomaly Detection</h1>
              <p className="text-xs text-muted-foreground">Real-time LSTM Monitoring</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Badge variant="outline" className="gap-2">
              <Activity className="h-3 w-3 text-chart-3" />
              <span className="text-xs">System Active</span>
            </Badge>

            <Button variant="ghost" size="icon">
              <Bell className="h-4 w-4" />
            </Button>

            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
