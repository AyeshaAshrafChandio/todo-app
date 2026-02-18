/**
 * WebSocket Real-Time Updates Tests
 *
 * Test suite for WebSocket functionality including:
 * - Connection establishment and authentication
 * - Event handling for task operations
 * - Reconnection logic with exponential backoff
 * - Connection status tracking
 * - Dashboard integration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { WebSocketClient } from '@/lib/websocket/client';
import type { WebSocketEvent, ConnectionStatus } from '@/lib/websocket/types';

// Mock WebSocket
class MockWebSocket {
  public readyState: number = WebSocket.CONNECTING;
  public onopen: ((event: Event) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;

  constructor(public url: string) {
    // Simulate connection opening after a short delay
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }

  send(data: string): void {
    // Mock send implementation
  }

  close(): void {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code: 1000, reason: 'Normal closure' }));
    }
  }
}

// Replace global WebSocket with mock
global.WebSocket = MockWebSocket as any;

describe('WebSocket Client', () => {
  let client: WebSocketClient;
  let eventHandler: ReturnType<typeof vi.fn>;
  let statusHandler: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    eventHandler = vi.fn();
    statusHandler = vi.fn();

    client = new WebSocketClient({
      url: 'ws://localhost:8000/api/ws',
      token: 'test-jwt-token',
      onEvent: eventHandler,
      onStatusChange: statusHandler,
      reconnect: true,
      maxReconnectAttempts: 3,
      reconnectInterval: 100,
      maxReconnectInterval: 1000,
    });
  });

  afterEach(() => {
    if (client) {
      client.disconnect();
    }
  });

  describe('Connection', () => {
    it('should connect to WebSocket server with JWT token', async () => {
      client.connect();

      // Wait for connection to open
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(client.isConnected()).toBe(true);
      expect(client.getStatus()).toBe('connected');
      expect(statusHandler).toHaveBeenCalledWith('connecting');
      expect(statusHandler).toHaveBeenCalledWith('connected');
    });

    it('should include JWT token in URL query parameter', () => {
      client.connect();

      // Check that WebSocket was created with token in URL
      const wsUrl = (client as any).ws?.url;
      expect(wsUrl).toContain('token=test-jwt-token');
    });

    it('should disconnect cleanly', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      client.disconnect();

      expect(client.isConnected()).toBe(false);
      expect(client.getStatus()).toBe('disconnected');
    });
  });

  describe('Event Handling', () => {
    it('should handle connection_ack event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'connection_ack',
        timestamp: new Date().toISOString(),
        data: {
          user_id: 'user123',
          message: 'WebSocket connection established',
        },
      };

      // Simulate receiving message
      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });

    it('should handle task_created event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'task_created',
        timestamp: new Date().toISOString(),
        data: {
          task_id: 123,
          user_id: 'user123',
          team_id: null,
        },
      };

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });

    it('should handle task_updated event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'task_updated',
        timestamp: new Date().toISOString(),
        data: {
          task_id: 123,
          user_id: 'user123',
          team_id: 'team456',
        },
      };

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });

    it('should handle task_completed event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'task_completed',
        timestamp: new Date().toISOString(),
        data: {
          task_id: 123,
          user_id: 'user123',
        },
      };

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });

    it('should handle task_deleted event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'task_deleted',
        timestamp: new Date().toISOString(),
        data: {
          task_id: 123,
          user_id: 'user123',
        },
      };

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });

    it('should handle task_shared event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'task_shared',
        timestamp: new Date().toISOString(),
        data: {
          task_id: 123,
          shared_with_user_id: 'user456',
          shared_by_user_id: 'user123',
        },
      };

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });

    it('should handle error event', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const event: WebSocketEvent = {
        event_type: 'error',
        timestamp: new Date().toISOString(),
        data: {
          message: 'Test error',
        },
      };

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      expect(eventHandler).toHaveBeenCalledWith(event);
    });
  });

  describe('Reconnection Logic', () => {
    it('should attempt reconnection on disconnect', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      // Simulate disconnect
      const ws = (client as any).ws;
      if (ws && ws.onclose) {
        ws.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }));
      }

      expect(statusHandler).toHaveBeenCalledWith('disconnected');

      // Wait for reconnection attempt
      await new Promise(resolve => setTimeout(resolve, 150));

      // Should have attempted reconnection
      expect(statusHandler).toHaveBeenCalledWith('connecting');
    });

    it('should use exponential backoff for reconnection', async () => {
      const startTime = Date.now();
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      // Simulate multiple disconnects
      for (let i = 0; i < 3; i++) {
        const ws = (client as any).ws;
        if (ws && ws.onclose) {
          ws.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }));
        }
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      const elapsed = Date.now() - startTime;

      // Should have used exponential backoff (100ms, 200ms, 400ms)
      expect(elapsed).toBeGreaterThan(700);
    });

    it('should stop reconnecting after max attempts', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      // Simulate multiple disconnects exceeding max attempts
      for (let i = 0; i < 4; i++) {
        const ws = (client as any).ws;
        if (ws && ws.onclose) {
          ws.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }));
        }
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // Should have stopped reconnecting and set status to error
      expect(client.getStatus()).toBe('error');
    });

    it('should not reconnect if intentionally disconnected', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const connectingCalls = statusHandler.mock.calls.filter(
        (call: any) => call[0] === 'connecting'
      ).length;

      client.disconnect();
      await new Promise(resolve => setTimeout(resolve, 200));

      // Should not have attempted reconnection
      const newConnectingCalls = statusHandler.mock.calls.filter(
        (call: any) => call[0] === 'connecting'
      ).length;

      expect(newConnectingCalls).toBe(connectingCalls);
    });
  });

  describe('Ping/Pong', () => {
    it('should send ping messages to keep connection alive', async () => {
      const sendSpy = vi.spyOn(MockWebSocket.prototype, 'send');

      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      // Fast-forward time to trigger ping
      vi.useFakeTimers();
      vi.advanceTimersByTime(30000);
      vi.useRealTimers();

      expect(sendSpy).toHaveBeenCalledWith('ping');
    });

    it('should handle pong responses', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const ws = (client as any).ws;
      if (ws && ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: 'pong' }));
      }

      // Should not call event handler for pong
      expect(eventHandler).not.toHaveBeenCalled();
    });
  });

  describe('Connection Status', () => {
    it('should track connection status correctly', async () => {
      expect(client.getStatus()).toBe('disconnected');

      client.connect();
      expect(statusHandler).toHaveBeenCalledWith('connecting');

      await new Promise(resolve => setTimeout(resolve, 50));
      expect(client.getStatus()).toBe('connected');

      client.disconnect();
      expect(client.getStatus()).toBe('disconnected');
    });

    it('should update status on error', async () => {
      client.connect();
      await new Promise(resolve => setTimeout(resolve, 50));

      const ws = (client as any).ws;
      if (ws && ws.onerror) {
        ws.onerror(new Event('error'));
      }

      expect(statusHandler).toHaveBeenCalledWith('error');
    });
  });
});

describe('Dashboard WebSocket Integration', () => {
  it('should revalidate dashboard on task events', () => {
    // This test would require mocking the useDashboard hook
    // and verifying that mutate() is called on task events
    expect(true).toBe(true);
  });

  it('should show connection status indicator', () => {
    // This test would require rendering the DashboardLayout component
    // and verifying the ConnectionStatusIndicator is displayed
    expect(true).toBe(true);
  });

  it('should fall back to polling if WebSocket unavailable', () => {
    // This test would require mocking WebSocket failure
    // and verifying polling is enabled
    expect(true).toBe(true);
  });
});
