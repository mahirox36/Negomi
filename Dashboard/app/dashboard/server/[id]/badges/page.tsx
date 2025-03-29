"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useParams } from "next/navigation";
import SettingsLayout from "@/app/components/ServerLayout";

interface Badge {
  id: string;
  name: string;
  description: string;
  icon_url: string;
  rarity: number;
  hidden: boolean;
  created_at: string;
  requirements: Array<{
    type: string;
    comparison: string;
    value: number;
    specific_value?: string;
  }>;
}

export default function ServerBadgesPage() {
  const params = useParams();
  const serverId = params.id;
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);
  const [previewBadge, setPreviewBadge] = useState<Badge | null>(null);

  useEffect(() => {
    fetchBadges();
  }, [serverId]);

  const fetchBadges = async () => {
    try {
      const response = await fetch(`/api/v1/servers/${serverId}/badges`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to fetch badges");
      const data = await response.json();
      setBadges(data.badges);
    } catch (error) {
      console.error("Error fetching badges:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this badge?")) return;

    try {
      const response = await fetch(`/api/v1/servers/${serverId}/badges/${id}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to delete badge");
      await fetchBadges();
    } catch (error) {
      console.error("Error deleting badge:", error);
    }
  };

  return (
    <SettingsLayout serverId={params.id as string}>
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
        >
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-pink-400 bg-clip-text text-transparent">
              Server Badges
            </h1>
            <Link
              href={`/dashboard/server/${serverId}/badges/create`}
              className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg transition-colors flex items-center space-x-2"
            >
              <i className="fas fa-plus text-sm" />
              <span>Create Badge</span>
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-4">
              {badges.map((badge) => (
                <motion.div
                  key={badge.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-4 bg-neutral-800/50 border border-neutral-700/50 rounded-lg flex items-center justify-between hover:bg-neutral-800/70 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <img
                      src={badge.icon_url}
                      alt={badge.name}
                      className="w-12 h-12 rounded-full"
                    />
                    <div>
                      <h3 className="text-lg font-semibold">{badge.name}</h3>
                      <p className="text-sm text-gray-300">
                        {badge.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setPreviewBadge(badge)}
                      className="px-3 py-1 bg-neutral-500/20 text-neutral-300 hover:bg-neutral-500/30 rounded transition-colors flex items-center space-x-1"
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
            </div>
          )}

          <AnimatePresence>
            {previewBadge && (
              <>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setPreviewBadge(null)}
                  className="fixed inset-0 bg-black/70 backdrop-blur-sm"
                  style={{ top: "4rem" }}
                />

                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="fixed inset-0 flex items-start justify-center"
                  style={{ top: "4rem", height: "calc(100vh - 4rem)" }}
                >
                  <motion.div className="bg-gradient-to-b from-neutral-800 to-neutral-900 border border-neutral-700 rounded-2xl p-6 max-w-lg w-full m-4 shadow-2xl overflow-y-auto max-h-[calc(100vh-8rem)]">
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
                            {new Date(
                              previewBadge.created_at
                            ).toLocaleDateString()}
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
                                {req.specific_value &&
                                  ` (${req.specific_value})`}
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
        </motion.div>
      </div>
    </SettingsLayout>
  );
}
