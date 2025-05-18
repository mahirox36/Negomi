"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { useLayout } from "@/providers/LayoutProvider";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import toast from "react-hot-toast";
import SettingsSection from "@/components/dashboard/SettingsSection";
import DiscordSelect from "@/components/form/DiscordSelect";
import { useColorPickerRefs } from "@/hooks/useColorPickerRefs";
import ColorPicker from "@/components/form/ColorPicker";
import dynamic from "next/dynamic";

const EmojiPicker = dynamic(
  () =>
    import("emoji-picker-react").then((mod) => {
      const { Theme } = mod;
      return mod.default;
    }),
  { ssr: false }
);

interface EmbedAuthor {
  name: string;
  icon_url?: string;
  url?: string;
}

interface EmbedFooter {
  text: string;
  icon_url?: string;
}

interface EmbedField {
  name: string;
  value: string;
  inline?: boolean;
}

interface EmbedData {
  title?: string;
  description?: string;
  color?: string;
  footer?: EmbedFooter;
  thumbnail?: { url: string };
  image?: { url: string };
  author?: EmbedAuthor;
  fields?: EmbedField[];
  timestamp?: string;
}

interface Message {
  id?: string;
  name: string;
  content: string;
  channel_id: string;
  embeds: EmbedData[];
  createdAt?: string;
  message_id?: string;
}

const defaultEmbed: EmbedData = {
  title: "",
  description: "",
  color: "#5865F2",
  fields: [],
};

const availableVariables = [
  { label: "Server Name", value: "{server}" },
  { label: "Channel Mention", value: "{channel}" },
  { label: "Member Count", value: "{memberCount}" },
  { label: "Current Date", value: "{date}" },
  { label: "Current Time", value: "{time}" },
];

