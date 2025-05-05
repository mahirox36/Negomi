"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useLayout } from "@/lib/contexts/LayoutContext";
import toast from "react-hot-toast";

interface SidebarItem {
  name: string;
  link: string;
  icon?: string;
}

interface ServerSidebarProps {
  serverId: string;
  hasUnsavedChanges?: boolean;
  onNavigationAttempt?: () => boolean;
}

export default function ServerSidebar({
  serverId,
  hasUnsavedChanges = false,
  onNavigationAttempt,
}: ServerSidebarProps) {
  const pathname = usePathname();
  const [hasInitiallyAnimated, setHasInitiallyAnimated] = useState(false);
  const [serverInfo, setServerInfo] = useState<{ name: string; icon_url: string | null } | null>(null);
  const router = useRouter();
  const { serverSidebar, fetchServerSidebar, isLoading } = useLayout();

  useEffect(() => {
    const fetchServerInfo = async () => {
      try {
        const response = await fetch(`/api/v1/guilds/${serverId}`);
        const data = await response.json();
        setServerInfo({
          name: data.name,
          icon_url: data.icon_url
        });
      } catch (error) {
        console.error('Failed to fetch server info:', error);
        toast.error('Failed to load server information');
      }
    };

    fetchServerInfo();
  }, [serverId]);

  useEffect(() => {
    fetchServerSidebar();
  }, [fetchServerSidebar]);

  useEffect(() => {
    setHasInitiallyAnimated(true);
  }, []);

  const handleNavigation = (e: React.MouseEvent, href: string) => {
    if (hasUnsavedChanges && onNavigationAttempt?.()) {
      e.preventDefault();
      return;
    }
    router.push(href);
  };

  if (isLoading || !serverSidebar) {
    return (
      <div className="fixed left-0 top-16 bottom-0 w-64 bg-white/5 backdrop-blur-lg border-r border-white/5 animate-pulse">
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-white/10"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-white/10 rounded w-3/4"></div>
              <div className="h-3 bg-white/10 rounded w-1/2"></div>
            </div>
          </div>
        </div>
        <div className="p-4 space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-2">
              <div className="h-3 bg-white/10 rounded w-1/3"></div>
              {[1, 2, 3].map((j) => (
                <div key={j} className="h-8 bg-white/5 rounded-lg"></div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      layout
      layoutRoot
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="fixed left-0 top-16 bottom-0 w-64 bg-white/5 backdrop-blur-lg border-r border-white/5"
    >
      <div className="h-full overflow-y-auto">
        {/* Server Info Header */}
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3 mb-4">
            {serverInfo?.icon_url ? (
              <img
                src={serverInfo.icon_url}
                alt={serverInfo.name}
                className="w-12 h-12 rounded-xl"
              />
            ) : (
              <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center">
                <i className="fas fa-server text-xl text-white/50" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <h2 className="text-white font-medium truncate">{serverInfo?.name}</h2>
              <p className="text-white/60 text-sm">Server Settings</p>
            </div>
          </div>
          
          <Link
            href="/dashboard"
            className="flex items-center px-3 py-2 rounded-lg text-white/60 hover:text-white transition-colors group bg-white/5 hover:bg-white/10"
          >
            <motion.div
              whileHover={{ x: -4 }}
              className="flex items-center w-full"
            >
              <div className="w-5 flex items-center justify-center mr-3">
                <i className="fa-solid fa-arrow-left group-hover:transform group-hover:-translate-x-1 transition-transform" />
              </div>
              <span className="font-medium">Back to Dashboard</span>
            </motion.div>
          </Link>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-2">
          {Object.entries(serverSidebar as Record<string, SidebarItem[]>).map(([section, items], sectionIndex) => (
            <motion.div key={section}>
              <h3 className="text-white/70 text-sm font-semibold mb-2 px-2">
                {section}
              </h3>
              <div className="space-y-1">
                {items.map((item, itemIndex) => {
                  const href = `/dashboard/server/${serverId}/${item.link}`;
                  const isActive = pathname === href;

                  return (
                    <motion.div
                      key={item.name}
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: (sectionIndex + itemIndex) * 0.1 }}
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
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ))}
        </nav>
      </div>
    </motion.div>
  );
}
