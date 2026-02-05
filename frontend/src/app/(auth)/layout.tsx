/**
 * Auth Layout - Layout for authentication pages (login, register)
 * Server Component - No authentication check needed (public pages)
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      {/* Header with branding */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg
                  className="h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
              </div>
              <span className="text-xl font-bold text-gray-900">Todo App</span>
            </div>
            <div className="text-sm text-gray-600">
              Your productivity companion
            </div>
          </div>
        </div>
      </header>

      {/* Main content area */}
      <main className="flex items-center justify-center px-4 py-12">
        {children}
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>
            Built with Next.js, FastAPI, and PostgreSQL
          </p>
        </div>
      </footer>
    </div>
  );
}
