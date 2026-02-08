/**
 * Shared Task List Component
 *
 * Displays a list of tasks that have been shared with the current user.
 * Shows task details, owner information, and permission level.
 */

'use client';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { Alert } from '@/components/ui/Alert';
import type { SharedTask } from '@/lib/types/share';
import { SharePermission } from '@/lib/types/share';

interface SharedTaskListProps {
  /** List of shared tasks to display */
  tasks: SharedTask[];

  /** Whether tasks are currently loading */
  loading?: boolean;

  /** Error message if loading failed */
  error?: string | null;

  /** Callback when a task is clicked */
  onTaskClick?: (task: SharedTask) => void;

  /** Callback to retry loading */
  onRetry?: () => void;
}

/**
 * List component for displaying shared tasks
 *
 * @example
 * ```tsx
 * const { tasks, loading, error, loadTasks } = useSharedTasks();
 *
 * <SharedTaskList
 *   tasks={tasks}
 *   loading={loading}
 *   error={error}
 *   onTaskClick={(task) => router.push(`/tasks/${task.id}`)}
 *   onRetry={loadTasks}
 * />
 * ```
 */
export function SharedTaskList({
  tasks,
  loading = false,
  error = null,
  onTaskClick,
  onRetry
}: SharedTaskListProps) {
  // Loading state
  if (loading) {
    return <ListSkeleton count={5} />;
  }

  // Error state
  if (error) {
    return (
      <Alert variant="error" className="mb-4">
        <div className="flex items-center justify-between">
          <span>{error}</span>
          {onRetry && (
            <button
              onClick={onRetry}
              className="ml-4 text-sm font-medium text-red-700 hover:text-red-800 underline"
            >
              Retry
            </button>
          )}
        </div>
      </Alert>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <Card className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg
            className="mx-auto h-12 w-12"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No Shared Tasks
        </h3>
        <p className="text-gray-600">
          You don't have any tasks shared with you yet.
        </p>
      </Card>
    );
  }

  // Task list
  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <Card
          key={task.id}
          className={`hover:shadow-md transition-shadow ${
            onTaskClick ? 'cursor-pointer' : ''
          }`}
          onClick={() => onTaskClick?.(task)}
        >
          <div className="flex items-start justify-between">
            {/* Task Info */}
            <div className="flex-1 min-w-0">
              {/* Title and Status */}
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-lg font-medium text-gray-900 truncate">
                  {task.title}
                </h3>
                {task.completed && (
                  <Badge variant="success">Completed</Badge>
                )}
              </div>

              {/* Description */}
              {task.description && (
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {task.description}
                </p>
              )}

              {/* Metadata */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                {/* Owner */}
                <div className="flex items-center gap-1">
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                  <span>Owner: {task.owner_email || task.owner_id}</span>
                </div>

                {/* Team */}
                {task.team_name && (
                  <div className="flex items-center gap-1">
                    <svg
                      className="h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                      />
                    </svg>
                    <span>Team: {task.team_name}</span>
                  </div>
                )}

                {/* Shared By */}
                <div className="flex items-center gap-1">
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
                    />
                  </svg>
                  <span>
                    Shared by: {task.shared_by_email || task.shared_by_user_id}
                  </span>
                </div>

                {/* Shared Date */}
                <div className="flex items-center gap-1">
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <span>
                    {new Date(task.shared_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Permission Badge */}
            <div className="ml-4 flex-shrink-0">
              <Badge
                variant={
                  task.permission === SharePermission.EDIT
                    ? 'info'
                    : 'default'
                }
              >
                {task.permission === SharePermission.EDIT
                  ? 'Can Edit'
                  : 'View Only'}
              </Badge>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
