"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import DiscordSelect from "@/app/components/form/DiscordSelect";
import { useLayout } from "@/providers/LayoutProvider";
import axios from "axios";
import toast from "react-hot-toast";

interface AutoRoleSettings {
  userRoles: string[];
  botRoles: string[];
}

export default function AutoRole() {
  const params = useParams();
  const serverId = params.id;
  const { setHasChanges, isLoading: layoutLoading, pageLayout, fetchPageLayout } = useLayout();
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
  const [isLoading, setIsLoading] = useState(false);
  const hasInitialFetch = useRef(false);

  const fetchSettings = useCallback(async () => {
    if (!serverId || hasInitialFetch.current) return;
    
    setIsLoading(true);
    try {
      const [settingsRes, statusRes] = await Promise.all([
        axios.get(`/api/v1/guilds/${serverId}/settings/auto-role`, {
          withCredentials: true
        }),
        axios.get(`/api/v1/guilds/${serverId}/features/auto_role/status`, {
          withCredentials: true
        })
      ]);
      
      if (settingsRes.data) {
        setSettings(settingsRes.data);
        setOriginalSettings(settingsRes.data);
        setHasChanges(false);
      }
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
          fetchPageLayout('auto-role'),
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
      {/* Header */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-white/20 to-white/10 rounded-xl shadow-inner">
            <i className="fas fa-user-tag text-2xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
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
        </div>

        <div className="p-6 space-y-6">
          {/* User Roles Panel */}
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 flex items-center justify-center bg-white/10 rounded-lg">
                <i className="fas fa-users text-xl text-white/90"></i>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Member Auto Roles</h2>
                <p className="text-sm text-white/70 mt-1">
                  Roles that will be automatically assigned to new members when they join
                </p>
              </div>
            </div>
            <DiscordSelect
              type="role"
              guildId={serverId as string}
              value={settings.userRoles}
              onChange={(value) => handleChange("userRoles", value as string[])}
              placeholder="Select roles..."
              multiple
              searchable
            />
          </div>

          {/* Bot Roles Panel */}
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 flex items-center justify-center bg-white/10 rounded-lg">
                <i className="fas fa-robot text-xl text-white/90"></i>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Bot Auto Roles</h2>
                <p className="text-sm text-white/70 mt-1">
                  Roles that will be automatically assigned to new bots when they are added
                </p>
              </div>
            </div>
            <DiscordSelect
              type="role"
              guildId={serverId as string}
              value={settings.botRoles}
              onChange={(value) => handleChange("botRoles", value as string[])}
              placeholder="Select roles..."
              multiple
              searchable
            />
          </div>
        </div>
      </div>
    </div>
  );
}
