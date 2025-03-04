"use client"

import { useEffect } from 'react'
import Link from 'next/link'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center">
      <div className="text-center text-white p-8">
        <h1 className="text-9xl font-bold mb-4">403</h1>
        <h2 className="text-2xl mb-6">Access Forbidden</h2>
        <p className="mb-8">Sorry, you don't have permission to access this page.</p>
        <div className="space-x-4">
          <button
            onClick={reset}
            className="px-6 py-3 bg-white text-purple-600 rounded-lg hover:bg-opacity-90 transition-all"
          >
            Try again
          </button>
          <Link 
            href="/" 
            className="px-6 py-3 bg-white text-purple-600 rounded-lg hover:bg-opacity-90 transition-all"
          >
            Return Home
          </Link>
        </div>
      </div>
    </main>
  )
}
