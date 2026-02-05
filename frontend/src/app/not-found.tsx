import Link from 'next/link';
import { Button } from '@/components/ui/Button';

/**
 * 404 Not Found page
 */
export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="text-center max-w-md">
        <div className="text-8xl font-bold text-primary-600 mb-4">404</div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Page Not Found
        </h1>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link href="/">
          <Button variant="primary" size="lg">
            Go Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
