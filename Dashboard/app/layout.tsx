import "./globals.css"
import { Inter } from "next/font/google"
import type { Metadata, Viewport } from 'next'
import type { ReactNode } from "react"
import { RootProvider } from '@/lib/providers/RootProvider'
import Navbar from "@/app/components/Navbar"

const inter = Inter({ subsets: ["latin"] })

//  Author
const mahiro = {
  name: "Mahiro",
  url: "https://discord.com/users/829806976702873621",
} 
 
export const viewport: Viewport = {
  themeColor: '#ff69b4',
}
export const metadata: Metadata = {
  title: 'Negomi',
  description: 'Manage your Discord server with powerful tools and analytics',
  icons: {
    icon: '/favicon.ico',
  },
  authors: [mahiro],
  openGraph: {
    title: "Negomi - The Ultimate Discord Server Management Tool",
    description: "Manage your Discord server with powerful tools and analytics",
    url: "https://negomi.mahirou.online",
    siteName: "Negomi",
    locale: "en_US",
    type: "website",
  }
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <head>
        <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" 
          crossOrigin="anonymous"
        />
      </head>
      <body suppressHydrationWarning>
        <RootProvider>
          <div className="min-h-screen bg-gradient-to-b from-purple-950 to-purple-950">
            <Navbar />
            <main className="relative z-0">
              {children}
            </main>
          </div>
        </RootProvider>
      </body>
    </html>
  )
}

