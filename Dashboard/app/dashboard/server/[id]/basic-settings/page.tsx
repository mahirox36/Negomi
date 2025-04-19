"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import { useColorPickerRefs } from "@/hooks/useColorPickerRefs";
import ColorPicker from "@/app/components/ColorPicker";
import ToggleSwitch from "@/app/components/form/ToggleSwitch";
import DiscordSelect from "@/app/components/form/DiscordSelect";
import TextInput from "@/app/components/form/TextInput";
import Textarea from "@/app/components/form/Textarea";
import toast from "react-hot-toast";
import axios from "axios";
import { useLayout } from "@/providers/LayoutProvider";

type Setting = {
  name: string;
  type: "color" | "toggle" | "select" | "number" | "text";
  value: any;
  description?: string;
  options?: Array<{ label: string; value: string }>;
  min?: number;
  max?: number;
  step?: number;
  multiline?: boolean;
  placeholder?: string;
  icon?: string;
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
  const serverId = params.id;
  const { setHasChanges, isLoading: layoutLoading, pageLayout, fetchPageLayout } = useLayout();
  const [currentValues, setCurrentValues] = useState<any>(null);
  const [originalValues, setOriginalValues] = useState<any>(null);
  const [colorPickerOpen, setColorPickerOpen] = useState<string | null>(null);
  const { getRef } = useColorPickerRefs();
  const [isLoading, setIsLoading] = useState(false);
  const hasInitialFetch = useRef(false);

  const fetchSettings = useCallback(async () => {
    if (!serverId || hasInitialFetch.current) return;
    
    setIsLoading(true);
    try {
      const settingsRes = await axios.get(`/api/v1/guilds/${serverId}/settings/basic-settings`, {
        withCredentials: true,
      });

      if (settingsRes.data?.settings) {
        setCurrentValues(settingsRes.data.settings);
        setOriginalValues(settingsRes.data.settings);
        setHasChanges(false);
      }
      hasInitialFetch.current = true;
    } catch (error) {
      console.error("Failed to fetch settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  }, [serverId, setHasChanges]);

  useEffect(() => {
    const handleSettingsReset = () => {
      hasInitialFetch.current = false;
      fetchSettings();
    };

    window.addEventListener('settingsReset', handleSettingsReset);
    return () => {
      window.removeEventListener('settingsReset', handleSettingsReset);
    };
  }, [fetchSettings]);

  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;

    const loadData = async () => {
      try {
        await Promise.all([
          fetchPageLayout('basic-settings'),
          fetchSettings()
        ]);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        toast.error('Failed to load settings');
      }
    };

    loadData();

    // Cleanup on unmount
    return () => {
      hasInitialFetch.current = false;
    };
  }, [serverId, fetchSettings, fetchPageLayout]);

  const handleValueChange = useCallback((settingId: string, value: any) => {
    const newValues = { ...currentValues, [settingId]: value };
    const changed = !isEqual(newValues, originalValues);
    setCurrentValues(newValues);
    setHasChanges(changed);
  }, [currentValues, originalValues, setHasChanges]);

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
          <ToggleSwitch
            enabled={currentValues?.[setting.name] || false}
            onChange={(value) => handleValueChange(setting.name, value)}
            size="md"
          />
        );

      case "select":
        if (setting.name.toLowerCase().includes('channel')) {
          return (
            <DiscordSelect
              type="channel"
              guildId={serverId as string}
              value={currentValues?.[setting.name] || ''}
              onChange={(value) => handleValueChange(setting.name, value)}
              placeholder="Select channel..."
            />
          );
        }
        if (setting.name.toLowerCase().includes('role')) {
          return (
            <DiscordSelect
              type="role"
              guildId={serverId as string}
              value={currentValues?.[setting.name] || ''}
              onChange={(value) => handleValueChange(setting.name, value)}
              placeholder="Select role..."
            />
          );
        }
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

      case "text":
        if (setting.multiline) {
          return (
            <Textarea
              value={currentValues?.[setting.name] || setting.value}
              onChange={(e) => handleValueChange(setting.name, e.target.value)}
              placeholder={setting.placeholder}
            />
          );
        }
        return (
          <TextInput
            value={currentValues?.[setting.name] || setting.value}
            onChange={(e) => handleValueChange(setting.name, e.target.value)}
            placeholder={setting.placeholder}
            icon={setting.icon}
            variant="glass"
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

  if (isLoading || layoutLoading) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-8 flex flex-col items-center">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-white/20 animate-[spin_3s_linear_infinite]"></div>
          <div className="absolute inset-2 rounded-full border-4 border-t-white/80 border-white/20 animate-[spin_2s_linear_infinite]"></div>
          <div className="absolute inset-[38%] rounded-full bg-white/80 animate-pulse"></div>
        </div>
        <p className="text-white text-base mt-4 font-medium animate-pulse">
          Loading...
        </p>
      </div>
    );
  }

  return (
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
                        {renderSettingInput(setting as Setting)}
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
