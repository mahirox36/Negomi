"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { formatNumber, formatDate, formatDuration } from "@/lib/utils";

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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!guild) return null;

  const topCommands = Object.entries(guild.statistics.command_usage)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="space-y-6 pb-8">
      {/* Server Header */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center gap-6">
          {guild.icon_url ? (
            <img
              src={guild.icon_url}
              alt={guild.name}
              className="w-24 h-24 rounded-2xl shadow-lg"
            />
          ) : (
            <div className="w-24 h-24 rounded-2xl bg-white/10 flex items-center justify-center">
              <i className="fas fa-server text-4xl text-white/50"></i>
            </div>
          )}
          <div>
            <h1 className="text-4xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
              {guild.name}
            </h1>
            <div className="flex items-center gap-4 mt-2 text-white/70">
              <div className="flex items-center gap-2">
                <i className="fas fa-users"></i>
                <span>{formatNumber(guild.member_count)} members</span>
              </div>
              <div className="flex items-center gap-2">
                <i className="fas fa-clock"></i>
                <span>Created {formatDate(guild.created_at * 1000)}</span>
              </div>
              {guild.boost_level > 0 && (
                <div className="flex items-center gap-2 text-purple-400">
                  <i className="fas fa-rocket"></i>
                  <span>Level {guild.boost_level} ({guild.boost_count} boosts)</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon="fa-message"
          title="Total Messages"
          value={formatNumber(guild.statistics.total_messages)}
        />
        <StatCard
          icon="fa-terminal"
          title="Commands Used"
          value={formatNumber(guild.statistics.total_commands_used)}
        />
        <StatCard
          icon="fa-users"
          title="Active Members"
          value={formatNumber(guild.statistics.active_members)}
        />
        <StatCard
          icon="fa-chart-simple"
          title="Avg Messages/Member"
          value={formatNumber(guild.statistics.average_messages_per_member)}
        />
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Top Commands</h3>
          <div className="space-y-3">
            {topCommands.map(([command, count]) => (
              <div
                key={command}
                className="flex items-center justify-between text-white/70"
              >
                <span className="font-mono">/{command}</span>
                <span>{formatNumber(count)} uses</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Content Statistics</h3>
          <div className="space-y-3 text-white/70">
            <div className="flex justify-between">
              <span>Total Characters</span>
              <span>{formatNumber(guild.statistics.total_characters)}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Attachments</span>
              <span>{formatNumber(guild.statistics.total_attachments)}</span>
            </div>
            <div className="flex justify-between">
              <span>Avg. Characters/Message</span>
              <span>
                {formatNumber(
                  guild.statistics.total_characters / guild.statistics.total_messages
                )}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  title,
  value,
}: {
  icon: string;
  title: string;
  value: string | number;
}) {
  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
      <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-4">
        <i className={`fas ${icon} text-xl text-white/90`}></i>
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-medium text-white/70">{title}</h3>
        <p className="text-2xl font-semibold text-white">{value}</p>
      </div>
    </div>
  );
}
