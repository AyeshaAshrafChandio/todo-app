import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
}

/**
 * Alert component for notifications and messages
 */
const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'info', title, children, ...props }, ref) => {
    const icons = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border p-4',
          {
            'bg-blue-50 border-blue-200 text-blue-900': variant === 'info',
            'bg-green-50 border-green-200 text-green-900': variant === 'success',
            'bg-yellow-50 border-yellow-200 text-yellow-900': variant === 'warning',
            'bg-red-50 border-red-200 text-red-900': variant === 'error',
          },
          className
        )}
        role="alert"
        {...props}
      >
        <div className="flex items-start">
          <span className="text-xl mr-3">{icons[variant]}</span>
          <div className="flex-1">
            {title && (
              <h5 className="font-semibold mb-1">{title}</h5>
            )}
            <div className="text-sm">{children}</div>
          </div>
        </div>
      </div>
    );
  }
);

Alert.displayName = 'Alert';

export { Alert };
