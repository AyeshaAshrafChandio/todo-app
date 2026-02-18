'use client';

import { useDashboard } from '@/hooks/useDashboard';
import { StatisticsCard } from './StatisticsCard';
import { Button } from '@/components/ui/Button';
import { ConnectionStatusIndicator } from './ConnectionStatus';
import type { StatisticCardData } from '@/lib/types/dashboard';

/**
 * DashboardLayout Component
 *
 * Main dashboard layout with statistics cards
 * Features:
 * - Real-time statistics with WebSocket updates (< 1 second latency)
 * - Automatic reconnection with exponential backoff
 * - Connection status indicator
 * - Loading states with skeleton UI
 * - Error handling with retry functionality
 * - Responsive grid layout (1 col mobile, 2 cols tablet, 4 cols desktop)
 *
 * @returns Dashboard layout with statistics
 */
export function DashboardLayout() {
  const { statistics, loading, error, retry, connectionStatus, isWebSocketConnected } = useDashboard();

  // Transform backend data to card data format
  const getCardData = (): StatisticCardData[] => {
    if (!statistics) {
      return [
        {
          label: 'Total Tasks',
          value: 0,
          icon: '📋',
          color: 'primary',
          bgColor: 'bg-primary-100',
        },
        {
          label: 'Pending Tasks',
          value: 0,
          icon: '⏳',
          color: 'yellow',
          bgColor: 'bg-yellow-100',
        },
        {
          label: 'Completed Tasks',
          value: 0,
          icon: '✅',
          color: 'green',
          bgColor: 'bg-green-100',
        },
        {
          label: 'Shared Tasks',
          value: 0,
          icon: '🤝',
          color: 'blue',
          bgColor: 'bg-blue-100',
        },
      ];
    }

    return [
      {
        label: 'Total Tasks',
        value: statistics.total_tasks,
        icon: '📋',
        color: 'primary',
        bgColor: 'bg-primary-100',
      },
      {
        label: 'Pending Tasks',
        value: statistics.pending_tasks,
        icon: '⏳',
        color: 'yellow',
        bgColor: 'bg-yellow-100',
      },
      {
        label: 'Completed Tasks',
        value: statistics.completed_tasks,
        icon: '✅',
        color: 'green',
        bgColor: 'bg-green-100',
      },
      {
        label: 'Shared Tasks',
        value: statistics.shared_tasks,
        icon: '🤝',
        color: 'blue',
        bgColor: 'bg-blue-100',
      },
    ];
  };

  const cardData = getCardData();

  // Error state
  if (error && !loading) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 text-lg font-semibold mb-2">
            Failed to Load Dashboard Statistics
          </div>
          <p className="text-red-600 text-sm mb-4">
            {error.message || 'An error occurred while fetching dashboard data.'}
          </p>
          <Button variant="primary" onClick={retry} size="sm">
            Retry
          </Button>
        </div>

        {/* Show empty cards in error state */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {cardData.map((card, index) => (
            <StatisticsCard key={index} data={card} loading={false} />
          ))}
        </div>
      </div>
    );
  }

  // Success state (with or without loading)
  return (
    <div className="space-y-6">
      {/* Connection Status and Auto-update indicator */}
      {!loading && statistics && (
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-3">
            <ConnectionStatusIndicator status={connectionStatus} />
            {isWebSocketConnected ? (
              <span className="text-green-600 font-medium">Real-time updates active</span>
            ) : (
              <span className="text-yellow-600 font-medium">Using polling fallback</span>
            )}
          </div>
          <button
            onClick={retry}
            className="text-primary-600 hover:text-primary-700 font-medium"
            aria-label="Refresh statistics"
          >
            Refresh Now
          </button>
        </div>
      )}

      {/* Statistics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {cardData.map((card, index) => (
          <StatisticsCard key={index} data={card} loading={loading} />
        ))}
      </div>
    </div>
  );
}
