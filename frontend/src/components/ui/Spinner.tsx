import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Loading spinner component
 */
const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size = 'md', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'inline-block animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent',
          {
            'h-4 w-4 border-2': size === 'sm',
            'h-8 w-8': size === 'md',
            'h-12 w-12': size === 'lg',
          },
          className
        )}
        role="status"
        aria-label="Loading"
        {...props}
      >
        <span className="sr-only">Loading...</span>
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

export { Spinner };
