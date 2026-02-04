'use client';

import { Team } from '@/lib/types/team';
import { TeamCard } from './TeamCard';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingState } from '@/components/shared/LoadingState';

interface TeamListProps {
  teams: Team[];
  loading?: boolean;
  error?: string | null;
  onTeamClick?: (teamId: string) => void;
  onTeamEdit?: (teamId: string) => void;
  onTeamDelete?: (teamId: string) => void;
  emptyMessage?: string;
  emptyAction?: React.ReactNode;
}

/**
 * TeamList component - displays a grid of team cards
 * Handles loading, error, and empty states
 */
export function TeamList({
  teams,
  loading = false,
  error = null,
  onTeamClick,
  onTeamEdit,
  onTeamDelete,
  emptyMessage = 'No teams yet',
  emptyAction,
}: TeamListProps) {
  if (loading) {
    return <LoadingState message="Loading teams..." />;
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (teams.length === 0) {
    return (
      <EmptyState
        title={emptyMessage}
        description="Create your first team to start collaborating"
        action={emptyAction}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {teams.map((team) => (
        <TeamCard
          key={team.id}
          team={team}
          onView={onTeamClick ? () => onTeamClick(team.id) : undefined}
          onEdit={onTeamEdit ? () => onTeamEdit(team.id) : undefined}
          onDelete={onTeamDelete ? () => onTeamDelete(team.id) : undefined}
        />
      ))}
    </div>
  );
}
