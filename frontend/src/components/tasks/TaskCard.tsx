/**
 * Task Card Component
 *
 * Displays a task summary with status, priority, team information, and access type.
 */

'use client';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import type { Task, TaskAccessType } from '@/lib/types/task';

interface TaskCardProps {
  /** Task to display */
  task: Task;

  /** Callback when card is clicked */
  onClick?: (task: Task) => void;

  /** Whether to show team information */
  showTeam?: boolean;

  /** Additional CSS classes */
  className?: string;
}

/**
 * Card component for displaying a task summary
 *
 * @example
 * ```tsx
 * <TaskCard
 *   task={task}
 *   onClick={(task) => router.push(`/tasks/${task.id}`)}
 *   showTeam={true}
 * />
 * ```
 */
export function TaskCard({
  task,
  onClick,
  showTeam = true,
  className = ''
}: TaskCardProps) {
  const handleClick = () => {
    if (onClick) {
      onClick(task);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getAccessTypeIcon = (accessType?: TaskAccessType) => {
    switch (accessType) {
      case 'team':
        return (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
        );
      case 'shared':
        return (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
            />
          </svg>
        );
      default:
        return (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        );
    }
  };

  const getAccessTypeLabel = (accessType?: TaskAccessType) => {
    switch (accessType) {
      case 'team':
        return 'Team Task';
      case 'shared':
        return 'Shared';
      default:
        return 'Personal';
    }
  };

  return (
    <Card
      className={`hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between">
        {/* Task Info */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-lg font-medium text-gray-900 mb-2 truncate">
            {task.title}
          </h3>

          {/* Description */}
          {task.description && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Metadata */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            {/* Status Badge */}
            <Badge variant={getStatusColor(task.status)}>
              {task.status.replace('_', ' ')}
            </Badge>

            {/* Priority Badge */}
            <Badge variant={getPriorityColor(task.priority)}>
              {task.priority}
            </Badge>

            {/* Completed Badge */}
            {task.completed && (
              <Badge variant="success">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                Completed
              </Badge>
            )}

            {/* Due Date */}
            {task.due_date && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
          </div>

          {/* Team and Access Type */}
          {showTeam && (
            <div className="flex items-center gap-3 text-sm text-gray-500">
              {/* Access Type */}
              <div className="flex items-center gap-1">
                {getAccessTypeIcon(task.access_type)}
                <span>{getAccessTypeLabel(task.access_type)}</span>
              </div>

              {/* Team Name */}
              {task.team_name && (
                <div className="flex items-center gap-1">
                  <span>•</span>
                  <span>{task.team_name}</span>
                </div>
              )}

              {/* Owner Email */}
              {task.owner_email && task.access_type === 'shared' && (
                <div className="flex items-center gap-1">
                  <span>•</span>
                  <span>Owner: {task.owner_email}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Arrow Icon */}
        {onClick && (
          <div className="ml-4 flex-shrink-0 text-gray-400">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        )}
      </div>
    </Card>
  );
}
