'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { LoadingState } from '@/components/shared/LoadingState';
import { MemberList } from '@/components/teams/MemberList';
import { MemberInvite } from '@/components/teams/MemberInvite';
import * as teamsApi from '@/lib/api/teams';
import type { Team, TeamMember, TeamRoleType } from '@/lib/types/team';

/**
 * Team Detail Page - View team details and manage members
 * Client Component - requires data fetching and interactions
 */
export default function TeamDetailPage() {
  const params = useParams();
  const router = useRouter();
  const teamId = params.teamId as string;

  const [team, setTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [currentUserRole, setCurrentUserRole] = useState<TeamRoleType | null>(null);

  useEffect(() => {
    loadTeamData();
  }, [teamId]);

  const loadTeamData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [teamData, membersData] = await Promise.all([
        teamsApi.getTeam(teamId),
        teamsApi.getTeamMembers(teamId),
      ]);

      setTeam(teamData);
      setMembers(membersData);

      // TODO: Get current user ID from auth context
      // For now, we'll assume the first member is the current user
      if (membersData.length > 0) {
        setCurrentUserRole(membersData[0].role);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load team';
      setError(message);
      console.error('Failed to load team:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInviteMember = async (userId: string, role: TeamRoleType) => {
    try {
      const newMember = await teamsApi.addTeamMember(teamId, { user_id: userId, role });
      setMembers((prev) => [...prev, newMember]);
      setShowInviteForm(false);
    } catch (err) {
      throw err; // Let MemberInvite component handle the error
    }
  };

  const handleChangeRole = async (userId: string, newRole: TeamRoleType) => {
    try {
      const updatedMember = await teamsApi.updateTeamMember(teamId, userId, { role: newRole });
      setMembers((prev) =>
        prev.map((m) => (m.user_id === userId ? updatedMember : m))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change role');
    }
  };

  const handleRemoveMember = async (userId: string) => {
    try {
      await teamsApi.removeTeamMember(teamId, userId);
      setMembers((prev) => prev.filter((m) => m.user_id !== userId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove member');
    }
  };

  const handleDeleteTeam = async () => {
    if (!confirm('Are you sure you want to delete this team? This action cannot be undone.')) {
      return;
    }

    try {
      await teamsApi.deleteTeam(teamId);
      router.push('/teams');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete team');
    }
  };

  if (loading) {
    return <LoadingState message="Loading team details..." />;
  }

  if (error && !team) {
    return (
      <div className="max-w-4xl mx-auto">
        <Alert variant="error">{error}</Alert>
        <Button onClick={() => router.push('/teams')} className="mt-4">
          Back to Teams
        </Button>
      </div>
    );
  }

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

  const canManageTeam = currentUserRole === 'owner' || currentUserRole === 'admin';
  const isOwner = currentUserRole === 'owner';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-900">{team.name}</h1>
            {currentUserRole && (
              <Badge variant={currentUserRole === 'owner' ? 'success' : 'info'}>
                {currentUserRole}
              </Badge>
            )}
          </div>
          {team.description && (
            <p className="text-gray-600">{team.description}</p>
          )}
          <p className="text-sm text-gray-500 mt-2">
            Created {new Date(team.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="flex gap-2">
          {canManageTeam && (
            <Button
              variant="outline"
              onClick={() => router.push(`/teams/${teamId}/settings`)}
            >
              Settings
            </Button>
          )}
          <Button variant="outline" onClick={() => router.push('/teams')}>
            Back
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Team Members Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">Team Members</h2>
              <p className="text-sm text-gray-600 mt-1">
                {members.length} {members.length === 1 ? 'member' : 'members'}
              </p>
            </div>
            {canManageTeam && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowInviteForm(!showInviteForm)}
              >
                {showInviteForm ? 'Cancel' : 'Invite Member'}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardBody>
          {showInviteForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-4">Invite New Member</h3>
              <MemberInvite
                onInvite={handleInviteMember}
                onCancel={() => setShowInviteForm(false)}
              />
            </div>
          )}

          <MemberList
            members={members}
            currentUserRole={currentUserRole || undefined}
            onChangeRole={isOwner ? handleChangeRole : undefined}
            onRemoveMember={canManageTeam ? handleRemoveMember : undefined}
          />
        </CardBody>
      </Card>

      {/* Danger Zone */}
      {isOwner && (
        <Card variant="bordered">
          <CardHeader>
            <h2 className="text-xl font-semibold text-red-600">Danger Zone</h2>
          </CardHeader>
          <CardBody>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Delete Team</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Permanently delete this team and all associated data. This action cannot be undone.
                </p>
              </div>
              <Button variant="danger" onClick={handleDeleteTeam}>
                Delete Team
              </Button>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
