// Task types
export type TaskStatus = 'pending' | 'in_progress' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high';

/**
 * Task access type indicating how the user has access to the task
 * - personal: User owns the task (no team)
 * - team: Task belongs to a team the user is a member of
 * - shared: Task was directly shared with the user
 */
export type TaskAccessType = 'personal' | 'team' | 'shared';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  user_id: string;
  team_id?: string;
  created_at: string;
  updated_at: string;

  // Extended fields for team context
  access_type?: TaskAccessType;
  team_name?: string;
  owner_email?: string;
  completed?: boolean;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  team_id?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
}

export interface TaskShare {
  id: string;
  task_id: string;
  shared_with_user_id: string;
  permission: 'view' | 'edit';
  shared_by_user_id: string;
  created_at: string;
}
