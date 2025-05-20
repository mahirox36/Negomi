"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import { useLayout } from "@/providers/LayoutProvider";
import DiscordSelect from "@/components/form/DiscordSelect";
import { ToggleSwitch } from "@/components/form/ToggleSwitch";
import TextInput from "@/components/form/TextInput";
import SettingsSection from "@/components/dashboard/SettingsSection";
import EmojiPicker from "@/components/form/EmojiPicker";
import MessagePreview from "@/components/dashboard/MessagePreview";
import axios from "axios";
import toast from "react-hot-toast";
import MessageSelect from "@/components/form/MessageSelect";

interface ReactionRole {
  emoji: string;
  role_id: string;
}

interface ReactionRoleSettings {
  message_id: number;
  reactions: ReactionRole[];
  allow_unselect: boolean;
  max_reactions_per_user: number | null;
  require_roles: string[] | null;
  forbidden_roles: string[] | null;
  cooldown: number | null;
  remove_reactions: boolean;
}

interface Message {
  id: number;
  content: string;
  embeds: any[];
}

export default function ReactionRoles() {
  const params = useParams();
  const serverId = params.id as string;
  const {
    setHasChanges,
    setCurrentPath,
    setServerId,
    setDisableProviderSave,
    setLoading,
  } = useLayout();
  const hasInitialFetch = useRef(false);

  // State management
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [reactionRoles, setReactionRoles] = useState<ReactionRoleSettings[]>(
    []
  );
  const [currentReactionRole, setCurrentReactionRole] = useState<ReactionRole>({
    emoji: "",
    role_id: "",
  });
  const [settings, setSettings] = useState<ReactionRoleSettings>({
    message_id: 0,
    reactions: [],
    allow_unselect: false,
    max_reactions_per_user: null,
    require_roles: null,
    forbidden_roles: null,
    cooldown: null,
    remove_reactions: false,
  });
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("basic"); // "basic" or "advanced"

  // Fetch messages and reaction roles
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [messagesRes, reactionRolesRes] = await Promise.all([
        axios.get(`/api/v1/guilds/${serverId}/messages`, {
          withCredentials: true,
        }),
        axios.get(`/api/v1/guilds/${serverId}/reaction-roles`, {
          withCredentials: true,
        }),
      ]);

      setMessages(messagesRes.data);
      setReactionRoles(reactionRolesRes.data);
    } catch (error) {
      console.error("Failed to fetch data:", error);
      toast.error("Failed to load messages and reaction roles");
    } finally {
      setIsLoading(false);
    }
  }, [serverId]);

  // Listen for save event from layout
  useEffect(() => {
    const handleSaveSettings = async (event: Event) => {
      const customEvent = event as CustomEvent;
      setLoading(true);
      if (isSaving) return; // Prevent multiple saves
      if (!selectedMessage) return;

      try {
        await axios.post(
          `/api/v1/guilds/${serverId}/reaction-roles`,
          settings,
          { withCredentials: true }
        );
        await fetchData();
        if (customEvent.detail?.callback) {
          customEvent.detail.callback(true);
        }
        setLoading(false);
        setHasChanges(false);
        toast.success("Changes saved successfully");
      } catch (error) {
        console.error("Failed to save settings:", error);
        toast.error("Failed to save settings");
        if (customEvent.detail?.callback) {
          customEvent.detail.callback(false);
        }
      }
    };

    window.addEventListener("getUnsavedSettings", handleSaveSettings);
    return () => {
      window.removeEventListener("getUnsavedSettings", handleSaveSettings);
    };
  }, [selectedMessage, settings, serverId, fetchData]);

  // Initialize
  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;

    setCurrentPath("reaction-roles");
    setServerId(serverId);

    // Disable provider save logic for this page
    setHasChanges(false); // Ensure no unsaved changes are flagged initially
    setDisableProviderSave(true);

    fetchData();
    hasInitialFetch.current = true;
  }, [
    serverId,
    fetchData,
    setCurrentPath,
    setServerId,
    setDisableProviderSave,
  ]);

  // Handle message selection
  // Ensure both messageId and message.id are treated as strings for comparison
  const handleMessageSelect = (messageId: string | string[]) => {
    console.log("handleMessageSelect called with:", messageId);
    console.log("Current messages:", messages);

    if (Array.isArray(messageId)) {
      console.error(
        "Expected a single string, but received an array:",
        messageId
      );
      return;
    }

    const message = messages.find((m) => m.id.toString() === messageId);
    if (!message) {
      console.error("Message not found for ID:", messageId);
      return;
    }

    setSelectedMessage(message);

    const existingSettings = reactionRoles.find(
      (rr) => rr.message_id.toString() === messageId
    );

    if (existingSettings) {
      setSettings(existingSettings);
    } else {
      setSettings({
        message_id: parseInt(messageId),
        reactions: [],
        allow_unselect: false,
        max_reactions_per_user: null,
        require_roles: null,
        forbidden_roles: null,
        cooldown: null,
        remove_reactions: false,
      });
    }

    // Reset fields
    setCurrentReactionRole({ emoji: "", role_id: "" });
    setActiveTab("basic");
    console.log("Message selected:", message);
  };

  // Add reaction role
  const handleAddReaction = () => {
    if (
      !currentReactionRole.emoji ||
      !currentReactionRole.role_id ||
      !selectedMessage
    ) {
      toast.error("Please select both an emoji and a role");
      return;
    }

    // Check for duplicate emoji
    if (settings.reactions.some((r) => r.emoji === currentReactionRole.emoji)) {
      toast.error("This emoji is already used for another role");
      return;
    }

    const newSettings: ReactionRoleSettings = {
      ...settings,
      message_id: selectedMessage.id,
      reactions: [...settings.reactions, currentReactionRole],
    };

    setSettings(newSettings);
    setCurrentReactionRole({ emoji: "", role_id: "" });
    toast.success("Reaction role added");
    setHasChanges(true);
  };

  // Remove reaction role
  const handleRemoveReaction = (emoji: string) => {
    if (confirmDelete === emoji) {
      const newReactions = settings.reactions.filter((r) => r.emoji !== emoji);
      setSettings({ ...settings, reactions: newReactions });
      setConfirmDelete(null);
      toast.success("Reaction role removed");
      setHasChanges(true);
    } else {
      setConfirmDelete(emoji);
      setTimeout(() => setConfirmDelete(null), 3000);
    }
  };

  // Update settings
  const updateSettings = (key: keyof ReactionRoleSettings, value: any) => {
    setSettings({ ...settings, [key]: value });
    setHasChanges(true);
  };

  // Role name resolver
  const getRoleName = (roleId: string) => {
    // This would be implemented with a Discord API call or cache
    return `Role ${roleId.substring(0, 6)}...`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-16 h-16 rounded-full bg-purple-500/30 flex items-center justify-center">
            <i className="fas fa-spinner-third fa-spin text-2xl text-purple-200"></i>
          </div>
          <p className="mt-4 text-purple-200">Loading reaction roles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-10">
      {/* Header Section */}
      <div className="bg-gradient-to-br from-purple-500/20 to-fuchsia-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 opacity-10 -rotate-6">
          <i className="fas fa-hands-clapping text-[180px] text-white"></i>
        </div>
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-500/40 to-fuchsia-500/40 rounded-xl shadow-inner border border-white/10">
            <i className="fas fa-hands-clapping text-3xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
              Reaction Roles
            </h1>
            <p className="text-lg text-white/70 mt-1 max-w-2xl">
              Let users assign themselves roles by reacting to messages with
              emojis
            </p>
          </div>
        </div>
      </div>

      {/* Step 1: Message Selection */}
      <SettingsSection
        title="Step 1: Select a Message"
        description="Choose a message to add reaction roles to"
        icon="fa-message"
        iconBgColor="bg-purple-500/20"
        iconColor="text-purple-300"
      >
        <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/5">
          <MessageSelect
            guildId={serverId}
            value={selectedMessage?.id.toString() || ""}
            onChange={(value) => handleMessageSelect(value)}
            placeholder="Select a message..."
            theme="purple"
            showPreview={true}
            showEmbedCount={true}
            showContent={true}
            maxContentLength={100}
            emptyMessage="No messages available"
            loadingMessage="Loading messages..."
          />

          {selectedMessage && (
            <div className="mt-6 bg-black/30 rounded-lg p-4 border border-white/10">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-white/90">
                  Message Preview
                </h3>
                <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full">
                  ID: {selectedMessage.id}
                </span>
              </div>
              <MessagePreview
                content={selectedMessage.content}
                embeds={selectedMessage.embeds || []}
              />
            </div>
          )}
        </div>
      </SettingsSection>

      {selectedMessage && (
        <>
          {/* Step 2: Configure Reaction Roles */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SettingsSection
              title="Step 2: Add Reaction Roles"
              description="Assign roles to emoji reactions"
              icon="fa-plus"
              iconBgColor="bg-fuchsia-500/20"
              iconColor="text-fuchsia-300"
            >
              <div className="space-y-6">
                {/* Reaction Role List First */}
                {settings.reactions.length > 0 && (
                  <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/5">
                    <h3 className="text-lg font-medium text-white/90 mb-4 flex items-center gap-2">
                      <i className="fas fa-list text-fuchsia-300"></i>
                      <span>Current Reaction Roles</span>
                      <span className="text-xs bg-fuchsia-500/20 text-fuchsia-300 px-2 py-0.5 rounded-full ml-2">
                        {settings.reactions.length}
                      </span>
                    </h3>

                    <div className="space-y-3">
                      {settings.reactions.map((reaction) => (
                        <div
                          key={reaction.emoji}
                          className="flex items-center justify-between p-4 rounded-lg bg-black/30 border border-white/5 transition-all hover:border-white/10"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 flex items-center justify-center bg-purple-500/10 rounded-full">
                              <span className="text-2xl">{reaction.emoji}</span>
                            </div>
                            <div className="flex flex-col">
                              <span className="text-sm text-white/50">
                                Assigns role:
                              </span>
                              <span className="text-white font-medium">
                                @{getRoleName(reaction.role_id)}
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRemoveReaction(reaction.emoji)}
                            className={`px-3 py-1.5 rounded text-sm transition-all ${
                              confirmDelete === reaction.emoji
                                ? "bg-red-500 text-white"
                                : "bg-white/5 text-white/70 hover:bg-red-500/20 hover:text-red-300"
                            }`}
                          >
                            {confirmDelete === reaction.emoji
                              ? "Confirm Remove"
                              : "Remove"}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Add New Reaction Form */}
                <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="relative">
                      <label className="block text-sm font-medium text-white/80 mb-1">
                        Select Emoji
                      </label>
                      <EmojiPicker
                        value={currentReactionRole.emoji}
                        onChange={(emoji: string) =>
                          setCurrentReactionRole({
                            ...currentReactionRole,
                            emoji,
                          })
                        }
                        placeholder="Choose an emoji..."
                        theme="purple"
                      />
                    </div>
                    <div className="relative">
                      <label className="block text-sm font-medium text-white/80 mb-1">
                        Select Role
                      </label>
                      <DiscordSelect
                        type="role"
                        guildId={serverId}
                        value={currentReactionRole.role_id}
                        onChange={(value: string | string[]) => {
                          const roleId = Array.isArray(value)
                            ? value[0]
                            : value;
                          setCurrentReactionRole({
                            ...currentReactionRole,
                            role_id: roleId,
                          });
                        }}
                        placeholder="Choose a role..."
                        theme="purple"
                      />
                    </div>
                  </div>
                  <button
                    onClick={handleAddReaction}
                    disabled={
                      !currentReactionRole.emoji || !currentReactionRole.role_id
                    }
                    className={`w-full mt-4 px-4 py-3 rounded-lg text-white font-medium transition-all flex items-center justify-center gap-2
                      ${
                        !currentReactionRole.emoji ||
                        !currentReactionRole.role_id
                          ? "bg-white/10 text-white/50 cursor-not-allowed"
                          : "bg-gradient-to-r from-purple-500 to-fuchsia-500 hover:opacity-90"
                      }`}
                  >
                    <i className="fas fa-plus"></i>
                    <span>Add Reaction Role</span>
                  </button>
                </div>
              </div>
            </SettingsSection>

            {/* Step 3: Settings */}
            <SettingsSection
              title="Step 3: Configure Settings"
              description="Set up behavior rules for your reaction roles"
              icon="fa-gear"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-300"
            >
              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/5">
                <div className="flex border-b border-white/10 mb-4">
                  <button
                    onClick={() => setActiveTab("basic")}
                    className={`px-4 py-2 font-medium text-sm transition-all ${
                      activeTab === "basic"
                        ? "text-purple-300 border-b-2 border-purple-400"
                        : "text-white/60 hover:text-white/80"
                    }`}
                  >
                    Basic Settings
                  </button>
                  <button
                    onClick={() => setActiveTab("advanced")}
                    className={`px-4 py-2 font-medium text-sm transition-all ${
                      activeTab === "advanced"
                        ? "text-purple-300 border-b-2 border-purple-400"
                        : "text-white/60 hover:text-white/80"
                    }`}
                  >
                    Advanced Settings
                  </button>
                </div>

                {activeTab === "basic" ? (
                  <div className="space-y-5">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-black/30 border border-white/5">
                      <div>
                        <h4 className="font-medium text-white/90">
                          Allow Users to Unselect
                        </h4>
                        <p className="text-sm text-white/60">
                          Users can remove reactions to lose the role
                        </p>
                      </div>
                      <ToggleSwitch
                        checked={settings.allow_unselect}
                        onChange={(value: boolean) =>
                          updateSettings("allow_unselect", value)
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-black/30 border border-white/5">
                      <div>
                        <h4 className="font-medium text-white/90">
                          Remove Reaction After Selection
                        </h4>
                        <p className="text-sm text-white/60">
                          Bot removes user's reaction after role is assigned
                        </p>
                      </div>
                      <ToggleSwitch
                        checked={settings.remove_reactions}
                        onChange={(value: boolean) =>
                          updateSettings("remove_reactions", value)
                        }
                      />
                    </div>

                    <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                      <h4 className="font-medium text-white/90 mb-2">
                        Max Roles Per User
                      </h4>
                      <p className="text-sm text-white/60 mb-3">
                        Limit how many reaction roles each user can select
                      </p>
                      <TextInput
                        type="number"
                        min="0"
                        value={
                          settings.max_reactions_per_user?.toString() || ""
                        }
                        onChange={(e) =>
                          updateSettings(
                            "max_reactions_per_user",
                            e.target.value ? parseInt(e.target.value) : null
                          )
                        }
                        placeholder="No limit"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-5">
                    <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                      <h4 className="font-medium text-white/90 mb-2">
                        Cooldown Period
                      </h4>
                      <p className="text-sm text-white/60 mb-3">
                        Time in seconds before a user can select another
                        reaction
                      </p>
                      <TextInput
                        type="number"
                        min="0"
                        value={settings.cooldown?.toString() || ""}
                        onChange={(e) =>
                          updateSettings(
                            "cooldown",
                            e.target.value ? parseInt(e.target.value) : null
                          )
                        }
                        placeholder="No cooldown"
                      />
                    </div>

                    <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                      <h4 className="font-medium text-white/90 mb-2">
                        Required Roles
                      </h4>
                      <p className="text-sm text-white/60 mb-3">
                        Users must have one of these roles to use the reactions
                      </p>
                      <DiscordSelect
                        type="role"
                        guildId={serverId}
                        value={settings.require_roles || []}
                        onChange={(value: string | string[]) => {
                          const roles = Array.isArray(value) ? value : [value];
                          updateSettings(
                            "require_roles",
                            roles.length ? roles : null
                          );
                        }}
                        placeholder="No required roles"
                        multiple={true}
                        theme="purple"
                      />
                    </div>

                    <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                      <h4 className="font-medium text-white/90 mb-2">
                        Forbidden Roles
                      </h4>
                      <p className="text-sm text-white/60 mb-3">
                        Users with these roles cannot use the reactions
                      </p>
                      <DiscordSelect
                        type="role"
                        guildId={serverId}
                        value={settings.forbidden_roles || []}
                        onChange={(value: string | string[]) => {
                          const roles = Array.isArray(value) ? value : [value];
                          updateSettings(
                            "forbidden_roles",
                            roles.length ? roles : null
                          );
                        }}
                        placeholder="No forbidden roles"
                        multiple={true}
                        theme="purple"
                      />
                    </div>
                  </div>
                )}
              </div>{" "}
              {/* Settings section ends here */}
            </SettingsSection>
          </div>
        </>
      )}
    </div>
  );
}
