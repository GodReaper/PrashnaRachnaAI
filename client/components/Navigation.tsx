import { SignOutButton } from '@clerk/nextjs';
import Link from 'next/link';

interface NavigationProps {
  currentPath: string;
  userName: string;
}

export function Navigation({ currentPath, userName }: NavigationProps) {
  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/upload', label: 'Upload Document' },
    { href: '/questions', label: 'My Questions' },
  ];

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="text-xl font-bold text-gray-800">
              Question Generator
            </Link>
            <div className="hidden md:flex space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`font-medium ${
                    currentPath === item.href
                      ? 'text-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">
              {userName}
            </span>
            <SignOutButton>
              <button className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded">
                Sign Out
              </button>
            </SignOutButton>
          </div>
        </div>
      </div>
    </nav>
  );
} 