'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import * as authApi from '@/lib/api/auth';
import type { User, LoginRequest, RegisterRequest } from '@/lib/types/auth';

interface UseAuthReturn {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

/**
 * Hook for authentication state and operations
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      if (!authApi.isAuthenticated()) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await authApi.getCurrentUser();
        setUser(currentUser);
      } catch (err) {
        // Silent fail - user will be redirected to login
        setUser(null);
      } finally {
        setLoading(false);
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

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    refreshUser,
  };
}
