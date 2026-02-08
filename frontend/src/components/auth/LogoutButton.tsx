'use client';

import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import type { ButtonHTMLAttributes } from 'react';

interface LogoutButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'onClick'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

/**
 * LogoutButton Component
 *
 * Reusable logout button that handles user sign out
 * Can be customized with different variants and sizes
 *
 * @example
 * ```tsx
 * // Default usage
 * <LogoutButton />
 *
 * // With custom styling
 * <LogoutButton variant="outline" size="sm" />
 *
 * // With icon
 * <LogoutButton showIcon />
 * ```
 */
export function LogoutButton({
  variant = 'outline',
  size = 'sm',
  showIcon = false,
  children,
  className,
  ...props
}: LogoutButtonProps) {
  const { logout, loading } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleLogout}
      disabled={loading}
      className={className}
      {...props}
    >
      {showIcon && (
        <svg
          className="h-4 w-4 mr-2"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
          />
        </svg>
      )}
      {children || 'Logout'}
    </Button>
  );
}
