"use client";

import { ReactNode, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import ServerSidebar from "@/components/ServerSidebar";
import AccessDenied from "@/components/forbidden";
import { useLayout } from "@/providers/LayoutProvider";
import toast from "react-hot-toast";

interface LayoutProps {
  children: ReactNode;
  serverId: string;
}

export default function ServerLayoutClient({
  children,
  serverId,
}: LayoutProps) {
  const pathname = usePathname();
  const {
    hasChanges,
    isLoading,
    currentPath,
    setServerId,
    setCurrentPath,
    saveChanges,
    revertChanges,
    resetToDefaults,
  } = useLayout();

  const pagesWithoutReset = [
    "/dashboard/server/[id]/overview",
    "/dashboard/server/[id]/badges",
    "/dashboard/server/[id]/messages",
    "/dashboard/server/[id]/reaction-roles",
  ];

  const showResetButton = !pagesWithoutReset.some((path) =>
    pathname.replace(serverId, "[id]").startsWith(path)
  );

  useEffect(() => {
    if (serverId) {
      const newPath = pathname.split("/").pop() || "";
      if (serverId !== currentPath || newPath !== currentPath) {
        setServerId(serverId);
        setCurrentPath(newPath);
      }
    }
  }, [serverId, pathname, setServerId, setCurrentPath, currentPath]);

  const handleNavigationAttempt = () => {
    if (hasChanges) {
      toast.error("Please save or revert your changes before navigating");
      return true;
    }
    return false;
  };

  if (!serverId) {
    return (
      <AccessDenied
        error={new Error("Invalid server ID")}
        reset={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      <div className="flex-1 pt-16 relative">
        <div className="flex h-full">
          <div className="lg:w-72 flex-shrink-0">
            <ServerSidebar
              serverId={serverId}
              hasUnsavedChanges={hasChanges}
              onNavigationAttempt={handleNavigationAttempt}
            />
          </div>
          <main className="flex-1 relative">
            <div className="absolute inset-0 overflow-y-auto">
              <motion.div
                key={pathname}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="p-8"
              >
                <div className="max-w-5xl mx-auto">{children}</div>
              </motion.div>
            </div>
          </main>
        </div>
      </div>

      <AnimatePresence>
        {hasChanges && (
          <motion.div
            key="changes-bar"
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.95 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 25,
              duration: 0.5,
            }}
            className="fixed bottom-8 inset-x-0 mx-auto w-fit max-w-[90%] py-4 px-6 rounded-lg backdrop-blur-lg border border-white/10 shadow-2xl bg-black/30"
          >
            <motion.div
              className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6"
              initial={{ x: -20 }}
              animate={{ x: 0 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
            >
              <motion.div
                className="flex items-center gap-2 text-white/80"
                animate={{ scale: [1, 1.02, 1] }}
                transition={{ duration: 1, repeat: Infinity, repeatDelay: 5 }}
              >
                <i className="fas fa-exclamation-circle text-yellow-500"></i>
                <span className="font-medium">Unsaved changes</span>
              </motion.div>
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: isLoading ? 1 : 1.02 }}
                  whileTap={{ scale: isLoading ? 1 : 0.98 }}
                  onClick={async () => {
                    if (isLoading) return;
                    await saveChanges();
                    toast.success("Changes saved successfully!", {
                      icon: "💾",
                      style: {
                        background: "#1f2937",
                        color: "#d1fae5",
                        border: "1px solid #10b981",
                      },
                    });
                  }}
                  disabled={isLoading}
                  className={`px-4 py-2 rounded-md font-medium text-sm flex items-center gap-2 transition-all w-full sm:w-auto justify-center
      ${
        isLoading
          ? "bg-emerald-700/40 text-white/70 cursor-not-allowed"
          : "bg-emerald-600/80 hover:bg-emerald-600 text-white"
      }`}
                >
                  {isLoading ? (
                    <>
                      <motion.div
                        className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                        initial={{ rotate: 0 }}
                        animate={{ rotate: 360 }}
                        transition={{
                          repeat: Infinity,
                          ease: "linear",
                          duration: 1,
                        }}
                      />
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-save"></i>
                      Save Changes
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: isLoading ? 1 : 1.02 }}
                  whileTap={{ scale: isLoading ? 1 : 0.98 }}
                  onClick={revertChanges}
                  disabled={isLoading}
                  className={`px-4 py-2 rounded-md font-medium text-sm flex items-center gap-2 transition-all w-full sm:w-auto justify-center
      ${
        isLoading
          ? "bg-gray-700/40 text-white/70 cursor-not-allowed"
          : "bg-gray-700/80 hover:bg-gray-700 text-white"
      }`}
                >
                  <i className="fas fa-undo"></i>
                  Revert
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}

        {showResetButton && !isLoading && !hasChanges && (
          <motion.button
            key="reset-button"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={resetToDefaults}
            className="fixed bottom-8 right-8 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-200 rounded-md transition-colors text-sm flex items-center gap-2 backdrop-blur-sm border border-red-500/20"
          >
            <i className="fas fa-history"></i>
            Reset All Settings
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
