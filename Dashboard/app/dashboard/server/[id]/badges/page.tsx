"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useParams } from "next/navigation";
import axios from "axios";
import toast from "react-hot-toast";

interface Badge {
  id: string;
  name: string;
  description: string;
  icon_url: string;
  rarity: number;
  hidden: boolean;
  created_at: string;
  roleId: string;
  emoji: string;
  requirements: Array<{
    type: string;
    comparison: string;
    value: number;
    specific_value?: string;
  }>;
}

export default function BadgesPage() {
  const params = useParams();
  const serverId = params.id;
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);
  const [previewBadge, setPreviewBadge] = useState<Badge | null>(null);
  const [badgeLimit] = useState(8);

  useEffect(() => {
    fetchBadges();
  }, [serverId]);

  const fetchBadges = async () => {
    try {
      const response = await axios.get(`/api/v1/guilds/${serverId}/badges`, {
        withCredentials: true,
      });
      setBadges(response.data.badges);
    } catch (error) {
      console.error("Error fetching badges:", error);
      toast.error("Failed to load badges");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this badge?")) return;

    try {
      await axios.delete(`/api/v1/guilds/${serverId}/badges/${id}`, {
        withCredentials: true,
      });
      await fetchBadges();
      toast.success("Badge deleted successfully");
    } catch (error) {
      console.error("Error deleting badge:", error);
      toast.error("Failed to delete badge");
    }
  };

  useEffect(() => {
    document.body.style.overflow = previewBadge ? "hidden" : "unset";
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [previewBadge]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <i className="fas fa-circle-notch fa-spin text-3xl text-indigo-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-500/20 to-fuchsia-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 opacity-10 -rotate-6">
          <i className="fas fa-medal text-[180px] text-white"></i>
        </div>
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-500/40 to-fuchsia-500/40 rounded-xl shadow-inner border border-white/10">
            <i className="fas fa-medal text-3xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
              Server Badges
            </h1>
            <p className="text-lg text-white/70 mt-1 max-w-2xl">
              Create and manage achievement badges for your server members
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
                badges.length > 0 ? "bg-green-500" : "bg-yellow-500"
              } animate-pulse`}
            ></div>
            <span className="text-sm font-medium text-white/90">
              {badges.length} / {badgeLimit} Badges
            </span>
          </div>

          <Link
            href={`/dashboard/server/${serverId}/badges/create`}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2
              ${
                badges.length >= badgeLimit
                  ? "bg-neutral-500/50 cursor-not-allowed"
                  : "bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600"
              }`}
            onClick={(e) => {
              if (badges.length >= badgeLimit) {
                e.preventDefault();
                toast.error("Badge limit reached");
              }
            }}
          >
            <i className="fas fa-plus text-sm" />
            <span>Create Badge</span>
          </Link>
        </div>

        {/* Badge List */}
        <div className="p-6">
          <div className="space-y-4">
            {badges.map((badge, index) => (
              <motion.div
                key={badge.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-neutral-800/50 border border-neutral-700/50 rounded-lg flex items-center justify-between hover:bg-neutral-800/70 transition-colors group"
              >
                <div className="flex items-center space-x-4">
                  <div className="relative group-hover:scale-110 transition-transform duration-200">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full blur opacity-75" />
                    <img
                      src={badge.icon_url}
                      alt={badge.name}
                      className="relative w-12 h-12 rounded-full"
                    />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-indigo-300 group-hover:to-purple-300 group-hover:bg-clip-text transition-all">
                      {badge.name}
                    </h3>
                    <p className="text-sm text-white/70">{badge.description}</p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => setPreviewBadge(badge)}
                    className="px-3 py-1 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white rounded transition-colors flex items-center space-x-1"
                  >
                    <i className="fas fa-eye text-sm" />
                    <span>View</span>
                  </button>
                  <Link
                    href={`/dashboard/server/${serverId}/badges/edit/${badge.id}`}
                    className="px-3 py-1 bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 rounded transition-colors flex items-center space-x-1"
                  >
                    <i className="fas fa-edit text-sm" />
                    <span>Edit</span>
                  </Link>
                  <button
                    onClick={() => handleDelete(badge.id)}
                    className="px-3 py-1 bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 rounded transition-colors flex items-center space-x-1"
                  >
                    <i className="fas fa-trash text-sm" />
                    <span>Delete</span>
                  </button>
                </div>
              </motion.div>
            ))}

            {badges.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                  <i className="fas fa-crown text-2xl text-white/30"></i>
                </div>
                <h3 className="text-lg font-medium text-white/90 mb-2">
                  No Badges Created
                </h3>
                <p className="text-white/50 text-sm max-w-sm mx-auto">
                  Create your first badge to start rewarding your community
                  members for their achievements
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Badge Preview Modal */}
      <AnimatePresence>
        {previewBadge && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setPreviewBadge(null)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-0 z-50 flex items-center justify-center px-4"
            >
              <motion.div className="bg-gradient-to-b from-neutral-800 to-neutral-900 border border-neutral-700 rounded-2xl p-6 max-w-lg w-full shadow-2xl overflow-y-auto max-h-[90vh]">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-pink-400 bg-clip-text text-transparent">
                      Badge Details
                    </h3>
                    <button
                      onClick={() => setPreviewBadge(null)}
                      className="p-2 hover:bg-neutral-700/50 rounded-lg transition-colors text-neutral-400 hover:text-white"
                    >
                      <i className="fas fa-times" />
                    </button>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="relative group">
                      <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-pink-500 rounded-full blur opacity-25 group-hover:opacity-75 transition duration-200" />
                      <img
                        src={previewBadge.icon_url}
                        alt={previewBadge.name}
                        className="relative w-20 h-20 rounded-full border-2 border-neutral-700 bg-neutral-800"
                      />
                    </div>
                    <div>
                      <h4 className="text-xl font-semibold text-white">
                        {previewBadge.name}
                      </h4>
                      <p className="text-neutral-300 text-sm mt-1">
                        {previewBadge.description}
                      </p>
                      <div className="flex items-center space-x-2 mt-2">
                        <span className="text-xs text-neutral-400">ID:</span>
                        <code className="text-xs bg-neutral-800 px-2 py-1 rounded text-neutral-300">
                          {previewBadge.id}
                        </code>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-neutral-800/50 p-3 rounded-lg text-center">
                      <div className="text-sm text-neutral-400 mb-1">
                        Rarity
                      </div>
                      <div className="text-white font-semibold">
                        Level {previewBadge.rarity}
                      </div>
                    </div>
                    <div className="bg-neutral-800/50 p-3 rounded-lg text-center">
                      <div className="text-sm text-neutral-400 mb-1">
                        Status
                      </div>
                      <div className="text-white font-semibold">
                        {previewBadge.hidden ? "Hidden" : "Visible"}
                      </div>
                    </div>
                    <div className="bg-neutral-800/50 p-3 rounded-lg text-center">
                      <div className="text-sm text-neutral-400 mb-1">
                        Created
                      </div>
                      <div className="text-white font-semibold text-sm">
                        {new Date(previewBadge.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-neutral-700/50 pt-4">
                    <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                      <i className="fas fa-list-check mr-2 text-indigo-400" />
                      Requirements
                    </h5>
                    <div className="space-y-2 max-h-[200px] overflow-y-auto scrollbar-thin scrollbar-track-neutral-800 scrollbar-thumb-neutral-700 pr-2">
                      {previewBadge.requirements.map((req, index) => (
                        <motion.div
                          key={index}
                          initial={{ x: -20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          transition={{ delay: index * 0.1 }}
                          className="bg-neutral-800/50 p-3 rounded-lg flex items-center justify-between hover:bg-neutral-800 transition-colors"
                        >
                          <span className="text-neutral-300 text-sm capitalize">
                            {req.type.replace(/_/g, " ")}
                          </span>
                          <span className="text-indigo-400 text-sm font-medium">
                            {req.comparison.replace(/_/g, " ")} {req.value}
                            {req.specific_value && ` (${req.specific_value})`}
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => setPreviewBadge(null)}
                    className="w-full mt-2 px-4 py-3 bg-gradient-to-r from-indigo-500 to-pink-500 hover:from-indigo-600 hover:to-pink-600 rounded-lg font-semibold transition-all transform hover:scale-[1.02] active:scale-[0.98] text-white"
                  >
                    Close Preview
                  </button>
                </div>
              </motion.div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
