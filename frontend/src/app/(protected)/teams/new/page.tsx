'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { TeamForm } from '@/components/teams/TeamForm';
import { useTeams } from '@/hooks/useTeams';
import type { CreateTeamRequest, UpdateTeamRequest } from '@/lib/types/team';

/**
 * New Team Page - Create a new team
 * Client Component - requires form interaction and navigation
 */
export default function NewTeamPage() {
  const router = useRouter();
  const { createTeam } = useTeams();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: CreateTeamRequest | UpdateTeamRequest) => {
    setIsSubmitting(true);
    try {
      const newTeam = await createTeam({
        name: data.name || '',
        description: data.description,
      });
      // Navigate to the new team's detail page
      router.push(`/teams/${newTeam.id}`);
    } catch (error) {
      console.error('Failed to create team:', error);
      setIsSubmitting(false);
      throw error; // Let TeamForm handle the error display
    }
  };

  const handleCancel = () => {
    router.push('/teams');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Create New Team</h1>
        <p className="text-gray-600 mt-1">
          Set up a new team to collaborate with others
        </p>
      </div>

      {/* Create Team Form */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">Team Details</h2>
        </CardHeader>
        <CardBody>
          <TeamForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            submitLabel="Create Team"
            isLoading={isSubmitting}
          />
        </CardBody>
      </Card>

      {/* Help Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          What happens next?
        </h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>You will be the team owner with full permissions</li>
          <li>You can invite members and assign roles</li>
          <li>Team members can create and manage tasks together</li>
          <li>You can manage team settings at any time</li>
        </ul>
      </div>
    </div>
  );
}
