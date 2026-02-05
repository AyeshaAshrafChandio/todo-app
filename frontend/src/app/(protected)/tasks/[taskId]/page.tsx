/**
 * Task Detail Page
 *
 * Displays full task information with team context and sharing functionality.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { getTask, updateTask, deleteTask } from '@/lib/api/tasks';
import { useShares } from '@/hooks/useShares';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { Alert } from '@/components/ui/Alert';
import { ShareTaskModal } from '@/components/shared/ShareTaskModal';
import type { Task } from '@/lib/types/task';
import { SharePermission } from '@/lib/types/share';

/**
 * Page component for viewing and managing a single task
 *
 * Route: /tasks/[taskId]
 *
 * Features:
 * - View full task details
 * - Edit task
 * - Delete task
 * - Share task with others
 * - View who task is shared with
 * - Show team information
 * - Show access type
 */
export default function TaskDetailPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params.taskId as string;

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  const { shares, loadShares, share, revoke } = useShares(taskId);

  // Load task on mount
  useEffect(() => {
    const loadTask = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getTask(taskId);
        setTask(data);
        // Load shares if user has permission
        if (data.access_type === 'personal' || data.access_type === 'team') {
          await loadShares();
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load task';
        setError(message);
        console.error('Error loading task:', err);
      } finally {
        setLoading(false);
      }
    };

    loadTask();
  }, [taskId, loadShares]);

  const handleEdit = () => {
    router.push(`/tasks/${taskId}/edit`);
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await deleteTask(taskId);
      router.push('/tasks');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete task';
      setError(message);
    }
  };

  const handleToggleComplete = async () => {
    if (!task) return;

    try {
      const updatedTask = await updateTask(taskId, {
        status: task.completed ? 'pending' : 'completed'
      });
      setTask(updatedTask);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update task';
      setError(message);
    }
  };

  const handleShare = async (email: string, permission: SharePermission) => {
    await share({ email, permission });
  };

  const handleRevokeShare = async (userId: string) => {
    if (!confirm('Are you sure you want to revoke this share?')) {
      return;
    }

    try {
      await revoke(userId);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to revoke share';
      setError(message);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex justify-center items-center py-12">
          <Spinner size="lg" />
          <span className="ml-3 text-gray-600">Loading task...</span>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Alert variant="error">
          {error || 'Task not found'}
        </Alert>
        <div className="mt-4">
          <Button onClick={() => router.push('/tasks')}>Back to Tasks</Button>
        </div>
      </div>
    );
  }

  const canEdit = task.access_type === 'personal' || task.access_type === 'team';
  const canShare = task.access_type === 'personal' || task.access_type === 'team';

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <Button variant="secondary" onClick={() => router.push('/tasks')}>
          <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Tasks
        </Button>
      </div>

      {/* Task Details Card */}
      <Card className="mb-6">
        {/* Title and Actions */}
        <div className="flex items-start justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">{task.title}</h1>
          <div className="flex gap-2">
            {canEdit && (
              <>
                <Button variant="secondary" onClick={handleEdit}>
                  Edit
                </Button>
                <Button variant="danger" onClick={handleDelete}>
                  Delete
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge variant={task.status === 'completed' ? 'success' : 'info'}>
            {task.status.replace('_', ' ')}
          </Badge>
          <Badge variant={task.priority === 'high' ? 'danger' : 'default'}>
            {task.priority}
          </Badge>
          {task.completed && (
            <Badge variant="success">Completed</Badge>
          )}
        </div>

        {/* Description */}
        {task.description && (
          <div className="mb-6">
            <h2 className="text-sm font-medium text-gray-700 mb-2">Description</h2>
            <p className="text-gray-600">{task.description}</p>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Due Date */}
          {task.due_date && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">Due Date</h3>
              <p className="text-gray-600">{new Date(task.due_date).toLocaleDateString()}</p>
            </div>
          )}

          {/* Access Type */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-1">Access Type</h3>
            <p className="text-gray-600 capitalize">{task.access_type || 'personal'}</p>
          </div>

          {/* Team */}
          {task.team_name && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">Team</h3>
              <p className="text-gray-600">{task.team_name}</p>
            </div>
          )}

          {/* Owner */}
          {task.owner_email && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">Owner</h3>
              <p className="text-gray-600">{task.owner_email}</p>
            </div>
          )}

          {/* Created */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-1">Created</h3>
            <p className="text-gray-600">{new Date(task.created_at).toLocaleString()}</p>
          </div>

          {/* Updated */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-1">Last Updated</h3>
            <p className="text-gray-600">{new Date(task.updated_at).toLocaleString()}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <Button onClick={handleToggleComplete}>
            {task.completed ? 'Mark as Incomplete' : 'Mark as Complete'}
          </Button>
          {canShare && (
            <Button variant="secondary" onClick={() => setIsShareModalOpen(true)}>
              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
                />
              </svg>
              Share Task
            </Button>
          )}
        </div>
      </Card>

      {/* Shares Section */}
      {canShare && shares.length > 0 && (
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Shared With</h2>
          <div className="space-y-3">
            {shares.map((share) => (
              <div
                key={share.shared_with_user_id}
                className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0"
              >
                <div>
                  <p className="font-medium text-gray-900">{share.shared_with_email}</p>
                  <p className="text-sm text-gray-500">
                    {share.permission === 'edit' ? 'Can edit' : 'View only'}
                  </p>
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleRevokeShare(share.shared_with_user_id)}
                >
                  Revoke
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Share Modal */}
      <ShareTaskModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        onShare={handleShare}
        taskTitle={task.title}
      />
    </div>
  );
}
