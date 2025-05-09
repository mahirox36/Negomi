"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from "react-chartjs-2";
import type { ChartOptions } from 'chart.js';
import PageWrapper from "../../components/PageWrapper";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface SystemStats {
  cpu_usage: number;
  memory_usage: number;
  memory_total: number;
  thread_count: number;
  python_version: string;
  os: string;
  historical_cpu: number[];
  historical_memory: number[];
}

interface BotHistoricalStats {
  messages: number[];
  commands: number[];
  latency: number[];
  timestamps: number[];
}

interface BotStats {
  uptime: number;
  latency: number;
  guild_count: number;
  user_count: number;
  channel_count: number;
  command_count: number;
  messages_sent: number;
  commands_processed: number;
  voice_connections: number;
  errors_encountered: number;
  historical_stats: BotHistoricalStats;
}

interface DetailedStats {
  system: SystemStats;
  bot: BotStats;
}

interface Guild {
  id: string;
  name: string;
  icon_url?: string;
  member_count: number;
}

const chartOptions: ChartOptions<"line"> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top" as const,
      labels: {
        color: "rgba(255, 255, 255, 0.7)",
        font: { family: "Inter", size: 12 }
      }
    },
    tooltip: {
      backgroundColor: "rgba(0, 0, 0, 0.8)",
      titleFont: { family: "Inter", size: 13 },
      bodyFont: { family: "Inter", size: 12 },
      padding: 12,
      borderColor: "rgba(255, 255, 255, 0.1)",
      borderWidth: 1
    }
  },
  scales: {
    y: {
      grid: {
        color: "rgba(255, 255, 255, 0.05)"
      },
      ticks: {
        color: "rgba(255, 255, 255, 0.7)",
        font: { family: "Inter", size: 11 }
      }
    },
    x: {
      grid: {
        color: "rgba(255, 255, 255, 0.05)"
      },
      ticks: {
        color: "rgba(255, 255, 255, 0.7)",
        font: { family: "Inter", size: 11 }
      }
    }
  }
};

// Helper functions
const formatNumber = (num: number) => 
  new Intl.NumberFormat().format(num);

const formatBytes = (bytes: number) => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const formatUptime = (seconds: number) => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor(((seconds % 86400) % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
};

const calculateTrend = (data: number[]) => {
  if (data.length < 2) return 0;
  const last = data[data.length - 1];
  const previous = data[data.length - 2];
  return previous === 0 ? 0 : Math.round(((last - previous) / previous) * 100);
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
          fetch("/api/v1/bot/stats", { credentials: "include" }).then(res => res.json()),
          fetch("/api/v1/guilds", { credentials: "include" }).then(res => res.json())
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
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 mb-8"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
              <i className="fas fa-chart-line text-2xl text-white/90"></i>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
                Statistics Dashboard
              </h1>
              <p className="text-lg text-white/70 mt-1">
                Real-time performance metrics and analytics
              </p>
            </div>
          </div>
        </motion.div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            {
              title: "CPU Usage",
              value: `${stats.system.cpu_usage}%`,
              icon: "microchip",
              trend: calculateTrend(stats.system.historical_cpu),
              colors: ["from-blue-500/20", "to-indigo-500/20"]
            },
            {
              title: "Memory Usage",
              value: `${stats.system.memory_usage}%`,
              icon: "memory",
              trend: calculateTrend(stats.system.historical_memory),
              colors: ["from-emerald-500/20", "to-green-500/20"]
            },
            {
              title: "Uptime",
              value: formatUptime(stats.bot.uptime),
              icon: "clock",
              colors: ["from-orange-500/20", "to-amber-500/20"]
            },
            {
              title: "Latency",
              value: `${stats.bot.latency}ms`,
              icon: "bolt",
              trend: calculateTrend(stats.bot.historical_stats.latency),
              colors: ["from-purple-500/20", "to-pink-500/20"]
            }
          ].map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <StatCard
                title={card.title}
                value={card.value}
                icon={`fas fa-${card.icon}`}
                trend={card.trend}
                gradientFrom={card.colors[0]}
                gradientTo={card.colors[1]}
              />
            </motion.div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard
            title="System Performance"
            icon="microchip"
            datasets={[
              {
                label: "CPU Usage",
                data: stats.system.historical_cpu,
                borderColor: "#818CF8",
                backgroundColor: "rgba(129, 140, 248, 0.1)"
              },
              {
                label: "Memory Usage",
                data: stats.system.historical_memory,
                borderColor: "#34D399",
                backgroundColor: "rgba(52, 211, 153, 0.1)"
              }
            ]}
            labels={stats.bot.historical_stats.timestamps}
          />
          <ChartCard
            title="Bot Activity"
            icon="robot"
            datasets={[
              {
                label: "Messages",
                data: stats.bot.historical_stats.messages,
                borderColor: "#F59E0B",
                backgroundColor: "rgba(245, 158, 11, 0.1)"
              },
              {
                label: "Commands",
                data: stats.bot.historical_stats.commands,
                borderColor: "#EC4899",
                backgroundColor: "rgba(236, 72, 153, 0.1)"
              }
            ]}
            labels={stats.bot.historical_stats.timestamps}
          />
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatsPanel
            title="Bot Overview"
            icon="robot"
            gradient={["from-indigo-500/10", "to-blue-500/10"]}
            stats={[
              { label: "Total Servers", value: stats.bot.guild_count, icon: "server" },
              { label: "Total Users", value: stats.bot.user_count, icon: "users" },
              { label: "Total Channels", value: stats.bot.channel_count, icon: "hashtag" },
              { label: "Commands", value: stats.bot.command_count, icon: "terminal" }
            ]}
          />
          <StatsPanel
            title="Activity Stats"
            icon="chart-bar"
            gradient={["from-purple-500/10", "to-pink-500/10"]}
            stats={[
              { label: "Messages Sent", value: formatNumber(stats.bot.messages_sent), icon: "message" },
              { label: "Commands Used", value: formatNumber(stats.bot.commands_processed), icon: "code" },
              { label: "Voice Connections", value: stats.bot.voice_connections, icon: "microphone" },
              { label: "Errors", value: stats.bot.errors_encountered, icon: "triangle-exclamation" }
            ]}
          />
          <StatsPanel
            title="System Info"
            icon="microchip"
            gradient={["from-emerald-500/10", "to-green-500/10"]}
            stats={[
              { label: "Total Memory", value: formatBytes(stats.system.memory_total), icon: "memory" },
              { label: "Threads", value: stats.system.thread_count, icon: "microchip" },
              { label: "Python Version", value: stats.system.python_version, icon: "code-branch" },
              { label: "OS", value: stats.system.os, icon: "desktop" }
            ]}
          />
        </div>

        {/* Server Rankings */}
        <ServerRankings guilds={guilds} />
      </main>
    </PageWrapper>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  icon: string;
  trend?: number;
  gradientFrom: string;
  gradientTo: string;
}

