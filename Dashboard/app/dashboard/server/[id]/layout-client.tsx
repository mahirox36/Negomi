"use client";

import { ReactNode, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import PageTransition from "@/app/components/PageTransition";
import ServerSidebar from "@/app/components/ServerSidebar";
import { useLayout } from "@/providers/LayoutProvider";

interface LayoutProps {
  children: ReactNode;
  serverId: string;
}

export default function ServerLayoutClient({ children, serverId }: LayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { 
    hasChanges, 
    isLoading, 
    setServerId, 
    setCurrentPath 
  } = useLayout();

  useEffect(() => {
    if (serverId) {
      setServerId(serverId);
      setCurrentPath(pathname.split("/").pop() || "");
    }
  }, [serverId, pathname, setServerId, setCurrentPath]);

  const handleNavigationAttempt = () => {
    if (hasChanges) {
      return true;
    }
    return false;
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      <div className="flex-1 pt-16 relative">
        <div className="flex h-full">
          <div className="w-64 flex-shrink-0">
            <ServerSidebar
              serverId={serverId}
              hasUnsavedChanges={hasChanges}
              onNavigationAttempt={handleNavigationAttempt}
            />
          </div>
          <main className="flex-1 relative">
            <div className="absolute inset-0 overflow-y-auto">
              <div className="p-8">
                <div className="max-w-4xl mx-auto">
                  <AnimatePresence mode="wait">
                    <PageTransition key={pathname}>
                      <motion.div
                        animate={{
                          opacity: isLoading ? 0.5 : 1,
                          scale: isLoading ? 0.99 : 1,
                        }}
                        transition={{ duration: 0.2 }}
                      >
                        {children}
                      </motion.div>
                    </PageTransition>
                  </AnimatePresence>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
