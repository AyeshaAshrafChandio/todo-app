/**
 * Task Sharing Type Definitions
 *
 * Defines types for task sharing functionality including permissions,
 * share records, and shared task representations.
 */

/**
 * Share permission levels
 * - view: Can only view the task
 * - edit: Can view and modify the task
 */
export enum SharePermission {
  VIEW = 'view',
  EDIT = 'edit'
}

/**
 * Task share record
 * Represents a task that has been shared with a user
 */
export interface TaskShare {
  /** ID of the task being shared */
  task_id: string;

  /** ID of the user the task is shared with */
  shared_with_user_id: string;

  /** Email of the user the task is shared with */
  shared_with_email: string;

  /** Permission level granted (view or edit) */
  permission: SharePermission;

  /** When the share was created */
  shared_at: string;

  /** ID of the user who shared the task */
  shared_by_user_id: string;

  /** Email of the user who shared the task */
  shared_by_email?: string;
}

/**
 * Shared task representation
 * Includes both the task details and sharing information
 */
export interface SharedTask {
  /** Task ID */
  id: string;

  /** Task title */
  title: string;

  /** Task description */
  description?: string;

  /** Whether the task is completed */
  completed: boolean;

  /** When the task was created */
  created_at: string;

  /** When the task was last updated */
  updated_at: string;

  /** ID of the task owner */
  owner_id: string;

  /** Email of the task owner */
  owner_email?: string;

  /** Team ID if task belongs to a team */
  team_id?: string;

  /** Team name if task belongs to a team */
  team_name?: string;

  /** Permission level for the current user */
  permission: SharePermission;

  /** When the task was shared with the current user */
  shared_at: string;

  /** ID of the user who shared the task */
  shared_by_user_id: string;

  /** Email of the user who shared the task */
  shared_by_email?: string;
}

/**
 * Request to share a task with a user
 */
export interface ShareTaskRequest {
  /** Email of the user to share with */
  email: string;

  /** Permission level to grant */
  permission: SharePermission;
}

/**
 * Response after sharing a task
 */
export interface ShareTaskResponse {
  /** Success message */
  message: string;

  /** The created share record */
  share: TaskShare;
}

/**
 * Response containing list of users a task is shared with
 */
export interface TaskSharesResponse {
  /** Task ID */
  task_id: string;

  /** List of share records */
  shares: TaskShare[];
}

/**
 * Response containing list of tasks shared with the current user
 */
export interface SharedTasksResponse {
  /** List of shared tasks */
  tasks: SharedTask[];

  /** Total count of shared tasks */
  total: number;
}
