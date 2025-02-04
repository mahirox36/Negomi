// get_statistics.ts
import { NextResponse } from "next/server"
import { getDetailedStats } from "@/lib/ipc"

export const dynamic = 'force-dynamic'
export const fetchCache = 'force-no-store'

export async function GET() {
  try {
    const data = await getDetailedStats() as Record<string, any>
    
    if ('error' in data) {
      console.warn("Backend returned error:", data.error)
      return NextResponse.json({
        system: {
          cpu_usage: 0,
          memory_usage: 0,
          memory_total: 0,
          python_version: "N/A",
          os: "N/A",
          process_uptime: 0,
          thread_count: 0,
          disk_usage: 0
        },
        bot: {
          guild_count: 0,
          user_count: 0,
          channel_count: 0,
          voice_connections: 0,
          latency: 0,
          uptime: 0,
          command_count: 0,
          cogs_loaded: 0,
          shard_count: 1,
          current_shard: 0,
          messages_sent: 0,
          commands_processed: 0,
          errors_encountered: 0
        },
        activity: {},
        guilds: [],
        timestamp: Date.now() / 1000
      })
    }

    return NextResponse.json(data)
    
  } catch (error) {
    console.error("Error fetching stats:", error)
    return NextResponse.json({
      system: {},
      bot: {},
      activity: {},
      guilds: [],
      timestamp: Date.now() / 1000
    }, { status: 200 })
  }
}
