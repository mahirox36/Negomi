"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, useCallback, useRef } from "react";
import { useLayout } from "@/providers/LayoutProvider";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
import axios from "axios";
import toast from "react-hot-toast";
import Link from "next/link";

const EmojiPicker = dynamic(
  () =>
    import("emoji-picker-react").then((mod) => {
      const { Theme } = mod;
      return mod.default;
    }),
  { ssr: false }
);

interface Message {
  id: string;
  name: string;
  content: string;
  channel_id: string;
  embeds: EmbedData[];
  created_at: string;
  message_id?: string;
}

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

export default function MessagesPage() {
  const params = useParams();
  const router = useRouter();
  const serverId = params.id as string;
  const { setHasChanges, setCurrentPath, setServerId } = useLayout();

  const [messages, setMessages] = useState<Message[]>([]);
  const [filteredMessages, setFilteredMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(
    null
  );
  const [sortOrder, setSortOrder] = useState<
    "newest" | "oldest" | "alphabetical"
  >("newest");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  const hasInitialFetch = useRef(false);

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.3 } },
  };

  const listItemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: (i: number) => ({
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.3,
        delay: i * 0.05,
      },
    }),
    exit: { opacity: 0, x: 20, transition: { duration: 0.2 } },
  };

  const staggerContainerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.06,
      },
    },
  };

  const fetchMessages = useCallback(async () => {
    if (!serverId) return;
    try {
      setIsLoading(true);
      const response = await axios.get(`/api/v1/guilds/${serverId}/messages`, {
        withCredentials: true,
      });
      setMessages(response.data || []);
      setFilteredMessages(response.data || []);
      hasInitialFetch.current = true;
    } catch (error) {
      console.error("Failed to fetch messages:", error);
      toast.error("Failed to load messages");
    } finally {
      setIsLoading(false);
    }
  }, [serverId]);

  const handleDeleteMessage = async (id: string) => {
    if (!serverId) return;
    setIsDeleting(id);
    try {
      await axios.delete(`/api/v1/guilds/${serverId}/messages/${id}`, {
        withCredentials: true,
      });
      toast.success("Message deleted successfully");
      fetchMessages();
      setShowDeleteConfirm(null);
    } catch (error) {
      console.error("Failed to delete message:", error);
      toast.error("Failed to delete message");
    } finally {
      setIsDeleting(null);
    }
  };

  const handleSendMessage = async (id: string) => {
    if (!serverId) return;
    try {
      await axios.post(
        `/api/v1/guilds/${serverId}/messages/${id}/send`,
        {},
        {
          withCredentials: true,
        }
      );
      toast.success("Message sent successfully");
      fetchMessages();
    } catch (error) {
      console.error("Failed to send message:", error);
      toast.error("Failed to send message");
    }
  };

  // Search and sort functions
  useEffect(() => {
    if (!messages.length) return;

    let result = [...messages];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (msg) =>
          msg.name.toLowerCase().includes(query) ||
          msg.content.toLowerCase().includes(query) ||
          msg.embeds.some(
            (embed) =>
              (embed.title?.toLowerCase() || "").includes(query) ||
              (embed.description?.toLowerCase() || "").includes(query)
          )
      );
    }

    // Apply sorting
    if (sortOrder === "newest") {
      result.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    } else if (sortOrder === "oldest") {
      result.sort(
        (a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
    } else if (sortOrder === "alphabetical") {
      result.sort((a, b) => a.name.localeCompare(b.name));
    }

    setFilteredMessages(result);
  }, [messages, searchQuery, sortOrder]);

  useEffect(() => {
    if (!serverId || hasInitialFetch.current) return;
    setCurrentPath("messages");
    setServerId(serverId);
    fetchMessages();
    return () => {
      hasInitialFetch.current = false;
    };
  }, [serverId, fetchMessages, setCurrentPath, setServerId]);

  // Format date function
  const formatDate = (dateString: string): string => {
    if (!dateString) return "N/A";

    try {
      const date = new Date(dateString);

      // Check if date is valid
      if (isNaN(date.getTime())) {
        return "Invalid date";
      }

      return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    } catch (error) {
      console.error("Date formatting error:", error);
      return "Invalid date";
    }
  };

  // truncate text
  const truncateText = (text: string, maxLength: number): string => {
    if (!text) return "";
    return text.length > maxLength
      ? text.substring(0, maxLength) + "..."
      : text;
  };

  // Get channel name
  const getChannelName = (message: Message): string => {
    const channelId = message.channel_id;
    if (!channelId) return "No channel set";
    return `#${channelId}`;
  };

  // Get embed color
  const getEmbedColor = (message: Message): string => {
    if (!message.embeds || !message.embeds.length) return "#5865F2";
    return message.embeds[0].color || "#5865F2";
  };

  // Get embed count
  const getEmbedCount = (message: Message): number => {
    return message.embeds?.length || 0;
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
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
              <i className="fas fa-envelope text-2xl text-white/90"></i>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
                Message Manager
              </h1>
              <p className="text-lg text-white/70 mt-1">
                Create and manage custom messages with rich embeds
              </p>
            </div>
          </div>
          <button
            onClick={() =>
              router.push(`/dashboard/server/${serverId}/messages/new`)
            }
            className="px-5 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 transition-all text-white font-medium flex items-center gap-2 shadow-lg shadow-indigo-500/20"
          >
            <i className="fas fa-plus"></i>
            Create New Message
          </button>
        </div>
      </div>
      {/* Search and Filter Bar */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-lg border border-white/10 bg-white/5 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50">
              <i className="fas fa-search"></i>
            </div>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 hover:text-white/80"
              >
                <i className="fas fa-times"></i>
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-white/5 border border-white/10 rounded-lg p-1 flex items-center">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === "grid"
                    ? "bg-purple-500 text-white"
                    : "text-white/70 hover:bg-white/10"
                }`}
              >
                <i className="fas fa-th-large"></i>
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === "list"
                    ? "bg-purple-500 text-white"
                    : "text-white/70 hover:bg-white/10"
                }`}
              >
                <i className="fas fa-list"></i>
              </button>
            </div>            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as any)}
              className="bg-black/60 border border-black/80 rounded-lg px-4 py-2 text-white font-normal focus:outline-none focus:ring-2 focus:ring-purple-500"
              style={{ 
                fontFamily: "inherit",
              }}
            >
              <option value="newest" style={{fontFamily: "inherit"}}>Newest first</option>
              <option value="oldest" style={{fontFamily: "inherit"}}>Oldest first</option>
              <option value="alphabetical" style={{fontFamily: "inherit"}}>Alphabetical</option>
            </select>
          </div>
        </div>
      </div>{" "}
      {/* Messages List */}
      <AnimatePresence mode="wait">
        {filteredMessages.length > 0 ? (
          viewMode === "grid" ? (
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
              key="grid-view"
              variants={staggerContainerVariants}
              initial="hidden"
              animate="visible"
            >
              {filteredMessages.map((message, index) => (
                <motion.div
                  key={message.id}
                  custom={index}
                  variants={cardVariants}
                  className="group relative bg-gradient-to-br from-white/10 to-white/5 overflow-hidden rounded-xl border border-white/10 hover:border-purple-500/40 transition-all hover:shadow-xl hover:shadow-purple-500/20 backdrop-blur-sm"
                  whileHover={{ y: -5, transition: { duration: 0.2 } }}
                >
                  {/* Color indicator */}
                  <div
                    className="absolute inset-0 opacity-10 rounded-xl"
                    style={{
                      backgroundColor: getEmbedColor(message),
                      filter: "blur(20px)",
                    }}
                  ></div>

                  <div
                    className="h-2 relative z-10"
                    style={{ backgroundColor: getEmbedColor(message) }}
                  ></div>

                  <div className="p-6 space-y-4 relative z-10">
                    <div className="flex justify-between items-start">
                      <h3 className="text-xl font-bold text-white truncate bg-gradient-to-r from-white to-white/80 bg-clip-text">
                        {message.name || "Untitled Message"}
                      </h3>
                      {getEmbedCount(message) > 0 && (
                        <span
                          className="ml-2 flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium"
                          style={{
                            backgroundColor: `${getEmbedColor(message)}30`,
                            color: getEmbedColor(message),
                          }}
                        >
                          <i className="fas fa-layer-group text-xs"></i>
                          {getEmbedCount(message)}
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-4">
                      <div className="flex items-center gap-2 text-white/60 text-sm">
                        <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center">
                          <i className="fas fa-calendar-alt text-xs"></i>
                        </div>
                        <span>{formatDate(message.created_at)}</span>
                      </div>

                      <div className="flex items-center gap-2 text-white/60 text-sm">
                        <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center">
                          <i className="fas fa-hashtag text-xs"></i>
                        </div>
                        <span className="truncate">
                          {getChannelName(message)}
                        </span>
                      </div>
                    </div>

                    <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                      <p className="text-white/80 line-clamp-2">
                        {message.content || (
                          <span className="italic text-white/40">
                            No content
                          </span>
                        )}
                      </p>
                    </div>

                    {message.embeds && message.embeds.length > 0 && (
                      <div className="flex gap-2 overflow-x-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent py-1">
                        {message.embeds.map((embed, i) => (
                          <div
                            key={i}
                            className="flex-shrink-0 w-8 h-8 rounded-md border-l-2"
                            style={{
                              backgroundColor: "rgba(47, 49, 54, 0.6)",
                              borderLeftColor: embed.color || "#5865F2",
                            }}
                          ></div>
                        ))}
                      </div>
                    )}

                    <div className="relative">
                      {/* Glowing action buttons */}
                      <div className="absolute -inset-x-6 -bottom-6 h-12 bg-gradient-to-t from-black/40 to-transparent rounded-b-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>

                      <div className="flex items-center justify-between border-t border-white/10 pt-4 relative z-10">
                        <div className="flex items-center gap-2">
                          <Link
                            href={`/dashboard/server/${serverId}/messages/${message.id}`}
                            className="p-2 rounded-lg bg-white/5 hover:bg-indigo-500/30 transition-all text-white/70 hover:text-indigo-300 hover:scale-110"
                          >
                            <i className="fas fa-edit"></i>
                          </Link>
                          <button
                            onClick={() => handleSendMessage(message.id)}
                            className="p-2 rounded-lg bg-white/5 hover:bg-green-500/30 transition-all text-white/70 hover:text-green-300 hover:scale-110"
                          >
                            <i className="fas fa-paper-plane"></i>
                          </button>
                        </div>

                        {showDeleteConfirm === message.id ? (
                          <div className="flex items-center gap-1 bg-black/30 backdrop-blur-sm rounded-lg p-1">
                            <button
                              onClick={() => setShowDeleteConfirm(null)}
                              className="text-xs px-3 py-1 rounded-md bg-white/10 text-white/80 hover:bg-white/20"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleDeleteMessage(message.id)}
                              className="text-xs px-3 py-1 rounded-md bg-red-500/20 text-red-300 hover:bg-red-500/40 flex items-center gap-2"
                              disabled={isDeleting === message.id}
                            >
                              {isDeleting === message.id ? (
                                <>
                                  <div className="w-3 h-3 border-t-2 border-r-2 border-red-300 rounded-full animate-spin"></div>
                                  <span>Deleting...</span>
                                </>
                              ) : (
                                <>
                                  <i className="fas fa-check-circle"></i>
                                  <span>Confirm</span>
                                </>
                              )}
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setShowDeleteConfirm(message.id)}
                            className="p-2 rounded-lg bg-white/5 hover:bg-red-500/30 transition-all text-white/70 hover:text-red-300 hover:scale-110"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <motion.div
              className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 overflow-hidden backdrop-blur-sm shadow-xl"
              key="list-view"
              variants={staggerContainerVariants}
              initial="hidden"
              animate="visible"
            >
              <div className="bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-b border-white/10 px-6 py-4 grid grid-cols-12 gap-4">
                <div className="col-span-5 font-semibold text-white flex items-center gap-2">
                  <i className="fas fa-file-alt text-purple-300"></i>
                  Message Name
                </div>
                <div className="col-span-2 font-semibold text-white flex items-center gap-2">
                  <i className="fas fa-hashtag text-indigo-300"></i>
                  Channel
                </div>
                <div className="col-span-3 font-semibold text-white flex items-center gap-2">
                  <i className="fas fa-calendar text-blue-300"></i>
                  Created
                </div>
                <div className="col-span-2 font-semibold text-white text-right">
                  Actions
                </div>
              </div>

              {filteredMessages.map((message, index) => (
                <motion.div
                  key={message.id}
                  custom={index}
                  variants={listItemVariants}
                  className="group px-6 py-4 border-b border-white/5 hover:bg-gradient-to-r hover:from-indigo-500/5 hover:to-purple-500/5 transition-all grid grid-cols-12 gap-4 items-center"
                  whileHover={{ backgroundColor: "rgba(255, 255, 255, 0.05)" }}
                >
                  <div className="col-span-5 flex items-center gap-3">
                    <div
                      className="w-2 h-10 rounded-full shadow-sm shadow-purple-500/20"
                      style={{ backgroundColor: getEmbedColor(message) }}
                    ></div>
                    <div className="flex-grow">
                      <h3 className="font-medium text-white group-hover:text-indigo-200 transition-colors">
                        {message.name || "Untitled Message"}
                      </h3>
                      <p className="text-xs text-white/50 truncate max-w-xs">
                        {truncateText(message.content, 60)}
                      </p>
                    </div>
                    {getEmbedCount(message) > 0 && (
                      <div
                        className="ml-2 flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: `${getEmbedColor(message)}20`,
                          color: getEmbedColor(message),
                        }}
                      >
                        <i className="fas fa-layer-group text-xs"></i>
                        <span className="hidden sm:inline">
                          {getEmbedCount(message)} embed
                          {getEmbedCount(message) !== 1 && "s"}
                        </span>
                        <span className="sm:hidden">
                          {getEmbedCount(message)}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="col-span-2 text-white/70 truncate flex items-center gap-2">
                    <div className="w-5 h-5 rounded bg-white/5 flex items-center justify-center text-xs">
                      <i className="fas fa-hashtag"></i>
                    </div>
                    <span>{getChannelName(message)}</span>
                  </div>

                  <div className="col-span-3 text-white/70 text-sm flex items-center gap-2">
                    <div className="w-5 h-5 rounded bg-white/5 flex items-center justify-center text-xs">
                      <i className="fas fa-clock"></i>
                    </div>
                    <span>{formatDate(message.created_at)}</span>
                  </div>

                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <Link
                      href={`/dashboard/server/${serverId}/messages/${message.id}`}
                      className="p-2 rounded-lg bg-white/5 hover:bg-indigo-500/30 transition-all text-white/70 hover:text-indigo-300 hover:scale-105"
                    >
                      <i className="fas fa-edit"></i>
                    </Link>
                    <button
                      onClick={() => handleSendMessage(message.id)}
                      className="p-2 rounded-lg bg-white/5 hover:bg-green-500/30 transition-all text-white/70 hover:text-green-300 hover:scale-105"
                      title="Send message"
                    >
                      <i className="fas fa-paper-plane"></i>
                    </button>

                    {showDeleteConfirm === message.id ? (
                      <div className="flex items-center gap-1 ml-1 bg-gray-900/50 backdrop-blur-sm p-1 rounded-lg">
                        <button
                          onClick={() => setShowDeleteConfirm(null)}
                          className="text-xs px-2 py-1 rounded bg-white/10 text-white/80 hover:bg-white/20"
                        >
                          <i className="fas fa-times mr-1"></i>
                          <span className="hidden sm:inline">Cancel</span>
                        </button>
                        <button
                          onClick={() => handleDeleteMessage(message.id)}
                          className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-300 hover:bg-red-500/40 flex items-center gap-1"
                          disabled={isDeleting === message.id}
                        >
                          {isDeleting === message.id ? (
                            <>
                              <div className="w-3 h-3 border-t-2 border-r-2 border-red-300 rounded-full animate-spin"></div>
                              <span className="hidden sm:inline">
                                Deleting...
                              </span>
                            </>
                          ) : (
                            <>
                              <i className="fas fa-check-circle"></i>
                              <span className="hidden sm:inline">Confirm</span>
                            </>
                          )}
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setShowDeleteConfirm(message.id)}
                        className="p-2 rounded-lg bg-white/5 hover:bg-red-500/30 transition-all text-white/70 hover:text-red-300 hover:scale-105"
                        title="Delete message"
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )
        ) : (
          <motion.div
            key="empty-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 p-12 flex flex-col items-center justify-center text-center"
          >
            <div className="relative mb-10">
              <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl"></div>
              <div className="w-28 h-28 rounded-full bg-gradient-to-br from-indigo-500/40 to-purple-500/40 flex items-center justify-center relative">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-400/20 to-purple-400/20 flex items-center justify-center animate-pulse">
                  <i className="fas fa-envelope-open text-5xl text-white/80"></i>
                </div>
              </div>
            </div>
            <h3 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-white to-indigo-200 bg-clip-text text-transparent mb-3">
              {searchQuery ? "No matches found" : "Your message canvas awaits"}
            </h3>
            <p className="text-white/60 max-w-md mb-10 text-lg">
              {searchQuery ? (
                <>
                  No messages matching{" "}
                  <span className="text-indigo-300 font-medium">
                    "{searchQuery}"
                  </span>{" "}
                  were found. Try a different search term.
                </>
              ) : (
                "Create your first custom message with beautiful embeds to share with your server members."
              )}
            </p>
            <button
              onClick={() => {
                if (searchQuery) {
                  setSearchQuery("");
                } else {
                  router.push(`/dashboard/server/${serverId}/messages/new`);
                }
              }}
              className="px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 transition-all text-white font-medium flex items-center gap-2 shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40"
            >
              {searchQuery ? (
                <>
                  <i className="fas fa-search"></i>
                  Clear Search
                </>
              ) : (
                <>
                  <i className="fas fa-plus"></i>
                  Create First Message
                </>
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Got to top button */}
      <div className="fixed bottom-6 right-6">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="p-3 rounded-full bg-purple-500/80 hover:bg-purple-500 text-white shadow-lg transition-all hover:scale-110"
        >
          <i className="fas fa-arrow-up"></i>
        </button>
      </div>
    </motion.div>
  );
}
