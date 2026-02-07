import { apiClient } from './client';
import { getUserIdFromToken } from '../auth/token';
import type { DashboardStatistics } from '../types/dashboard';

/**
 * Get current user ID from token
 */
function getCurrentUserId(): string {
  const userId = getUserIdFromToken();
  if (!userId) {
    throw new Error('User not authenticated');
  }
  return userId;
}

/**
 * Get dashboard statistics for current user
 *
 * Returns statistics including:
 * - total_tasks: Total number of tasks
 * - pending_tasks: Number of pending tasks
 * - completed_tasks: Number of completed tasks
 * - shared_tasks: Number of tasks shared with user
 *
 * @returns Promise with dashboard statistics
 */
export async function getDashboardStatistics(): Promise<DashboardStatistics> {
  const userId = getCurrentUserId();
  return apiClient<DashboardStatistics>(`/api/${userId}/dashboard/statistics`);
}

/**
 * Fetcher function for SWR
 * This is used by the useDashboard hook for data fetching
 */
export const dashboardFetcher = () => getDashboardStatistics();
