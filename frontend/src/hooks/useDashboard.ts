'use client';

import useSWR from 'swr';
import { dashboardFetcher } from '@/lib/api/dashboard';
import type { DashboardStatistics } from '@/lib/types/dashboard';

/**
 * Hook for fetching dashboard statistics with real-time polling
 *
 * Features:
 * - Automatic polling every 5 seconds
 * - Revalidates on focus and reconnect
 * - Handles loading and error states
 * - Provides retry functionality
 *
 * @returns Dashboard statistics data, loading state, error, and mutate function
 */
export function useDashboard() {
  const { data, error, isLoading, mutate } = useSWR<DashboardStatistics>(
    'dashboard-statistics',
    dashboardFetcher,
    {
      refreshInterval: 5000, // Poll every 5 seconds
      revalidateOnFocus: true, // Revalidate when window regains focus
      revalidateOnReconnect: true, // Revalidate when network reconnects
      dedupingInterval: 2000, // Dedupe requests within 2 seconds
      errorRetryCount: 3, // Retry failed requests up to 3 times
      errorRetryInterval: 5000, // Wait 5 seconds between retries
      shouldRetryOnError: true, // Enable automatic retry on error
    }
  );

  return {
    statistics: data,
    loading: isLoading,
    error,
    mutate, // Manual revalidation function
    retry: () => mutate(), // Explicit retry function
  };
}
