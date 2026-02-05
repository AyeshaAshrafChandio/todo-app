/**
 * Task Sharing API Client
 *
 * Provides functions for sharing tasks with other users, managing share permissions,
 * and retrieving shared tasks.
 */

import { apiClient } from './client';
import type {
  ShareTaskRequest,
  ShareTaskResponse,
  TaskSharesResponse,
  SharedTasksResponse,
  TaskShare
} from '../types/share';

/**
 * Share a task with another user
 *
 * @param taskId - ID of the task to share
 * @param request - Share request with email and permission
 * @returns Promise with share response
 * @throws Error if sharing fails
 *
 * @example
 * ```ts
 * const response = await shareTask('task-123', {
 *   email: 'colleague@example.com',
 *   permission: SharePermission.EDIT
 * });
 * console.log(response.message); // "Task shared successfully"
 * ```
 */
export async function shareTask(
  taskId: string,
  request: ShareTaskRequest
): Promise<ShareTaskResponse> {
  return apiClient<ShareTaskResponse>(
    `/tasks/${taskId}/share`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    }
  );
}

/**
 * Revoke task share from a user
 *
 * @param taskId - ID of the task
 * @param userId - ID of the user to revoke share from
 * @returns Promise with success message
 * @throws Error if revocation fails
 *
 * @example
 * ```ts
 * await revokeShare('task-123', 'user-456');
 * console.log('Share revoked successfully');
 * ```
 */
export async function revokeShare(
  taskId: string,
  userId: string
): Promise<{ message: string }> {
  return apiClient<{ message: string }>(
    `/tasks/${taskId}/share/${userId}`,
    {
      method: 'DELETE',
    }
  );
}

/**
 * Get list of users a task is shared with
 *
 * @param taskId - ID of the task
 * @returns Promise with list of share records
 * @throws Error if retrieval fails
 *
 * @example
 * ```ts
 * const response = await getTaskShares('task-123');
 * console.log(`Shared with ${response.shares.length} users`);
 * response.shares.forEach(share => {
 *   console.log(`${share.shared_with_email}: ${share.permission}`);
 * });
 * ```
 */
export async function getTaskShares(taskId: string): Promise<TaskSharesResponse> {
  return apiClient<TaskSharesResponse>(`/tasks/${taskId}/shares`);
}

/**
 * Get list of tasks shared with the current user
 *
 * @returns Promise with list of shared tasks
 * @throws Error if retrieval fails
 *
 * @example
 * ```ts
 * const response = await getSharedTasks();
 * console.log(`You have ${response.total} shared tasks`);
 * response.tasks.forEach(task => {
 *   console.log(`${task.title} (${task.permission} access)`);
 * });
 * ```
 */
export async function getSharedTasks(): Promise<SharedTasksResponse> {
  return apiClient<SharedTasksResponse>('/tasks/shared-with-me');
}

/**
 * Update share permission for a user
 *
 * @param taskId - ID of the task
 * @param userId - ID of the user
 * @param permission - New permission level
 * @returns Promise with updated share record
 * @throws Error if update fails
 *
 * @example
 * ```ts
 * const share = await updateSharePermission(
 *   'task-123',
 *   'user-456',
 *   SharePermission.VIEW
 * );
 * console.log(`Permission updated to ${share.permission}`);
 * ```
 */
export async function updateSharePermission(
  taskId: string,
  userId: string,
  permission: string
): Promise<TaskShare> {
  return apiClient<TaskShare>(
    `/tasks/${taskId}/share/${userId}`,
    {
      method: 'PATCH',
      body: JSON.stringify({ permission }),
    }
  );
}

/**
 * Check if current user has permission to share a task
 *
 * @param taskId - ID of the task
 * @returns Promise with boolean indicating if user can share
 *
 * @example
 * ```ts
 * const canShare = await canShareTask('task-123');
 * if (canShare) {
 *   // Show share button
 * }
 * ```
 */
export async function canShareTask(taskId: string): Promise<boolean> {
  try {
    // Try to get task shares - if successful, user has permission
    await getTaskShares(taskId);
    return true;
  } catch (error) {
    // If 403 or 404, user doesn't have permission
    return false;
  }
}
