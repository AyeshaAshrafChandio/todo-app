/**
 * Task Sharing Hooks
 *
 * Custom React hooks for managing task sharing state and operations.
 */

import { useState, useCallback } from 'react';
import {
  shareTask,
  revokeShare,
  getTaskShares,
  getSharedTasks,
  updateSharePermission
} from '../lib/api/shares';
import type {
  ShareTaskRequest,
  TaskShare,
  SharedTask,
  SharePermission
} from '../lib/types/share';

/**
 * Hook for managing task shares
 *
 * Provides state and functions for sharing tasks, revoking shares,
 * and managing share permissions.
 *
 * @param taskId - Optional task ID to manage shares for
 * @returns Object with shares state and management functions
 *
 * @example
 * ```tsx
 * function TaskShareManager({ taskId }: { taskId: string }) {
 *   const {
 *     shares,
 *     loading,
 *     error,
 *     loadShares,
 *     share,
 *     revoke,
 *     updatePermission
 *   } = useShares(taskId);
 *
 *   useEffect(() => {
 *     loadShares();
 *   }, [loadShares]);
 *
 *   return (
 *     <div>
 *       {shares.map(share => (
 *         <div key={share.shared_with_user_id}>
 *           {share.shared_with_email} - {share.permission}
 *           <button onClick={() => revoke(share.shared_with_user_id)}>
 *             Revoke
 *           </button>
 *         </div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useShares(taskId?: string) {
  const [shares, setShares] = useState<TaskShare[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load shares for the current task
   */
  const loadShares = useCallback(async () => {
    if (!taskId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await getTaskShares(taskId);
      setShares(response.shares);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load shares';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  /**
   * Share task with a user
   */
  const share = useCallback(
    async (request: ShareTaskRequest) => {
      if (!taskId) {
        throw new Error('Task ID is required to share');
      }

      setLoading(true);
      setError(null);

      try {
        const response = await shareTask(taskId, request);
        // Add new share to the list
        setShares(prev => [...prev, response.share]);
        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to share task';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [taskId]
  );

  /**
   * Revoke share from a user
   */
  const revoke = useCallback(
    async (userId: string) => {
      if (!taskId) {
        throw new Error('Task ID is required to revoke share');
      }

      setLoading(true);
      setError(null);

      try {
        await revokeShare(taskId, userId);
        // Remove share from the list
        setShares(prev => prev.filter(s => s.shared_with_user_id !== userId));
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to revoke share';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [taskId]
  );

  /**
   * Update share permission
   */
  const updatePermission = useCallback(
    async (userId: string, permission: SharePermission) => {
      if (!taskId) {
        throw new Error('Task ID is required to update permission');
      }

      setLoading(true);
      setError(null);

      try {
        const updatedShare = await updateSharePermission(taskId, userId, permission);
        // Update share in the list
        setShares(prev =>
          prev.map(s =>
            s.shared_with_user_id === userId ? updatedShare : s
          )
        );
        return updatedShare;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update permission';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [taskId]
  );

  return {
    shares,
    loading,
    error,
    loadShares,
    share,
    revoke,
    updatePermission
  };
}

/**
 * Hook for managing shared tasks (tasks shared with current user)
 *
 * Provides state and functions for loading and managing tasks
 * that have been shared with the current user.
 *
 * @returns Object with shared tasks state and management functions
 *
 * @example
 * ```tsx
 * function SharedTasksPage() {
 *   const { tasks, loading, error, loadTasks, refresh } = useSharedTasks();
 *
 *   useEffect(() => {
 *     loadTasks();
 *   }, [loadTasks]);
 *
 *   if (loading) return <Spinner />;
 *   if (error) return <Alert type="error">{error}</Alert>;
 *
 *   return (
 *     <div>
 *       <h1>Tasks Shared With Me</h1>
 *       {tasks.map(task => (
 *         <TaskCard key={task.id} task={task} />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSharedTasks() {
  const [tasks, setTasks] = useState<SharedTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load tasks shared with current user
   */
  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getSharedTasks();
      setTasks(response.tasks);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load shared tasks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Refresh shared tasks list
   */
  const refresh = useCallback(() => {
    return loadTasks();
  }, [loadTasks]);

  /**
   * Remove a task from the local list (after deletion or revocation)
   */
  const removeTask = useCallback((taskId: string) => {
    setTasks(prev => prev.filter(t => t.id !== taskId));
  }, []);

  /**
   * Update a task in the local list
   */
  const updateTask = useCallback((taskId: string, updates: Partial<SharedTask>) => {
    setTasks(prev =>
      prev.map(t => (t.id === taskId ? { ...t, ...updates } : t))
    );
  }, []);

  return {
    tasks,
    loading,
    error,
    loadTasks,
    refresh,
    removeTask,
    updateTask
  };
}
