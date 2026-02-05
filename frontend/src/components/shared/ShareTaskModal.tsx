/**
 * Share Task Modal Component
 *
 * Modal dialog for sharing a task with other users.
 * Allows selecting a user by email and choosing permission level.
 */

'use client';

import { useState } from 'react';
import { SharePermission } from '@/lib/types/share';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';

interface ShareTaskModalProps {
  /** Whether the modal is open */
  isOpen: boolean;

  /** Callback when modal should close */
  onClose: () => void;

  /** Callback when task is shared successfully */
  onShare: (email: string, permission: SharePermission) => Promise<void>;

  /** Task title for display */
  taskTitle: string;
}

/**
 * Modal for sharing a task with another user
 *
 * @example
 * ```tsx
 * const [isOpen, setIsOpen] = useState(false);
 *
 * <ShareTaskModal
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   onShare={async (email, permission) => {
 *     await shareTask(taskId, { email, permission });
 *   }}
 *   taskTitle="Complete project documentation"
 * />
 * ```
 */
export function ShareTaskModal({
  isOpen,
  onClose,
  onShare,
  taskTitle
}: ShareTaskModalProps) {
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState<SharePermission>(SharePermission.VIEW);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onShare(email, permission);
      // Reset form and close modal on success
      setEmail('');
      setPermission(SharePermission.VIEW);
      onClose();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to share task';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setEmail('');
      setPermission(SharePermission.VIEW);
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Share Task</h2>
          <p className="mt-1 text-sm text-gray-600 truncate">{taskTitle}</p>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="px-6 py-4">
          {error && (
            <Alert variant="error" className="mb-4">
              {error}
            </Alert>
          )}

          {/* Email Input */}
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              User Email
            </label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="colleague@example.com"
              disabled={loading}
              required
              autoFocus
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter the email address of the user you want to share with
            </p>
          </div>

          {/* Permission Select */}
          <div className="mb-4">
            <label htmlFor="permission" className="block text-sm font-medium text-gray-700 mb-1">
              Permission Level
            </label>
            <select
              id="permission"
              value={permission}
              onChange={(e) => setPermission(e.target.value as SharePermission)}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value={SharePermission.VIEW}>View Only</option>
              <option value={SharePermission.EDIT}>Can Edit</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {permission === SharePermission.VIEW
                ? 'User can view the task but cannot make changes'
                : 'User can view and edit the task'}
            </p>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Sharing...
                </>
              ) : (
                'Share Task'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
