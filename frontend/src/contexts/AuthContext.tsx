'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import * as authApi from '@/lib/api/auth';
import type { User, LoginRequest, RegisterRequest } from '@/lib/types/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component - Provides authentication state to the entire app
 * Must wrap the root layout to ensure shared auth state
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Load user on mount with timeout protection
  useEffect(() => {
    const loadUser = async () => {
      console.log('[AuthContext] Initializing authentication check...');
      console.log('[AuthContext] isAuthenticated:', authApi.isAuthenticated());

      if (!authApi.isAuthenticated()) {
        console.log('[AuthContext] No valid token found - user not authenticated');
        setLoading(false);
        return;
      }

      console.log('[AuthContext] Valid token found - fetching user data from /api/auth/me');

      try {
        // Add 5-second timeout to prevent hanging
        const timeoutPromise = new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Request timeout')), 5000)
        );

        const userPromise = authApi.getCurrentUser();
        const currentUser = await Promise.race([userPromise, timeoutPromise]) as User;

        console.log('[AuthContext] User data loaded successfully:', currentUser);
        setUser(currentUser);
      } catch (err) {
        // Silent fail - clear auth and allow page to render
        console.error('[AuthContext] Failed to load user session:', err);
        authApi.logout();
        setUser(null);
      } finally {
        setLoading(false);
        console.log('[AuthContext] Authentication check complete');
      }
    };

    loadUser();
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authApi.login(data);
      setUser(response.user);
      router.push('/dashboard');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [router]);

  const register = useCallback(async (data: RegisterRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authApi.register(data);
      setUser(response.user);
      router.push('/dashboard');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [router]);

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authApi.logout();
      setUser(null);
      router.push('/login');
    } catch (err) {
      // Silent fail - user will be redirected to login anyway
      setUser(null);
      router.push('/login');
    } finally {
      setLoading(false);
    }
  }, [router]);

  const refreshUser = useCallback(async () => {
    if (!authApi.isAuthenticated()) return;

    try {
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      // Silent fail - user will be redirected to login
      setUser(null);
    }
  }, []);

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access authentication context
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
