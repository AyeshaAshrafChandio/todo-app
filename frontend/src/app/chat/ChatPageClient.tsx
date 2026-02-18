'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { ChatProvider } from '@/contexts/ChatContext';
import { ChatInterface } from '@/components/chat/ChatInterface';

export function ChatPageClient() {
  const { user, loading } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login?redirect=/chat');
    }
  }, [user, loading, router]);

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render chat if not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatProvider>
        <ChatInterface />
      </ChatProvider>
    </div>
  );
}
