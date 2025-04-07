"use client";

import { useState, ReactNode, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster } from "react-hot-toast";
import { usePathname } from "next/navigation";
import PageTransition from "@/app/components/PageTransition";
import ServerSidebar from "@/app/components/ServerSidebar";
import AccessDenied from "@/app/components/forbidden";
import { LayoutProvider } from "@/app/contexts/LayoutContext";
import toast from "react-hot-toast";
import axios from "axios";

interface LayoutProps {
  children: ReactNode;
  serverId: string;
}

export default function ServerLayoutClient({ children, serverId }: LayoutProps) {
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [shouldShowLoading, setShouldShowLoading] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const pathname = usePathname();
  const isChecking = useRef(false);

  const pagesWithoutReset = [
    '/dashboard/server/[id]/overview',
    '/dashboard/server/[id]/badges',
  ];

  const showResetButton = !pagesWithoutReset.some(path => 
    pathname.replace(serverId, '[id]').startsWith(path)
  );

  useEffect(() => {
    const loadingTimeout = setTimeout(() => {
      if (isLoading) {
        setShouldShowLoading(true);
      }
    }, 200);

    return () => clearTimeout(loadingTimeout);
  }, [isLoading]);

  useEffect(() => {
    if (isChecking.current || !serverId) return;
    isChecking.current = true;

    const checkAdminStatus = async () => {
      try {
        const response = await fetch(`/api/v1/guilds/${serverId}/is_admin`, {
          method: "POST",
          credentials: "include",
          cache: 'no-store'
        });

        const data = await response.json();

        if (!response.ok || !data.isAdmin) {
          setError(
            data.detail || "You don't have permission to access this page"
          );
          setIsAdmin(false);
        } else {
          setIsAdmin(true);
        }
      } catch (error) {
        setIsAdmin(false);
        setError(
          error instanceof Error ? error.message : "Failed to check permissions"
        );
      } finally {
        setIsLoading(false);
        isChecking.current = false;
      }
    };

    checkAdminStatus();
  }, [serverId]);

  const triggerShake = () => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 500);
  };

  const handleReset = async () => {
    setIsResetting(true);
    const currentPath = pathname.split("/").pop() || "";
    
    try {
      await axios.delete(`/api/v1/guilds/${serverId}/settings/${currentPath}`, {
        withCredentials: true,
      });
      setHasChanges(false);
      toast.success("Settings have been reset to defaults!");
      
      // Dispatch custom event for settings reset
      window.dispatchEvent(new CustomEvent('settingsReset'));
    } catch (error) {
      toast.error("Failed to reset settings");
    } finally {
      setIsResetting(false);
      setShowResetConfirm(false);
    }
  };

  const handleNavigationAttempt = useCallback(() => {
    if (hasChanges) {
      triggerShake();
      toast.error("Please save or revert your changes before navigating");
      return true;
    }
    return false;
  }, [hasChanges]);

  if (!isAdmin && !isLoading) {
    return (
      <AccessDenied
        error={
          new Error(error || "You don't have permission to access this page")
        }
        reset={() => window.location.reload()}
      />
    );
  }

  return (
    <LayoutProvider
      value={{
        hasChanges,
        setHasChanges,
        onSave: async () => {
          // Get current path to determine which settings to save
          const currentPath = pathname.split("/").pop() || "";
          
          try {
            await axios.post(`/api/v1/guilds/${serverId}/settings/${currentPath}`, {
              settings: {
                // This will be handled by each page's own save handler
              }
            });
            setHasChanges(false);
            toast.success("Settings saved successfully!");
          } catch (error) {
            console.error("Failed to save settings:", error);
            toast.error("Failed to save settings");
          }
        },
        onRevert: () => {
          if (hasChanges) {
            window.dispatchEvent(new CustomEvent('revertChanges'));
          }
        },
        onReset: handleReset,
      }}
    >
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
                    <Toaster
                      position="bottom-left"
                      toastOptions={{
                        style: {
                          zIndex: 100,
                          position: "relative",
                          background: "rgba(23, 23, 23, 0.9)",
                          color: "#fff",
                          backdropFilter: "blur(8px)",
                          border: "1px solid rgba(255, 255, 255, 0.1)",
                        },
                      }}
                    />
                    <AnimatePresence mode="wait">
                      <PageTransition key={pathname}>
                        <motion.div
                          animate={{
                            opacity: isLoading && shouldShowLoading ? 0.5 : 1,
                            scale: isLoading && shouldShowLoading ? 0.99 : 1,
                          }}
                          transition={{ duration: 0.2 }}
                        >
                          {isLoading && shouldShowLoading ? (
                            <div className="bg-white/10 backdrop-blur-lg rounded-lg p-8 flex flex-col items-center">
                              <div className="relative w-16 h-16">
                                <div className="absolute inset-0 rounded-full border-4 border-white/20 animate-[spin_3s_linear_infinite]"></div>
                                <div className="absolute inset-2 rounded-full border-4 border-t-white/80 border-white/20 animate-[spin_2s_linear_infinite]"></div>
                                <div className="absolute inset-[38%] rounded-full bg-white/80 animate-pulse"></div>
                              </div>
                              <p className="text-white text-base mt-4 font-medium animate-pulse">
                                Checking permissions...
                              </p>
                            </div>
                          ) : (
                            children
                          )}
                        </motion.div>
                      </PageTransition>
                    </AnimatePresence>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {/* Changes Bar */}
          {hasChanges && (
            <motion.div
              key="changes-bar"
              initial={{ opacity: 0, y: 20 }}
              animate={{
                opacity: 1,
                y: 0,
                backgroundColor: isShaking ? "rgba(239, 68, 68, 0.2)" : "rgba(0, 0, 0, 0.3)",
              }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.2 }}
              className={`fixed bottom-8 inset-x-0 mx-auto w-fit py-4 px-6 rounded-lg backdrop-blur-lg border border-white/10 shadow-2xl transition-colors duration-300 ${
                isShaking ? "animate-shake" : ""
              }`}
            >
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2 text-white/80">
                  <i className="fas fa-exclamation-circle text-yellow-500"></i>
                  <span className="font-medium">You have unsaved changes</span>
                </div>
                <div className="flex gap-3">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => window.dispatchEvent(new CustomEvent('saveChanges'))}
                    className="px-4 py-2 bg-emerald-600/80 hover:bg-emerald-600 text-white rounded-md transition-colors font-medium text-sm flex items-center gap-2"
                  >
                    <i className="fas fa-save"></i>
                    Save Changes
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => window.dispatchEvent(new CustomEvent('revertChanges'))}
                    className="px-4 py-2 bg-gray-700/80 hover:bg-gray-700 text-white rounded-md transition-colors font-medium text-sm flex items-center gap-2"
                  >
                    <i className="fas fa-undo"></i>
                    Revert
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Reset Button */}
          {showResetButton && (
            <motion.button
              key="reset-button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowResetConfirm(true)}
              className="fixed bottom-8 right-8 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-200 rounded-md transition-colors text-sm flex items-center gap-2 backdrop-blur-sm border border-red-500/20"
            >
              <i className="fas fa-history"></i>
              Reset All Settings
            </motion.button>
          )}

          {/* Reset Modal */}
          {showResetConfirm && (
            <motion.div
              key="reset-modal"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
              onClick={() => setShowResetConfirm(false)}
            >
              <motion.div
                initial={{ scale: 0.95 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0.95 }}
                className="bg-gray-900/90 p-6 rounded-lg border border-white/10 shadow-xl max-w-md mx-4"
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="text-xl font-semibold text-white mb-2">
                  Reset All Settings
                </h3>
                <p className="text-white/70 mb-6">
                  Are you sure you want to reset all settings to their
                  default values? This action cannot be undone.
                </p>
                <div className="flex justify-end gap-3">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setShowResetConfirm(false)}
                    className="px-4 py-2 bg-gray-700/80 hover:bg-gray-700 text-white rounded-md transition-colors"
                  >
                    Cancel
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleReset}
                    className="px-4 py-2 bg-red-500/80 hover:bg-red-500 text-white rounded-md transition-colors flex items-center gap-2"
                  >
                    <i className="fas fa-history"></i>
                    Reset All Settings
                  </motion.button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </LayoutProvider>
  );
}
