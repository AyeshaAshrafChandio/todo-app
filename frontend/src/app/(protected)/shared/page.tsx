/**
 * Shared Tasks Page
 *
 * Displays all tasks that have been shared with the current user.
 * Shows task details, owner information, and permission levels.
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSharedTasks } from '@/hooks/useShares';
import { SharedTaskList } from '@/components/shared/SharedTaskList';
import { Button } from '@/components/ui/Button';

/**
 * Page component for viewing tasks shared with the current user
 *
 * Route: /shared
 *
 * Features:
 * - Displays all shared tasks
 * - Shows permission level for each task
 * - Shows who shared the task
 * - Allows clicking to view task details
 * - Refresh functionality
 */
export default function SharedTasksPage() {
  const router = useRouter();
  const { tasks, loading, error, loadTasks, refresh } = useSharedTasks();

  // Load shared tasks on mount
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleTaskClick = (task: any) => {
    // Navigate to task detail page
    router.push(`/tasks/${task.id}`);
  };

  const handleRefresh = () => {
    refresh();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-gray-900">
            Shared With Me
          </h1>
          <Button
            variant="secondary"
            onClick={handleRefresh}
            disabled={loading}
          >
            <svg
              className="h-4 w-4 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh
          </Button>
        </div>
        <p className="text-gray-600">
          Tasks that other users have shared with you
        </p>
      </div>

      {/* Task Count */}
      {!loading && !error && tasks.length > 0 && (
        <div className="mb-4 text-sm text-gray-600">
          Showing {tasks.length} shared {tasks.length === 1 ? 'task' : 'tasks'}
        </div>
      )}

      {/* Shared Tasks List */}
      <SharedTaskList
        tasks={tasks}
        loading={loading}
        error={error}
        onTaskClick={handleTaskClick}
        onRetry={loadTasks}
      />
    </div>
  );
}
