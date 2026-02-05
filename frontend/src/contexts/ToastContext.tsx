'use client';

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import { Toast, ToastContainer, ToastVariant } from '@/components/ui/Toast';

interface ToastData {
  id: string;
  message: string;
  variant: ToastVariant;
  duration: number;
}

interface ToastContextType {
  showToast: (
    message: string,
    variant?: ToastVariant,
    duration?: number
  ) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

/**
 * ToastProvider component
 * Manages toast notifications state and provides toast methods
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (message: string, variant: ToastVariant = 'info', duration = 5000) => {
      const id = `toast-${Date.now()}-${Math.random()}`;
      const newToast: ToastData = {
        id,
        message,
        variant,
        duration,
      };

      setToasts((prev) => [...prev, newToast]);
    },
    []
  );

  const success = useCallback(
    (message: string, duration = 5000) => {
      showToast(message, 'success', duration);
    },
    [showToast]
  );

  const error = useCallback(
    (message: string, duration = 7000) => {
      showToast(message, 'error', duration);
    },
    [showToast]
  );

  const warning = useCallback(
    (message: string, duration = 6000) => {
      showToast(message, 'warning', duration);
    },
    [showToast]
  );

  const info = useCallback(
    (message: string, duration = 5000) => {
      showToast(message, 'info', duration);
    },
    [showToast]
  );

  return (
    <ToastContext.Provider
      value={{ showToast, success, error, warning, info }}
    >
      {children}
      <ToastContainer>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            id={toast.id}
            message={toast.message}
            variant={toast.variant}
            duration={toast.duration}
            onClose={removeToast}
          />
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
}

/**
 * useToast hook
 * Provides access to toast notification methods
 * @throws Error if used outside ToastProvider
 */
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}
