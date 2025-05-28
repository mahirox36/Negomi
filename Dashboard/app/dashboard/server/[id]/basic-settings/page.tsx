"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import { useLayout } from "@/providers/LayoutProvider";
import { useColorPickerRefs } from "@/hooks/useColorPickerRefs";
import ColorPicker from "@/components/form/ColorPicker";
import DiscordSelect from "@/components/form/DiscordSelect";
import TextInput from "@/components/form/TextInput";
import Textarea from "@/components/form/Textarea";
import SettingsSection from "@/components/dashboard/SettingsSection";
import { ToggleSwitch } from "@/components/form/ToggleSwitch";
import axios from "axios";
import toast from "react-hot-toast";

interface BasicSettings {
  [key: string]: any;
}

export default function BasicSettings() {
  const params = useParams();
  const serverId = Array.isArray(params.id) ? params.id[0] : params.id;
  const { setHasChanges, setCurrentPath, setServerId } = useLayout();
  const [settings, setSettings] = useState<BasicSettings>({});
  const [originalSettings, setOriginalSettings] = useState<BasicSettings>({});
  const [isLoading, setIsLoading] = useState(true);
  const [colorPickerOpen, setColorPickerOpen] = useState<string | null>(null);
  const { getRef } = useColorPickerRefs();
  const hasInitialFetch = useRef(false);

  // Fetch settings from API
  const fetchSettings = useCallback(async () => {
    if (!serverId) return;

    try {
      const response = await axios.get(
        `/api/v1/guilds/${serverId}/settings/basic-settings`,
        {
          withCredentials: true,
        }
      );

      const settingsData = response.data?.settings || response.data || {};
      setSettings(settingsData);
      setOriginalSettings(settingsData);
      setHasChanges(false);
      hasInitialFetch.current = true;
    } catch (error) {
      console.error("Failed to fetch settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  }, [serverId, setHasChanges]);

  // Initialize data
  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;

    setCurrentPath("basic-settings");
    setServerId(serverId as string);
    fetchSettings();

    return () => {
      hasInitialFetch.current = false;
    };
  }, [serverId, fetchSettings, setCurrentPath, setServerId]);

  // Layout Provider event handlers
  useEffect(() => {
    const handleGetUnsavedSettings = (event: CustomEvent) => {
      if (event.detail && event.detail.callback) {
        event.detail.callback(settings);
      }
      setOriginalSettings(settings);
    };

    const handleRevertChanges = () => {
      setSettings({ ...originalSettings });
    };

    const handleSettingsReset = () => {
      hasInitialFetch.current = false;
      fetchSettings();
    };

    window.addEventListener(
      "getUnsavedSettings",
      handleGetUnsavedSettings as EventListener
    );
    window.addEventListener("revertChanges", handleRevertChanges);
    window.addEventListener("settingsReset", handleSettingsReset);

    return () => {
      window.removeEventListener(
        "getUnsavedSettings",
        handleGetUnsavedSettings as EventListener
      );
      window.removeEventListener("revertChanges", handleRevertChanges);
      window.removeEventListener("settingsReset", handleSettingsReset);
    };
  }, [settings, originalSettings, fetchSettings]);

  const handleSettingChange = (key: string, value: any) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    setHasChanges(
      JSON.stringify(newSettings) !== JSON.stringify(originalSettings)
    );
  };

  if (isLoading) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-500/20 to-fuchsia-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 opacity-10 -rotate-6">
          <i className="fas fa-cog text-[180px] text-white"></i>
        </div>
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-500/40 to-fuchsia-500/40 rounded-xl shadow-inner border border-white/10">
            <i className="fas fa-cog text-3xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
              Basic Settings
            </h1>
            <p className="text-lg text-white/70 mt-1 max-w-2xl">
              Configure basic server settings and preferences
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10">
        <div className="p-6 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
            {/* Data Deletion Preference */}
            <SettingsSection
              title="Data Deletion Preference"
              description="Choose whether to delete data instantly when the bot leaves the server or wait 3 days"
              icon="fa-trash-alt"
              iconBgColor="bg-red-500/20"
              iconColor="text-red-300"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-white">
                    Delete Data Instantly
                  </h3>
                  <p className="text-xs text-white/50">
                    Enable to delete data immediately when the bot leaves the
                    server. Default: Wait 3 days.
                  </p>
                </div>
                <ToggleSwitch
                  checked={settings.deleteDataInstantly || false}
                  onChange={(value) =>
                    handleSettingChange("deleteDataInstantly", value)
                  }
                />
              </div>
            </SettingsSection>

            {/* Badge Colors */}
            <SettingsSection
              title="Badge Rarity Colors"
              description="Set colors for different badge rarity levels"
              icon="fa-gem"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-300"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-white">
                      Common Badge Color
                    </h3>
                    <p className="text-xs text-white/50">
                      Color for common rarity badges
                    </p>
                  </div>
                  <ColorPicker
                    color={settings.commonColor || "#ff1493"}
                    onChange={(color) =>
                      handleSettingChange("commonColor", color)
                    }
                    ref={getRef("commonColor")}
                    isOpen={colorPickerOpen === "commonColor"}
                    onToggle={() =>
                      setColorPickerOpen(
                        colorPickerOpen === "commonColor" ? null : "commonColor"
                      )
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-white">
                      Uncommon Badge Color
                    </h3>
                    <p className="text-xs text-white/50">
                      Color for uncommon rarity badges
                    </p>
                  </div>
                  <ColorPicker
                    color={settings.uncommonColor || "#00ffb9"}
                    onChange={(color) =>
                      handleSettingChange("uncommonColor", color)
                    }
                    ref={getRef("uncommonColor")}
                    isOpen={colorPickerOpen === "uncommonColor"}
                    onToggle={() =>
                      setColorPickerOpen(
                        colorPickerOpen === "uncommonColor"
                          ? null
                          : "uncommonColor"
                      )
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-white">
                      Rare Badge Color
                    </h3>
                    <p className="text-xs text-white/50">
                      Color for rare rarity badges
                    </p>
                  </div>
                  <ColorPicker
                    color={settings.rareColor || "#ff4500"}
                    onChange={(color) =>
                      handleSettingChange("rareColor", color)
                    }
                    ref={getRef("rareColor")}
                    isOpen={colorPickerOpen === "rareColor"}
                    onToggle={() =>
                      setColorPickerOpen(
                        colorPickerOpen === "rareColor" ? null : "rareColor"
                      )
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-white">
                      Epic Badge Color
                    </h3>
                    <p className="text-xs text-white/50">
                      Color for epic rarity badges
                    </p>
                  </div>
                  <ColorPicker
                    color={settings.epicColor || "#32cd32"}
                    onChange={(color) =>
                      handleSettingChange("epicColor", color)
                    }
                    ref={getRef("epicColor")}
                    isOpen={colorPickerOpen === "epicColor"}
                    onToggle={() =>
                      setColorPickerOpen(
                        colorPickerOpen === "epicColor" ? null : "epicColor"
                      )
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-white">
                      Legendary Badge Color
                    </h3>
                    <p className="text-xs text-white/50">
                      Color for legendary rarity badges
                    </p>
                  </div>
                  <ColorPicker
                    color={settings.legendaryColor || "#9400d3"}
                    onChange={(color) =>
                      handleSettingChange("legendaryColor", color)
                    }
                    ref={getRef("legendaryColor")}
                    isOpen={colorPickerOpen === "legendaryColor"}
                    onToggle={() =>
                      setColorPickerOpen(
                        colorPickerOpen === "legendaryColor"
                          ? null
                          : "legendaryColor"
                      )
                    }
                  />
                </div>
              </div>
            </SettingsSection>
          </div>
        </div>
      </div>
    </div>
  );
}
