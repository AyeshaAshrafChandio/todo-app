'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { LoadingState } from '@/components/shared/LoadingState';
import { TeamForm } from '@/components/teams/TeamForm';
import * as teamsApi from '@/lib/api/teams';
import type { Team, UpdateTeamRequest } from '@/lib/types/team';

/**
 * Team Settings Page - Edit team details
 * Client Component - requires form interaction and data fetching
 */
export default function TeamSettingsPage() {
  const params = useParams();
  const router = useRouter();
  const teamId = params.teamId as string;

  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    loadTeam();
  }, [teamId]);

  const loadTeam = async () => {
    setLoading(true);
    setError(null);

    try {
      const teamData = await teamsApi.getTeam(teamId);
      setTeam(teamData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load team';
      setError(message);
      console.error('Failed to load team:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: UpdateTeamRequest) => {
    setIsSubmitting(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const updatedTeam = await teamsApi.updateTeam(teamId, data);
      setTeam(updatedTeam);
      setSuccessMessage('Team settings updated successfully');

      // Redirect back to team detail page after a short delay
      setTimeout(() => {
        router.push(`/teams/${teamId}`);
      }, 1500);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update team';
      setError(message);
      setIsSubmitting(false);
      throw err; // Let TeamForm handle the error display
    }
  };

  const handleCancel = () => {
    router.push(`/teams/${teamId}`);
  };

  if (loading) {
    return <LoadingState message="Loading team settings..." />;
  }

  if (error && !team) {
    return (
      <div className="max-w-2xl mx-auto">
        <Alert variant="error">{error}</Alert>
        <Button onClick={() => router.push('/teams')} className="mt-4">
          Back to Teams
        </Button>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="max-w-2xl mx-auto">
        <Alert variant="error">Team not found</Alert>
        <Button onClick={() => router.push('/teams')} className="mt-4">
          Back to Teams
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Team Settings</h1>
          <p className="text-gray-600 mt-1">Update your team details</p>
        </div>
        <Button variant="outline" onClick={handleCancel}>
          Cancel
        </Button>
      </div>

      {/* Success Message */}
      {successMessage && (
        <Alert variant="success" onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Edit Team Form */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">Team Details</h2>
        </CardHeader>
        <CardBody>
          <TeamForm
            initialData={{
              name: team.name,
              description: team.description,
            }}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            submitLabel="Save Changes"
            isLoading={isSubmitting}
          />
        </CardBody>
      </Card>

      {/* Team Info */}
      <Card variant="bordered">
        <CardBody>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Team Information</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-600">Team ID:</dt>
              <dd className="text-gray-900 font-mono">{team.id}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Created:</dt>
              <dd className="text-gray-900">
                {new Date(team.created_at).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Last Updated:</dt>
              <dd className="text-gray-900">
                {new Date(team.updated_at).toLocaleString()}
              </dd>
            </div>
          </dl>
        </CardBody>
      </Card>
    </div>
  );
}
