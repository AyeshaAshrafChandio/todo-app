import Link from 'next/link';
import { Button } from '@/components/ui/Button';

/**
 * Home page - Landing page for the application
 * Server Component
 */
export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary-600">Todo App</h1>
          <nav className="flex gap-4">
            <Link href="/login">
              <Button variant="outline" size="sm">
                Login
              </Button>
            </Link>
            <Link href="/register">
              <Button variant="primary" size="sm">
                Sign Up
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center">
        <div className="container mx-auto px-4 py-16 text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Manage Your Tasks Efficiently
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            A modern task management application with team collaboration,
            role-based access control, and task sharing capabilities.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/register">
              <Button variant="primary" size="lg">
                Get Started
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg">
                Sign In
              </Button>
            </Link>
          </div>

          {/* Features */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-100">
              <div className="text-4xl mb-4">✓</div>
              <h3 className="text-lg font-semibold mb-2">Task Management</h3>
              <p className="text-gray-600">
                Create, organize, and track your tasks with ease
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-100">
              <div className="text-4xl mb-4">👥</div>
              <h3 className="text-lg font-semibold mb-2">Team Collaboration</h3>
              <p className="text-gray-600">
                Work together with your team on shared projects
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-100">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="text-lg font-semibold mb-2">Secure & Private</h3>
              <p className="text-gray-600">
                Your data is protected with enterprise-grade security
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-6 text-center text-gray-600">
          <p>&copy; 2026 Todo App. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
