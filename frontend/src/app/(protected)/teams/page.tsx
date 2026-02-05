'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTeams } from '@/hooks/useTeams';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/contexts/ToastContext';
import { useConfirmDialog } from '@/components/ui/ConfirmDialog';
import type { CreateTeamRequest } from '@/lib/types/team';

// Note: Metadata cannot be exported from Client Components
// For dynamic metadata in client components, use next/head or document.title

/**
 * Teams page - List and manage all teams
 * Client Component - requires authentication and data fetching
 */
export default function TeamsPage() {
  const router = useRouter();
  const { teams, loading, createTeam, updateTeam, deleteTeam } = useTeams();
  const toast = useToast();
  const { confirm, ConfirmDialog } = useConfirmDialog();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<CreateTeamRequest>({
    name: '',
    description: '',
  });

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTeam(formData);
      setFormData({ name: '', description: '' });
      setShowCreateForm(false);
      toast.success('Team created successfully');
    } catch (err) {
      toast.error('Failed to create team. Please try again.');
    }
  };

  const handleDeleteTeam = async (teamId: string) => {
    const confirmed = await confirm(
      'Delete Team',
      'Are you sure you want to delete this team? This will remove all team members and cannot be undone.',
      { variant: 'danger', confirmText: 'Delete' }
    );

    if (!confirmed) return;

    try {
      await deleteTeam(teamId);
      toast.success('Team deleted successfully');
    } catch (err) {
      toast.error('Failed to delete team');
    }
  };

  return (
    <div className="space-y-6">
      {ConfirmDialog}
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Teams</h1>
          <p className="text-gray-600 mt-1">Collaborate with your team members</p>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : 'Create Team'}
        </Button>
      </div>

      {/* Create Team Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Create New Team</h2>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleCreateTeam} className="space-y-4">
              <Input
                label="Team Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter team name"
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Team description (optional)"
                  rows={3}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
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
                  Create Team
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>
      )}

      {/* Teams List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <ListSkeleton count={6} />
        ) : teams.length === 0 ? (
          <Card className="col-span-full">
            <CardBody>
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No teams yet</p>
                {!showCreateForm && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowCreateForm(true)}
                  >
                    Create Your First Team
                  </Button>
                )}
              </div>
            </CardBody>
          </Card>
        ) : (
          teams.map((team) => (
            <Card key={team.id} variant="elevated">
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {team.name}
                      </h3>
                      <span className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-xl">👥</span>
                      </span>
                    </div>
                    {team.description && (
                      <p className="text-gray-600 text-sm">{team.description}</p>
                    )}
                  </div>

                  <div className="text-xs text-gray-500">
                    Created: {new Date(team.created_at).toLocaleDateString()}
                  </div>

                  <div className="flex space-x-2 pt-2 border-t border-gray-200">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => router.push(`/teams/${team.id}`)}
                    >
                      View
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteTeam(team.id)}
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
