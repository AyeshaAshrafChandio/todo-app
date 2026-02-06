import { apiClient } from './client';
import { getUserIdFromToken } from '../auth/token';
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskShare } from '../types/task';

/**
 * Get current user ID from token
 */
function getCurrentUserId(): string {
  const userId = getUserIdFromToken();
  if (!userId) {
    throw new Error('User not authenticated');
  }
  return userId;
}

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
  const userId = getCurrentUserId();
  const params = new URLSearchParams();
  if (filters?.team_id) params.append('team_id', filters.team_id);
  if (filters?.access_type) params.append('access_type', filters.access_type);
  if (filters?.status) params.append('status', filters.status);

  const queryString = params.toString();
  const url = queryString ? `/api/${userId}/tasks?${queryString}` : `/api/${userId}/tasks`;

  return apiClient<Task[]>(url);
}

/**
 * Get a single task by ID
 */
export async function getTask(taskId: string): Promise<Task> {
  const userId = getCurrentUserId();
  return apiClient<Task>(`/api/${userId}/tasks/${taskId}`);
}

/**
 * Create a new task
 */
export async function createTask(data: CreateTaskRequest): Promise<Task> {
  const userId = getCurrentUserId();
  return apiClient<Task>(`/api/${userId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update a task
 */
export async function updateTask(taskId: string, data: UpdateTaskRequest): Promise<Task> {
  const userId = getCurrentUserId();
  return apiClient<Task>(`/api/${userId}/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: string): Promise<void> {
  const userId = getCurrentUserId();
  return apiClient<void>(`/api/${userId}/tasks/${taskId}`, {
    method: 'DELETE',
  });
}

/**
 * Get tasks shared with current user
 */
export async function getSharedTasks(): Promise<Task[]> {
  const userId = getCurrentUserId();
  return apiClient<Task[]>(`/api/${userId}/tasks/shared`);
}

/**
 * Share a task with another user
 */
export async function shareTask(
  taskId: string,
  userId: string,
  permission: 'view' | 'edit'
): Promise<TaskShare> {
  const currentUserId = getCurrentUserId();
  return apiClient<TaskShare>(`/api/${currentUserId}/tasks/${taskId}/share`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, permission }),
  });
}

/**
 * Get task shares
 */
export async function getTaskShares(taskId: string): Promise<TaskShare[]> {
  const userId = getCurrentUserId();
  return apiClient<TaskShare[]>(`/api/${userId}/tasks/${taskId}/shares`);
}

/**
 * Remove task share
 */
export async function removeTaskShare(taskId: string, shareId: string): Promise<void> {
  const userId = getCurrentUserId();
  return apiClient<void>(`/api/${userId}/tasks/${taskId}/shares/${shareId}`, {
    method: 'DELETE',
  });
}
