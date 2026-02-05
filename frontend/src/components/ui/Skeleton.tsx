import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
}

/**
 * Skeleton loading component
 * Displays animated placeholder while content is loading
 */
export function Skeleton({
  className,
  variant = 'rectangular',
  width,
  height,
  ...props
}: SkeletonProps) {
  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return (
    <div
      className={cn(
        'animate-pulse bg-gray-200',
        {
          'rounded-full': variant === 'circular',
          'rounded': variant === 'rectangular',
          'rounded-md h-4': variant === 'text',
        },
        className
      )}
      style={style}
      {...props}
    />
  );
}

/**
 * Card skeleton for loading task/team cards
 */
export function CardSkeleton() {
  return (
    <div className="rounded-lg border border-gray-100 bg-white p-6 shadow-sm">
      <div className="space-y-3">
        <Skeleton variant="text" className="h-6 w-3/4" />
        <Skeleton variant="text" className="h-4 w-full" />
        <Skeleton variant="text" className="h-4 w-5/6" />
        <div className="flex items-center justify-between pt-4">
          <Skeleton variant="text" className="h-4 w-24" />
          <Skeleton variant="text" className="h-4 w-20" />
        </div>
      </div>
    </div>
  );
}

/**
 * List skeleton for loading lists
 */
export function ListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

/**
 * Table row skeleton for loading table rows
 */
export function TableRowSkeleton() {
  return (
    <tr className="border-b border-gray-200">
      <td className="px-6 py-4">
        <Skeleton variant="text" className="h-4 w-32" />
      </td>
      <td className="px-6 py-4">
        <Skeleton variant="text" className="h-4 w-24" />
      </td>
      <td className="px-6 py-4">
        <Skeleton variant="text" className="h-4 w-20" />
      </td>
      <td className="px-6 py-4">
        <Skeleton variant="text" className="h-4 w-16" />
      </td>
    </tr>
  );
}

/**
 * Dashboard skeleton for loading dashboard page
 */
export function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      {/* Header skeleton */}
      <div className="space-y-2">
        <Skeleton variant="text" className="h-8 w-64" />
        <Skeleton variant="text" className="h-4 w-96" />
      </div>

      {/* Stats skeleton */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-lg border border-gray-100 bg-white p-6 shadow-sm">
            <Skeleton variant="text" className="h-4 w-24 mb-2" />
            <Skeleton variant="text" className="h-8 w-16" />
          </div>
        ))}
      </div>

      {/* Content sections skeleton */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <Skeleton variant="text" className="h-6 w-48" />
          <ListSkeleton count={3} />
        </div>
        <div className="space-y-4">
          <Skeleton variant="text" className="h-6 w-48" />
          <ListSkeleton count={3} />
        </div>
      </div>
    </div>
  );
}
