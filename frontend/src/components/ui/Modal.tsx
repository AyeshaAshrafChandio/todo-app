'use client';

import { ReactNode, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showCloseButton?: boolean;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  className?: string;
}

/**
 * Reusable Modal component with overlay and accessibility features
 *
 * Features:
 * - Overlay backdrop with click-to-close
 * - Escape key to close
 * - Focus trap
 * - Accessible with ARIA labels
 * - Multiple size options
 */
export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  className,
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle escape key press
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Focus trap - focus first focusable element when modal opens
  useEffect(() => {
    if (isOpen && modalRef.current) {
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0] as HTMLElement;
      if (firstElement) {
        firstElement.focus();
      }
    }
  }, [isOpen]);

  // Handle overlay click
  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={handleOverlayClick}
        aria-hidden="true"
      />

      {/* Modal content */}
      <div
        ref={modalRef}
        className={cn(
          'relative z-10 w-full rounded-lg bg-white shadow-xl',
          'transform transition-all',
          {
            'max-w-sm': size === 'sm',
            'max-w-md': size === 'md',
            'max-w-lg': size === 'lg',
            'max-w-2xl': size === 'xl',
          },
          className
        )}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
            {title && (
              <h2
                id="modal-title"
                className="text-lg font-semibold text-gray-900"
              >
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                type="button"
                onClick={onClose}
                className={cn(
                  'rounded-md p-1 text-gray-400 hover:text-gray-500',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500',
                  'transition-colors',
                  !title && 'ml-auto'
                )}
                aria-label="Close modal"
              >
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  );
}

/**
 * Modal Footer component for action buttons
 */
interface ModalFooterProps {
  children: ReactNode;
  className?: string;
}

export function ModalFooter({ children, className }: ModalFooterProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-end gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4',
        className
      )}
    >
      {children}
    </div>
  );
}

/**
 * Modal Body component for content
 */
interface ModalBodyProps {
  children: ReactNode;
  className?: string;
}

export function ModalBody({ children, className }: ModalBodyProps) {
  return <div className={cn('space-y-4', className)}>{children}</div>;
}
