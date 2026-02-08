'use client';

import { useState, useEffect, useCallback } from 'react';
import * as tasksApi from '@/lib/api/tasks';
import type { Task, CreateTaskRequest, UpdateTaskRequest } from '@/lib/types/task';

interface UseTasksFilters {
  team_id?: string;
  access_type?: string;
  status?: string;
}

interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  createTask: (data: CreateTaskRequest) => Promise<Task>;
  updateTask: (taskId: string, data: UpdateTaskRequest) => Promise<Task>;
  deleteTask: (taskId: string) => Promise<void>;
  refreshTasks: () => Promise<void>;
  setFilters: (filters: UseTasksFilters) => void;
}

/**
 * Hook for managing tasks with optional filtering
 *
 * @param initialFilters - Optional initial filters for tasks
 * @returns Object with tasks state and management functions
 *
 * @example
 * ```tsx
 * // Get all tasks
 * const { tasks, loading } = useTasks();
 *
 * // Get only team tasks
 * const { tasks, loading } = useTasks({ access_type: 'team' });
 *
 * // Get tasks for specific team
 * const { tasks, loading } = useTasks({ team_id: 'team-123' });
 * ```
 */
export function useTasks(initialFilters?: UseTasksFilters): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<UseTasksFilters>(initialFilters || {});

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await tasksApi.getTasks(filters);
      setTasks(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load tasks';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const createTask = useCallback(async (data: CreateTaskRequest): Promise<Task> => {
    try {
      const newTask = await tasksApi.createTask(data);
      setTasks((prev) => [newTask, ...prev]);
      return newTask;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create task';
      setError(message);
      throw err;
    }
  }, []);

  const updateTask = useCallback(async (taskId: string, data: UpdateTaskRequest): Promise<Task> => {
    try {
      const updatedTask = await tasksApi.updateTask(taskId, data);
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      return updatedTask;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update task';
      setError(message);
      throw err;
    }
  }, []);

  const deleteTask = useCallback(async (taskId: string): Promise<void> => {
    try {
      await tasksApi.deleteTask(taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete task';
      setError(message);
      throw err;
    }
  }, []);

  return {
    tasks,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
    refreshTasks: loadTasks,
    setFilters,
  };
}
