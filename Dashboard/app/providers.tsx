'use client'

import { ReactNode } from 'react'
import { UserProvider } from './contexts/UserContext'

export default function ClientProvider({ children }: { children: ReactNode }) {
  return (
    <UserProvider>{children}</UserProvider>
  )
}
