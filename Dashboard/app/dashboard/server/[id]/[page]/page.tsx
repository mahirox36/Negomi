"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import LoadingScreen from "@/app/components/LoadingScreen";
import { Toaster } from "react-hot-toast";
import { AnimatePresence, motion } from "framer-motion";
import toast from "react-hot-toast";
import ServerLayout from "@/app/components/ServerLayout";
import { useLayout } from "@/providers/LayoutProvider";
import { LayoutItem } from "@/types/layout";
import Link from "next/link";
import axios from "axios";
import AccessDenied from "@/app/components/forbidden";
import { useRouter } from "next/navigation";

export default function ServerPage() {
  const params = useParams();
  const { pageLayout, fetchPageLayout } = useLayout();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [originalValues, setOriginalValues] = useState<any>(null);
  const [currentValues, setCurrentValues] = useState<any>(null);
  const [shake, setShake] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await fetch(`/api/guilds/${params.id}/is_admin`, {
          method: 'POST',
          credentials: 'include',
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to check admin status');
        }
        
        setIsAdmin(data.isAdmin);
      } catch (error) {
        console.error("Admin check error:", error);
        setIsAdmin(false);
        setError(error instanceof Error ? error.message : 'Failed to check permissions');
      }
    };

    const loadSavedValues = async () => {
      try {
        const response = await axios.get(`/api/guilds/${params.id}/settings/${params.page}`);
        if (response.data && response.data.settings) {
          const savedValues = response.data.settings;
          console.log("Loaded values:", savedValues);
          setOriginalValues(savedValues);
          setCurrentValues({...savedValues});
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
      await axios.post(`/api/guilds/${params.id}/settings/${params.page}`, {
        settings: currentValues
      });
      setOriginalValues(currentValues);
      setHasChanges(false);
      toast.success("Changes saved successfully!", {
        style: {
          background: 'rgba(34, 197, 94, 0.9)',
          color: '#fff',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        duration: 3000,
      });
    } catch (error) {
      toast.error("Failed to save changes", {
        style: {
          background: 'rgba(239, 68, 68, 0.9)',
          color: '#fff',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
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

  if (isAdmin === null) {
    return <LoadingScreen message="Checking Permissions" />;
  }

  if (!isAdmin) {
    return (
      <AccessDenied 
        error={new Error(error || "You do not have permission to view this page.")} 
        reset={() => window.location.reload()} 
      />
    );
  }

  if (!pageLayout) {
    return <LoadingScreen message="Loading Page" />;
  }

  const renderLayoutItem = (item: LayoutItem, index: number) => {
    switch (item.type) {
      case "header":
        return (
          <div key={index} className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              {item.icon && (
                <div className="w-10 h-10 flex items-center justify-center bg-white/10 rounded-lg">
                  <i className={`${item.icon} text-2xl text-white`}></i>
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold text-white">{item.text}</h1>
                <p className="text-white/70">{item.subtext}</p>
              </div>
            </div>
          </div>
        );
      case "cards":
        return (
          <div key={index} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {item.buttons?.map((button, buttonIndex) => (
              <div
                key={buttonIndex}
                onClick={() => handleNavigation(button.link)}
                className="block p-6 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3 mb-3">
                  {button.icon && (
                    <div className="w-8 h-8 flex items-center justify-center bg-white/10 rounded-lg">
                      <i className={`${button.icon} text-white`}></i>
                    </div>
                  )}
                  <h3 className="text-white font-semibold">{button.text}</h3>
                </div>
                <p className="text-white/60 text-sm mb-4">{button.subtext}</p>
                {button.buttonText && (
                  <span className="inline-block px-4 py-2 bg-white/10 rounded-md text-sm text-white hover:bg-white/20 transition-colors">
                    {button.buttonText}
                  </span>
                )}
              </div>
            ))}
          </div>
        );
      case "panel":
        return (
          <div key={index} className="bg-white/5 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3 mb-4">
              {item.icon && (
                <div className="w-8 h-8 flex items-center justify-center bg-white/10 rounded-lg">
                  <i className={`${item.icon} text-white`}></i>
                </div>
              )}
              <div>
                <h2 className="text-lg font-semibold text-white">{item.text}</h2>
                <p className="text-sm text-white/70">{item.subtext}</p>
              </div>
            </div>
            <div className="space-y-4">
              {item.settings?.map((setting, settingIndex) => (
                <div key={settingIndex} className="flex items-center justify-between group relative">
                  <div className="flex flex-col">
                    <span className="text-white">{setting.name}</span>
                    {setting.description && (
                      <span className="text-xs text-white/50">{setting.description}</span>
                    )}
                  </div>
                  {setting.type === "color" && (
                    <div className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded border border-white/20"
                        style={{ backgroundColor: currentValues?.[setting.name] || setting.value }}
                      />
                      <input
                        type="text"
                        value={currentValues?.[setting.name] || setting.value}
                        className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white w-24"
                        onChange={(e) => handleValueChange(setting.name, e.target.value)}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <ServerLayout serverId={params.id as string}>
      <Toaster 
        position="top-center"
        toastOptions={{
          className: 'bg-gray-800/80 text-white backdrop-blur-lg border border-white/10',
          duration: 3000,
        }}
      />
      
      <div className={`space-y-6 ${shake ? 'animate-shake' : ''}`}>
        {pageLayout.map((item, index) => renderLayoutItem(item, index))}
      </div>

      <AnimatePresence>
        {hasChanges && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-8 inset-x-0 mx-auto w-fit py-4 px-6 rounded-lg bg-gray-900/90 backdrop-blur-lg border border-white/10 shadow-2xl"
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

// Add these styles to your global CSS
const styles = `
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.animate-shake {
  animation: shake 0.2s ease-in-out 0s 2;
}
`;
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

