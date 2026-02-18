/**
 * Connection Status Indicator Component
 *
 * Displays the current WebSocket connection status with visual indicators:
 * - Connected (green): WebSocket active, real-time updates enabled
 * - Connecting (yellow): Attempting to establish connection
 * - Disconnected (red): Connection lost, attempting to reconnect
 * - Polling (blue): WebSocket unavailable, using fallback polling
 */

'use client';

import type { ConnectionStatus } from '@/lib/websocket/types';

interface ConnectionStatusIndicatorProps {
  status: ConnectionStatus;
  className?: string;
}

export function ConnectionStatusIndicator({
  status,
  className = '',
}: ConnectionStatusIndicatorProps) {
  const getStatusConfig = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return {
          label: 'Connected',
          color: 'bg-green-500',
          textColor: 'text-green-700',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          icon: '●',
          description: 'Real-time updates active',
        };
      case 'connecting':
        return {
          label: 'Connecting',
          color: 'bg-yellow-500',
          textColor: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          icon: '◐',
          description: 'Establishing connection...',
        };
      case 'disconnected':
        return {
          label: 'Disconnected',
          color: 'bg-red-500',
          textColor: 'text-red-700',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          icon: '○',
          description: 'Reconnecting...',
        };
      case 'error':
        return {
          label: 'Error',
          color: 'bg-red-500',
          textColor: 'text-red-700',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          icon: '✕',
          description: 'Connection error',
        };
      default:
        return {
          label: 'Unknown',
          color: 'bg-gray-500',
          textColor: 'text-gray-700',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          icon: '?',
          description: 'Unknown status',
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${config.bgColor} ${config.borderColor} ${className}`}
      title={config.description}
    >
      <span
        className={`inline-block w-2 h-2 rounded-full ${config.color} ${
          status === 'connecting' ? 'animate-pulse' : ''
        }`}
        aria-hidden="true"
      />
      <span className={`text-sm font-medium ${config.textColor}`}>
        {config.label}
      </span>
    </div>
  );
}

/**
 * Compact Connection Status Badge
 *
 * Minimal version showing only the status indicator dot
 */
export function ConnectionStatusBadge({
  status,
  className = '',
}: ConnectionStatusIndicatorProps) {
  const getStatusConfig = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return {
          color: 'bg-green-500',
          description: 'Connected - Real-time updates active',
        };
      case 'connecting':
        return {
          color: 'bg-yellow-500',
          description: 'Connecting...',
        };
      case 'disconnected':
        return {
          color: 'bg-red-500',
          description: 'Disconnected - Reconnecting...',
        };
      case 'error':
        return {
          color: 'bg-red-500',
          description: 'Connection error',
        };
      default:
        return {
          color: 'bg-gray-500',
          description: 'Unknown status',
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span
      className={`inline-block w-2.5 h-2.5 rounded-full ${config.color} ${
        status === 'connecting' ? 'animate-pulse' : ''
      } ${className}`}
      title={config.description}
      aria-label={config.description}
    />
  );
}
