/**
 * Example usage of foundational components
 * This file demonstrates how to use the new utilities and components
 */

// ============================================
// 1. VALIDATION UTILITIES
// ============================================

import {
  validateEmail,
  validatePassword,
  validateTaskTitle,
  validateRequired,
} from '@/lib/utils/validation';

// Example: Form validation
function validateLoginForm(email: string, password: string) {
  const emailResult = validateEmail(email);
  if (!emailResult.isValid) {
    return { error: emailResult.error };
  }

  const passwordResult = validatePassword(password);
  if (!passwordResult.isValid) {
    return { error: passwordResult.error };
  }

  return { error: null };
}

// ============================================
// 2. ERROR HANDLING UTILITIES
// ============================================

import {
  getErrorMessage,
  isAuthError,
  formatValidationErrors,
  handleAsyncError,
} from '@/lib/utils/errors';

// Example: API error handling
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) throw new Error('Failed to fetch');
    return await response.json();
  } catch (error) {
    if (isAuthError(error)) {
      // Redirect to login
      window.location.href = '/login';
    }
    const message = getErrorMessage(error);
    console.error(message);
  }
}

// Example: Async error handling with tuple
async function loadUserData() {
  const [data, error] = await handleAsyncError(
    fetch('/api/user').then((r) => r.json())
  );

  if (error) {
    console.error('Failed to load user:', getErrorMessage(error));
    return null;
  }

  return data;
}

// ============================================
// 3. FORMAT UTILITIES
// ============================================

import {
  formatRelativeTime,
  formatTaskStatus,
  formatCount,
  capitalize,
} from '@/lib/utils/format';

// Example: Display task information
function TaskInfo({ task }: { task: any }) {
  return (
    <div>
      <p>Status: {formatTaskStatus(task.status)}</p>
      <p>Created: {formatRelativeTime(task.created_at)}</p>
      <p>{formatCount(task.comments?.length || 0, 'comment')}</p>
    </div>
  );
}

// ============================================
// 4. SESSION MANAGEMENT
// ============================================

import {
  createSession,
  getSession,
  destroySession,
  isAuthenticated,
} from '@/lib/auth/session';

// Example: Login flow
async function handleLogin(email: string, password: string) {
  const response = await fetch('/api/auth/signin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  // Create session with token and user data
  createSession(data.token, data.user);

  // Redirect to dashboard
  window.location.href = '/dashboard';
}

// Example: Check authentication
function ProtectedComponent() {
  const session = getSession();

  if (!session.isAuthenticated) {
    return <div>Please log in</div>;
  }

  return <div>Welcome, {session.user?.email}</div>;
}

// Example: Logout
function handleLogout() {
  destroySession();
  window.location.href = '/login';
}

// ============================================
// 5. MODAL COMPONENT
// ============================================

import { Modal, ModalBody, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

function DeleteConfirmationModal({ isOpen, onClose, onConfirm }: any) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirm Deletion"
      size="md"
    >
      <ModalBody>
        <p>Are you sure you want to delete this task?</p>
        <p className="text-sm text-gray-500 mt-2">
          This action cannot be undone.
        </p>
      </ModalBody>
      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="danger" onClick={onConfirm}>
          Delete
        </Button>
      </ModalFooter>
    </Modal>
  );
}

// ============================================
// 6. EMPTY STATE COMPONENT
// ============================================

import { EmptyState, EmptyStateIcons } from '@/components/ui/EmptyState';

function TaskList({ tasks }: { tasks: any[] }) {
  if (tasks.length === 0) {
    return (
      <EmptyState
        icon={<EmptyStateIcons.NoTasks />}
        title="No tasks yet"
        description="Create your first task to get started with your todo list"
        action={{
          label: 'Create Task',
          onClick: () => console.log('Create task'),
        }}
      />
    );
  }

  return (
    <div>
      {tasks.map((task) => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}

// ============================================
// 7. COMPLETE FORM EXAMPLE
// ============================================

import { useState } from 'react';

function TaskForm() {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate
    const validation = validateTaskTitle(title);
    if (!validation.isValid) {
      setError(validation.error || 'Invalid title');
      return;
    }

    setLoading(true);

    // Submit
    const [data, submitError] = await handleAsyncError(
      fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      }).then((r) => r.json())
    );

    setLoading(false);

    if (submitError) {
      setError(getErrorMessage(submitError));
      return;
    }

    // Success
    console.log('Task created:', data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
      />
      {error && <p className="text-red-600">{error}</p>}
      <Button type="submit" isLoading={loading}>
        Create Task
      </Button>
    </form>
  );
}

export {
  validateLoginForm,
  fetchData,
  loadUserData,
  TaskInfo,
  handleLogin,
  ProtectedComponent,
  handleLogout,
  DeleteConfirmationModal,
  TaskList,
  TaskForm,
};
