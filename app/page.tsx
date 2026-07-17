import { DashboardHeader } from "@/components/dashboard-header"
import { StatsGrid } from "@/components/stats-grid"
import { TrafficCharts } from "@/components/traffic-charts"
import { AnomalyFeed } from "@/components/anomaly-feed"
import { PacketInspector } from "@/components/packet-inspector"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-4 py-6 space-y-6">
        <StatsGrid />
        <TrafficCharts />

        <div className="grid gap-6 lg:grid-cols-2">
          <AnomalyFeed />
          <PacketInspector />
        </div>
      </main>
    </div>
  )
}
