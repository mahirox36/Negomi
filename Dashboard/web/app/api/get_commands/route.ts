// get_commands.ts
import { NextResponse } from "next/server"
import { getAllCommands } from "@/lib/ipc"

export const dynamic = 'force-dynamic'
export const fetchCache = 'force-no-store'

export async function GET() {
  try {
    const data = await getAllCommands() as any[]
    
    if (data && typeof data === 'object' && 'commands' in data) {
      return NextResponse.json(data.commands)
    }
    
    if (Array.isArray(data)) {
      return NextResponse.json(data)
    }
    
    console.error("Unexpected data format:", data)
    return NextResponse.json([], { status: 200 })
    
  } catch (error) {
    console.error("Error fetching commands:", error)
    return NextResponse.json([], { status: 200 })
  }
}

