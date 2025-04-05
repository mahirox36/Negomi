"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { useLayout } from "@/app/contexts/LayoutContext";
import DiscordSelect from "@/app/components/form/DiscordSelect";
import axios from "axios";
import toast from "react-hot-toast";

interface AutoRoleSettings {
  userRoles: string[];
  botRoles: string[];
}

export default function AutoRole() {
  const params = useParams();
  const serverId = params.id;
  const { setHasChanges } = useLayout();
  const [settings, setSettings] = useState<AutoRoleSettings>({
    userRoles: [],
    botRoles: [],
  });
  const [originalSettings, setOriginalSettings] = useState<AutoRoleSettings>({
    userRoles: [],
    botRoles: [],
  });

  const fetchSettings = useCallback(async () => {
    try {
      const response = await axios.get(`/api/v1/guilds/${serverId}/settings/auto-role`);
      if (response.data) {
        setSettings(response.data);
        setOriginalSettings(response.data);
        setHasChanges(false);
      }
    } catch (error) {
      console.error("Failed to fetch auto-role settings:", error);
      toast.error("Failed to load settings");
    }
  }, [serverId, setHasChanges]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleChange = (type: 'userRoles' | 'botRoles', value: string[]) => {
    const newSettings = { ...settings, [type]: value };
    setSettings(newSettings);
    setHasChanges(true);
  };

  const handleSave = async (e?: CustomEvent) => {
    e?.stopPropagation();
    
    try {
      await axios.post(`/api/v1/guilds/${serverId}/settings/auto-role`, settings);
      setOriginalSettings(settings);
      setHasChanges(false);
      toast.success("Auto-role settings saved!");
    } catch (error) {
      console.error("Failed to save auto-role settings:", error);
      toast.error("Failed to save settings");
    }
  };

  const handleRevert = (e?: CustomEvent) => {
    e?.stopPropagation();
    setSettings(originalSettings);
    setHasChanges(false);
  };

  useEffect(() => {
    const saveHandler = (e: Event) => handleSave(e as CustomEvent);
    const revertHandler = (e: Event) => handleRevert(e as CustomEvent);

    window.addEventListener("saveChanges", saveHandler);
    window.addEventListener("revertChanges", revertHandler);

    return () => {
      window.removeEventListener("saveChanges", saveHandler);
      window.removeEventListener("revertChanges", revertHandler);
    };
  }, [settings, originalSettings]);

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

      {/* User Roles Panel */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 border border-white/10">
        <div className="flex items-center gap-4 mb-6">
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
          onChange={(value) => handleChange('userRoles', value as string[])}
          placeholder="Select roles..."
          multiple
          searchable
        />
      </div>

      {/* Bot Roles Panel */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 border border-white/10">
        <div className="flex items-center gap-4 mb-6">
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
          onChange={(value) => handleChange('botRoles', value as string[])}
          placeholder="Select roles..."
          multiple
          searchable
        />
      </div>
    </div>
  );
}
