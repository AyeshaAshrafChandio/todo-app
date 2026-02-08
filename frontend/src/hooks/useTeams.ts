'use client';

import { useState, useEffect, useCallback } from 'react';
import * as teamsApi from '@/lib/api/teams';
import type { Team, CreateTeamRequest, UpdateTeamRequest } from '@/lib/types/team';

export { useTeamDetails } from './useTeamDetails';

interface UseTeamsReturn {
  teams: Team[];
  loading: boolean;
  error: string | null;
  createTeam: (data: CreateTeamRequest) => Promise<Team>;
  updateTeam: (teamId: string, data: UpdateTeamRequest) => Promise<Team>;
  deleteTeam: (teamId: string) => Promise<void>;
  refreshTeams: () => Promise<void>;
}

/**
 * Hook for managing teams
 */
export function useTeams(): UseTeamsReturn {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTeams = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await teamsApi.getTeams();
      setTeams(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load teams';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTeams();
  }, [loadTeams]);

  const createTeam = useCallback(async (data: CreateTeamRequest): Promise<Team> => {
    try {
      const newTeam = await teamsApi.createTeam(data);
      setTeams((prev) => [newTeam, ...prev]);
      return newTeam;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create team';
      setError(message);
      throw err;
    }
  }, []);

  const updateTeam = useCallback(async (teamId: string, data: UpdateTeamRequest): Promise<Team> => {
    try {
      const updatedTeam = await teamsApi.updateTeam(teamId, data);
      setTeams((prev) =>
        prev.map((team) => (team.id === teamId ? updatedTeam : team))
      );
      return updatedTeam;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update team';
      setError(message);
      throw err;
    }
  }, []);

  const deleteTeam = useCallback(async (teamId: string): Promise<void> => {
    try {
      await teamsApi.deleteTeam(teamId);
      setTeams((prev) => prev.filter((team) => team.id !== teamId));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete team';
      setError(message);
      throw err;
    }
  }, []);

  return {
    teams,
    loading,
    error,
    createTeam,
    updateTeam,
    deleteTeam,
    refreshTeams: loadTeams,
  };
}
