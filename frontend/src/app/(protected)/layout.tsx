'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Header } from '@/components/layout/Header';
import { ToastProvider } from '@/contexts/ToastContext';

/**
 * Protected layout - Wraps protected pages with authentication check
 * Client Component - requires authentication state
 */
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  console.log('[ProtectedLayout] Render state:', { user: user ? 'present' : 'null', loading });

  useEffect(() => {
    if (!loading && !user) {
      console.log('[ProtectedLayout] No user and not loading - redirecting to /login');
      router.push('/login');
    }
  }, [user, loading, router]);

  // Show loading state while checking authentication
  if (loading) {
    console.log('[ProtectedLayout] Showing loading spinner');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show redirecting message instead of null while redirect happens
  if (!user) {
    console.log('[ProtectedLayout] No user - showing redirect message');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  console.log('[ProtectedLayout] User authenticated - rendering protected content');

  return (
    <ToastProvider>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation Header */}
        <Header />

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
      </div>
    </ToastProvider>
  );
}
