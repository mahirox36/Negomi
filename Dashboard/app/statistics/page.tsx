"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BiServer,
  BiUser,
  BiMessageDetail,
  BiCommand,
  BiError,
} from "react-icons/bi";
import { FiCpu, FiHardDrive, FiClock, FiActivity } from "react-icons/fi";
import Link from "next/link";
import PageWrapper from "../components/PageWrapper";
import { API_BASE_URL } from "../config";

// Update the type to match the API response structure
type DetailedStats = {
  system: {
    cpu_usage: number;
    memory_usage: number;
    memory_total: number;
    python_version: string;
    os: string;
    uptime: number;
    thread_count: number;
    disk_usage: number;
  };
  bot: {
    guild_count: number;
    user_count: number;
    channel_count: number;
    voice_connections: number;
    latency: number;
    uptime: number;
    command_count: number;
    cogs_loaded: number;
    current_shard: number;
    messages_sent: number;
    commands_processed: number;
    errors_encountered: number;
    shard_count: number;
  };
  // guilds: Array<{
  //   id: string
  //   name: string
  //   member_count: number
  //   channel_count: number
  //   role_count: number
  //   emoji_count: number
  //   features: string[]
  //   created_at: number
  //   icon_url: string | null
  //   boost_level: number
  //   boost_count: number
  //   verification_level: string
  //   owner_id: string
  // }>
  timestamp: number;
};
type Guild = {
  id: number;
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
};

