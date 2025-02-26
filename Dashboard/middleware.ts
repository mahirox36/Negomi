import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || ''

  // Check if the request is coming from localhost
  if (!hostname.includes('localhost') && !hostname.includes('127.0.0.1')) {
    // Redirect to 404 or return error response
    return new NextResponse('Access Denied', {
      status: 403,
      statusText: 'Forbidden',
      headers: {
        'Content-Type': 'text/plain',
      },
    })
  }

  return NextResponse.next()
}

// Configure which paths the middleware will run on
export const config = {
  matcher: '/admin/:path*',  // Replace with your specific path
}