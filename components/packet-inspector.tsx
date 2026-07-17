"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface Packet {
  id: string
  timestamp: string
  srcIp: string
  dstIp: string
  protocol: string
  length: number
  flags: string[]
}

export function PacketInspector() {
  const [packets, setPackets] = useState<Packet[]>([])
  const [selectedPacket, setSelectedPacket] = useState<Packet | null>(null)

  useEffect(() => {
    const fetchPackets = async () => {
      try {
        const response = await fetch("/api/packets")
        const data = await response.json()
        setPackets(data)
        if (data.length > 0 && !selectedPacket) {
          setSelectedPacket(data[0])
        }
      } catch (error) {
        console.error("Failed to fetch packets:", error)
      }
    }

    fetchPackets()
    const interval = setInterval(fetchPackets, 2000)
    return () => clearInterval(interval)
  }, [selectedPacket])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Packet Inspector</CardTitle>
        <CardDescription>Deep packet analysis and metadata</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="list" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="list">Recent Packets</TabsTrigger>
            <TabsTrigger value="detail">Packet Detail</TabsTrigger>
          </TabsList>

          <TabsContent value="list" className="mt-4">
            <ScrollArea className="h-[350px] pr-4">
              <div className="space-y-2">
                {packets.map((packet) => (
                  <button
                    key={packet.id}
                    onClick={() => setSelectedPacket(packet)}
                    className="w-full text-left rounded-lg border border-border bg-card p-3 transition-colors hover:bg-accent"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs font-mono">
                          {packet.protocol}
                        </Badge>
                        <span className="text-xs font-mono text-muted-foreground">
                          {packet.srcIp} → {packet.dstIp}
                        </span>
                      </div>
                      <span className="text-xs text-muted-foreground">{packet.length}B</span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{packet.timestamp}</p>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="detail" className="mt-4">
            {selectedPacket ? (
              <div className="space-y-4 rounded-lg border border-border bg-muted p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Source IP</p>
                    <p className="mt-1 font-mono text-sm text-foreground">{selectedPacket.srcIp}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Destination IP</p>
                    <p className="mt-1 font-mono text-sm text-foreground">{selectedPacket.dstIp}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Protocol</p>
                    <p className="mt-1 font-mono text-sm text-foreground">{selectedPacket.protocol}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Length</p>
                    <p className="mt-1 font-mono text-sm text-foreground">{selectedPacket.length} bytes</p>
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-2">Flags</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedPacket.flags.map((flag) => (
                      <Badge key={flag} variant="secondary" className="font-mono text-xs">
                        {flag}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium text-muted-foreground">Timestamp</p>
                  <p className="mt-1 font-mono text-sm text-foreground">{selectedPacket.timestamp}</p>
                </div>
              </div>
            ) : (
              <div className="flex h-[300px] items-center justify-center text-muted-foreground">
                <p className="text-sm">Select a packet to view details</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
