import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import ErrorBoundary from '@/components/ErrorBoundary';
import { Providers } from '@/components/Providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'Todo App - Manage Your Tasks Efficiently',
    template: '%s | Todo App',
  },
  description: 'A modern task management application with team collaboration, role-based access control, and real-time updates. Organize your work, collaborate with teams, and boost productivity.',
  keywords: ['todo', 'task management', 'productivity', 'team collaboration', 'project management', 'task tracking'],
  authors: [{ name: 'Todo App Team' }],
  creator: 'Todo App',
  publisher: 'Todo App',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'Todo App - Manage Your Tasks Efficiently',
    description: 'A modern task management application with team collaboration, role-based access control, and real-time updates.',
    siteName: 'Todo App',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Todo App - Task Management',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Todo App - Manage Your Tasks Efficiently',
    description: 'A modern task management application with team collaboration and real-time updates.',
    images: ['/og-image.png'],
    creator: '@todoapp',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

/**
 * Root layout component
 * Server Component - handles global layout and metadata
 * Wrapped with ErrorBoundary for global error handling
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </Providers>
      </body>
    </html>
  );
}
