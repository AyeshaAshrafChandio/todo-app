'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Providers component - Wraps all client-side providers
 * This allows the root layout to remain a Server Component
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}