export default function StatisticsPage() {
  const [stats, setStats] = useState<DetailedStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = `${API_BASE_URL}/stats`;

        const response = await fetch(apiUrl);
        const data = await response.json();

        const processedData = {
          system: {
            cpu_usage: data.system?.cpu_usage ?? 0,
            memory_usage: data.system?.memory_usage ?? 0,
            memory_total: data.system?.memory_total ?? 0,
            python_version: data.system?.python_version ?? "N/A",
            os: data.system?.os ?? "N/A",
            uptime: data.system?.uptime ?? 0,
            thread_count: data.system?.thread_count ?? 0,
            disk_usage: data.system?.disk_usage ?? 0,
          },
          bot: {
            guild_count: data.bot?.guild_count ?? 0,
            user_count: data.bot?.user_count ?? 0,
            channel_count: data.bot?.channel_count ?? 0,
            voice_connections: data.bot?.voice_connections ?? 0,
            latency: data.bot?.latency ?? 0,
            uptime: data.bot?.uptime ?? 0,
            command_count: data.bot?.command_count ?? 0,
            cogs_loaded: data.bot?.cogs_loaded ?? 0,
            shard_count: data.bot?.shard_count ?? 1,
            current_shard: data.bot?.current_shard ?? 0,
            messages_sent: data.bot?.messages_sent ?? 0,
            commands_processed: data.bot?.commands_processed ?? 0,
            errors_encountered: data.bot?.errors_encountered ?? 0,
          },
          timestamp: data.timestamp ?? Date.now() / 1000,
        };

        setStats(processedData);
        setError(null);
      } catch (error) {
        console.error("Error fetching statistics:", error);
        setError("Failed to load statistics");
      } finally {
        setLoading(false);
      }
    };

    const fetchGuilds = async () => {
      try {
        const apiUrl = `${API_BASE_URL}/guilds`;

        const response = await fetch(apiUrl);
        const data = await response.json();
        setGuilds(data.guilds);
      } catch (error) {
        console.error("Error fetching guilds:", error);
      }
    };

    // Set loading immediately when component mounts
    setLoading(true);
    fetchStats();
    fetchGuilds();
  }, []);

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const formatBytes = (bytes: number) => {
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    if (bytes === 0) return "0 Byte";
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)).toString());
    return Math.round(bytes / Math.pow(1024, i)) + " " + sizes[i];
  };

  if (error || !stats) {
    return (
      <PageWrapper loading={false}>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-white text-xl text-center">
            <p>Error loading statistics</p>
            <p className="text-sm text-red-300 mt-2">{error}</p>
            <motion.div
              initial="initial"
              animate="animate"
              variants={{
                initial: { y: 20, opacity: 0 },
                animate: {
                  y: 0,
                  opacity: 1,
                  transition: {
                    duration: 1,
                    ease: "easeOut",
                  },
                },
              }}
              className="mt-8"
            >
              <Link href="/" className="group relative inline-block">
                <motion.div
                  className="absolute -inset-0.5 rounded-full bg-gradient-to-r from-pink-600 to-purple-600 opacity-75 blur-sm"
                  animate={{
                    scale: [1, 1.05, 1],
                    opacity: [0.75, 0.85, 0.75],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    repeatType: "reverse",
                  }}
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative px-8 py-4 bg-white rounded-full font-bold text-lg text-purple-600 hover:text-purple-700 transition-colors duration-200"
                >
                  Back to homepage
                </motion.button>
              </Link>
            </motion.div>
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper loading={loading} loadingMessage="Loading statistics...">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-white text-center mb-12"
        >
          Bot Statistics
        </motion.h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Quick Stats Cards */}
          <StatsCard
            icon={<BiServer className="w-6 h-6" />}
            title="Servers"
            value={stats.bot.guild_count.toLocaleString()}
          />
          <StatsCard
            icon={<BiUser className="w-6 h-6" />}
            title="Users"
            value={stats.bot.user_count.toLocaleString()}
          />
          <StatsCard
            icon={<BiMessageDetail className="w-6 h-6" />}
            title="Messages Sent"
            value={stats.bot.messages_sent.toLocaleString()}
          />
          <StatsCard
            icon={<BiCommand className="w-6 h-6" />}
            title="Commands"
            value={stats.bot.command_count.toLocaleString()}
          />
          <StatsCard
            icon={<BiMessageDetail className="w-6 h-6" />}
            title="Messages Sent"
            value={stats.bot.messages_sent.toLocaleString()}
          />
          <StatsCard
            icon={<BiCommand className="w-6 h-6" />}
            title="Commands Processed"
            value={stats.bot.commands_processed.toLocaleString()}
          />
          <StatsCard
            icon={<BiError className="w-6 h-6" />}
            title="Errors"
            value={stats.bot.errors_encountered.toLocaleString()}
            className="text-red-400"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* System Stats */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
          >
            <h2 className="text-2xl font-bold text-white mb-4">
              System Status
            </h2>
            <div className="space-y-4">
              <ProgressBar
                label="CPU Usage"
                value={stats.system.cpu_usage}
                icon={<FiCpu />}
              />
              <ProgressBar
                label="Memory Usage"
                value={stats.system.memory_usage}
                icon={<FiHardDrive />}
              />
              <ProgressBar
                label="Disk Usage"
                value={stats.system.disk_usage}
                icon={<FiHardDrive />}
              />
              <div className="text-white/80">
                <p>OS: {stats.system.os}</p>
                <p>Python: {stats.system.python_version}</p>
                <p>Threads: {stats.system.thread_count}</p>
                <p>Memory Total: {formatBytes(stats.system.memory_total)}</p>
              </div>
            </div>
          </motion.div>

          {/* Bot Stats */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
          >
            <h2 className="text-2xl font-bold text-white mb-4">Bot Status</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <StatusItem
                  icon={<FiClock />}
                  label="Uptime"
                  value={formatUptime(stats.bot.uptime)}
                />
                <StatusItem
                  icon={<FiActivity />}
                  label="Latency"
                  value={`${stats.bot.latency}ms`}
                />
              </div>
              <div className="text-white/80">
                <p>
                  Shards: {stats.bot.current_shard + 1}/{stats.bot.shard_count}
                </p>
                <p>Voice Connections: {stats.bot.voice_connections}</p>
                <p>Channels: {stats.bot.channel_count.toLocaleString()}</p>
                <p>Classes Loaded: {stats.bot.cogs_loaded}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Server List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold text-white mb-4">Top Servers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {guilds
              .sort((a, b) => b.member_count - a.member_count)
              .slice(0, 9)
              .map((guild) => (
                <motion.div
                  key={guild.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/5 rounded-lg p-4"
                >
                  <div className="flex items-center space-x-3">
                    {guild.icon_url && (
                      <img
                        src={guild.icon_url}
                        alt={guild.name}
                        className="w-12 h-12 rounded-full"
                      />
                    )}
                    <div>
                      <h3 className="text-white font-semibold">{guild.name}</h3>
                      <p className="text-white/60 text-sm">
                        {guild.member_count.toLocaleString()} members
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
          </div>
        </motion.div>
      </main>
    </PageWrapper>
  );
}

const StatsCard = ({
  icon,
  title,
  value,
  className = "",
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  className?: string;
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ scale: 1.02 }}
    className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
  >
    <div className="flex items-center space-x-3">
      <div className="text-white/80">{icon}</div>
      <div>
        <p className="text-white/60">{title}</p>
        <p className={`text-2xl font-bold ${className || "text-white"}`}>
          {value}
        </p>
      </div>
    </div>
  </motion.div>
);

const ProgressBar = ({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) => (
  <div>
    <div className="flex items-center justify-between mb-1">
      <div className="flex items-center space-x-2">
        <span className="text-white/80">{icon}</span>
        <span className="text-white/80">{label}</span>
      </div>
      <span className="text-white/80">{value}%</span>
    </div>
    <div className="w-full bg-white/10 rounded-full h-2">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value}%` }}
        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
      />
    </div>
  </div>
);

const StatusItem = ({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) => (
  <div className="flex items-center space-x-3">
    <div className="text-white/80">{icon}</div>
    <div>
      <p className="text-white/60">{label}</p>
      <p className="text-white font-semibold">{value}</p>
    </div>
  </div>
);
