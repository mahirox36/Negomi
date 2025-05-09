"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ThemeType, themeConfig } from '@/lib/theme';
import axios from "axios";

interface Guild {
  id: string;
  name: string;
  member_count: number;
  icon_url: string | null;
  owner_id: string;
  boost_level: number;
  boost_count: number;
  verification_level: string;
  features: string[];
  created_at: number;
  channel_count: number;
  role_count: number;
  emoji_count: number;
}

export default function ServersPage() {
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);

  useEffect(() => {
    fetchGuilds();
  }, []);

  const fetchGuilds = async () => {
    try {
      const response = await axios.get("/api/v1/admin/guilds", {
        withCredentials: true,
      });
      setGuilds(response.data.guilds);
    } catch (error) {
      console.error("Error fetching guilds:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
      >
        <div className="flex justify-between items-center mb-8">
          <h1 className={`text-4xl font-bold ${themeConfig.blue.gradient} bg-clip-text text-transparent`}>
            All Servers ({guilds.length})
          </h1>
        </div>

        {loading ? (
          <div className="text-center py-8">Loading servers...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {guilds.map((guild) => (
              <motion.div
                key={guild.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-neutral-800/50 border border-neutral-700/50 rounded-lg p-4 hover:bg-neutral-800/70 transition-colors"
              >
                <div className="flex items-start space-x-4">
                  {guild.icon_url ? (
                    <img
                      src={guild.icon_url}
                      alt={guild.name}
                      className="w-16 h-16 rounded-full"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-neutral-700 flex items-center justify-center text-2xl font-bold text-white">
                      {guild.name.charAt(0)}
                    </div>
                  )}
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white">{guild.name}</h3>
                    <p className="text-sm text-neutral-400">{guild.member_count.toLocaleString()} members</p>
                    <button
                      onClick={() => setSelectedGuild(guild)}
                      className="mt-2 px-3 py-1 bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 rounded transition-colors text-sm"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        <AnimatePresence>
          {selectedGuild && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                onClick={() => setSelectedGuild(null)}
                className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
                style={{ overflow: "hidden" }} // Prevent scrolling
              />

              {/* Modal */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  transition: {
                    type: "spring",
                    duration: 0.5,
                    bounce: 0.3,
                  },
                }}
                exit={{
                  opacity: 0,
                  scale: 0.95,
                  transition: {
                    duration: 0.3,
                    ease: "easeInOut",
                  },
                }}
                className="fixed inset-x-0 top-[4rem] z-50 flex items-center justify-center px-4"
                style={{ height: "calc(80vh - 4rem)" }} // Adjust height to account for navbar
              >
                <div className="bg-gradient-to-b from-neutral-900 to-neutral-950 rounded-2xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto shadow-2xl border border-white/10">
                  {/* Modal Content */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      transition: { delay: 0.1, duration: 0.3 },
                    }}
                    className="flex justify-between items-start mb-6"
                  >
                    <h2 className={`text-2xl font-bold ${themeConfig.blue.gradient} bg-clip-text text-transparent`}>
                      {selectedGuild.name}
                    </h2>
                    <motion.button
                      whileHover={{ scale: 1.1, rotate: 90 }}
                      whileTap={{ scale: 0.9 }}
                      transition={{ duration: 0.2 }}
                      onClick={() => setSelectedGuild(null)}
                      className="text-neutral-400 hover:text-white"
                    >
                      <i className="fas fa-times" />
                    </motion.button>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      transition: { delay: 0.2, duration: 0.3 },
                    }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6"
                  >
                    <div className="space-y-2">
                      <InfoItem label="Server ID" value={selectedGuild.id} />
                      <InfoItem label="Owner ID" value={selectedGuild.owner_id} />
                      <InfoItem
                        label="Created At"
                        value={new Date(selectedGuild.created_at * 1000).toLocaleDateString()}
                      />
                      <InfoItem
                        label="Verification Level"
                        value={selectedGuild.verification_level}
                      />
                    </div>
                    <div className="space-y-2">
                      <InfoItem
                        label="Members"
                        value={selectedGuild.member_count.toLocaleString()}
                      />
                      <InfoItem
                        label="Channels"
                        value={selectedGuild.channel_count.toLocaleString()}
                      />
                      <InfoItem
                        label="Roles"
                        value={selectedGuild.role_count.toLocaleString()}
                      />
                      <InfoItem
                        label="Emojis"
                        value={selectedGuild.emoji_count.toLocaleString()}
                      />
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      transition: { delay: 0.3, duration: 0.3 },
                    }}
                    className="mb-6"
                  >
                    <h3 className="text-lg font-semibold text-white mb-2">Boost Status</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-neutral-800 rounded-lg p-3">
                        <div className="text-sm text-neutral-400">Level</div>
                        <div className="text-lg font-semibold text-white">
                          {selectedGuild.boost_level}
                        </div>
                      </div>
                      <div className="bg-neutral-800 rounded-lg p-3">
                        <div className="text-sm text-neutral-400">Boosts</div>
                        <div className="text-lg font-semibold text-white">
                          {selectedGuild.boost_count}
                        </div>
                      </div>
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      transition: { delay: 0.4, duration: 0.3 },
                    }}
                  >
                    <h3 className="text-lg font-semibold text-white mb-2">Features</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedGuild.features.map((feature, index) => (
                        <motion.span
                          key={feature}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{
                            opacity: 1,
                            scale: 1,
                            transition: { delay: 0.4 + index * 0.05 },
                          }}
                          whileHover={{
                            scale: 1.05,
                            backgroundColor: "rgba(99, 102, 241, 0.3)",
                          }}
                          className="px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded text-sm"
                        >
                          {feature.toLowerCase().replace(/_/g, " ")}
                        </motion.span>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

const InfoItem = ({ label, value }: { label: string; value: string | number }) => (
  <div className="bg-neutral-800 rounded-lg p-3">
    <div className="text-sm text-neutral-400">{label}</div>
    <div className="text-white font-medium break-all">{value}</div>
  </div>
);