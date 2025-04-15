"use client";

import { useEffect, useState } from "react";
import { useBackendCheck } from "../hooks/useBackendCheck";
import DashboardLayout from "../components/DashboardLayout";
import { User, Guild } from "../types/discord";
import { UserDataDashboard } from "../types/UserData";
import LoadingScreen from "../components/LoadingScreen";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { formatNumber } from "@/lib/utils";

// Animation variants for staggered animations
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

export default function Dashboard() {
  const { loading: backendLoading, error: backendError } = useBackendCheck();
  const [user, setUser] = useState<User | undefined>(undefined);
  const [userData, setUserData] = useState<UserDataDashboard | undefined>(undefined);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUserData = async () => {
      // Don't fetch if backend is offline
      if (backendError) {
        setLoading(false);
        return;
      }

      try {
        const userResponse = await fetch("/api/v1/auth/user", {
          credentials: "include",
        });

        if (!userResponse.ok) {
          if (userResponse.status === 401 || userResponse.status === 403) {
            router.push("/api/v1/auth/discord/login");
            return;
          }
          throw new Error("Failed to fetch user data");
        }

        const userData = await userResponse.json();
        setUser(userData.user);

        // Only fetch guild data if we have a valid user
        const guildResponse = await fetch("/api/v1/auth/user/guilds", {
          credentials: "include",
        });

        if (!guildResponse.ok) {
          throw new Error("Failed to fetch guild data");
        }

        const guildData = await guildResponse.json();
        setGuilds(guildData.guilds);

        // Fetch user data for dashboard
        const userDataResponse = await fetch("/api/v1/auth/user/dashboard", {
          credentials: "include",
        });

        if (!userDataResponse.ok) {
          throw new Error("Failed to fetch user data");
        }

        const userDataData = await userDataResponse.json();
        setUserData(userDataData);
      } catch (error) {
        console.error("Error:", error);
      } finally {
        setLoading(false);
      }
    };

    if (!backendLoading) {
      fetchUserData();
    }
  }, [router, backendLoading, backendError]);

  if (backendLoading || loading) {
    return <LoadingScreen />;
  }

  if (backendError) {
    router.push("/error");
    return null;
  }

  if (!user || !userData) {
    return null;
  }

  return (
    <DashboardLayout user={user} guilds={guilds}>
      <motion.div 
        initial="hidden"
        animate="show"
        variants={containerVariants}
        className="space-y-8 pb-8 max-w-7xl mx-auto"
      >
        {/* User Profile Card */}
        <motion.div 
          variants={itemVariants}
          className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
        >
          <div className="flex items-center gap-6">
            {user?.avatar && (
              <img
                src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${user.avatar?.startsWith("a_") ? "gif" : "png"}`}
                alt={user.username}
                className="w-24 h-24 rounded-2xl shadow-lg"
              />
            )}
            <div>
              <h1 className="text-4xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                {user?.global_name || user?.username}
              </h1>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-2 text-white/70">
                  <i className="fas fa-server"></i>
                  <span>{userData.guildsCount} servers</span>
                </div>
                <div className="flex items-center gap-2 text-white/70">
                  <i className="fas fa-crown"></i>
                  <span>{userData.adminGuildsCount} admin servers</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div variants={itemVariants} className="col-span-2">
            <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Level Progress</h3>
                <span className="text-purple-400">Level {userData.milestoneProgress.currentLevel}</span>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(userData.xp / (userData.xp + userData.milestoneProgress.xpToNextLevel)) * 100}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="h-full bg-gradient-to-r from-purple-500 to-purple-600"
                  />
                </div>
                <div className="flex justify-between text-sm text-white/60">
                  <span>{formatNumber(userData.xp)} XP</span>
                  <span>{formatNumber(userData.milestoneProgress.xpToNextLevel)} XP to next level</span>
                </div>
              </div>
            </div>
          </motion.div>

          <StatCard
            icon="fa-fire"
            title="Activity Streak"
            value={userData.activityStreak}
            subtitle={`Longest: ${userData.longestStreak}`}
            gradient="from-orange-500/10 to-red-600/10"
            variants={itemVariants}
          />

          <StatCard
            icon="fa-chart-line"
            title="Daily Messages"
            value={userData.messageStats.averageDailyMessages}
            subtitle="Average per day"
            gradient="from-blue-500/10 to-blue-600/10"
            variants={itemVariants}
          />
        </div>

        {/* Detailed Stats Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Message Statistics */}
          <motion.div variants={itemVariants} className="bg-white/5 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Message Statistics</h3>
            <div className="space-y-3">
              <StatRow icon="fa-message" label="Total Messages" value={formatNumber(userData.totalMessages)} />
              <StatRow icon="fa-font" label="Characters" value={formatNumber(userData.messageStats.totalCharacters)} />
              <StatRow icon="fa-file" label="Words" value={formatNumber(userData.messageStats.totalWords)} />
              <StatRow icon="fa-reply" label="Replies" value={formatNumber(userData.messageStats.totalReplies)} />
              <StatRow icon="fa-at" label="Mentions" value={formatNumber(userData.messageStats.totalMentions)} />
              <StatRow icon="fa-face-smile" label="Emojis" value={formatNumber(userData.messageStats.totalEmojis)} />
            </div>
          </motion.div>

          {/* Command Usage */}
          <motion.div variants={itemVariants} className="bg-white/5 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Command Usage</h3>
            <div className="space-y-3">
              <StatRow icon="fa-terminal" label="Total Commands" value={formatNumber(userData.commandStats.totalCommands)} />
              <div className="mt-4">
                <h4 className="text-sm font-medium text-white/70 mb-2">Most Used Commands</h4>
                {userData.commandStats.favoriteCommands.map(([command, count], index) => (
                  <div key={command} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                    <span className="text-white/80 font-mono">/{command}</span>
                    <span className="text-white/60">{formatNumber(count)} uses</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Attachment Stats */}
          <motion.div variants={itemVariants} className="bg-white/5 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Attachments</h3>
            <div className="grid grid-cols-2 gap-4">
              <StatBox icon="fa-image" label="Images" value={formatNumber(userData.attachmentStats.images)} />
              <StatBox icon="fa-video" label="Videos" value={formatNumber(userData.attachmentStats.videos)} />
              <StatBox icon="fa-music" label="Audio" value={formatNumber(userData.attachmentStats.audio)} />
              <StatBox icon="fa-file" label="Other" value={formatNumber(userData.attachmentStats.other)} />
            </div>
          </motion.div>

          {/* Achievements */}
          <motion.div variants={itemVariants} className="bg-white/5 backdrop-blur-lg rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Achievements</h3>
            <div className="grid grid-cols-2 gap-4">
              {userData.milestoneProgress.achievements.map((achievement) => (
                <div key={achievement} className="bg-white/5 rounded-lg p-3 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                    <i className="fas fa-trophy text-yellow-400"></i>
                  </div>
                  <span className="text-white/80">{achievement.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}

// Reusable components
function StatCard({ icon, title, value, subtitle, gradient, variants }: any) {
  return (
    <motion.div variants={variants} className={`bg-gradient-to-br ${gradient} backdrop-blur-lg rounded-xl p-6 border border-white/10`}>
      <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-4">
        <i className={`fas ${icon} text-xl text-white/90`}></i>
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-medium text-white/70">{title}</h3>
        <p className="text-2xl font-semibold text-white">{value}</p>
        {subtitle && <p className="text-sm text-white/60">{subtitle}</p>}
      </div>
    </motion.div>
  );
}

function StatRow({ icon, label, value }: any) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
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
    <div className="bg-white/5 rounded-lg p-4">
      <div className="flex items-center gap-3 mb-2">
        <i className={`fas ${icon} text-white/90`}></i>
        <span className="text-white/70">{label}</span>
      </div>
      <p className="text-xl font-semibold text-white">{value}</p>
    </div>
  );
}
