'use client';

import { useState, useEffect, useCallback } from 'react';
import * as teamsApi from '@/lib/api/teams';
import type { Team, TeamMember } from '@/lib/types/team';

interface UseTeamDetailsReturn {
  team: Team | null;
  members: TeamMember[];
  loading: boolean;
  error: string | null;
  refreshTeam: () => Promise<void>;
  refreshMembers: () => Promise<void>;
  refresh: () => Promise<void>;
}

/**
 * Hook for managing team details and members
 * Fetches team data and members list
 */
export function useTeamDetails(teamId: string): UseTeamDetailsReturn {
  const [team, setTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTeam = useCallback(async () => {
    if (!teamId) return;

    try {
      const teamData = await teamsApi.getTeam(teamId);
      setTeam(teamData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load team';
      setError(message);
      throw err;
    }
  }, [teamId]);

  const loadMembers = useCallback(async () => {
    if (!teamId) return;

    try {
      const membersData = await teamsApi.getTeamMembers(teamId);
      setMembers(membersData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load members';
      setError(message);
      throw err;
    }
  }, [teamId]);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await Promise.all([loadTeam(), loadMembers()]);
    } catch (err) {
      // Error already set in individual load functions
    } finally {
      setLoading(false);
    }
  }, [loadTeam, loadMembers]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  return {
    team,
    members,
    loading,
    error,
    refreshTeam: loadTeam,
    refreshMembers: loadMembers,
    refresh: loadAll,
  };
}
