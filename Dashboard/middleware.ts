import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || ''

  // Check if the request is coming from localhost
  if (!hostname.includes('localhost') && !hostname.includes('127.0.0.1')) {
    // Redirect to a custom error page
    return NextResponse.redirect(new URL('/error', request.url))
  }

  return NextResponse.next()
}

// Configure which paths the middleware will run on
export const config = {
  matcher: '/admin/:path*',  // Replace with your specific path
}
