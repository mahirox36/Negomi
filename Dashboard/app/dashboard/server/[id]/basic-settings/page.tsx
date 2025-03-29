"use client";

import { useParams } from "next/navigation";
import LoadingScreen from "@/app/components/LoadingScreen";
import AccessDenied from "@/app/components/forbidden";
import { useEffect, useState } from "react";
import { useColorPickerRefs } from "@/hooks/useColorPickerRefs";
import ColorPicker from "@/app/components/ColorPicker";
import { Toaster } from "react-hot-toast";
import toast from "react-hot-toast";
import axios from "axios";
import SettingsLayout from "../../../../components/ServerLayout";

type Setting = {
  name: string;
  type: "color" | "toggle" | "select" | "number" | "text";
  value: any;
  description?: string;
  options?: Array<{ label: string; value: string }>;
  min?: number;
  max?: number;
  step?: number;
};

type LayoutItem = {
  type: "header" | "panel";
  text: string;
  subtext?: string;
  icon?: string;
  settings?: Setting[];
};

export default function BasicSettings() {
  const params = useParams();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pageLayout, setPageLayout] = useState<LayoutItem[]>([]);
  const [currentValues, setCurrentValues] = useState<any>(null);
  const [originalValues, setOriginalValues] = useState<any>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [colorPickerOpen, setColorPickerOpen] = useState<string | null>(null);
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

    const fetchPageLayout = async () => {
      try {
        const response = await fetch(`/api/v1/layout/settings/server/basic-settings`);
        const layoutData = await response.json();
        setPageLayout(Array.isArray(layoutData) ? layoutData : layoutData.layout || []);

        const settingsResponse = await axios.get(
          `/api/v1/guilds/${params.id}/settings/basic-settings`,
          { withCredentials: true }
        );

        if (settingsResponse.data?.settings) {
          setCurrentValues(settingsResponse.data.settings);
          setOriginalValues(settingsResponse.data.settings);
        }
      } catch (error) {
        console.error("Failed to fetch layout or settings:", error);
        setPageLayout([]);
      }
    };

    checkAdminStatus();
    fetchPageLayout();
  }, [params.id]);

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
      await axios.post(`/api/v1/guilds/${params.id}/settings/basic-settings`, {
        settings: currentValues,
        withCredentials: true,
      });
      setOriginalValues(currentValues);
      setHasChanges(false);
      toast.success("Changes saved successfully!");
    } catch (error) {
      toast.error("Failed to save changes");
    }
  };

  const handleRevert = () => {
    setCurrentValues(originalValues);
    setHasChanges(false);
  };

  const handleReset = async () => {
    try {
      await axios.delete(`/api/v1/guilds/${params.id}/settings/basic-settings`, {
        withCredentials: true,
      });

      const newDefaults = pageLayout.reduce((acc: any, section) => {
        if (section.type === "panel" && section.settings) {
          section.settings.forEach((setting) => {
            acc[setting.name] = setting.value;
          });
        }
        return acc;
      }, {});

      setCurrentValues(newDefaults);
      setOriginalValues(newDefaults);
      setHasChanges(false);
    } catch (error) {
      throw error;
    }
  };

  const renderSettingInput = (setting: Setting) => {
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
            {setting.options?.map((option) => (
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

  if (isAdmin === null) {
    return <LoadingScreen message="Checking Permissions" />;
  }

  if (!isAdmin) {
    return (
      <AccessDenied
        error={new Error(error || "You don't have permission to access this page")}
        reset={() => window.location.reload()}
      />
    );
  }

  return (
    <SettingsLayout
      serverId={params.id as string}
      hasChanges={hasChanges}
      onSave={handleSave}
      onRevert={handleRevert}
      onReset={handleReset}
    >
      <div className="space-y-6">
        {pageLayout?.map((item, index) => {
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
                  </div>
                  <div className="space-y-3">
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
                  </div>
                </div>
              );
            default:
              return null;
          }
        })}
      </div>
    </SettingsLayout>
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