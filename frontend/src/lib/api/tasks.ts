import { apiClient } from './client';
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskShare } from '../types/task';

/**
 * Get all tasks for current user
 *
 * @param filters - Optional filters for tasks
 * @param filters.team_id - Filter by team ID
 * @param filters.access_type - Filter by access type (personal, team, shared)
 * @param filters.status - Filter by status
 * @returns Promise with array of tasks
 */
export async function getTasks(filters?: {
  team_id?: string;
  access_type?: string;
  status?: string;
}): Promise<Task[]> {
  const params = new URLSearchParams();
  if (filters?.team_id) params.append('team_id', filters.team_id);
  if (filters?.access_type) params.append('access_type', filters.access_type);
  if (filters?.status) params.append('status', filters.status);

  const queryString = params.toString();
  const url = queryString ? `/api/tasks?${queryString}` : '/api/tasks';

  return apiClient<Task[]>(url);
}

/**
 * Get a single task by ID
 */
export async function getTask(taskId: string): Promise<Task> {
  return apiClient<Task>(`/api/tasks/${taskId}`);
}

/**
 * Create a new task
 */
export async function createTask(data: CreateTaskRequest): Promise<Task> {
  return apiClient<Task>('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update a task
 */
export async function updateTask(taskId: string, data: UpdateTaskRequest): Promise<Task> {
  return apiClient<Task>(`/api/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: string): Promise<void> {
  return apiClient<void>(`/api/tasks/${taskId}`, {
    method: 'DELETE',
  });
}

/**
 * Get tasks shared with current user
 */
export async function getSharedTasks(): Promise<Task[]> {
  return apiClient<Task[]>('/api/tasks/shared');
}

/**
 * Share a task with another user
 */
export async function shareTask(
  taskId: string,
  userId: string,
  permission: 'view' | 'edit'
): Promise<TaskShare> {
  return apiClient<TaskShare>(`/api/tasks/${taskId}/share`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, permission }),
  });
}

/**
 * Get task shares
 */
export async function getTaskShares(taskId: string): Promise<TaskShare[]> {
  return apiClient<TaskShare[]>(`/api/tasks/${taskId}/shares`);
}

/**
 * Remove task share
 */
export async function removeTaskShare(taskId: string, shareId: string): Promise<void> {
  return apiClient<void>(`/api/tasks/${taskId}/shares/${shareId}`, {
    method: 'DELETE',
  });
}
