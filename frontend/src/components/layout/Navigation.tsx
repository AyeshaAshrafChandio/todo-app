'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * Navigation Component
 *
 * Main navigation menu for authenticated users
 * Highlights active route based on current pathname
 */
export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/tasks', label: 'Tasks' },
    { href: '/teams', label: 'Teams' },
    { href: '/shared', label: 'Shared' },
    { href: '/chat', label: '💬 AI Chat' },
  ];

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === href;
    }
    return pathname.startsWith(href);
  };

  return (
    <nav className="hidden md:flex space-x-1">
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            isActive(item.href)
              ? 'bg-primary-50 text-primary-700'
              : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
          }`}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
