'use client';

import { ReactNode } from 'react';
import { AnimatePresence } from 'framer-motion';
import Navbar from './Navbar';
import ServerSidebar from './ServerSidebar';
import PageTransition from './PageTransition';
import { usePathname } from 'next/navigation';

interface ServerLayoutProps {
  children: ReactNode;
  serverId: string;
  sidebarProps?: {
    hasUnsavedChanges?: boolean;
    onNavigationAttempt?: () => void;
  };
}

export default function ServerLayout({ children, serverId, sidebarProps }: ServerLayoutProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      <Navbar />
      <div className="pt-16">
        <div className="flex">
          <ServerSidebar 
            serverId={serverId}
            hasUnsavedChanges={sidebarProps?.hasUnsavedChanges}
            onNavigationAttempt={sidebarProps?.onNavigationAttempt}
          />
          <div className="flex-1 p-8 relative">
            <div className="max-w-4xl mx-auto">
              <AnimatePresence mode="wait">
                <PageTransition key={pathname}>
                  {children}
                </PageTransition>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
