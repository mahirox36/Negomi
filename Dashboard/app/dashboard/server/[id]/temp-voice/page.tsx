"use client";

import { useParams } from "next/navigation";
import { useState, useEffect, useCallback, useRef } from "react";
import DiscordSelect from "@/components/form/DiscordSelect";
import SettingsSection from "@/components/dashboard/SettingsSection";
import { useLayout } from "@/providers/LayoutProvider";
import axios from "axios";
import toast from "react-hot-toast";

interface TempVoiceSettings {
  categoryID: string;
}

export default function TempVoice() {
  const params = useParams();
  const serverId = params.id;
  const { setHasChanges, setCurrentPath, setServerId } = useLayout();
  const [settings, setSettings] = useState<TempVoiceSettings>({ categoryID: '' });
  const [originalSettings, setOriginalSettings] = useState<TempVoiceSettings>({ categoryID: '' });
  const [isEnabled, setIsEnabled] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const hasInitialFetch = useRef(false);

  const fetchSettings = useCallback(async () => {
    if (!serverId) return;
    
    try {
      const [settingsRes, statusRes] = await Promise.all([
        axios.get(`/api/v1/guilds/${serverId}/settings/temp-voice`, {
          withCredentials: true
        }),
        axios.get(`/api/v1/guilds/${serverId}/features/temp_voice/status`, {
          withCredentials: true
        })
      ]);
      
      const settingsData = {
        categoryID: settingsRes.data?.categoryID || ''
      };
      
      setSettings(settingsData);
      setOriginalSettings(settingsData);
      setIsEnabled(statusRes.data.enabled);
      setHasChanges(false);
      hasInitialFetch.current = true;
    } catch (error) {
      console.error("Failed to fetch temp-voice settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  }, [serverId, setHasChanges]);

  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;
    
    setCurrentPath('temp-voice');
    setServerId(Array.isArray(serverId) ? serverId[0] : serverId);
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

  const handleCategoryChange = (value: string | string[]) => {
    const categoryID = Array.isArray(value) ? value[0] || '' : value;
    const newSettings = { ...settings, categoryID };
    setSettings(newSettings);
    setHasChanges(JSON.stringify(newSettings) !== JSON.stringify(originalSettings));
  };

  const toggleFeature = async () => {
    if (isToggling) return;
    
    setIsToggling(true);
    try {
      const endpoint = isEnabled ? 'disable' : 'enable';
      await axios.post(`/api/v1/guilds/${serverId}/features/temp_voice/${endpoint}`, {}, {
        withCredentials: true
      });
      setIsEnabled(!isEnabled);
      toast.success(`Temporary voice ${isEnabled ? 'disabled' : 'enabled'}`);
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
            <i className="fas fa-microphone text-2xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
              Temporary Voice
            </h1>
            <p className="text-lg text-white/70 mt-1">
              Configure temporary voice channels that users can create on demand
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10">
        {/* Status Bar */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${settings.categoryID ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`}></div>
            <span className="text-sm font-medium text-white/90">
              {settings.categoryID ? 'Configured' : 'Not Configured'}
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
          {/* Category Selection */}
          <SettingsSection
            title="Voice Category"
            description="Select where temporary voice channels will be created"
            icon="fa-folder"
            iconBgColor="bg-blue-500/20"
            iconColor="text-blue-300"
          >
            <DiscordSelect
              type="category"
              guildId={serverId as string}
              value={settings.categoryID}
              onChange={handleCategoryChange}
              placeholder="Select a category..."
            />
          </SettingsSection>

          {/* Info Section */}
          <SettingsSection
            title="How It Works"
            description="Learn about temporary voice channels"
            icon="fa-info-circle"
            iconBgColor="bg-purple-500/20"
            iconColor="text-purple-300"
          >
            <div className="space-y-4">
              <p className="text-white/90 text-sm">
                When enabled, a special voice channel will be created in the selected category.
                Users can join this channel to automatically create their own temporary voice channel.
              </p>
              <ul className="list-disc list-inside text-sm text-white/70 space-y-2">
                <li>Temporary channels are automatically deleted when empty</li>
                <li>Users get full control over their created channels</li>
                <li>Channel creators can modify their channel name and settings</li>
              </ul>
            </div>
          </SettingsSection>
        </div>
      </div>
    </div>
  );
}