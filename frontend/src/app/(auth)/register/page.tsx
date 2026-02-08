import { RegisterForm } from '@/components/auth/RegisterForm';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Register',
  description: 'Create a new Todo App account to start managing your tasks and collaborating with teams.',
  openGraph: {
    title: 'Register - Todo App',
    description: 'Create a new Todo App account to start managing your tasks and collaborating with teams.',
    url: '/register',
  },
  twitter: {
    card: 'summary',
    title: 'Register - Todo App',
    description: 'Create a new Todo App account.',
  },
  robots: {
    index: false,
    follow: true,
  },
};

/**
 * Register page - Client Component for user registration
 * Uses the reusable RegisterForm component
 */
export default function RegisterPage() {
  return <RegisterForm />;
}
