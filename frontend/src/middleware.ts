import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Next.js Middleware for route protection
 * Handles authentication checks and redirects
 */

// Public routes that don't require authentication
const publicRoutes = ['/login', '/register', '/'];

// Protected route prefixes that require authentication
const protectedRoutes = ['/dashboard', '/tasks', '/teams', '/chat', '/shared'];

/**
 * Check if route is public
 */
function isPublicRoute(pathname: string): boolean {
  return publicRoutes.some((route) => pathname === route || pathname.startsWith(route));
}

/**
 * Check if route is protected
 */
function isProtectedRoute(pathname: string): boolean {
  return protectedRoutes.some((route) => pathname.startsWith(route));
}

/**
 * Middleware function
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from cookies or headers
  const token = request.cookies.get('auth_token')?.value;

  // Check if user is authenticated
  const isAuthenticated = !!token;

  // Redirect authenticated users away from login/register pages
  if (isAuthenticated && (pathname === '/login' || pathname === '/register')) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Redirect unauthenticated users to login for protected routes
  if (!isAuthenticated && isProtectedRoute(pathname)) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Allow the request to proceed
  return NextResponse.next();
}

/**
 * Middleware configuration
 * Specify which routes should run the middleware
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
