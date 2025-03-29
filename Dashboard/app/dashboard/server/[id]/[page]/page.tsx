"use client";


import { useEffect, useState, useRef, useMemo } from "react";
import { useParams } from "next/navigation";
import { Toaster } from "react-hot-toast";
import { AnimatePresence, motion } from "framer-motion";
import toast from "react-hot-toast";
import ServerLayout from "@/app/components/ServerLayout";
import { useLayout } from "@/providers/LayoutProvider";
import { LayoutItem } from "@/types/layout";
import axios from "axios";
import AccessDenied from "@/app/components/forbidden";
import { useRouter } from "next/navigation";
import ColorPicker from "@/app/components/ColorPicker";
import { useColorPickerRefs } from "@/hooks/useColorPickerRefs";
import LoadingScreen from "@/app/components/LoadingScreen";

export default function ServerPage() {
  const params = useParams();
  const { pageLayout, fetchPageLayout } = useLayout();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [originalValues, setOriginalValues] = useState<any>(null);
  const [currentValues, setCurrentValues] = useState<any>(null);
  const [shake, setShake] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [colorPickerOpen, setColorPickerOpen] = useState<string | null>(null);
  const [isDraggingColor, setIsDraggingColor] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [resettingPanel, setResettingPanel] = useState<number | null>(null);
  const router = useRouter();

  const { getRef } = useColorPickerRefs();

  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await fetch(`/api/v1/guilds/${params.id}/is_admin`, {
          method: "POST",
          credentials: "include",
        });

        const data = await response.json();
        setIsAdmin(data.isAdmin);
        
        if (!response.ok || !data.isAdmin) {
          setError(data.detail || "You don't have permission to access this page");
          setIsAdmin(false);
        }
      } catch (error) {
        console.error("Admin check error:", error);
        setIsAdmin(false);
        setError(error instanceof Error ? error.message : "Failed to check permissions");
      }
    };

    const loadSavedValues = async () => {
      try {
        const response = await axios.get(
          `/api/v1/guilds/${params.id}/settings/${params.page}`, {withCredentials: true}
        );
        if (response.data && response.data.settings) {
          const savedValues = response.data.settings;
          console.log("Loaded values:", savedValues);
          setOriginalValues(savedValues);
          setCurrentValues({ ...savedValues });
        }
      } catch (error) {
        console.error("Failed to load saved values:", error);
        toast.error("Failed to load settings");
      }
    };

    checkAdminStatus();
    loadSavedValues();
    fetchPageLayout(params.page as string);
  }, [fetchPageLayout, params.id, params.page]);

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasChanges) {
        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasChanges]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // Only handle click-outside if we're not dragging and the picker is open
      if (colorPickerOpen && !isDraggingColor) {
        const target = event.target as Element;
        const isColorPicker = target.closest(".react-colorful");
        const isColorPickerTrigger = target.closest(".color-picker-trigger");

        // Don't close if clicking inside color picker or the trigger button
        if (!isColorPicker && !isColorPickerTrigger) {
          setColorPickerOpen(null);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [colorPickerOpen, isDraggingColor]);

  const handleValueChange = (settingId: string, value: any) => {
    setCurrentValues((prev: any) => {
      const newValues = { ...prev, [settingId]: value };
      const changed = !isEqual(newValues, originalValues);
      setHasChanges(changed);
      return newValues;
    });
  };

  const handleSave = async () => {
    try {
      await axios.post(`/api/v1/guilds/${params.id}/settings/${params.page}`, {
        settings: currentValues,
        withCredentials: true
      });
      setOriginalValues(currentValues);
      setHasChanges(false);
      toast.success("Changes saved successfully!", {
        style: {
          background: "rgba(34, 197, 94, 0.9)",
          color: "#fff",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        },
        duration: 3000,
      });
    } catch (error) {
      toast.error("Failed to save changes", {
        style: {
          background: "rgba(239, 68, 68, 0.9)",
          color: "#fff",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        },
      });
    }
  };

  const handleRevert = () => {
    setCurrentValues(originalValues);
    setHasChanges(false);
  };

  const handleNavigation = (href: string) => {
    if (hasChanges) {
      setShake(true);
      setTimeout(() => setShake(false), 500);
      toast.error("Please save or revert your changes before navigating");
      return;
    }
    router.push(`/dashboard/server/${params.id}/${href}`);
  };

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  const triggerWarningAnimation = () => {
    setShowWarning(true);
    setTimeout(() => setShowWarning(false), 1500);
  };

  const handleReset = async () => {
    try {
      setResettingPanel(0); // Use this for the animation effect
      await axios.delete(`/api/v1/guilds/${params.id}/settings/${params.page}`, {withCredentials: true});

      // Reset all values to defaults
      const newValues: Record<string, any> = {};
      pageLayout?.forEach((section) => {
        if (section.type === "panel" && section.settings) {
          section.settings.forEach((setting) => {
            newValues[setting.name] = setting.value;
          });
        }
      });

      setCurrentValues(newValues);
      setOriginalValues(newValues);
      setHasChanges(false);

      toast.success("All settings have been reset to defaults!", {
        style: {
          background: "rgba(34, 197, 94, 0.9)",
          color: "#fff",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        },
      });
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 403) {
        router.push(`/dashboard/server/${params.id}`);
        return;
      }
      toast.error("Failed to reset settings");
    } finally {
      setResettingPanel(null);
      setShowResetConfirm(false);
    }
  };

  const renderLayoutItem = (item: LayoutItem, index: number) => {
    switch (item.type) {
      case "header":
        return (
          <div
            key={index}
            className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
          >
            <div className="flex items-center gap-4">
              {item.icon && (
                <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-white/20 to-white/10 rounded-xl shadow-inner">
                  <i className={`${item.icon} text-2xl text-white/90`}></i>
                </div>
              )}
              <div>
                <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                  {item.text}
                </h1>
                <p className="text-lg text-white/70 mt-1">{item.subtext}</p>
              </div>
            </div>
          </div>
        );

      case "cards":
        return (
          <div
            key={index}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
          >
            {item.buttons?.map((button, buttonIndex) => (
              <div
                key={buttonIndex}
                onClick={() => handleNavigation(button.link)}
                className="group relative overflow-hidden p-6 bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="flex items-center gap-3 mb-4">
                    {button.icon && (
                      <div className="w-10 h-10 flex items-center justify-center bg-white/10 rounded-lg group-hover:scale-110 transition-transform duration-300">
                        <i className={`${button.icon} text-white/90`}></i>
                      </div>
                    )}
                    <h3 className="text-xl text-white font-semibold">
                      {button.text}
                    </h3>
                  </div>
                  <p className="text-white/70 text-sm mb-4">{button.subtext}</p>
                  {button.buttonText && (
                    <span className="inline-flex items-center px-4 py-2 bg-white/10 rounded-lg text-sm text-white group-hover:bg-white/20 transition-colors">
                      {button.buttonText}
                      <i className="fas fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        );

      case "panel":
        return (
          <div
            key={index}
            className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 mb-6 border border-white/10"
          >
            <div className="flex items-center justify-between gap-4 mb-4">
              <div className="flex items-center gap-4">
                {item.icon && (
                  <div className="w-10 h-10 flex items-center justify-center bg-white/10 rounded-lg">
                    <i className={`${item.icon} text-xl text-white/90`}></i>
                  </div>
                )}
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    {item.text}
                  </h2>
                  <p className="text-sm text-white/70 mt-1">{item.subtext}</p>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowResetConfirm(true)}
                className="px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-200 rounded-md transition-colors text-sm flex items-center gap-2"
              >
                <i className="fas fa-history"></i>
                Reset
              </motion.button>
            </div>
            <motion.div
              className="space-y-3"
              animate={{
                opacity: resettingPanel !== null ? 0.5 : 1,
                scale: resettingPanel !== null ? 0.99 : 1,
              }}
              transition={{ duration: 0.2 }}
            >
              {item.settings?.map((setting, settingIndex) => (
                <div
                  key={settingIndex}
                  className="flex items-start justify-between group relative p-3 rounded-lg hover:bg-white/5 transition-colors"
                >
                  <div className="flex flex-col flex-grow mr-4">
                    <span className="text-white font-medium">
                      {setting.name}
                    </span>
                    {setting.description && (
                      <span className="text-sm text-white/50 mt-1">
                        {setting.description}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    {renderSettingInput(setting)}
                  </div>
                </div>
              ))}
            </motion.div>
            <AnimatePresence>
              {showResetConfirm && (
                <motion.div
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
                      Reset Settings
                    </h3>
                    <p className="text-white/70 mb-6">
                      Are you sure you want to reset all settings in this
                      section to their default values? This action cannot be
                      undone.
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
                        Reset Settings
                      </motion.button>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );

      default:
        return null;
    }
  };

  const renderSettingInput = (setting: any) => {
    switch (setting.type) {
      case "color": {
        const triggerRef = getRef(setting.name);
        return (
          <div className="flex items-center gap-3 relative">
            <div
              ref={triggerRef}
              className="w-10 h-10 rounded-lg border-2 border-white/20 cursor-pointer relative overflow-hidden group"
              onClick={() =>
                setColorPickerOpen((prev) =>
                  prev === setting.name ? null : setting.name
                )
              }
              style={{
                backgroundColor: currentValues?.[setting.name] || setting.value,
              }}
            >
              <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <i className="fas fa-eye-dropper text-white/90"></i>
              </div>
            </div>
            <input
              type="text"
              value={currentValues?.[setting.name] || setting.value}
              className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white w-32 focus:outline-none focus:border-white/40 transition-colors"
              onChange={(e) => handleValueChange(setting.name, e.target.value)}
              placeholder="#FFFFFF"
            />
            <ColorPicker
              color={currentValues?.[setting.name] || setting.value}
              onChange={(color) => handleValueChange(setting.name, color)}
              onClose={() => setColorPickerOpen(null)}
              isOpen={colorPickerOpen === setting.name}
              triggerRef={triggerRef}
            />
          </div>
        );
      }
      case "toggle":
        return (
          <div
            onClick={() =>
              handleValueChange(setting.name, !currentValues?.[setting.name])
            }
            className={`w-14 h-8 rounded-full transition-colors duration-200 cursor-pointer relative ${
              currentValues?.[setting.name] ? "bg-emerald-500" : "bg-white/20"
            }`}
          >
            <div
              className={`absolute w-6 h-6 rounded-full bg-white top-1 transition-transform duration-200 ${
                currentValues?.[setting.name]
                  ? "translate-x-7"
                  : "translate-x-1"
              }`}
            />
          </div>
        );

      case "select":
        return (
          <select
            value={currentValues?.[setting.name] || setting.value}
            onChange={(e) => handleValueChange(setting.name, e.target.value)}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-white/40 transition-colors"
          >
            {setting.options?.map((option: any) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case "number":
        return (
          <input
            type="number"
            value={currentValues?.[setting.name] || setting.value}
            onChange={(e) =>
              handleValueChange(setting.name, parseFloat(e.target.value))
            }
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white w-32 focus:outline-none focus:border-white/40 transition-colors"
            min={setting.min}
            max={setting.max}
            step={setting.step || 1}
          />
        );

      default:
        return (
          <input
            type="text"
            value={currentValues?.[setting.name] || setting.value}
            onChange={(e) => handleValueChange(setting.name, e.target.value)}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white w-full focus:outline-none focus:border-white/40 transition-colors"
          />
        );
    }
  };

  // Early return for loading state
  if (isAdmin === null) {
    return <LoadingScreen message="Checking Permissions" />;
  }

  // Early return for access denied - remove the ServerLayout wrapper
  if (!isAdmin) {
    return (
      <AccessDenied 
        error={new Error(error || "You don't have permission to access this page")}
        reset={() => window.location.reload()}
      />
    );
  }

  return (
    <ServerLayout
      serverId={params.id as string}
      sidebarProps={{
        hasUnsavedChanges: hasChanges,
        onNavigationAttempt: triggerWarningAnimation,
      }}
    >
      <Toaster
        position="top-center"
        toastOptions={{
          className:
            "bg-gray-800/80 text-white backdrop-blur-lg border border-white/10",
          duration: 3000,
        }}
      />

      <div className={`space-y-6 ${shake ? "animate-shake" : ""}`}>
        {pageLayout?.map((item, index) => renderLayoutItem(item, index)) || []}
      </div>

      {/* Add reset all settings button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setShowResetConfirm(true)}
        className="fixed bottom-8 right-8 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-200 rounded-md transition-colors text-sm flex items-center gap-2 backdrop-blur-sm border border-red-500/20"
      >
        <i className="fas fa-history"></i>
        Reset All Settings
      </motion.button>

      <AnimatePresence>
        {showResetConfirm && (
          <motion.div
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
                Are you sure you want to reset all settings on this page to
                their default values? This action cannot be undone.
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
        {hasChanges && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{
              opacity: 1,
              y: 0,
              backgroundColor: showWarning
                ? "rgba(239, 68, 68, 0.9)"
                : "rgba(17, 24, 39, 0.9)",
            }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.2 }}
            className={`fixed bottom-8 inset-x-0 mx-auto w-fit py-4 px-6 rounded-lg backdrop-blur-lg border border-white/10 shadow-2xl transition-all duration-300 ${
              showWarning ? "animate-warning-shake" : ""
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
                  onClick={handleSave}
                  className="px-4 py-2 bg-emerald-600/80 hover:bg-emerald-600 text-white rounded-md transition-colors font-medium text-sm flex items-center gap-2"
                >
                  <i className="fas fa-save"></i>
                  Save Changes
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleRevert}
                  className="px-4 py-2 bg-gray-700/80 hover:bg-gray-700 text-white rounded-md transition-colors font-medium text-sm flex items-center gap-2"
                >
                  <i className="fas fa-undo"></i>
                  Revert
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </ServerLayout>
  );
}
function isEqual(newValues: any, originalValues: any) {
  if (newValues === originalValues) return true;
  if (!newValues || !originalValues) return false;
  if (typeof newValues !== typeof originalValues) return false;

  const keys1 = Object.keys(newValues);
  const keys2 = Object.keys(originalValues);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (newValues[key] !== originalValues[key]) {
      return false;
    }
  }

  return true;
}
