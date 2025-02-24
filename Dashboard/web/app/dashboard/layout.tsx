"use client"

import * as React from "react"
import { SidebarProvider, Sidebar, SidebarHeader, SidebarContent, SidebarMenu, SidebarMenuButton, SidebarGroup, SidebarGroupLabel } from "@/components/ui/sidebar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { Separator } from "@/components/ui/separator"
import { FiServer, FiSettings, FiUsers, FiBell, FiShield, FiMessageSquare, FiHash } from "react-icons/fi"

interface ServerData {
  id: string
  name: string
  icon: string | null
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [servers, setServers] = React.useState<ServerData[]>([])
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await fetch("/api/servers")
        const data = await response.json()
        setServers(data)
      } catch (error) {
        console.error("Failed to fetch servers:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchServers()
  }, [])

  return (
    <SidebarProvider defaultOpen>
      <div className="grid grid-cols-[auto_1fr]">
        <Sidebar>
          <SidebarHeader className="border-b border-sidebar-border">
            <div className="flex h-[60px] items-center px-6">
              <span className="font-semibold">Dashboard</span>
            </div>
          </SidebarHeader>

          <SidebarContent>
            <ScrollArea className="h-[calc(100vh-60px)]">
              {/* Servers Group */}
              <SidebarGroup>
                <SidebarGroupLabel>Your Servers</SidebarGroupLabel>
                <SidebarMenu>
                  {loading ? (
                    // Loading skeletons
                    Array(5).fill(0).map((_, i) => (
                      <Skeleton key={i} className="h-10 w-full" />
                    ))
                  ) : (
                    servers.map((server) => (
                      <SidebarMenuButton
                        key={server.id}
                        href={`/dashboard/${server.id}`}
                        tooltip="View Server Dashboard"
                      >
                        {server.icon ? (
                          <img
                            src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png`}
                            alt={server.name}
                            className="w-5 h-5 rounded-full"
                          />
                        ) : (
                          <FiServer />
                        )}
                        <span>{server.name}</span>
                      </SidebarMenuButton>
                    ))
                  )}
                </SidebarMenu>
              </SidebarGroup>

              <Separator className="my-4" />

              {/* Global Settings Group */}
              <SidebarGroup>
                <SidebarGroupLabel>Global Settings</SidebarGroupLabel>
                <SidebarMenu>
                  <SidebarMenuButton href="/dashboard/settings">
                    <FiSettings />
                    <span>Settings</span>
                  </SidebarMenuButton>
                </SidebarMenu>
              </SidebarGroup>

              {/* Features Group */}
              <SidebarGroup>
                <SidebarGroupLabel>Features</SidebarGroupLabel>
                <SidebarMenu>
                  <SidebarMenuButton href="/dashboard/moderation">
                    <FiShield />
                    <span>Moderation</span>
                  </SidebarMenuButton>
                  <SidebarMenuButton href="/dashboard/auto-mod">
                    <FiShield />
                    <span>Auto Moderation</span>
                  </SidebarMenuButton>
                  <SidebarMenuButton href="/dashboard/welcome">
                    <FiUsers />
                    <span>Welcome System</span>
                  </SidebarMenuButton>
                  <SidebarMenuButton href="/dashboard/notifications">
                    <FiBell />
                    <span>Notifications</span>
                  </SidebarMenuButton>
                  <SidebarMenuButton href="/dashboard/channels">
                    <FiHash />
                    <span>Channel Management</span>
                  </SidebarMenuButton>
                  <SidebarMenuButton href="/dashboard/commands">
                    <FiMessageSquare />
                    <span>Custom Commands</span>
                  </SidebarMenuButton>
                </SidebarMenu>
              </SidebarGroup>
            </ScrollArea>
          </SidebarContent>
        </Sidebar>

        <main className="min-h-screen bg-background">
          {children}
        </main>
      </div>
    </SidebarProvider>
  )
}
