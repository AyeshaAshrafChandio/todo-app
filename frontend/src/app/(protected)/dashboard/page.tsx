'use client';

import { useTasks } from '@/hooks/useTasks';
import { useTeams } from '@/hooks/useTeams';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DashboardSkeleton } from '@/components/ui/Skeleton';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import Link from 'next/link';

// Note: Metadata cannot be exported from Client Components
// For dynamic metadata in client components, use next/head or document.title

/**
 * Dashboard page - Overview of user's tasks and teams
 * Client Component - requires authentication and data fetching
 *
 * Features:
 * - Real-time statistics with 5-second polling
 * - Recent tasks overview
 * - Teams overview
 * - Quick action buttons
 */
export default function DashboardPage() {
  const { tasks, loading: tasksLoading } = useTasks();
  const { teams, loading: teamsLoading } = useTeams();

  // Show skeleton while loading initial data
  if (tasksLoading || teamsLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your overview.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link href="/chat">
            <Button variant="primary" size="sm">💬 AI Chat Assistant</Button>
          </Link>
          <Link href="/tasks">
            <Button variant="outline" size="sm">Create Task</Button>
          </Link>
        </div>
      </div>

      {/* Real-time Dashboard Statistics */}
      <DashboardLayout />

      {/* Recent Tasks */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Recent Tasks</h2>
            <Link href="/tasks">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardBody>
          {tasksLoading ? (
            <div className="text-center py-8 text-gray-500">Loading tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No tasks yet</p>
              <Link href="/tasks">
                <Button variant="primary" size="sm">
                  Create Your First Task
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.slice(0, 5).map((task) => (
                <div
                  key={task.id}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors gap-2"
                >
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">{task.title}</h3>
                    {task.description && (
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">{task.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${
                        task.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : task.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {task.status ? task.status.replace('_', ' ') : 'pending'}
                    </span>
                    {task.priority && (
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${
                          task.priority === 'high'
                            ? 'bg-red-100 text-red-700'
                            : task.priority === 'medium'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {task.priority}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Teams Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Your Teams</h2>
            <Link href="/teams">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardBody>
          {teamsLoading ? (
            <div className="text-center py-8 text-gray-500">Loading teams...</div>
          ) : teams.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No teams yet</p>
              <Link href="/teams">
                <Button variant="primary" size="sm">
                  Create Your First Team
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {teams.slice(0, 6).map((team) => (
                <div
                  key={team.id}
                  className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <h3 className="font-medium text-gray-900">{team.name}</h3>
                  {team.description && (
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{team.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
