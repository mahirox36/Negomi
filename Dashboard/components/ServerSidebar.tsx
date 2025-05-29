"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  // Close mobile menu on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.server-sidebar') && !target.closest('.mobile-menu-button')) {
        setIsMobileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMobileMenuOpen]);

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
    setIsMobileMenuOpen(false);
    router.push(href);
  };

  const getBackInfo = () => {
    const paths = pathname.split('/');
    if (paths.length > 5) {
      return {
        href: `/dashboard/server/${serverId}/${paths[4]}`,
        text: `Back to ${paths[4].charAt(0).toUpperCase() + paths[4].slice(1)}`
      };
    }
    return {
      href: '/dashboard',
      text: 'Back to Dashboard'
    };
  };

  if (isLoading || !serverSidebar) {
    return (
      <>
        {/* Enhanced Mobile Menu Button */}
        <motion.button
          className="fixed top-20 left-4 z-50 p-3 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 backdrop-blur-xl border border-white/20 shadow-xl mobile-menu-button"
          whileTap={{ scale: 0.95 }}
          animate={{ 
            boxShadow: ["0 0 20px rgba(139, 92, 246, 0.3)", "0 0 30px rgba(59, 130, 246, 0.4)", "0 0 20px rgba(139, 92, 246, 0.3)"],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <div className="w-6 h-6 flex items-center justify-center">
            <div className="w-4 h-4 rounded bg-white/20 animate-pulse"></div>
          </div>
        </motion.button>

        {/* Desktop Sidebar Loading */}
        <div className="hidden lg:block fixed left-0 top-16 bottom-0 w-72 backdrop-blur-xl border-r border-white/10 animate-pulse">
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20"></div>
              <div className="flex-1 space-y-3">
                <div className="h-5 bg-white/10 rounded-lg w-3/4"></div>
                <div className="h-3 bg-white/10 rounded-lg w-1/2"></div>
              </div>
            </div>
          </div>
          <div className="p-6 space-y-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-3">
                <div className="h-4 bg-white/10 rounded-lg w-1/3"></div>
                {[1, 2, 3].map((j) => (
                  <div key={j} className="h-12 bg-white/5 rounded-xl"></div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      {/* Enhanced Mobile Menu Button */}
      <motion.button
        className="lg:hidden fixed top-20 left-4 z-50 p-3 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 backdrop-blur-xl border border-white/20 shadow-xl mobile-menu-button overflow-hidden"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        whileTap={{ scale: 0.95 }}
        whileHover={{ scale: 1.05 }}
      >
        {/* Animated background */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-blue-500/30"
          animate={{
            opacity: isMobileMenuOpen ? 1 : 0,
            scale: isMobileMenuOpen ? 1 : 0.8,
          }}
          transition={{ duration: 0.3 }}
        />
        
        {/* Icon container */}
        <motion.div
          className="relative w-6 h-6 flex items-center justify-center"
          animate={{ rotate: isMobileMenuOpen ? 180 : 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <AnimatePresence mode="wait">
            {isMobileMenuOpen ? (
              <motion.i
                key="close"
                className="fas fa-times text-white text-lg"
                initial={{ opacity: 0, rotate: -90 }}
                animate={{ opacity: 1, rotate: 0 }}
                exit={{ opacity: 0, rotate: 90 }}
                transition={{ duration: 0.2 }}
              />
            ) : (
              <motion.i
                key="menu"
                className="fas fa-bars text-white text-lg"
                initial={{ opacity: 0, rotate: 90 }}
                animate={{ opacity: 1, rotate: 0 }}
                exit={{ opacity: 0, rotate: -90 }}
                transition={{ duration: 0.2 }}
              />
            )}
          </AnimatePresence>
        </motion.div>

        {/* Ripple effect */}
        <motion.div
          className="absolute inset-0 rounded-2xl"
          animate={{
            background: isMobileMenuOpen 
              ? "radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%)"
              : "radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%)"
          }}
          transition={{ duration: 0.3 }}
        />
      </motion.button>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            className="lg:hidden server-sidebar fixed left-0 top-0 bottom-0 w-80 bg-gradient-to-br backdrop-blur-xl border-r border-white/20 shadow-2xl z-50 overflow-hidden"
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 30,
              opacity: { duration: 0.2 }
            }}
          >
            {/* Animated background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-blue-500/5 to-emerald-500/10 opacity-50" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/20 via-transparent to-blue-500/20" />
            
            <div className="relative h-full overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
              {/* Enhanced Server Info Header */}
              <div className="p-6 pt-20 border-b border-white/10 bg-gradient-to-r from-white/5 to-transparent">
                <motion.div 
                  className="flex items-center gap-4 mb-6"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <div className="relative">
                    {serverInfo?.icon_url ? (
                      <motion.img
                        src={serverInfo.icon_url}
                        alt={serverInfo.name}
                        className="w-16 h-16 rounded-2xl shadow-lg border-2 border-white/20"
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      />
                    ) : (
                      <motion.div 
                        className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/30 to-blue-500/30 flex items-center justify-center shadow-lg border-2 border-white/20"
                        whileHover={{ scale: 1.1, rotate: -5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <i className="fas fa-server text-2xl text-white/70" />
                      </motion.div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h2 className="text-white font-bold text-xl truncate bg-gradient-to-r from-white to-white/80 bg-clip-text">
                      {serverInfo?.name}
                    </h2>
                    <p className="text-white/60 text-sm font-medium">Server Settings</p>
                  </div>
                </motion.div>
                
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  onClick={(e) => {
                    const backInfo = getBackInfo();
                    handleNavigation(e, backInfo.href);
                  }}
                  className="cursor-pointer flex items-center px-4 py-3 rounded-xl text-white/70 hover:text-white transition-all group bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 backdrop-blur-sm"
                >
                  <motion.div
                    whileHover={{ x: -6 }}
                    className="flex items-center w-full"
                    transition={{ type: "spring", stiffness: 400 }}
                  >
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center mr-3 group-hover:from-purple-500/30 group-hover:to-blue-500/30 transition-all">
                      <i className="fa-solid fa-arrow-left group-hover:transform group-hover:-translate-x-1 transition-transform" />
                    </div>
                    <span className="font-semibold">
                      {getBackInfo().text}
                    </span>
                  </motion.div>
                </motion.div>
              </div>

              {/* Enhanced Navigation Items */}
              <nav className="p-6 space-y-6">
                {Object.entries(serverSidebar as Record<string, SidebarItem[]>).map(([section, items], sectionIndex) => (
                  <motion.div 
                    key={section}
                    initial={{ y: 30, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.3 + sectionIndex * 0.1 }}
                  >
                    <h3 className="text-white/80 text-sm font-bold mb-4 px-2 uppercase tracking-wider bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                      {section}
                    </h3>
                    <div className="space-y-2">
                      {items.map((item, itemIndex) => {
                        const href = `/dashboard/server/${serverId}/${item.link}`;
                        const isActive = pathname.startsWith(href);

                        return (
                          <motion.div
                            key={item.name}
                            initial={{ x: -30, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ 
                              delay: 0.4 + sectionIndex * 0.1 + itemIndex * 0.05,
                              type: "spring",
                              stiffness: 300
                            }}
                            onClick={(e) => handleNavigation(e, href)}
                            className="cursor-pointer"
                          >
                            <motion.div
                              className={`relative flex items-center px-4 py-3 rounded-xl transition-all group overflow-hidden ${
                                isActive
                                  ? "text-white bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30 shadow-lg"
                                  : "text-white/70 hover:text-white hover:bg-white/10 border border-transparent hover:border-white/20"
                              }`}
                              whileHover={{ 
                                scale: 1.02,
                                x: 6,
                              }}
                              whileTap={{ scale: 0.98 }}
                              transition={{ type: "spring", stiffness: 400 }}
                            >
                              {/* Background effects */}
                              {isActive && (
                                <motion.div
                                  layoutId="mobile-sidebar-active"
                                  className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-xl"
                                  initial={false}
                                  transition={{
                                    type: "spring",
                                    stiffness: 500,
                                    damping: 30,
                                  }}
                                />
                              )}
                              
                              {/* Icon container */}
                              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mr-4 transition-all ${
                                isActive 
                                  ? "bg-gradient-to-br from-purple-500/30 to-blue-500/30 shadow-lg" 
                                  : "bg-white/5 group-hover:bg-white/10"
                              }`}>
                                <i className={`${item.icon || "fa-solid fa-gear"} ${isActive ? 'text-purple-300' : 'text-white/70 group-hover:text-white'}`} />
                              </div>
                              
                              {/* Text */}
                              <span className="font-semibold flex-1">
                                {item.name}
                              </span>
                              
                              {/* Arrow indicator */}
                              <motion.i 
                                className={`fas fa-chevron-right text-xs transition-all ${
                                  isActive ? 'text-purple-300' : 'text-white/30 group-hover:text-white/60'
                                }`}
                                whileHover={{ x: 2 }}
                              />

                              {/* Active indicator */}
                              {isActive && (
                                <motion.div
                                  className="absolute left-0 top-1/2 w-1 h-8 bg-gradient-to-b from-purple-500 to-blue-500 rounded-r-full -translate-y-1/2"
                                  layoutId="mobile-active-indicator"
                                  initial={false}
                                  transition={{
                                    type: "spring",
                                    stiffness: 500,
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

              {/* Bottom gradient fade */}
              <div className="h-20 bg-gradient-to-t from-slate-900/50 to-transparent pointer-events-none" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop Sidebar - Enhanced */}
      <motion.div
        className="hidden lg:block fixed left-0 top-16 bottom-0 w-72 backdrop-blur-xl border-r border-white/10 shadow-2xl overflow-hidden"
        initial={{ x: -50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
        {/* Background effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-blue-500/3 to-emerald-500/5" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/10 via-transparent to-blue-500/10" />
        
        <div className="relative h-full overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
          {/* Desktop Server Info Header */}
          <div className="p-6 border-b border-white/10 bg-gradient-to-r from-white/5 to-transparent">
            <div className="flex items-center gap-4 mb-6">
              <div className="relative">
                {serverInfo?.icon_url ? (
                  <motion.img
                    src={serverInfo.icon_url}
                    alt={serverInfo.name}
                    className="w-14 h-14 rounded-2xl shadow-lg border-2 border-white/20"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  />
                ) : (
                  <motion.div 
                    className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/30 to-blue-500/30 flex items-center justify-center shadow-lg border-2 border-white/20"
                    whileHover={{ scale: 1.1, rotate: -5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <i className="fas fa-server text-xl text-white/70" />
                  </motion.div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-white font-bold text-lg truncate bg-gradient-to-r from-white to-white/80 bg-clip-text">
                  {serverInfo?.name}
                </h2>
                <p className="text-white/60 text-sm font-medium">Server Settings</p>
              </div>
            </div>
            
            <motion.div
              onClick={(e) => {
                const backInfo = getBackInfo();
                handleNavigation(e, backInfo.href);
              }}
              className="cursor-pointer flex items-center px-4 py-3 rounded-xl text-white/70 hover:text-white transition-all group bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <motion.div
                whileHover={{ x: -4 }}
                className="flex items-center w-full"
                transition={{ type: "spring", stiffness: 400 }}
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center mr-3 group-hover:from-purple-500/30 group-hover:to-blue-500/30 transition-all">
                  <i className="fa-solid fa-arrow-left text-sm group-hover:transform group-hover:-translate-x-1 transition-transform" />
                </div>
                <span className="font-semibold text-sm">
                  {getBackInfo().text}
                </span>
              </motion.div>
            </motion.div>
          </div>

          {/* Desktop Navigation Items */}
          <nav className="p-6 space-y-6">
            {Object.entries(serverSidebar as Record<string, SidebarItem[]>).map(([section, items], sectionIndex) => (
              <motion.div 
                key={section}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: sectionIndex * 0.1 }}
              >
                <h3 className="text-white/80 text-xs font-bold mb-3 px-2 uppercase tracking-wider bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                  {section}
                </h3>
                <div className="space-y-1">
                  {items.map((item, itemIndex) => {
                    const href = `/dashboard/server/${serverId}/${item.link}`;
                    const isActive = pathname.startsWith(href);

                    return (
                      <motion.div
                        key={item.name}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: sectionIndex * 0.1 + itemIndex * 0.05 }}
                        onClick={(e) => handleNavigation(e, href)}
                        className="cursor-pointer"
                      >
                        <motion.div
                          className={`relative flex items-center px-3 py-2.5 rounded-lg transition-all group ${
                            isActive
                              ? "text-white bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30"
                              : "text-white/70 hover:text-white hover:bg-white/10 border border-transparent hover:border-white/20"
                          }`}
                          whileHover={{ 
                            scale: 1.02,
                            x: 4,
                          }}
                          whileTap={{ scale: 0.98 }}
                        >
                          {isActive && (
                            <motion.div
                              layoutId="desktop-sidebar-active"
                              className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg"
                              initial={false}
                              transition={{
                                type: "spring",
                                stiffness: 500,
                                damping: 30,
                              }}
                            />
                          )}
                          
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center mr-3 transition-all ${
                            isActive 
                              ? "bg-gradient-to-br from-purple-500/30 to-blue-500/30" 
                              : "bg-white/5 group-hover:bg-white/10"
                          }`}>
                            <i className={`${item.icon || "fa-solid fa-gear"} text-sm ${isActive ? 'text-purple-300' : 'text-white/70 group-hover:text-white'}`} />
                          </div>
                          
                          <span className="font-medium text-sm flex-1">
                            {item.name}
                          </span>

                          {isActive && (
                            <motion.div
                              className="absolute left-0 top-1/2 w-0.5 h-6 bg-gradient-to-b from-purple-500 to-blue-500 rounded-r-full -translate-y-1/2"
                              layoutId="desktop-active-indicator"
                              initial={false}
                              transition={{
                                type: "spring",
                                stiffness: 500,
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
    </>
  );
}