function StatCard({ title, value, icon, trend, gradientFrom, gradientTo }: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className={`bg-gradient-to-br ${gradientFrom} ${gradientTo} backdrop-blur-lg rounded-xl p-6 border border-white/10 h-full`}
    >
      <div className="flex items-center justify-between">
        <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center backdrop-blur-sm">
          <i className={`${icon} text-xl text-white/90`} />
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1.5 ${trend >= 0 ? 'text-green-400' : 'text-red-400'} bg-white/5 px-2 py-1 rounded-lg`}>
            <i className={`fas fa-${trend >= 0 ? 'arrow-up' : 'arrow-down'} text-xs`} />
            <span className="text-sm font-medium">{Math.abs(trend)}%</span>
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

interface ChartCardProps {
  title: string;
  icon: string;
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
  }>;
  labels: number[];
}

function ChartCard({ title, icon, datasets, labels }: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-lg rounded-xl p-6 border border-white/10"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-lg">
          <i className={`fas fa-${icon} text-lg text-white/90`}></i>
        </div>
        <h2 className="text-xl font-semibold text-white">{title}</h2>
      </div>
      <div className="h-[300px]">
        <Line
          data={{
            labels: labels.map(ts => new Date(ts * 1000).toLocaleTimeString()),
            datasets: datasets.map(ds => ({
              ...ds,
              borderWidth: 2,
              tension: 0.4,
              fill: true,
            }))
          }}
          options={chartOptions}
        />
      </div>
    </motion.div>
  );
}

interface StatsPanelProps {
  title: string;
  icon: string;
  gradient: [string, string];
  stats: Array<{
    label: string;
    value: string | number;
    icon: string;
  }>;
}

function StatsPanel({ title, icon, gradient, stats }: StatsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-br ${gradient[0]} ${gradient[1]} backdrop-blur-lg rounded-xl p-6 border border-white/10`}
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-lg">
          <i className={`fas fa-${icon} text-lg text-white/90`}></i>
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      <div className="space-y-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                <i className={`fas fa-${stat.icon} text-white/90 text-sm`} />
              </div>
              <span className="text-white/70 group-hover:text-white/90 transition-colors">{stat.label}</span>
            </div>
            <span className="text-white font-medium bg-white/5 px-2 py-1 rounded-lg text-sm">
              {stat.value}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

interface ServerRankingsProps {
  guilds: Array<{
    id: string;
    name: string;
    icon_url?: string;
    member_count: number;
  }>;
}

function ServerRankings({ guilds }: ServerRankingsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-lg rounded-xl p-6 border border-white/10"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-lg">
          <i className="fas fa-trophy text-lg text-white/90"></i>
        </div>
        <h3 className="text-xl font-semibold text-white">Top Servers</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {guilds
          .sort((a, b) => b.member_count - a.member_count)
          .slice(0, 6)
          .map((guild, index) => (
            <motion.div
              key={guild.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: 1.02 }}
              className="bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-sm rounded-xl p-4 border border-white/10"
            >
              <div className="flex items-center space-x-3">
                {guild.icon_url ? (
                  <img
                    src={guild.icon_url}
                    alt={guild.name}
                    className="w-12 h-12 rounded-xl object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                    <i className="fas fa-server text-white/50" />
                  </div>
                )}
                <div>
                  <h4 className="text-white font-medium truncate max-w-[200px]">
                    {guild.name}
                  </h4>
                  <div className="flex items-center gap-2 text-white/60 text-sm mt-1">
                    <i className="fas fa-users text-xs" />
                    <span>{formatNumber(guild.member_count)} members</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
      </div>
    </motion.div>
  );
}