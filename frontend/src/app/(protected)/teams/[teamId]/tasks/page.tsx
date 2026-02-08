'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/shared/LoadingState';
import { EmptyState } from '@/components/shared/EmptyState';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskCard } from '@/components/tasks/TaskCard';
import { useTeamDetails } from '@/hooks/useTeamDetails';
import { useTasks } from '@/hooks/useTasks';
import { useAuth } from '@/hooks/useAuth';
import type { CreateTaskRequest, TaskStatus, UpdateTaskRequest } from '@/lib/types/task';
import type { TeamRoleType } from '@/lib/types/team';

/**
 * Team Tasks Page - Display and manage tasks for a specific team
 * Client Component - requires data fetching and interactions
 *
 * Features:
 * - Display all team tasks
 * - Create new team tasks (members and above)
 * - Edit/delete tasks based on role permissions
 * - Filter tasks by status
 */
export default function TeamTasksPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const teamId = params.teamId as string;

  // Load team details and members
  const { team, members, loading: teamLoading, error: teamError } = useTeamDetails(teamId);

  // Load team tasks
  const {
    tasks,
    loading: tasksLoading,
    error: tasksError,
    createTask,
    updateTask,
    deleteTask,
    setFilters,
  } = useTasks({ team_id: teamId });

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filter, setFilter] = useState<'all' | TaskStatus>('all');
  const [currentUserRole, setCurrentUserRole] = useState<TeamRoleType | null>(null);

  // Determine current user's role in the team
  useEffect(() => {
    if (user && members.length > 0) {
      const member = members.find((m) => m.user_id === user.id);
      if (member) {
        setCurrentUserRole(member.role);
      }
    }
  }, [user, members]);

  // Update filters when filter changes
  useEffect(() => {
    if (filter === 'all') {
      setFilters({ team_id: teamId });
    } else {
      setFilters({ team_id: teamId, status: filter });
    }
  }, [filter, teamId, setFilters]);

  const handleCreateTask = async (data: CreateTaskRequest | UpdateTaskRequest) => {
    try {
      // For team tasks, ensure team_id is set
      await createTask({
        title: data.title || '',
        description: data.description,
        status: data.status,
        priority: data.priority,
        due_date: data.due_date,
        team_id: teamId,
      });
      setShowCreateForm(false);
    } catch (err) {
      throw err; // Let TaskForm handle the error
    }
  };

  const handleStatusChange = async (taskId: string, status: TaskStatus) => {
    try {
      await updateTask(taskId, { status });
    } catch (err) {
      console.error('Failed to update task:', err);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await deleteTask(taskId);
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };

  // Permission checks
  const canCreateTasks = currentUserRole && ['owner', 'admin', 'member'].includes(currentUserRole);
  const canEditTasks = currentUserRole && ['owner', 'admin', 'member'].includes(currentUserRole);
  const canDeleteTasks = currentUserRole && ['owner', 'admin'].includes(currentUserRole);

  // Loading state
  if (teamLoading || tasksLoading) {
    return <LoadingState message="Loading team tasks..." />;
  }

  // Error state
  if (teamError) {
    return (
      <div className="max-w-4xl mx-auto">
        <Alert variant="error">{teamError}</Alert>
        <Button onClick={() => router.push('/teams')} className="mt-4">
          Back to Teams
        </Button>
      </div>
    );
  }

  // Team not found
  if (!team) {
    return (
      <div className="max-w-4xl mx-auto">
        <Alert variant="error">Team not found</Alert>
        <Button onClick={() => router.push('/teams')} className="mt-4">
          Back to Teams
        </Button>
      </div>
    );
  }

  const filteredTasks = filter === 'all' ? tasks : tasks.filter((t) => t.status === filter);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-900">{team.name} Tasks</h1>
            {currentUserRole && (
              <Badge variant={currentUserRole === 'owner' ? 'success' : 'info'}>
                {currentUserRole}
              </Badge>
            )}
          </div>
          <p className="text-gray-600">
            Manage tasks for your team
          </p>
        </div>

        <div className="flex gap-2">
          {canCreateTasks && (
            <Button
              variant="primary"
              onClick={() => setShowCreateForm(!showCreateForm)}
            >
              {showCreateForm ? 'Cancel' : 'Create Task'}
            </Button>
          )}
          <Button variant="outline" onClick={() => router.push(`/teams/${teamId}`)}>
            Back to Team
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {tasksError && (
        <Alert variant="error">{tasksError}</Alert>
      )}

      {/* Create Task Form */}
      {showCreateForm && canCreateTasks && (
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Create Team Task</h2>
          </CardHeader>
          <CardBody>
            <TaskForm
              onSubmit={handleCreateTask}
              onCancel={() => setShowCreateForm(false)}
            />
          </CardBody>
        </Card>
      )}

      {/* Permission Notice for Viewers */}
      {currentUserRole === 'viewer' && (
        <Alert variant="info">
          You have view-only access to this team. You can view tasks but cannot create or modify them.
        </Alert>
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
        {filteredTasks.length === 0 ? (
          <EmptyState
            title={filter === 'all' ? 'No tasks yet' : `No ${filter.replace('_', ' ')} tasks`}
            description={
              canCreateTasks
                ? 'Create your first team task to get started'
                : 'No tasks to display'
            }
            action={
              canCreateTasks && !showCreateForm ? (
                <Button onClick={() => setShowCreateForm(true)}>
                  Create Task
                </Button>
              ) : undefined
            }
          />
        ) : (
          filteredTasks.map((task) => (
            <Card key={task.id} variant="bordered">
              <CardBody>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <TaskCard
                      task={task}
                      showTeam={false}
                      onClick={() => router.push(`/tasks/${task.id}`)}
                    />
                  </div>

                  {/* Action Controls */}
                  <div className="flex flex-col space-y-2 ml-4">
                    {/* Status Selector - enabled for members and above */}
                    <select
                      value={task.status}
                      onChange={(e) => handleStatusChange(task.id, e.target.value as TaskStatus)}
                      disabled={!canEditTasks}
                      className={`px-3 py-1 text-sm font-medium rounded-md border ${
                        task.status === 'completed'
                          ? 'bg-green-50 text-green-700 border-green-200'
                          : task.status === 'in_progress'
                          ? 'bg-blue-50 text-blue-700 border-blue-200'
                          : 'bg-yellow-50 text-yellow-700 border-yellow-200'
                      } ${!canEditTasks ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                    </select>

                    {/* Delete Button - only for admins and owners */}
                    {canDeleteTasks && (
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteTask(task.id)}
                      >
                        Delete
                      </Button>
                    )}
                  </div>
                </div>
              </CardBody>
            </Card>
          ))
        )}
      </div>

      {/* Team Stats */}
      <Card variant="bordered">
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{tasks.length}</div>
              <div className="text-sm text-gray-600">Total Tasks</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">
                {tasks.filter((t) => t.status === 'pending').length}
              </div>
              <div className="text-sm text-gray-600">Pending</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {tasks.filter((t) => t.status === 'in_progress').length}
              </div>
              <div className="text-sm text-gray-600">In Progress</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {tasks.filter((t) => t.status === 'completed').length}
              </div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
