"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import DiscordSelect from "@/components/form/DiscordSelect";
import SettingsSection from "@/components/dashboard/SettingsSection";
import { useLayout } from "@/providers/LayoutProvider";
import axios from "axios";
import toast from "react-hot-toast";

interface AutoRoleSettings {
  userRoles: string[];
  botRoles: string[];
}

export default function AutoRole() {
  const params = useParams();
  const serverId = Array.isArray(params.id) ? params.id[0] : params.id;
  const { setHasChanges, setCurrentPath, setServerId } = useLayout();
  const [settings, setSettings] = useState<AutoRoleSettings>({
    userRoles: [],
    botRoles: [],
  });
  const [originalSettings, setOriginalSettings] = useState<AutoRoleSettings>({
    userRoles: [],
    botRoles: [],
  });
  const [isEnabled, setIsEnabled] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const hasInitialFetch = useRef(false);

  const fetchSettings = useCallback(async () => {
    if (!serverId) return;

    try {
      const [settingsRes, statusRes] = await Promise.all([
        axios.get(`/api/v1/guilds/${serverId}/settings/auto-role`, {
          withCredentials: true,
        }),
        axios.get(`/api/v1/guilds/${serverId}/features/auto_role/status`, {
          withCredentials: true,
        }),
      ]);

      let settingsData = {
        userRoles: [],
        botRoles: [],
      };

      if (settingsRes.data) {
        const data = settingsRes.data.settings || settingsRes.data;
        if (data) {
          settingsData = {
            userRoles: Array.isArray(data.userRoles) ? data.userRoles : [],
            botRoles: Array.isArray(data.botRoles) ? data.botRoles : [],
          };
        }
      }

      setSettings(settingsData);
      setOriginalSettings(settingsData);
      setHasChanges(false);
      setIsEnabled(statusRes.data.enabled);
      hasInitialFetch.current = true;
    } catch (error) {
      console.error("Failed to fetch auto-role settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  }, [serverId, setHasChanges]);

  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;

    setCurrentPath("auto-role");
    setServerId(serverId as string);
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

  const handleChange = (type: "userRoles" | "botRoles", value: string[]) => {
    const newSettings = { ...settings, [type]: value };
    setSettings(newSettings);
    setHasChanges(
      JSON.stringify(newSettings) !== JSON.stringify(originalSettings)
    );
  };

  const toggleFeature = async () => {
    if (isToggling) return;

    setIsToggling(true);
    try {
      const endpoint = isEnabled ? "disable" : "enable";
      await axios.post(
        `/api/v1/guilds/${serverId}/features/auto_role/${endpoint}`,
        {},
        {
          withCredentials: true,
        }
      );
      setIsEnabled(!isEnabled);
      toast.success(`Auto role ${isEnabled ? "disabled" : "enabled"}`);
    } catch (error) {
      console.error("Failed to toggle feature:", error);
      toast.error("Failed to toggle feature");
    } finally {
      setIsToggling(false);
    }
  };

  if (isLoading) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-500/20 to-fuchsia-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 opacity-10 -rotate-6">
          <i className="fas fa-user-plus text-[180px] text-white"></i>
        </div>
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-500/40 to-fuchsia-500/40 rounded-xl shadow-inner border border-white/10">
            <i className="fas fa-user-plus text-3xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
              Auto Role
            </h1>
            <p className="text-lg text-white/70 mt-1 max-w-2xl">
              Configure roles that are automatically assigned to new members
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10">
        {/* Status Bar */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                settings.userRoles.length > 0 || settings.botRoles.length > 0
                  ? "bg-green-500"
                  : "bg-yellow-500"
              } animate-pulse`}
            ></div>
            <span className="text-sm font-medium text-white/90">
              {settings.userRoles.length > 0 || settings.botRoles.length > 0
                ? "Configured"
                : "Not Configured"}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-white/70">
              {isEnabled ? "Enabled" : "Disabled"}
            </span>
            <button
              onClick={toggleFeature}
              disabled={isToggling}
              className={`relative w-12 h-6 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 focus:ring-offset-gray-900
          ${isEnabled ? "bg-purple-500" : "bg-gray-700"}`}
            >
              <div
                className={`absolute w-4 h-4 transition-transform duration-200 rounded-full top-1 left-1 bg-white transform
          ${isEnabled ? "translate-x-6" : "translate-x-0"}
          ${isToggling ? "opacity-70" : ""}`}
              />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Member Roles Section */}
          <SettingsSection
            title="Member Auto Roles"
            description="Roles automatically assigned to new members"
            icon="fa-users"
            iconBgColor="bg-blue-500/20"
            iconColor="text-blue-300"
          >
            <DiscordSelect
              type="role"
              guildId={serverId as string}
              value={settings.userRoles}
              onChange={(value) => handleChange("userRoles", value as string[])}
              placeholder="Select roles..."
              multiple
              searchable
            />
          </SettingsSection>

          {/* Bot Roles Section */}
          <SettingsSection
            title="Bot Auto Roles"
            description="Roles automatically assigned to new bots"
            icon="fa-robot"
            iconBgColor="bg-purple-500/20"
            iconColor="text-purple-300"
          >
            <DiscordSelect
              type="role"
              guildId={serverId as string}
              value={settings.botRoles}
              onChange={(value) => handleChange("botRoles", value as string[])}
              placeholder="Select roles..."
              multiple
              searchable
            />
          </SettingsSection>
        </div>
      </div>
    </div>
  );
}