export default function MessageEditorPage() {
  const params = useParams();
  const router = useRouter();
  const serverId = params.id as string;
  const messageId = params.messageId as string;
  const isNewMessage = messageId === "new";
  const { setCurrentPath, setServerId } = useLayout();
  
  const [message, setMessage] = useState<Message>({
    name: "",
    content: "",
    channel_id: "",
    embeds: [],
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showEmojiPickerIndex, setShowEmojiPickerIndex] = useState<number>(-1);
  const [previewMode, setPreviewMode] = useState<"desktop" | "mobile">(
    "desktop"
  );
  const [botAvatar, setBotAvatar] = useState<string | null>(null);
  const [botDisplayName, setBotDisplayName] = useState<string>("Negomi");
  const [colorPickerOpen, setColorPickerOpen] = useState<string | null>(null);
  const { getRef } = useColorPickerRefs();

  const emojiPickerRef = useRef<HTMLDivElement>(null);

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1 },
  };

  useEffect(() => {
    setCurrentPath("messages");
    setServerId(serverId);

    if (!isNewMessage) {
      fetchMessage();
    } else {
      setIsLoading(false);
    }

    fetchBotInfo();
  }, [serverId, messageId, setCurrentPath, setServerId]);

  const fetchBotInfo = async () => {
    try {
      const response = await axios.get("/api/v1/bot/pfp_url");
      setBotAvatar(response.data.pfp_url);
    } catch (error) {
      console.error("Failed to fetch bot avatar:", error);
    }
  };

  const fetchMessage = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(
        `/api/v1/guilds/${serverId}/messages/${messageId}`,
        {
          withCredentials: true,
        }
      );

      // Ensure the message has the necessary properties
      const fetchedMessage = response.data;
      fetchedMessage.embeds = fetchedMessage.embeds || [];

      setMessage(fetchedMessage);
    } catch (error) {
      console.error("Failed to fetch message:", error);
      toast.error("Failed to load message");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!message.channel_id) {
      toast.error("Please select a channel before saving.");
      return;
    }

    setIsSaving(true);
    try {
      if (isNewMessage) {
        await axios.post(
          `/api/v1/guilds/${serverId}/messages/create`,
          message,
          {
            withCredentials: true,
          }
        );
        toast.success("Message created successfully");
      } else {
        await axios.put(
          `/api/v1/guilds/${serverId}/messages/${messageId}`,
          message,
          {
            withCredentials: true,
          }
        );
        toast.success("Message updated successfully");
      }
      router.push(`/dashboard/server/${serverId}/messages`);
    } catch (error) {
      console.error("Failed to save message:", error);
      toast.error("Failed to save message");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddEmbed = () => {
    setMessage((prev) => ({
      ...prev,
      embeds: [...prev.embeds, { ...defaultEmbed }],
    }));
  };

  const handleRemoveEmbed = (index: number) => {
    setMessage((prev) => ({
      ...prev,
      embeds: prev.embeds.filter((_, i) => i !== index),
    }));
  };

  const handleUpdateEmbed = (index: number, embed: EmbedData) => {
    const newEmbeds = [...message.embeds];
    newEmbeds[index] = embed;
    setMessage({ ...message, embeds: newEmbeds });
  };

  const handleAddField = (embedIndex: number) => {
    const newEmbeds = [...message.embeds];
    const currentEmbed = { ...newEmbeds[embedIndex] };
    currentEmbed.fields = [
      ...(currentEmbed.fields || []),
      { name: "", value: "", inline: false },
    ];
    newEmbeds[embedIndex] = currentEmbed;
    setMessage({ ...message, embeds: newEmbeds });
  };

  const handleToggleColorPicker = (index: number) => {
    const key = `embed-${index}`;
    setColorPickerOpen(colorPickerOpen === key ? null : key);
  };

  const onEmojiClick = (emoji: { emoji: string }) => {
    if (showEmojiPickerIndex >= 0) {
      const embed = message.embeds[showEmojiPickerIndex];
      setMessage({
        ...message,
        embeds: message.embeds.map((e, i) =>
          i === showEmojiPickerIndex
            ? { ...embed, description: (embed.description || "") + emoji.emoji }
            : e
        ),
      });
    } else {
      setMessage({
        ...message,
        content: message.content + emoji.emoji,
      });
    }
    setShowEmojiPickerIndex(-1);
    setShowEmojiPicker(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Header Section */}
      <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
              <i className="fas fa-edit text-2xl text-white/90"></i>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
                {isNewMessage ? "Create New Message" : "Edit Message"}
              </h1>
              <p className="text-lg text-white/70 mt-1">
                {isNewMessage
                  ? "Create a custom message with rich embeds"
                  : `Editing message: ${message.name}`}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.back()}
              className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white"
            >
              Cancel
            </button>
            <button
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 transition-all text-white"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? (
                <span className="flex items-center gap-2">
                  <div className="animate-spin h-4 w-4 border-2 border-white/60 border-t-transparent rounded-full"></div>
                  Saving...
                </span>
              ) : (
                "Save Message"
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 p-6 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Message Editor Section */}
          <div className="space-y-6">
            <SettingsSection
              title="Message Editor"
              description="Create or edit your message"
              icon="fa-pen"
              iconBgColor="bg-indigo-500/20"
              iconColor="text-indigo-300"
            >
              {/* Message Editor Content */}
              <div className="space-y-4">
                <input
                  type="text"
                  className="w-full px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                  placeholder="Message Name"
                  value={message.name}
                  onChange={(e) =>
                    setMessage({
                      ...message,
                      name: e.target.value,
                    })
                  }
                />{" "}
                <DiscordSelect
                  type="channel"
                  guildId={serverId}
                  value={message.channel_id}
                  onChange={(value) =>
                    setMessage({
                      ...message,
                      channel_id: Array.isArray(value) ? value[0] : value,
                    })
                  }
                  placeholder="Select a channel..."
                  multiple={false}
                  searchable={true}
                  theme="purple"
                />
                <div className="relative">
                  <textarea
                    className="w-full p-4 rounded-lg border border-white/10 bg-white/5 text-white min-h-[100px]"
                    value={message.content}
                    onChange={(e) =>
                      setMessage({
                        ...message,
                        content: e.target.value,
                      })
                    }
                    placeholder="Write your message content here..."
                  />
                  <div className="absolute bottom-2 right-2 flex gap-2">
                    <button
                      onClick={() => {
                        setShowEmojiPicker(!showEmojiPicker);
                        setShowEmojiPickerIndex(-1);
                      }}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                      <i className="fas fa-smile text-white/70"></i>
                    </button>
                    {showEmojiPicker && (
                      <div
                        ref={emojiPickerRef}
                        className="absolute bottom-full right-0 mb-2 z-50"
                      >
                        <EmojiPicker onEmojiClick={onEmojiClick} />
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {availableVariables.map((variable) => (
                    <button
                      key={variable.value}
                      onClick={() =>
                        setMessage({
                          ...message,
                          content: message.content + " " + variable.value,
                        })
                      }
                      className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/70 text-sm"
                    >
                      {variable.label}
                    </button>
                  ))}
                </div>
              </div>
            </SettingsSection>

            {/* Embed Editor Section */}
            <SettingsSection
              title="Embed Editor"
              description="Create rich embeds for your message"
              icon="fa-cube"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-300"
            >
              {/* Embed Editor Content */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-white">Embeds</h3>
                  <button
                    onClick={handleAddEmbed}
                    className="px-4 py-2 rounded-lg bg-purple-500 hover:bg-purple-600 transition-colors text-white"
                    disabled={message.embeds?.length >= 10}
                  >
                    Add Embed
                  </button>
                </div>

                {message.embeds?.map((embed, index) => (
                  <motion.div
                    key={index}
                    variants={cardVariants}
                    initial="hidden"
                    animate="visible"
                    className="p-4 rounded-lg border border-white/10 bg-white/5"
                  >
                    <div className="flex justify-between items-center mb-4">
                      <h4 className="text-white/90">Embed {index + 1}</h4>
                      <button
                        onClick={() => handleRemoveEmbed(index)}
                        className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 transition-colors"
                      >
                        <i className="fas fa-trash text-red-400"></i>
                      </button>
                    </div>

                    <div className="space-y-4">
                      <input
                        type="text"
                        className="w-full px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                        placeholder="Embed Title"
                        value={embed.title || ""}
                        onChange={(e) =>
                          handleUpdateEmbed(index, {
                            ...embed,
                            title: e.target.value,
                          })
                        }
                      />
                      <div className="flex items-center justify-between">
                        <label className="text-white/70">Embed Color</label>
                        <ColorPicker
                          color={embed.color || "#5865F2"}
                          onChange={(color) =>
                            handleUpdateEmbed(index, { ...embed, color })
                          }
                          ref={getRef(`embed-${index}`)}
                          isOpen={colorPickerOpen === `embed-${index}`}
                          onToggle={() => handleToggleColorPicker(index)}
                        />
                      </div>
                      <div className="relative">
                        <textarea
                          className="w-full p-4 rounded-lg border border-white/10 bg-white/5 text-white min-h-[100px]"
                          placeholder="Embed Description"
                          value={embed.description || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              description: e.target.value,
                            })
                          }
                        />
                        <div className="absolute bottom-2 right-2">
                          <button
                            onClick={() => {
                              setShowEmojiPicker(!showEmojiPicker);
                              setShowEmojiPickerIndex(index);
                            }}
                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                          >
                            <i className="fas fa-smile text-white/70"></i>
                          </button>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <input
                          type="text"
                          className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                          placeholder="Author Name"
                          value={embed.author?.name || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              author: embed.author
                                ? {
                                    ...embed.author,
                                    name: e.target.value,
                                  }
                                : { name: e.target.value },
                            })
                          }
                        />
                        <input
                          type="text"
                          className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                          placeholder="Author Icon URL"
                          value={embed.author?.icon_url || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              author: embed.author
                                ? {
                                    ...embed.author,
                                    icon_url: e.target.value,
                                  }
                                : { name: "", icon_url: e.target.value },
                            })
                          }
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <input
                          type="text"
                          className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                          placeholder="Footer Text"
                          value={embed.footer?.text || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              footer: embed.footer
                                ? {
                                    ...embed.footer,
                                    text: e.target.value,
                                  }
                                : { text: e.target.value },
                            })
                          }
                        />
                        <input
                          type="text"
                          className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                          placeholder="Footer Icon URL"
                          value={embed.footer?.icon_url || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              footer: embed.footer
                                ? {
                                    ...embed.footer,
                                    icon_url: e.target.value,
                                  }
                                : { text: "", icon_url: e.target.value },
                            })
                          }
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <input
                          type="text"
                          className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                          placeholder="Thumbnail URL"
                          value={embed.thumbnail?.url || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              thumbnail: { url: e.target.value },
                            })
                          }
                        />
                        <input
                          type="text"
                          className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                          placeholder="Image URL"
                          value={embed.image?.url || ""}
                          onChange={(e) =>
                            handleUpdateEmbed(index, {
                              ...embed,
                              image: { url: e.target.value },
                            })
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <h4 className="text-white/90">Fields</h4>
                          <button
                            onClick={() => handleAddField(index)}
                            className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/70"
                          >
                            Add Field
                          </button>
                        </div>

                        {embed.fields?.map((field, fieldIndex) => (
                          <motion.div
                            key={fieldIndex}
                            variants={cardVariants}
                            initial="hidden"
                            animate="visible"
                            className="grid grid-cols-2 gap-4 p-4 rounded-lg border border-white/10 bg-white/5"
                          >
                            <input
                              type="text"
                              className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                              placeholder="Field Name"
                              value={field.name}
                              onChange={(e) => {
                                const newFields = [...(embed.fields || [])];
                                newFields[fieldIndex] = {
                                  ...field,
                                  name: e.target.value,
                                };
                                handleUpdateEmbed(index, {
                                  ...embed,
                                  fields: newFields,
                                });
                              }}
                            />
                            <input
                              type="text"
                              className="px-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white"
                              placeholder="Field Value"
                              value={field.value}
                              onChange={(e) => {
                                const newFields = [...(embed.fields || [])];
                                newFields[fieldIndex] = {
                                  ...field,
                                  value: e.target.value,
                                };
                                handleUpdateEmbed(index, {
                                  ...embed,
                                  fields: newFields,
                                });
                              }}
                            />
                            <div className="col-span-2 flex items-center justify-between">
                              <label className="flex items-center gap-2 text-white/70">
                                <input
                                  type="checkbox"
                                  checked={field.inline}
                                  onChange={(e) => {
                                    const newFields = [...(embed.fields || [])];
                                    newFields[fieldIndex] = {
                                      ...field,
                                      inline: e.target.checked,
                                    };
                                    handleUpdateEmbed(index, {
                                      ...embed,
                                      fields: newFields,
                                    });
                                  }}
                                  className="rounded border-white/10 bg-white/5"
                                />
                                Inline
                              </label>
                              <button
                                onClick={() => {
                                  const newFields = embed.fields?.filter(
                                    (_, i) => i !== fieldIndex
                                  );
                                  handleUpdateEmbed(index, {
                                    ...embed,
                                    fields: newFields,
                                  });
                                }}
                                className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 transition-colors"
                              >
                                <i className="fas fa-times text-red-400"></i>
                              </button>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </SettingsSection>
          </div>

          {/* Preview Section */}
          <div className="space-y-6">
            <SettingsSection
              title="Live Preview"
              description="See how your message will look"
              icon="fa-eye"
              iconBgColor="bg-emerald-500/20"
              iconColor="text-emerald-300"
            >
              <div className="space-y-4">
                <div className="flex justify-end gap-2 mb-4">
                  <button
                    onClick={() => setPreviewMode("desktop")}
                    className={`p-2 rounded-lg transition-colors ${
                      previewMode === "desktop"
                        ? "bg-purple-500 text-white"
                        : "bg-white/5 text-white/70 hover:bg-white/10"
                    }`}
                  >
                    <i className="fas fa-desktop"></i>
                  </button>
                  <button
                    onClick={() => setPreviewMode("mobile")}
                    className={`p-2 rounded-lg transition-colors ${
                      previewMode === "mobile"
                        ? "bg-purple-500 text-white"
                        : "bg-white/5 text-white/70 hover:bg-white/10"
                    }`}
                  >
                    <i className="fas fa-mobile-alt"></i>
                  </button>
                </div>

                <div
                  className={`discord-message-preview ${
                    previewMode === "mobile" ? "max-w-[300px]" : ""
                  } mx-auto`}
                >
                  <div className="bg-[#323339] rounded-lg p-4 space-y-2">
                    <div className="flex items-center gap-3 mb-2">
                      {botAvatar && (
                        <img
                          src={botAvatar}
                          alt="Bot Avatar"
                          className="w-10 h-10 rounded-full"
                        />
                      )}
                      <span className="font-medium text-white">
                        {botDisplayName}
                      </span>
                    </div>
                    {message.content && (
                      <p className="text-white/90 whitespace-pre-wrap">
                        {message.content}
                      </p>
                    )}

                    {message.embeds?.map((embed, index) => (
                      <div
                        key={index}
                        className="border-l-4 rounded bg-[#2f3136] p-4 mt-2 relative"
                        style={{ borderColor: embed.color || "#5865F2" }}
                      >
                        {embed.thumbnail?.url && (
                          <div className="absolute top-4 right-4 max-w-[80px]">
                            <img
                              src={embed.thumbnail.url}
                              alt=""
                              className="w-full h-auto rounded"
                            />
                          </div>
                        )}

                        {embed.author && (
                          <div className="flex items-center gap-2 mb-2">
                            {embed.author.icon_url && (
                              <img
                                src={embed.author.icon_url}
                                alt=""
                                className="w-6 h-6 rounded-full"
                              />
                            )}
                            <span className="text-white font-semibold">
                              {embed.author.name}
                            </span>
                          </div>
                        )}

                        {embed.title && (
                          <div className="font-bold text-white mb-2">
                            {embed.title}
                          </div>
                        )}

                        {embed.description && (
                          <div className="text-white/90 whitespace-pre-wrap mb-2">
                            {embed.description}
                          </div>
                        )}

                        {embed.fields && embed.fields.length > 0 && (
                          <div className="grid grid-cols-2 gap-4 my-2">
                            {embed.fields.map((field, fieldIndex) => (
                              <div
                                key={fieldIndex}
                                className={
                                  field.inline ? "col-span-1" : "col-span-2"
                                }
                              >
                                <div className="font-semibold text-white">
                                  {field.name}
                                </div>
                                <div className="text-white/70">
                                  {field.value}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {embed.image?.url && (
                          <div className="mt-2">
                            <img
                              src={embed.image.url}
                              alt=""
                              className="max-w-full rounded"
                            />
                          </div>
                        )}

                        {embed.footer && (
                          <div className="flex items-center gap-2 mt-2 text-white/60 text-sm">
                            {embed.footer.icon_url && (
                              <img
                                src={embed.footer.icon_url}
                                alt=""
                                className="w-5 h-5 rounded-full"
                              />
                            )}
                            <span>{embed.footer.text}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </SettingsSection>

            <SettingsSection
              title="Message Information"
              description="Additional details and tips"
              icon="fa-info-circle"
              iconBgColor="bg-blue-500/20"
              iconColor="text-blue-300"
            >
              <div className="space-y-4">
                {!isNewMessage && message.message_id && (
                  <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-4">
                  <h4 className="text-yellow-300 font-medium mb-2">Editing Linked Message</h4>
                  <p className="text-white/80">
                    This message is linked to an existing Discord message (<span className="font-mono">{message.message_id}</span>).
                    <br />
                    <span className="text-yellow-200 font-semibold">When you save, the original message will be updated in Discord.</span>
                  </p>
                  </div>
                )}
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-2">
                    Available Variables
                  </h4>
                  <ul className="list-disc pl-5 text-white/70 space-y-1">
                    <li>{"{server}"} - Displays the server name</li>
                    <li>{"{channel}"} - Mentions the current channel</li>
                    <li>{"{memberCount}"} - Shows the total server members</li>
                    <li>{"{date}"} - Current date</li>
                    <li>{"{time}"} - Current time</li>
                  </ul>
                </div>

                <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-2">
                    Tips for Great Embeds
                  </h4>
                  <ul className="list-disc pl-5 text-white/70 space-y-1">
                    <li>Use clear, concise titles</li>
                    <li>Choose colors that match your server's theme</li>
                    <li>Add relevant images to enhance visual appeal</li>
                    <li>Keep fields organized and easy to read</li>
                  </ul>
                </div>
              </div>
            </SettingsSection>
          </div>
        </div>
      </div>

      {/* Emoji Picker Portal */}
      {showEmojiPickerIndex !== -1 && (
        <div className="fixed bottom-4 right-4 z-50">
          <div className="bg-gray-900/95 p-4 rounded-lg border border-white/10 shadow-xl backdrop-blur-lg">
            <div className="flex justify-between items-center mb-2 border-b border-white/10 pb-2">
              <h4 className="text-white font-medium">
                Add Emoji to {showEmojiPickerIndex >= 0 ? "Embed" : "Message"}
              </h4>
              <button
                onClick={() => setShowEmojiPickerIndex(-1)}
                className="p-1 hover:bg-white/10 rounded-full"
              >
                <i className="fas fa-times text-white/70"></i>
              </button>
            </div>
            <EmojiPicker onEmojiClick={onEmojiClick} />
          </div>
        </div>
      )}
    </motion.div>
  );
}
