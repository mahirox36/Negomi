"use client";

import { useParams } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import DiscordSelect from "@/app/components/form/DiscordSelect";
import axios from "axios";
import toast from "react-hot-toast";

interface TempVoiceSettings {
  categoryID: string;
}

export default function TempVoice() {
  const params = useParams();
  const serverId = params.id;
  const [settings, setSettings] = useState<TempVoiceSettings>({ categoryID: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEnabled, setIsEnabled] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const fetchSettings = useCallback(async () => {
    setIsFetching(true);
    setError(null);
    try {
      const response = await axios.get(`/api/v1/guilds/${serverId}/temp-voice`);
      if (response.data) {
        setSettings({ categoryID: response.data });
      }
    } catch (error) {
      console.error("Failed to fetch temp-voice settings:", error);
      setError("Failed to load settings. Please try again later.");
      toast.error("Failed to load settings");
    } finally {
      setIsFetching(false);
    }
  }, [serverId]);

  const toggleFeature = async () => {
    setIsToggling(true);
    try {
      const endpoint = isEnabled ? 'disable' : 'enable';
      await axios.post(`/api/v1/guilds/${serverId}/features/temp_voice/${endpoint}`);
      setIsEnabled(!isEnabled);
      toast.success(`Temporary voice ${isEnabled ? 'disabled' : 'enabled'}`);
    } catch (error) {
      console.error('Failed to toggle feature:', error);
      toast.error('Failed to toggle feature');
    } finally {
      setIsToggling(false);
    }
  };

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await axios.get(`/api/v1/guilds/${serverId}/features/temp_voice/status`);
        setIsEnabled(response.data.enabled);
      } catch (error) {
        console.error('Failed to check feature status:', error);
      }
    };
    checkStatus();
  }, [serverId]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleSave = async () => {
    if (!settings.categoryID) {
      toast.error("Please select a category first");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await axios.post(`/api/v1/guilds/${serverId}/temp-voice`, { categoryID: settings.categoryID });
      toast.success("Settings saved successfully!");
      await fetchSettings(); // Refresh settings after save
    } catch (error) {
      console.error("Failed to save settings:", error);
      setError("Failed to save settings. Please try again later.");
      toast.error("Failed to save settings");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-white/20 to-white/10 rounded-xl shadow-inner">
            <i className="fas fa-microphone text-2xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
              Temporary Voice
            </h1>
            <p className="text-lg text-white/70 mt-1">
              Configure temporary voice channels that users can create on demand
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl shadow-xl border border-white/10">
        {/* Status Bar */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${settings.categoryID ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`}></div>
            <span className="text-sm font-medium text-white/90">
              {settings.categoryID ? 'Active' : 'Not Configured'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {isFetching && (
              <div className="flex items-center gap-2">
                <i className="fas fa-spinner-third animate-spin text-purple-400"></i>
                <span className="text-sm text-white/70">Loading settings...</span>
              </div>
            )}
            
            <div className="flex items-center gap-3 ml-4">
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

        {/* Settings Form */}
        <div className="p-6">
          {error ? (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-3">
                <i className="fas fa-exclamation-triangle text-red-400"></i>
                <p className="text-red-100">{error}</p>
              </div>
            </div>
          ) : null}

          <div className="space-y-6">
            {/* Category Selection */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <i className="fas fa-folder text-lg text-white/70"></i>
                <div>
                  <h3 className="text-lg font-medium text-white">Voice Category</h3>
                  <p className="text-sm text-white/70">
                    Select a category where temporary voice channels will be created
                  </p>
                </div>
              </div>

              <DiscordSelect
                type="category"
                guildId={serverId as string}
                value={settings.categoryID?.toString() || ''}
                onChange={(value) => setSettings({ ...settings, categoryID: Array.isArray(value) ? value[0] : value })}
                placeholder="Select a category..."
                className="mt-2"
              />
            </div>

            {/* Info Box */}
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <i className="fas fa-info-circle text-purple-400 mt-0.5"></i>
                <div className="space-y-2">
                  <p className="text-white/90 text-sm">
                    When enabled, a special voice channel will be created in the selected category.
                    Users can join this channel to automatically create their own temporary voice channel.
                  </p>
                  <ul className="list-disc list-inside text-sm text-white/70 space-y-1">
                    <li>Temporary channels are automatically deleted when empty</li>
                    <li>Users get full control over their created channels</li>
                    <li>Channel creators can modify their channel name and settings</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <button
              onClick={handleSave}
              disabled={isLoading || !settings.categoryID || isFetching}
              className="w-full px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 
                rounded-lg font-medium text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                flex items-center justify-center gap-2 relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full transition-transform group-hover:translate-y-0"></div>
              <div className="relative flex items-center gap-2">
                {isLoading ? (
                  <>
                    <i className="fas fa-spinner-third animate-spin"></i>
                    <span>Saving Changes...</span>
                  </>
                ) : (
                  <>
                    <i className="fas fa-save"></i>
                    <span>Save Settings</span>
                  </>
                )}
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}