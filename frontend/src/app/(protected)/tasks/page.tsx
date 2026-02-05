'use client';

import { useState } from 'react';
import { useTasks } from '@/hooks/useTasks';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/contexts/ToastContext';
import { useConfirmDialog } from '@/components/ui/ConfirmDialog';
import type { CreateTaskRequest, TaskStatus, TaskPriority } from '@/lib/types/task';

// Note: Metadata cannot be exported from Client Components
// For dynamic metadata in client components, use next/head or document.title

/**
 * Tasks page - List and manage all tasks
 * Client Component - requires authentication and data fetching
 */
export default function TasksPage() {
  const { tasks, loading, createTask, updateTask, deleteTask } = useTasks();
  const toast = useToast();
  const { confirm, ConfirmDialog } = useConfirmDialog();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<CreateTaskRequest>({
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium',
  });
  const [filter, setFilter] = useState<'all' | TaskStatus>('all');

  const filteredTasks = filter === 'all'
    ? tasks
    : tasks.filter((task) => task.status === filter);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTask(formData);
      setFormData({
        title: '',
        description: '',
        status: 'pending',
        priority: 'medium',
      });
      setShowCreateForm(false);
      toast.success('Task created successfully');
    } catch (err) {
      toast.error('Failed to create task. Please try again.');
    }
  };

  const handleStatusChange = async (taskId: string, status: TaskStatus) => {
    try {
      await updateTask(taskId, { status });
      toast.success('Task status updated');
    } catch (err) {
      toast.error('Failed to update task status');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    const confirmed = await confirm(
      'Delete Task',
      'Are you sure you want to delete this task? This action cannot be undone.',
      { variant: 'danger', confirmText: 'Delete' }
    );

    if (!confirmed) return;

    try {
      await deleteTask(taskId);
      toast.success('Task deleted successfully');
    } catch (err) {
      toast.error('Failed to delete task');
    }
  };

  return (
    <div className="space-y-6">
      {ConfirmDialog}
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="text-gray-600 mt-1">Manage your personal tasks</p>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : 'Create Task'}
        </Button>
      </div>

      {/* Create Task Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Create New Task</h2>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <Input
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Task title"
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Task description (optional)"
                  rows={3}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value as TaskPriority })}
                    className="block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as TaskStatus })}
                    className="block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Create Task
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>
      )}

      {/* Filter Tabs */}
      <div className="flex space-x-2 border-b border-gray-200">
        {(['all', 'pending', 'in_progress', 'completed'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              filter === status
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {status === 'all' ? 'All' : status.replace('_', ' ')}
            {status !== 'all' && (
              <span className="ml-2 px-2 py-0.5 text-xs bg-gray-100 rounded-full">
                {tasks.filter((t) => t.status === status).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {loading ? (
          <ListSkeleton count={5} />
        ) : filteredTasks.length === 0 ? (
          <Card>
            <CardBody>
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">
                  {filter === 'all' ? 'No tasks yet' : `No ${filter.replace('_', ' ')} tasks`}
                </p>
                {!showCreateForm && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowCreateForm(true)}
                  >
                    Create Your First Task
                  </Button>
                )}
              </div>
            </CardBody>
          </Card>
        ) : (
          filteredTasks.map((task) => (
            <Card key={task.id} variant="bordered">
              <CardBody>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {task.title}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          task.priority === 'high'
                            ? 'bg-red-100 text-red-700'
                            : task.priority === 'medium'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {task.priority}
                      </span>
                    </div>
                    {task.description && (
                      <p className="text-gray-600 mb-3">{task.description}</p>
                    )}
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                      {task.due_date && (
                        <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col space-y-2 ml-4">
                    <select
                      value={task.status}
                      onChange={(e) => handleStatusChange(task.id, e.target.value as TaskStatus)}
                      className={`px-3 py-1 text-sm font-medium rounded-md border ${
                        task.status === 'completed'
                          ? 'bg-green-50 text-green-700 border-green-200'
                          : task.status === 'in_progress'
                          ? 'bg-blue-50 text-blue-700 border-blue-200'
                          : 'bg-yellow-50 text-yellow-700 border-yellow-200'
                      }`}
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                    </select>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteTask(task.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
