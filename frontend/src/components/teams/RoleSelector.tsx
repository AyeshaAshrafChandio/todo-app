'use client';

import { TeamRoleType } from '@/lib/types/team';
import { cn } from '@/lib/utils';

interface RoleSelectorProps {
  value: TeamRoleType;
  onChange: (role: TeamRoleType) => void;
  disabled?: boolean;
  excludeOwner?: boolean;
  className?: string;
}

/**
 * RoleSelector component - dropdown for selecting team member role
 * Can exclude owner role for regular member invitations
 */
export function RoleSelector({
  value,
  onChange,
  disabled = false,
  excludeOwner = false,
  className,
}: RoleSelectorProps) {
  const roles: { value: TeamRoleType; label: string; description: string }[] = [
    {
      value: 'owner',
      label: 'Owner',
      description: 'Full control over team and members',
    },
    {
      value: 'admin',
      label: 'Admin',
      description: 'Can manage team settings and members',
    },
    {
      value: 'member',
      label: 'Member',
      description: 'Can create and manage tasks',
    },
    {
      value: 'viewer',
      label: 'Viewer',
      description: 'Can only view team tasks',
    },
  ];

  const availableRoles = excludeOwner
    ? roles.filter((r) => r.value !== 'owner')
    : roles;

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as TeamRoleType)}
      disabled={disabled}
      className={cn(
        'block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900',
        'focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
        'disabled:bg-gray-100 disabled:cursor-not-allowed',
        className
      )}
    >
      {availableRoles.map((role) => (
        <option key={role.value} value={role.value}>
          {role.label} - {role.description}
        </option>
      ))}
    </select>
  );
}
