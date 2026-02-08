import { LoginForm } from '@/components/auth/LoginForm';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Login',
  description: 'Sign in to your Todo App account to manage your tasks and collaborate with your team.',
  openGraph: {
    title: 'Login - Todo App',
    description: 'Sign in to your Todo App account to manage your tasks and collaborate with your team.',
    url: '/login',
  },
  twitter: {
    card: 'summary',
    title: 'Login - Todo App',
    description: 'Sign in to your Todo App account.',
  },
  robots: {
    index: false,
    follow: true,
  },
};

/**
 * Login page - Client Component for authentication
 * Uses the reusable LoginForm component
 */
export default function LoginPage() {
  return <LoginForm />;
}
