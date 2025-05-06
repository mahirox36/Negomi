'use client'

import { RootProvider } from '@/lib/providers/RootProvider'
import type { ReactNode } from 'react'

export default function Providers({ children }: { children: ReactNode }) {
  return <RootProvider>{children}</RootProvider>
}
