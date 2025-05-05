"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import DiscordSelect from "@/app/components/form/DiscordSelect";
import SettingsSection from "@/app/components/dashboard/SettingsSection";
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
          withCredentials: true
        }),
        axios.get(`/api/v1/guilds/${serverId}/features/auto_role/status`, {
          withCredentials: true
        })
      ]);
      
      let settingsData = {
        userRoles: [],
        botRoles: []
      };
      
      if (settingsRes.data) {
        const data = settingsRes.data.settings || settingsRes.data;
        if (data) {
          settingsData = {
            userRoles: Array.isArray(data.userRoles) ? data.userRoles : [],
            botRoles: Array.isArray(data.botRoles) ? data.botRoles : []
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
    
    setCurrentPath('auto-role');
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
    };

    const handleRevertChanges = () => {
      setSettings({...originalSettings});
    };

    const handleSettingsReset = () => {
      hasInitialFetch.current = false;
      fetchSettings();
    };

    window.addEventListener('getUnsavedSettings', handleGetUnsavedSettings as EventListener);
    window.addEventListener('revertChanges', handleRevertChanges);
    window.addEventListener('settingsReset', handleSettingsReset);
    
    return () => {
      window.removeEventListener('getUnsavedSettings', handleGetUnsavedSettings as EventListener);
      window.removeEventListener('revertChanges', handleRevertChanges);
      window.removeEventListener('settingsReset', handleSettingsReset);
    };
  }, [settings, originalSettings, fetchSettings]);

  const handleChange = (type: "userRoles" | "botRoles", value: string[]) => {
    const newSettings = { ...settings, [type]: value };
    setSettings(newSettings);
    setHasChanges(JSON.stringify(newSettings) !== JSON.stringify(originalSettings));
  };

  const toggleFeature = async () => {
    if (isToggling) return;
    
    setIsToggling(true);
    try {
      const endpoint = isEnabled ? 'disable' : 'enable';
      await axios.post(`/api/v1/guilds/${serverId}/features/auto_role/${endpoint}`, {}, {
        withCredentials: true
      });
      setIsEnabled(!isEnabled);
      toast.success(`Auto role ${isEnabled ? 'disabled' : 'enabled'}`);
    } catch (error) {
      console.error('Failed to toggle feature:', error);
      toast.error('Failed to toggle feature');
    } finally {
      setIsToggling(false);
    }
  };

  if (isLoading) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
            <i className="fas fa-user-tag text-2xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
              Auto Role
            </h1>
            <p className="text-lg text-white/70 mt-1">
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
            <div className={`w-2 h-2 rounded-full ${settings.userRoles.length > 0 || settings.botRoles.length > 0 ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`}></div>
            <span className="text-sm font-medium text-white/90">
              {settings.userRoles.length > 0 || settings.botRoles.length > 0 ? 'Configured' : 'Not Configured'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-white/70">
              {isEnabled ? 'Enabled' : 'Disabled'}
            </span>
            <button
              onClick={toggleFeature}
              disabled={isToggling}
              className={`relative w-12 h-6 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 focus:ring-offset-gray-900
                ${isEnabled ? 'bg-purple-500' : 'bg-gray-700'}`}
            >
              <div className={`absolute w-4 h-4 transition-transform duration-200 rounded-full top-1 left-1 bg-white transform
                ${isEnabled ? 'translate-x-6' : 'translate-x-0'}
                ${isToggling ? 'opacity-70' : ''}`}
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
