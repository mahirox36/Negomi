'use client';

import { ReactNode } from 'react';
import Sidebar from './Sidebar';
import { User, Guild } from '../types/discord';

interface DashboardLayoutProps {
  children: ReactNode;
  user?: User;
  guilds?: Guild[];
}

export default function DashboardLayout({ children, user, guilds }: DashboardLayoutProps) {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      <div className="flex">
        <Sidebar user={user} guilds={guilds} />
        <div className="flex-1 pt-20 px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </div>
    </main>
  );
}
