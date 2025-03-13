"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useLayout } from "@/providers/LayoutProvider";
import toast from "react-hot-toast";

interface ServerSidebarProps {
  serverId: string;
  hasUnsavedChanges?: boolean;
  onNavigationAttempt?: () => void;
}

export default function ServerSidebar({ 
  serverId, 
  hasUnsavedChanges = false,
  onNavigationAttempt 
}: ServerSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { serverSidebar, fetchServerSidebar } = useLayout();

  useEffect(() => {
    fetchServerSidebar();
  }, [fetchServerSidebar]);

  const handleNavigation = (e: React.MouseEvent, href: string) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      onNavigationAttempt?.();
      return;
    }
    router.push(href);
  };

  if (!serverSidebar) return null;

  return (
    <motion.div
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-white/5 backdrop-blur-lg min-h-[calc(100vh-4rem)] sticky top-16 px-4 py-6"
    >
      <div className="space-y-8">
        {Object.entries(serverSidebar).map(([section, items]) => (
          <motion.div key={section}>
            <h3 className="text-white/70 text-sm font-semibold mb-2 px-2">
              {section}
            </h3>
            <div className="space-y-1">
              {items.map((item) => {
                const href = `/dashboard/server/${serverId}/${item.link}`;
                const isActive = pathname === href;

                return (
                  <div
                    key={item.name}
                    onClick={(e) => handleNavigation(e, href)}
                    className="cursor-pointer"
                  >
                    <motion.div
                      className={`flex items-center px-2 py-2 rounded-lg transition-colors relative ${
                        isActive
                          ? "text-white"
                          : "text-white/60 hover:text-white"
                      }`}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="w-5 flex items-center justify-center mr-3">
                        <i className={`${item.icon || "fa-solid fa-gear"}`} />
                      </div>
                      {item.name}
                      {isActive && (
                        <motion.div
                          layoutId="sidebar-active"
                          className="absolute inset-0 bg-white/10 rounded-lg -z-10"
                          initial={false}
                          transition={{
                            type: "spring",
                            stiffness: 380,
                            damping: 30,
                          }}
                        />
                      )}
                    </motion.div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
