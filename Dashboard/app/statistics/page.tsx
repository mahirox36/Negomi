"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import axios from "axios";
import PageWrapper from "../components/PageWrapper";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  height: 300,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        color: 'rgba(255, 255, 255, 0.7)',
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
    },
  },
  scales: {
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
      ticks: {
        color: 'rgba(255, 255, 255, 0.7)',
      }
    },
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
      ticks: {
        color: 'rgba(255, 255, 255, 0.7)',
      }
    }
  }
};

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
    historical_cpu: number[];
    historical_memory: number[];
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
    historical_stats: {
      timestamps: number[];
      latency: number[];
      messages: number[];
      commands: number[];
    };
  };
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
    const fetchData = async () => {
      try {
        const [statsRes, guildsRes] = await Promise.all([
          axios.get("/api/v1/bot/stats", { withCredentials: true }),
          axios.get("/api/v1/guilds", { withCredentials: true })
        ]);
        
        setStats(statsRes.data);
        setGuilds(guildsRes.data.guilds);
        setError(null);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to load statistics");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (error || !stats) {
    return (
      <PageWrapper loading={false}>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-white text-xl text-center">
            <p>Error loading statistics</p>
            <p className="text-sm text-red-300 mt-2">{error}</p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper loading={loading} loadingMessage="Loading statistics...">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="CPU Usage"
            value={`${stats.system.cpu_usage}%`}
            icon="fas fa-microchip"
            trend={calculateTrend(stats.system.historical_cpu)}
          />
          <StatCard
            title="Memory Usage"
            value={`${stats.system.memory_usage}%`}
            icon="fas fa-memory"
            trend={calculateTrend(stats.system.historical_memory)}
          />
          <StatCard
            title="Bot Uptime"
            value={formatUptime(stats.bot.uptime)}
            icon="fas fa-clock"
          />
          <StatCard
            title="Latency"
            value={`${stats.bot.latency}ms`}
            icon="fas fa-bolt"
            trend={calculateTrend(stats.bot.historical_stats.latency)}
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">System Performance</h2>
            <div className="h-[300px]">
              <Line
                data={{
                  labels: stats.bot.historical_stats.timestamps.map(ts => 
                    new Date(ts * 1000).toLocaleTimeString()
                  ),
                  datasets: [
                    {
                      label: 'CPU Usage',
                      data: stats.system.historical_cpu,
                      borderColor: '#3B82F6',
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      fill: true,
                    },
                    {
                      label: 'Memory Usage',
                      data: stats.system.historical_memory,
                      borderColor: '#10B981',
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      fill: true,
                    }
                  ]
                }}
                options={chartOptions}
              />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Bot Activity</h2>
            <div className="h-[300px]">
              <Line
                data={{
                  labels: stats.bot.historical_stats.timestamps.map(ts => 
                    new Date(ts * 1000).toLocaleTimeString()
                  ),
                  datasets: [
                    {
                      label: 'Messages',
                      data: stats.bot.historical_stats.messages,
                      borderColor: '#F59E0B',
                      backgroundColor: 'rgba(245, 158, 11, 0.1)',
                      fill: true,
                    },
                    {
                      label: 'Commands',
                      data: stats.bot.historical_stats.commands,
                      borderColor: '#EC4899',
                      backgroundColor: 'rgba(236, 72, 153, 0.1)',
                      fill: true,
                    }
                  ]
                }}
                options={chartOptions}
              />
            </div>
          </div>
        </div>

        {/* Bot Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Bot Overview</h3>
            <div className="space-y-4">
              <StatRow icon="fa-server" label="Total Servers" value={stats.bot.guild_count} />
              <StatRow icon="fa-users" label="Total Users" value={stats.bot.user_count} />
              <StatRow icon="fa-hashtag" label="Total Channels" value={stats.bot.channel_count} />
              <StatRow icon="fa-terminal" label="Commands" value={stats.bot.command_count} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Activity Stats</h3>
            <div className="space-y-4">
              <StatRow icon="fa-message" label="Messages Sent" value={stats.bot.messages_sent} />
              <StatRow icon="fa-code" label="Commands Used" value={stats.bot.commands_processed} />
              <StatRow icon="fa-microphone" label="Voice Connections" value={stats.bot.voice_connections} />
              <StatRow icon="fa-triangle-exclamation" label="Errors" value={stats.bot.errors_encountered} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">System Info</h3>
            <div className="space-y-4">
              <StatRow icon="fa-memory" label="Total Memory" value={formatBytes(stats.system.memory_total)} />
              <StatRow icon="fa-microchip" label="Threads" value={stats.system.thread_count} />
              <StatRow icon="fa-code-branch" label="Python" value={stats.system.python_version} />
              <StatRow icon="fa-desktop" label="OS" value={stats.system.os} />
            </div>
          </div>
        </div>

        {/* Top Servers */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6">Top Servers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {guilds
              .sort((a, b) => b.member_count - a.member_count)
              .slice(0, 6)
              .map((guild) => (
                <motion.div
                  key={guild.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/5 rounded-lg p-4"
                >
                  <div className="flex items-center space-x-3">
                    {guild.icon_url ? (
                      <img
                        src={guild.icon_url}
                        alt={guild.name}
                        className="w-12 h-12 rounded-full"
                      />
                    ) : (
                      <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center">
                        <i className="fas fa-server text-white/50" />
                      </div>
                    )}
                    <div>
                      <h4 className="text-white font-medium">{guild.name}</h4>
                      <div className="flex items-center gap-2 text-white/60 text-sm">
                        <i className="fas fa-users" />
                        <span>{formatNumber(guild.member_count)}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
          </div>
        </div>
      </main>
    </PageWrapper>
  );
}

function StatCard({ title, value, icon, trend }: { title: string; value: string; icon: string; trend?: number }) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="bg-white/10 backdrop-blur-lg rounded-xl p-6"
    >
      <div className="flex items-center justify-between">
        <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center">
          <i className={`${icon} text-xl text-white/90`} />
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1 ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            <i className={`fas fa-${trend >= 0 ? 'arrow-up' : 'arrow-down'}`} />
            <span className="text-sm">{Math.abs(trend)}%</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-sm font-medium text-white/70">{title}</h3>
        <p className="text-2xl font-semibold text-white mt-1">{value}</p>
      </div>
    </motion.div>
  );
}

function StatRow({ icon, label, value }: { icon: string; label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
          <i className={`fas ${icon} text-white/90`} />
        </div>
        <span className="text-white/70">{label}</span>
      </div>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}

function formatBytes(bytes: number): string {
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 B';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function calculateTrend(data: number[]): number {
  if (!data || data.length < 2) return 0;
  const last = data[data.length - 1];
  const prev = data[data.length - 2];
  if (prev === 0) return 0;
  return Number(((last - prev) / prev * 100).toFixed(1));
}
