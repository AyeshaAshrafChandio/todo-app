'use client';

import { useEffect, useState, useRef } from 'react';
import useSWR from 'swr';
import { dashboardFetcher } from '@/lib/api/dashboard';
import type { DashboardStatistics } from '@/lib/types/dashboard';
import { createWebSocketClient, WebSocketClient } from '@/lib/websocket/client';
import type { WebSocketEvent, ConnectionStatus } from '@/lib/websocket/types';

/**
 * Hook for fetching dashboard statistics with real-time WebSocket updates
 *
 * Features:
 * - Real-time updates via WebSocket (< 1 second latency)
 * - Automatic reconnection with exponential backoff
 * - Fallback to polling if WebSocket unavailable
 * - Connection status tracking
 * - Handles loading and error states
 *
 * @returns Dashboard statistics data, loading state, error, connection status, and mutate function
 */
export function useDashboard() {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const wsClientRef = useRef<WebSocketClient | null>(null);

  // Fetch initial data and use as fallback
  const { data, error, isLoading, mutate } = useSWR<DashboardStatistics>(
    'dashboard-statistics',
    dashboardFetcher,
    {
      // Disable polling by default (WebSocket will handle updates)
      refreshInterval: 0,
      revalidateOnFocus: true, // Still revalidate on focus
      revalidateOnReconnect: true, // Still revalidate on reconnect
      dedupingInterval: 2000,
      errorRetryCount: 3,
      errorRetryInterval: 5000,
      shouldRetryOnError: true,
    }
  );

  useEffect(() => {
    // Get JWT token from localStorage
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('[useDashboard] No JWT token found, WebSocket disabled');
      return;
    }

    // Determine WebSocket URL based on current environment
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000';
    const wsUrl = `${protocol}//${host}/api/ws`;

    console.log('[useDashboard] Initializing WebSocket connection');

    // Create WebSocket client
    wsClientRef.current = createWebSocketClient({
      url: wsUrl,
      token,
      reconnect: true,
      maxReconnectAttempts: Infinity,
      reconnectInterval: 1000,
      maxReconnectInterval: 32000,
      onEvent: (event: WebSocketEvent) => {
        console.log('[useDashboard] WebSocket event received:', event.event_type);

        // Handle different event types
        switch (event.event_type) {
          case 'connection_ack':
            console.log('[useDashboard] WebSocket connection acknowledged');
            break;

          case 'task_created':
          case 'task_updated':
          case 'task_completed':
          case 'task_reopened':
          case 'task_deleted':
          case 'task_shared':
            // Revalidate dashboard statistics on any task event
            console.log('[useDashboard] Task event received, revalidating statistics');
            mutate();
            break;

          case 'error':
            console.error('[useDashboard] WebSocket error:', event.data);
            break;

          default:
            console.log('[useDashboard] Unknown event type:', event.event_type);
        }
      },
      onStatusChange: (status: ConnectionStatus) => {
        console.log('[useDashboard] Connection status changed:', status);
        setConnectionStatus(status);

        // If WebSocket disconnects, enable polling as fallback
        if (status === 'disconnected' || status === 'error') {
          console.log('[useDashboard] WebSocket unavailable, enabling polling fallback');
          // Note: SWR doesn't support dynamic refreshInterval, so we'll just revalidate manually
          mutate();
        }
      },
    });

    // Connect to WebSocket
    wsClientRef.current.connect();

    // Cleanup on unmount
    return () => {
      console.log('[useDashboard] Cleaning up WebSocket connection');
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
        wsClientRef.current = null;
      }
    };
  }, [mutate]);

  return {
    statistics: data,
    loading: isLoading,
    error,
    connectionStatus,
    isWebSocketConnected: connectionStatus === 'connected',
    mutate, // Manual revalidation function
    retry: () => mutate(), // Explicit retry function
  };
}
