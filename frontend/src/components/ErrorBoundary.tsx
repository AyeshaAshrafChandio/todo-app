'use client';

import { Component, ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Global Error Boundary Component
 * Catches React component errors and displays a user-friendly fallback UI
 *
 * Features:
 * - Catches unhandled errors in React component tree
 * - Displays user-friendly error message
 * - Provides reload button to recover
 * - Shows error details in development mode
 * - Logs errors to console for debugging
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error details to console
    console.error('Error Boundary caught an error:', error);
    console.error('Error Info:', errorInfo);

    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });

    // In production, you could send error to logging service here
    // Example: logErrorToService(error, errorInfo);
  }

  handleReload = () => {
    // Reset error state and reload the page
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
            {/* Error Icon */}
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>

            {/* Error Message */}
            <h1 className="text-3xl font-bold text-gray-900 text-center mb-4">
              Oops! Something went wrong
            </h1>
            <p className="text-gray-600 text-center mb-8">
              We encountered an unexpected error. Please try reloading the page.
              If the problem persists, contact support.
            </p>

            {/* Reload Button */}
            <div className="flex justify-center mb-8">
              <button
                onClick={this.handleReload}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                Reload Page
              </button>
            </div>

            {/* Error Details (Development Only) */}
            {isDevelopment && this.state.error && (
              <div className="mt-8 border-t border-gray-200 pt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Error Details (Development Mode)
                </h2>

                {/* Error Message */}
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">
                    Error Message:
                  </h3>
                  <pre className="bg-red-50 border border-red-200 rounded p-4 text-sm text-red-800 overflow-x-auto">
                    {this.state.error.toString()}
                  </pre>
                </div>

                {/* Stack Trace */}
                {this.state.error.stack && (
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Stack Trace:
                    </h3>
                    <pre className="bg-gray-50 border border-gray-200 rounded p-4 text-xs text-gray-700 overflow-x-auto max-h-64 overflow-y-auto">
                      {this.state.error.stack}
                    </pre>
                  </div>
                )}

                {/* Component Stack */}
                {this.state.errorInfo?.componentStack && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Component Stack:
                    </h3>
                    <pre className="bg-gray-50 border border-gray-200 rounded p-4 text-xs text-gray-700 overflow-x-auto max-h-64 overflow-y-auto">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Help Text */}
            <div className="mt-8 text-center text-sm text-gray-500">
              <p>
                If you continue to experience issues, please contact support at{' '}
                <a
                  href="mailto:support@example.com"
                  className="text-blue-600 hover:text-blue-700 underline"
                >
                  support@example.com
                </a>
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
