"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import DiscordSelect from "@/components/form/DiscordSelect";
import { ToggleSwitch } from "@/components/form/ToggleSwitch";
import SettingsSection from "@/components/dashboard/SettingsSection";
import OptionCard from "@/components/dashboard/OptionCard";
import { useLayout } from "@/providers/LayoutProvider";
import axios from "axios";
import toast from "react-hot-toast";

// Define the settings interface
interface CustomRoleSettings {
  creation_mode: "everyone" | "boosters" | "specific_roles";
  not_allowed: string[];
  allowed_roles: string[];
  max_roles_per_user: number;
  can_hoist: boolean;
  can_mention: boolean;
  color_restriction: "all" | "preset" | "none";
  max_members_per_role: number;
  require_confirmation: boolean;
  parent_role_id?: string;
}

// Default settings
const defaultSettings: CustomRoleSettings = {
  creation_mode: "everyone",
  not_allowed: [],
  allowed_roles: [],
  max_roles_per_user: 1,
  can_hoist: true,
  can_mention: false,
  color_restriction: "all",
  max_members_per_role: 10,
  require_confirmation: true,
};

export default function CustomRole() {
  const params = useParams();
  const serverId = params.id as string;

  // Layout provider integration
  const { setHasChanges, setCurrentPath, setServerId } = useLayout();

  // State setup
  const [settings, setSettings] = useState<CustomRoleSettings>({
    ...defaultSettings,
  });
  const [originalSettings, setOriginalSettings] = useState<CustomRoleSettings>({
    ...defaultSettings,
  });
  const [isEnabled, setIsEnabled] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [prohibitedWord, setProhibitedWord] = useState("");
  const hasInitialFetch = useRef(false);

  // Fetch settings from the API
  const fetchSettings = useCallback(async () => {
    if (!serverId) return;

    try {
      const [settingsRes, statusRes] = await Promise.all([
        axios.get(`/api/v1/guilds/${serverId}/settings/custom-roles`, {
          withCredentials: true,
        }),
        axios.get(`/api/v1/guilds/${serverId}/features/roles/status`, {
          withCredentials: true,
        }),
      ]);

      // Use data if available, otherwise use defaults
      let settingsData = defaultSettings;

      if (settingsRes.data) {
        // Handle both nested settings and direct object formats
        const data = settingsRes.data.settings || settingsRes.data;

        if (data) {
          settingsData = {
            creation_mode: data.creation_mode || defaultSettings.creation_mode,
            not_allowed: Array.isArray(data.not_allowed)
              ? data.not_allowed
              : defaultSettings.not_allowed,
            allowed_roles: Array.isArray(data.allowed_roles)
              ? data.allowed_roles
              : defaultSettings.allowed_roles,
            max_roles_per_user:
              data.max_roles_per_user || defaultSettings.max_roles_per_user,
            can_hoist:
              data.can_hoist !== undefined
                ? data.can_hoist
                : defaultSettings.can_hoist,
            can_mention:
              data.can_mention !== undefined
                ? data.can_mention
                : defaultSettings.can_mention,
            color_restriction:
              data.color_restriction || defaultSettings.color_restriction,
            max_members_per_role:
              data.max_members_per_role || defaultSettings.max_members_per_role,
            require_confirmation:
              data.require_confirmation !== undefined
                ? data.require_confirmation
                : defaultSettings.require_confirmation,
            parent_role_id:
              data.parent_role_id || defaultSettings.parent_role_id,
          };
        }
      }

      setSettings(settingsData);
      setOriginalSettings(settingsData);
      setIsEnabled(statusRes.data.enabled);
      hasInitialFetch.current = true;
      // Update LayoutProvider state - no changes yet as we just loaded
      setHasChanges(false);
    } catch (error) {
      console.error("Failed to fetch custom role settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  }, [serverId, setHasChanges]);

  // Initialize data on component mount
  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;

    // Set current path and server ID in layout provider
    setCurrentPath("custom-roles");
    setServerId(serverId);
    fetchSettings();

    return () => {
      hasInitialFetch.current = false;
    };
  }, [serverId, fetchSettings, setCurrentPath, setServerId]);

  // Hook up LayoutProvider event handlers
  useEffect(() => {
    // Handle getting unsaved settings from the layout provider
    const handleGetUnsavedSettings = (event: CustomEvent) => {
      if (event.detail && event.detail.callback) {
        event.detail.callback(settings);
      }
      setOriginalSettings(settings);
    };

    // Handle reverting changes from the layout provider
    const handleRevertChanges = () => {
      setSettings({ ...originalSettings });
    };

    // Handle settings reset from the layout provider
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

  // Function to toggle feature status
  const toggleFeature = async () => {
    if (isToggling) return;

    setIsToggling(true);
    try {
      const endpoint = isEnabled ? "disable" : "enable";
      await axios.post(
        `/api/v1/guilds/${serverId}/features/roles/${endpoint}`,
        {},
        {
          withCredentials: true,
        }
      );
      setIsEnabled(!isEnabled);
      toast.success(`Custom roles ${isEnabled ? "disabled" : "enabled"}`);
    } catch (error) {
      console.error("Failed to toggle feature:", error);
      toast.error("Failed to toggle feature");
    } finally {
      setIsToggling(false);
    }
  };

  // General change handler for settings
  const handleSettingChange = <K extends keyof CustomRoleSettings>(
    key: K,
    value: CustomRoleSettings[K]
  ) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    // Update LayoutProvider state
    const hasChanges =
      JSON.stringify(newSettings) !== JSON.stringify(originalSettings);
    setHasChanges(hasChanges);
  };

  // Add prohibited word handler
  const addProhibitedWord = () => {
    if (!prohibitedWord.trim()) return;

    // Don't add duplicates
    if (settings.not_allowed.includes(prohibitedWord.toLowerCase())) {
      toast.error("Word already in the list");
      return;
    }

    handleSettingChange("not_allowed", [
      ...settings.not_allowed,
      prohibitedWord.toLowerCase(),
    ]);
    setProhibitedWord("");
  };

  // Remove prohibited word handler
  const removeProhibitedWord = (word: string) => {
    const updated = settings.not_allowed.filter((w) => w !== word);
    handleSettingChange("not_allowed", updated);
  };

  // Loading UI handled by layout-client.tsx

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-500/20 to-fuchsia-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 opacity-10 -rotate-6">
          <i className="fas fa-user-tag text-[180px] text-white"></i>
        </div>
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-500/40 to-fuchsia-500/40 rounded-xl shadow-inner border border-white/10">
            <i className="fas fa-user-tag text-3xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
              Custom Roles
            </h1>
            <p className="text-lg text-white/70 mt-1 max-w-2xl">
              Configure how server members can create and manage their custom
              roles
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10">
        {/* Status Bar */}
        <div className="px-6 py-2 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isEnabled ? "bg-green-500" : "bg-orange-500"
              } animate-pulse`}
            ></div>
            <span className="text-sm font-large text-white/90">
              {isEnabled ? "Active" : "Inactive"}
            </span>
          </div>

          {/* Toggle switch */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-white/70">
              {isEnabled ? "Enabled" : "Disabled"}
            </span>
            <ToggleSwitch
              checked={isEnabled}
              onChange={toggleFeature}
              disabled={isToggling}
              theme="purple"
              size="md"
            />
          </div>
        </div>

        <div className="p-6 space-y-8">
          {/* Creation Mode Section */}
          <SettingsSection
            title="Role Creation Permissions"
            description="Control who can create custom roles in your server"
            icon="fa-user-plus"
            iconBgColor="bg-indigo-500/20"
            iconColor="text-indigo-300"
          >
            {/* Creation Mode Selection */}
            <div className="grid grid-cols-3 gap-4">
              <OptionCard
                title="Everyone"
                description="Any server member can create custom roles"
                icon="fa-users"
                iconColor="text-indigo-300"
                selected={settings.creation_mode === "everyone"}
                onClick={() => handleSettingChange("creation_mode", "everyone")}
              />

              <OptionCard
                title="Server Boosters"
                description="Only members who boost the server"
                icon="fa-rocket"
                iconColor="text-pink-300"
                selected={settings.creation_mode === "boosters"}
                borderColor="border-pink-500"
                bgColor="bg-pink-500/10"
                onClick={() => handleSettingChange("creation_mode", "boosters")}
              />

              <OptionCard
                title="Specific Roles"
                description="Only members with specific roles"
                icon="fa-user-shield"
                iconColor="text-emerald-300"
                selected={settings.creation_mode === "specific_roles"}
                borderColor="border-emerald-500"
                bgColor="bg-emerald-500/10"
                onClick={() =>
                  handleSettingChange("creation_mode", "specific_roles")
                }
              />
            </div>

            {/* Allowed Roles Selection (when specific_roles is selected) */}
            {settings.creation_mode === "specific_roles" && (
              <div className="mt-4 p-4 rounded-lg bg-white/5 border border-white/10">
                <h3 className="text-sm font-medium text-white mb-3">
                  Select Allowed Roles
                </h3>
                <DiscordSelect
                  type="role"
                  guildId={serverId}
                  value={settings.allowed_roles}
                  onChange={(value) =>
                    handleSettingChange("allowed_roles", value as string[])
                  }
                  placeholder="Select roles that can create custom roles..."
                  multiple
                  searchable
                  theme="purple"
                />
              </div>
            )}
          </SettingsSection>

          {/* Parent Role Section */}
          <SettingsSection
            title="Role Position"
            description="Control where custom roles are placed in the hierarchy"
            icon="fa-layer-group"
            iconBgColor="bg-amber-500/20"
            iconColor="text-amber-300"
          >
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-white mb-2">
                  Parent Role
                </h3>
                <p className="text-sm text-white/70 mb-4">
                  New custom roles will be created just below this role
                </p>
                <DiscordSelect
                  type="role"
                  guildId={serverId}
                  value={settings.parent_role_id || ""}
                  onChange={(value) =>
                    handleSettingChange("parent_role_id", value as string)
                  }
                  placeholder="Select parent role..."
                  theme="purple"
                />
              </div>

              {settings.parent_role_id && (
                <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20">
                  <div className="flex gap-3">
                    <i className="fas fa-triangle-exclamation text-amber-500 mt-1"></i>
                    <div className="space-y-2">
                      <p className="text-sm text-amber-200 font-medium">
                        Role Position Warning
                      </p>
                      <ul className="text-xs text-amber-100/70 space-y-1.5 list-disc ml-4">
                        <li>
                          Setting this too high in the role hierarchy could be
                          dangerous
                        </li>
                        <li>
                          Custom roles will inherit permissions from roles above
                          them
                        </li>
                        <li>
                          Members could gain unintended permissions if the
                          parent role is too high
                        </li>
                        <li>
                          Recommended: Create a dedicated "Custom Roles" role
                          with minimal permissions
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </SettingsSection>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Role Limits Section */}
            <SettingsSection
              title="Role Limits"
              description="Configure role quantity and member limits"
              icon="fa-sliders-h"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-300"
            >
              {/* Max Roles Per User */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-white">
                    Max Roles Per User
                  </label>
                  <span className="px-2 py-1 bg-white/10 rounded text-sm text-white/80">
                    {settings.max_roles_per_user}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={settings.max_roles_per_user}
                  onChange={(e) =>
                    handleSettingChange(
                      "max_roles_per_user",
                      parseInt(e.target.value)
                    )
                  }
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                />
                <div className="flex justify-between text-xs text-white/50 mt-1">
                  <span>1</span>
                  <span>5</span>
                  <span>10</span>
                </div>
              </div>

              {/* Max Members Per Role */}
              <div className="pt-4">
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-white">
                    Max Members Per Role
                  </label>
                  <span className="px-2 py-1 bg-white/10 rounded text-sm text-white/80">
                    {settings.max_members_per_role}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="100"
                  step="1"
                  value={settings.max_members_per_role}
                  onChange={(e) =>
                    handleSettingChange(
                      "max_members_per_role",
                      parseInt(e.target.value)
                    )
                  }
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                />
                <div className="flex justify-between text-xs text-white/50 mt-1">
                  <span>1</span>
                  <span>50</span>
                  <span>100</span>
                </div>
              </div>
            </SettingsSection>

            {/* Role Properties Section */}
            <SettingsSection
              title="Role Properties"
              description="Configure appearance and behavior options"
              icon="fa-palette"
              iconBgColor="bg-blue-500/20"
              iconColor="text-blue-300"
            >
              {/* Color Restrictions */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white">
                  Color Restrictions
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <div
                    className={`flex flex-col items-center p-3 rounded-lg cursor-pointer transition-all
              ${
                settings.color_restriction === "all"
                  ? "bg-gradient-to-br from-purple-500/30 to-blue-500/30 border-2 border-blue-400/50"
                  : "bg-white/10 hover:bg-white/15 border border-white/10"
              }`}
                    onClick={() =>
                      handleSettingChange("color_restriction", "all")
                    }
                  >
                    <div className="flex gap-1 mb-2">
                      <span className="w-3 h-3 rounded-full bg-red-500"></span>
                      <span className="w-3 h-3 rounded-full bg-green-500"></span>
                      <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                    </div>
                    <span className="text-xs font-medium text-white">
                      Any Color
                    </span>
                  </div>

                  <div
                    className={`flex flex-col items-center p-3 rounded-lg cursor-pointer transition-all
              ${
                settings.color_restriction === "preset"
                  ? "bg-gradient-to-br from-purple-500/30 to-blue-500/30 border-2 border-blue-400/50"
                  : "bg-white/10 hover:bg-white/15 border border-white/10"
              }`}
                    onClick={() =>
                      handleSettingChange("color_restriction", "preset")
                    }
                  >
                    <div className="flex gap-1 mb-2">
                      <span className="w-3 h-3 rounded-full bg-purple-500"></span>
                      <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                    </div>
                    <span className="text-xs font-medium text-white">
                      Preset Only
                    </span>
                  </div>

                  <div
                    className={`flex flex-col items-center p-3 rounded-lg cursor-pointer transition-all
              ${
                settings.color_restriction === "none"
                  ? "bg-gradient-to-br from-purple-500/30 to-blue-500/30 border-2 border-blue-400/50"
                  : "bg-white/10 hover:bg-white/15 border border-white/10"
              }`}
                    onClick={() =>
                      handleSettingChange("color_restriction", "none")
                    }
                  >
                    <div className="flex gap-1 mb-2">
                      <span className="w-3 h-3 rounded-full bg-gray-500"></span>
                    </div>
                    <span className="text-xs font-medium text-white">
                      No Colors
                    </span>
                  </div>
                </div>
              </div>

              {/* Toggle Options */}
              <div className="space-y-4 pt-2">
                {/* Can Hoist */}
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-white">
                      Allow Hoisting
                    </h4>
                    <p className="text-xs text-white/50">
                      Let members display their roles separately in the member
                      list
                    </p>
                  </div>
                  <ToggleSwitch
                    checked={settings.can_hoist}
                    onChange={(value: boolean) =>
                      handleSettingChange("can_hoist", value)
                    }
                    theme="purple"
                  />
                </div>

                {/* Can Mention */}
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-white">
                      Allow Mentionable Roles
                    </h4>
                    <p className="text-xs text-white/50">
                      Let members make their roles mentionable by anyone
                    </p>
                  </div>
                  <ToggleSwitch
                    checked={settings.can_mention}
                    onChange={(value: boolean) =>
                      handleSettingChange("can_mention", value)
                    }
                    theme="purple"
                  />
                </div>

                {/* Require Confirmation */}
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-white">
                      Require Confirmation
                    </h4>
                    <p className="text-xs text-white/50">
                      Users must confirm before being added to a custom role
                    </p>
                  </div>
                  <ToggleSwitch
                    checked={settings.require_confirmation}
                    onChange={(value: boolean) =>
                      handleSettingChange("require_confirmation", value)
                    }
                    theme="purple"
                  />
                </div>
              </div>
            </SettingsSection>
          </div>

          {/* Prohibited Words Section */}
          <SettingsSection
            title="Prohibited Words"
            description="Words that cannot be used in role names"
            icon="fa-ban"
            iconBgColor="bg-red-500/20"
            iconColor="text-red-300"
          >
            {/* Add new prohibited word */}
            <div className="flex gap-3">
              <div className="flex-grow">
                <input
                  type="text"
                  value={prohibitedWord}
                  onChange={(e) => setProhibitedWord(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white/10 border border-white/20 rounded-lg
            text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-red-500/40
            focus:border-red-500/40"
                  placeholder="Enter a prohibited word..."
                  onKeyDown={(e) => e.key === "Enter" && addProhibitedWord()}
                />
              </div>
              <button
                onClick={addProhibitedWord}
                className="px-4 py-2.5 bg-red-500/20 hover:bg-red-500/30 transition-colors
            rounded-lg text-white font-medium focus:outline-none focus:ring-2 focus:ring-red-500/40"
              >
                Add
              </button>
            </div>

            {/* Word list */}
            <div className="max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent pr-2">
              {settings.not_allowed.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {settings.not_allowed.map((word) => (
                    <div
                      key={word}
                      className="px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/30
              text-sm text-white flex items-center gap-2"
                    >
                      {word}
                      <button
                        onClick={() => removeProhibitedWord(word)}
                        className="text-red-300 hover:text-red-100 transition-colors focus:outline-none"
                      >
                        <i className="fas fa-times text-xs"></i>
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4 text-white/50 text-sm">
                  No prohibited words added yet
                </div>
              )}
            </div>
          </SettingsSection>
        </div>
      </div>
    </div>
  );
}
