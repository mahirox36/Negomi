import "./globals.css"
import { Inter } from "next/font/google"
import type { ReactNode } from "react"
import ClientProvider from './providers'
import { metadata } from './metadata'
import { LayoutProvider } from '@/providers/LayoutProvider';
import Navbar from "./components/Navbar";

const inter = Inter({ subsets: ["latin"] })

export { metadata }

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" 
        />
      </head>
      <body className={inter.className} suppressHydrationWarning>
        <LayoutProvider>
          <ClientProvider>
            <div className="min-h-screen bg-gradient-to-b from-purple-950 to-purple-950">
              <div className="relative z-50">
                <Navbar />
              </div>
              <div className="relative z-0">
                {children}
              </div>
            </div>
          </ClientProvider>
        </LayoutProvider>
      </body>
    </html>
  )
}

