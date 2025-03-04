import "./globals.css"
import { Inter } from "next/font/google"
import type { ReactNode } from "react"
import ClientProvider from './providers'
import { metadata } from './metadata'
import { LayoutProvider } from '@/providers/LayoutProvider';

const inter = Inter({ subsets: ["latin"] })

export { metadata }

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <LayoutProvider>
          <ClientProvider>{children}</ClientProvider>
        </LayoutProvider>
      </body>
    </html>
  )
}

