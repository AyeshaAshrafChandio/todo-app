/**
 * Loading component for protected pages
 */
export default function ProtectedLoading() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
