/**
 * Dashboard statistics response from backend
 */
export interface DashboardStatistics {
  total_tasks: number;
  pending_tasks: number;
  completed_tasks: number;
  shared_tasks: number;
}

/**
 * Statistics card data for UI display
 */
export interface StatisticCardData {
  label: string;
  value: number;
  icon: string;
  color: 'primary' | 'yellow' | 'green' | 'blue';
  bgColor: string;
}
