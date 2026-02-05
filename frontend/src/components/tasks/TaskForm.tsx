/**
 * Task Form Component
 *
 * Form for creating and editing tasks with team selection support.
 */

'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskStatus, TaskPriority } from '@/lib/types/task';
import type { Team } from '@/lib/types/team';
import { getTeams } from '@/lib/api/teams';
import { sanitizeInput } from '@/lib/utils/sanitize';

interface TaskFormProps {
  /** Existing task to edit (undefined for create mode) */
  task?: Task;

  /** Callback when form is submitted */
  onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => Promise<void>;

  /** Callback when form is cancelled */
  onCancel?: () => void;

  /** Whether the form is in loading state */
  loading?: boolean;

  /** Error message to display */
  error?: string | null;
}

/**
 * Form component for creating and editing tasks
 *
 * @example
 * ```tsx
 * // Create mode
 * <TaskForm
 *   onSubmit={async (data) => {
 *     await createTask(data);
 *   }}
 *   onCancel={() => router.back()}
 * />
 *
 * // Edit mode
 * <TaskForm
 *   task={existingTask}
 *   onSubmit={async (data) => {
 *     await updateTask(task.id, data);
 *   }}
 * />
 * ```
 */
export function TaskForm({
  task,
  onSubmit,
  onCancel,
  loading = false,
  error = null
}: TaskFormProps) {
  const isEditMode = !!task;

  // Form state
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [status, setStatus] = useState<TaskStatus>(task?.status || 'pending');
  const [priority, setPriority] = useState<TaskPriority>(task?.priority || 'medium');
  const [dueDate, setDueDate] = useState(task?.due_date || '');
  const [teamId, setTeamId] = useState(task?.team_id || '');

  // Teams state
  const [teams, setTeams] = useState<Team[]>([]);
  const [loadingTeams, setLoadingTeams] = useState(false);

  // Load user's teams on mount
  useEffect(() => {
    const loadTeams = async () => {
      setLoadingTeams(true);
      try {
        const userTeams = await getTeams();
        setTeams(userTeams);
      } catch (err) {
        console.error('Failed to load teams:', err);
      } finally {
        setLoadingTeams(false);
      }
    };

    loadTeams();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      return;
    }

    // Sanitize user input before submission
    const sanitizedTitle = sanitizeInput(title.trim());
    const sanitizedDescription = description.trim()
      ? sanitizeInput(description.trim())
      : undefined;

    const data: CreateTaskRequest | UpdateTaskRequest = {
      title: sanitizedTitle,
      description: sanitizedDescription,
      status,
      priority,
      due_date: dueDate || undefined,
      ...(isEditMode ? {} : { team_id: teamId || undefined })
    };

    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <Alert variant="error">{error}</Alert>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <Input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          disabled={loading}
          required
          autoFocus
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description (optional)"
          disabled={loading}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
      </div>

      {/* Status and Priority Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Status */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as TaskStatus)}
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </div>

      {/* Due Date and Team Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Due Date */}
        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
            Due Date
          </label>
          <Input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            disabled={loading}
          />
        </div>

        {/* Team Selection (only in create mode) */}
        {!isEditMode && (
          <div>
            <label htmlFor="team" className="block text-sm font-medium text-gray-700 mb-1">
              Team (Optional)
            </label>
            <select
              id="team"
              value={teamId}
              onChange={(e) => setTeamId(e.target.value)}
              disabled={loading || loadingTeams}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Personal Task</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>
            {loadingTeams && (
              <p className="mt-1 text-xs text-gray-500">Loading teams...</p>
            )}
            {!loadingTeams && teams.length === 0 && (
              <p className="mt-1 text-xs text-gray-500">
                You're not a member of any teams yet
              </p>
            )}
          </div>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={loading || !title.trim()}>
          {loading ? (
            <>
              <Spinner size="sm" className="mr-2" />
              {isEditMode ? 'Updating...' : 'Creating...'}
            </>
          ) : (
            <>{isEditMode ? 'Update Task' : 'Create Task'}</>
          )}
        </Button>
      </div>
    </form>
  );
}
