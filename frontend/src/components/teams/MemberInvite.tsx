'use client';

import { useState, FormEvent } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { RoleSelector } from './RoleSelector';
import type { TeamRoleType } from '@/lib/types/team';
import { sanitizeInput } from '@/lib/utils/sanitize';

interface MemberInviteProps {
  onInvite: (userId: string, role: TeamRoleType) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

/**
 * MemberInvite component - invite member form
 * Allows selecting user ID and role
 */
export function MemberInvite({
  onInvite,
  onCancel,
  isLoading = false,
}: MemberInviteProps) {
  const [userId, setUserId] = useState('');
  const [role, setRole] = useState<TeamRoleType>('member');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    if (!userId.trim()) {
      setError('User ID is required');
      return;
    }

    try {
      // Sanitize user input before submission
      const sanitizedUserId = sanitizeInput(userId.trim());
      await onInvite(sanitizedUserId, role);
      setSuccess('Member invited successfully');
      setUserId('');
      setRole('member');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to invite member');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="error">
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          {success}
        </Alert>
      )}

      <Input
        label="User ID"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        placeholder="Enter user ID to invite"
        required
        disabled={isLoading}
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Role
        </label>
        <RoleSelector
          value={role}
          onChange={setRole}
          disabled={isLoading}
          excludeOwner
        />
        <p className="mt-1 text-xs text-gray-500">
          {role === 'admin' && 'Can manage team settings and members'}
          {role === 'member' && 'Can create and manage tasks'}
          {role === 'viewer' && 'Can only view team tasks'}
        </p>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        )}
        <Button type="submit" variant="primary" isLoading={isLoading}>
          Invite Member
        </Button>
      </div>
    </form>
  );
}
