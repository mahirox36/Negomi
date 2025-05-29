"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { formatNumber, formatDate } from "@/lib/utils";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 },
};

type GuildData = {
  id: string;
  name: string;
  member_count: number;
  icon_url: string;
  created_at: number;
  boost_level: number;
  boost_count: number;
  verification_level: string;
  statistics: {
    total_messages: number;
    total_commands_used: number;
    total_characters: number;
    total_attachments: number;
    command_usage: Record<string, number>;
    active_members: number;
    average_messages_per_member: number;
  };
};

export default function Overview() {
  const params = useParams();
  const [guild, setGuild] = useState<GuildData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const fetchGuildData = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/guilds/${params.id}`);
      const data = await response.json();
      setGuild(data);
    } catch (error) {
      console.error("Failed to fetch guild data:", error);
    } finally {
      setIsLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    fetchGuildData();
  }, [fetchGuildData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="rounded-full h-12 w-12 border-4 border-white/10 border-t-white/90"
        />
      </div>
    );
  }

  if (!guild) return null;

  const topCommands = Object.entries(guild.statistics.command_usage)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="space-y-8 pb-8 max-w-7xl mx-auto"
    >
      {/* Server Header */}
      {/* Server Header */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-purple-500/20 to-fuchsia-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 opacity-10 -rotate-6">
          <i className="fas fa-server text-[180px] text-white"></i>
        </div>
        <div className="flex items-center gap-6 relative z-10">
          {guild.icon_url ? (
            <div className="w-20 h-20 rounded-xl shadow-lg overflow-hidden border border-white/20">
              <img
                src={guild.icon_url}
                alt={guild.name}
                className="w-full h-full object-cover"
              />
            </div>
          ) : (
            <div className="w-20 h-20 flex items-center justify-center bg-gradient-to-br from-purple-500/40 to-fuchsia-500/40 rounded-xl shadow-inner border border-white/10">
              <i className="fas fa-server text-3xl text-white/90"></i>
            </div>
          )}
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
              {guild.name}
            </h1>
            <div className="flex items-center gap-4 mt-2 text-lg text-white/70">
              <div className="flex items-center gap-2">
                <i className="fas fa-users"></i>
                <span>{formatNumber(guild.member_count)} members</span>
              </div>
              <div className="hidden sm:flex items-center gap-2">
                <i className="fas fa-clock"></i>
                <span>Created {formatDate(guild.created_at * 1000)}</span>
              </div>
              {guild.boost_level > 0 && (
                <div className="flex items-center gap-2 text-fuchsia-400">
                  <i className="fas fa-rocket"></i>
                  <span>
                    Level {guild.boost_level} ({guild.boost_count} boosts)
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon="fa-message"
          title="Total Messages"
          value={formatNumber(guild.statistics.total_messages)}
          gradient="from-purple-500/10 to-fuchsia-600/10"
          variants={itemVariants}
        />
        <StatCard
          icon="fa-terminal"
          title="Commands Used"
          value={formatNumber(guild.statistics.total_commands_used)}
          gradient="from-blue-500/10 to-cyan-600/10"
          variants={itemVariants}
        />
        <StatCard
          icon="fa-users"
          title="Active Members"
          value={formatNumber(guild.statistics.active_members)}
          gradient="from-green-500/10 to-emerald-600/10"
          variants={itemVariants}
        />
        <StatCard
          icon="fa-chart-simple"
          title="Avg Messages/Member"
          value={formatNumber(guild.statistics.average_messages_per_member)}
          gradient="from-yellow-500/10 to-amber-600/10"
          variants={itemVariants}
        />
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Command Usage */}
        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
              <i className="fas fa-terminal text-lg text-white/90"></i>
            </div>
            <h3 className="text-lg font-semibold text-white">Top Commands</h3>
          </div>
          <div className="space-y-3">
            {topCommands.map(([command, count]) => (
              <div
                key={command}
                className="flex items-center justify-between py-2 border-b border-white/5 last:border-0"
              >
                <span className="text-white/80 font-mono bg-white/5 px-2 py-1 rounded">
                  /{command}
                </span>
                <span className="text-white/60">
                  {formatNumber(count)} uses
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Server Stats */}
        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
              <i className="fas fa-chart-simple text-lg text-white/90"></i>
            </div>
            <h3 className="text-lg font-semibold text-white">
              Content Statistics
            </h3>
          </div>
          <div className="space-y-3">
            <StatRow
              icon="fa-font"
              label="Total Characters"
              value={formatNumber(guild.statistics.total_characters)}
            />
            <StatRow
              icon="fa-paperclip"
              label="Total Attachments"
              value={formatNumber(guild.statistics.total_attachments)}
            />
            <StatRow
              icon="fa-chart-line"
              label="Avg. Characters/Message"
              value={formatNumber(
                guild.statistics.total_characters /
                  guild.statistics.total_messages
              )}
            />
          </div>
        </motion.div>

        {/* Server Info */}
        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10 md:col-span-2"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
              <i className="fas fa-shield text-lg text-white/90"></i>
            </div>
            <h3 className="text-lg font-semibold text-white">
              Server Information
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatBox
              icon="fa-shield"
              label="Verification"
              value={guild.verification_level}
            />
            <StatBox
              icon="fa-rocket"
              label="Boost Level"
              value={`Level ${guild.boost_level}`}
            />
            <StatBox
              icon="fa-gift"
              label="Boosts"
              value={formatNumber(guild.boost_count)}
            />
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}

function StatCard({ icon, title, value, gradient, variants }: any) {
  return (
    <motion.div
      variants={variants}
      className={`bg-gradient-to-br ${gradient} backdrop-blur-lg rounded-xl p-6 border border-white/10 shadow-lg`}
    >
      <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-4 shadow-inner">
        <i className={`fas ${icon} text-xl text-white/90`}></i>
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-medium text-white/70">{title}</h3>
        <p className="text-2xl font-semibold text-white">{value}</p>
      </div>
    </motion.div>
  );
}

function StatRow({ icon, label, value }: any) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg hover:bg-white/5 transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500/10 to-purple-500/10 flex items-center justify-center">
          <i className={`fas ${icon} text-white/90`}></i>
        </div>
        <span className="text-white/70">{label}</span>
      </div>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}

function StatBox({ icon, label, value }: any) {
  return (
    <div className="bg-gradient-to-br from-indigo-500/5 to-purple-500/5 rounded-lg p-4 border border-white/5 shadow-inner">
      <div className="flex items-center gap-3 mb-2">
        <i className={`fas ${icon} text-white/90`}></i>
        <span className="text-white/70">{label}</span>
      </div>
      <p className="text-xl font-semibold text-white">{value}</p>
    </div>
  );
}
