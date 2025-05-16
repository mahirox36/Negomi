"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import { useLayout } from "@/providers/LayoutProvider";
import DiscordSelect from "@/components/form/DiscordSelect";
import {ToggleSwitch} from "@/components/form/ToggleSwitch";
import SettingsSection from "@/components/dashboard/SettingsSection";
import axios from "axios";
import toast from "react-hot-toast";

interface AISettings {
  allow_threads: boolean;
  allowed_roles: string[];
  cooldown_seconds: number;
  public_channels: string[];
}

const defaultSettings: AISettings = {
  allow_threads: true,
  allowed_roles: [],
  cooldown_seconds: 5,
  public_channels: []
};

export default function AISettings() {
  const params = useParams();
  const serverId = params.id as string;
  const { setHasChanges, setCurrentPath, setServerId } = useLayout();

  const [settings, setSettings] = useState<AISettings>({ ...defaultSettings });
  const [originalSettings, setOriginalSettings] = useState<AISettings>({ ...defaultSettings });
  const [isEnabled, setIsEnabled] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const hasInitialFetch = useRef(false);

  const fetchSettings = useCallback(async () => {
    if (!serverId) return;

    try {
      const [settingsRes, statusRes] = await Promise.all([
        axios.get(`/api/v1/guilds/${serverId}/settings/ai`, {
          withCredentials: true,
        }),
        axios.get(`/api/v1/guilds/${serverId}/features/ai/status`, {
          withCredentials: true,
        }),
      ]);

      let settingsData = defaultSettings;
      if (settingsRes.data) {
        const data = settingsRes.data.settings || settingsRes.data;
        if (data) {
          settingsData = {
            ...defaultSettings,
            ...data,
          };
        }
      }

      setSettings(settingsData);
      setOriginalSettings(settingsData);
      setIsEnabled(statusRes.data.enabled);
      hasInitialFetch.current = true;
      setHasChanges(false);
    } catch (error) {
      console.error("Failed to fetch settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  }, [serverId, setHasChanges]);

  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;

    setCurrentPath("ai");
    setServerId(serverId);
    fetchSettings();

    return () => {
      hasInitialFetch.current = false;
    };
  }, [serverId, fetchSettings, setCurrentPath, setServerId]);

  useEffect(() => {
    const handleGetUnsavedSettings = (event: CustomEvent) => {
      if (event.detail && event.detail.callback) {
        event.detail.callback(settings);
      }
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

  const toggleFeature = async () => {
    if (isToggling) return;

    setIsToggling(true);
    try {
      const endpoint = isEnabled ? "disable" : "enable";
      await axios.post(
        `/api/v1/guilds/${serverId}/features/ai/${endpoint}`,
        {},
        {
          withCredentials: true,
        }
      );
      setIsEnabled(!isEnabled);
      toast.success(`AI ${isEnabled ? "disabled" : "enabled"}`);
    } catch (error) {
      console.error("Failed to toggle AI:", error);
      toast.error("Failed to toggle AI");
    } finally {
      setIsToggling(false);
    }
  };

  const handleSettingChange = <K extends keyof AISettings>(
    key: K,
    value: AISettings[K]
  ) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    const hasChanges =
      JSON.stringify(newSettings) !== JSON.stringify(originalSettings);
    setHasChanges(hasChanges);
  };

  if (isLoading) return null;

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
            <i className="fas fa-robot text-2xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
              AI Settings
            </h1>
            <p className="text-lg text-white/70 mt-1">
              Configure AI behavior and access controls
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10">
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isEnabled ? "bg-green-500" : "bg-orange-500"} animate-pulse`}></div>
            <span className="text-sm font-medium text-white/90">
              {isEnabled ? "Active" : "Inactive"}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-white/70">
              {isEnabled ? "Enabled" : "Disabled"}
            </span>
            <ToggleSwitch
              checked={isEnabled}
              onChange={toggleFeature}
              disabled={isToggling}
              theme="purple"
            />
          </div>
        </div>

        <div className="p-6 space-y-8">
          <SettingsSection
            title="Access Control"
            description="Configure who can use AI commands and where"
            icon="fa-lock"
            iconBgColor="bg-blue-500/20"
            iconColor="text-blue-300"
          >
            <div className="space-y-6">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-white/90">Allowed Roles</label>
                <DiscordSelect
                  type="role"
                  guildId={serverId}
                  value={settings.allowed_roles}
                  onChange={(value) =>
                    handleSettingChange(
                      "allowed_roles",
                      Array.isArray(value) ? value : value ? [value] : []
                    )
                  }
                  placeholder="Select roles..."
                  multiple={true}
                  searchable={true}
                  theme="purple"
                  permissionRestrictions={false}
                />
                <p className="text-xs text-white/50">Users must have at least one of these roles to use AI commands. Leave empty to allow all roles.</p>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-white/90">Public Channels</label>
                <DiscordSelect
                  type="channel"
                  guildId={serverId}
                  value={settings.public_channels}
                  onChange={(value) =>
                    handleSettingChange(
                      "public_channels",
                      Array.isArray(value) ? value : value ? [value] : []
                    )
                  }
                  placeholder="Select channels..."
                  multiple={true}
                  searchable={true}
                  theme="purple"
                />
                <p className="text-xs text-white/50">AI will only respond in these channels. Leave empty to allow all channels.</p>
              </div>
            </div>
          </SettingsSection>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SettingsSection
              title="Thread Settings"
              description="Control AI behavior in threads"
              icon="fa-comments"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-300"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-white/90">Allow in Threads</h4>
                  <p className="text-xs text-white/50">Enable AI responses in thread channels</p>
                </div>
                <ToggleSwitch
                  checked={settings.allow_threads}
                  onChange={(value) => handleSettingChange("allow_threads", value)}
                  theme="purple"
                />
              </div>
            </SettingsSection>

            <SettingsSection
              title="Rate Limiting"
              description="Control how often users can interact with AI"
              icon="fa-clock"
              iconBgColor="bg-orange-500/20"
              iconColor="text-orange-300"
            >
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-white/90">Cooldown (seconds)</label>
                <input
                  type="number"
                  min="0"
                  value={settings.cooldown_seconds}
                  onChange={(e) => handleSettingChange("cooldown_seconds", parseInt(e.target.value) || 0)}
                  className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white/90 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                />
                <p className="text-xs text-white/50">Time users must wait between AI responses (0 for no cooldown)</p>
              </div>
            </SettingsSection>
          </div>
        </div>
      </div>
    </div>
  );
}