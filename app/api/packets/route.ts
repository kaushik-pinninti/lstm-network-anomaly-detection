import { NextResponse } from "next/server"

const protocols = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS"]
const flags = ["SYN", "ACK", "FIN", "PSH", "RST", "URG"]

function generateIP() {
  return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
}

export async function GET() {
  const packets = Array.from({ length: 20 }, (_, i) => ({
    id: `packet-${Date.now()}-${i}`,
    timestamp: new Date(Date.now() - Math.random() * 60000).toLocaleString(),
    srcIp: generateIP(),
    dstIp: generateIP(),
    protocol: protocols[Math.floor(Math.random() * protocols.length)],
    length: Math.floor(Math.random() * 1500) + 64,
    flags: Array.from(
      { length: Math.floor(Math.random() * 3) + 1 },
      () => flags[Math.floor(Math.random() * flags.length)],
    ),
  }))

  return NextResponse.json(packets)
}
