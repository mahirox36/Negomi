"use client";

import { useEffect, useState } from "react";
import { useBackendCheck } from "../../hooks/useBackendCheck";
import DashboardLayout from "../../components/DashboardLayout";
import { User, Guild } from "../../types/discord";
import { UserDataDashboard } from "../../types/UserData";
import LoadingScreen from "../../components/LoadingScreen";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { formatNumber } from "@/lib/utils";

// Animation variants for staggered animations
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

export default function Dashboard() {
  const { loading: backendLoading, error: backendError } = useBackendCheck();
  const [user, setUser] = useState<User | undefined>(undefined);
  const [userData, setUserData] = useState<UserDataDashboard | undefined>(
    undefined
  );
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
        const guildPromise = fetch("/api/v1/auth/user/guilds", {
          credentials: "include",
        });

        // Fetch user data for dashboard
        const userDataPromise = fetch("/api/v1/auth/user/dashboard", {
          credentials: "include",
        });

        // Wait for both fetches to complete
        const [guildResponse, userDataResponse] = await Promise.all([
          guildPromise,
          userDataPromise,
        ]);

        if (!guildResponse.ok) {
          throw new Error("Failed to fetch guild data");
        }

        const guildData = await guildResponse.json();
        setGuilds(guildData.guilds);

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
          className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
        >
          <div className="flex items-center gap-6">
            {user?.avatar && (
              <div className="w-24 h-24 rounded-2xl shadow-lg overflow-hidden border border-white/20">
                <img
                  src={`https://cdn.discordapp.com/avatars/${user.id}/${
                    user.avatar
                  }.${user.avatar?.startsWith("a_") ? "gif" : "png"}`}
                  alt={user.username}
                  className="w-full h-full object-cover"
                />
              </div>
            )}
            <div>
              <h1 className="text-4xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
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

          <StatCard
            icon="fa-message"
            title="Total Messages"
            value={formatNumber(userData.totalMessages)}
            subtitle="All time"
            gradient="from-indigo-500/10 to-purple-500/10"
            variants={itemVariants}
          />

          <StatCard
            icon="fa-terminal"
            title="Commands Used"
            value={formatNumber(userData.commandsUsed)}
            subtitle="Total commands"
            gradient="from-pink-500/10 to-rose-500/10"
            variants={itemVariants}
          />
        </div>

        {/* Detailed Stats Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Message Statistics */}
          <motion.div
            variants={itemVariants}
            className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                <i className="fas fa-message text-lg text-white/90"></i>
              </div>
              <h3 className="text-lg font-semibold text-white">
                Message Statistics
              </h3>
            </div>
            <div className="space-y-3">
              <StatRow
                icon="fa-message"
                label="Total Messages"
                value={formatNumber(userData.totalMessages)}
              />
              <StatRow
                icon="fa-font"
                label="Characters"
                value={formatNumber(userData.messageStats.totalCharacters)}
              />
              <StatRow
                icon="fa-file"
                label="Words"
                value={formatNumber(userData.messageStats.totalWords)}
              />
              <StatRow
                icon="fa-reply"
                label="Replies"
                value={formatNumber(userData.messageStats.totalReplies)}
              />
              <StatRow
                icon="fa-at"
                label="Mentions"
                value={formatNumber(userData.messageStats.totalMentions)}
              />
              <StatRow
                icon="fa-face-smile"
                label="Emojis"
                value={formatNumber(userData.messageStats.totalEmojis)}
              />
            </div>
          </motion.div>

          {/* Command Usage */}
          <motion.div
            variants={itemVariants}
            className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                <i className="fas fa-terminal text-lg text-white/90"></i>
              </div>
              <h3 className="text-lg font-semibold text-white">
                Command Usage
              </h3>
            </div>
            <div className="space-y-3">
              <StatRow
                icon="fa-terminal"
                label="Total Commands"
                value={formatNumber(userData.commandStats.totalCommands)}
              />
              <div className="mt-4">
                <h4 className="text-sm font-medium text-white/70 mb-2">
                  Most Used Commands
                </h4>
                {userData.commandStats.favoriteCommands.map(
                  ([command, count], index) => (
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
                  )
                )}
              </div>
            </div>
          </motion.div>

          {/* Attachment Stats */}
          <motion.div
            variants={itemVariants}
            className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10"
          >
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                <i className="fas fa-paperclip text-lg text-white/90"></i>
                
              </div>
              <h3 className="text-lg font-semibold text-white">Attachments</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <StatBox
                icon="fa-image"
                label="Images"
                value={formatNumber(userData.attachmentStats.images)}
              />
              <StatBox
                icon="fa-video"
                label="Videos"
                value={formatNumber(userData.attachmentStats.videos)}
              />
              <StatBox
                icon="fa-music"
                label="Audio"
                value={formatNumber(userData.attachmentStats.audio)}
              />
              <StatBox
                icon="fa-file"
                label="Other"
                value={formatNumber(userData.attachmentStats.other)}
              />
            </div>
          </motion.div>

          {/* Badges */}
          <motion.div
            variants={itemVariants}
            className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-xl p-6 shadow-lg border border-white/10"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="relative">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                  <i className="fas fa-award text-lg text-white/90"></i>
                </div>
                <motion.div
                  className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg blur opacity-30"
                  animate={{ opacity: [0.2, 0.4, 0.2] }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
              </div>
              <h3 className="text-lg font-semibold text-white">
                Achievement Badges
              </h3>
            </div>

            <motion.div
              className="grid grid-cols-2 gap-4"
              variants={{
                hidden: { opacity: 0 },
                show: { opacity: 1, transition: { staggerChildren: 0.1 } },
              }}
              initial="hidden"
              animate="show"
            >
              {userData.badges?.map(
                (badge) =>
                  badge && (
                    <motion.div
                      key={badge.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="group relative"
                    >
                      <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg blur opacity-30 group-hover:opacity-50 transition duration-300" />
                      <div className="relative bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-sm rounded-lg p-4 flex items-center gap-4 border border-white/10 hover:border-white/20 transition-all duration-300">
                        <motion.div
                          className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center shadow-lg"
                          whileHover={{ rotate: [0, -5, 5, -5, 0] }}
                          transition={{ duration: 0.5 }}
                        >
                          <img
                            src={badge.icon_url}
                            alt={badge.name}
                            className="w-8 h-8 transform group-hover:scale-110 transition-transform duration-300"
                          />
                        </motion.div>
                        <div className="space-y-1">
                          <span className="text-white/90 block text-sm font-medium">
                            {badge.name}
                          </span>
                          <span className="inline-flex items-center space-x-1 text-xs">
                            <span
                              className={`
                    px-2 py-0.5 rounded-full 
                    ${
                      badge.rarity === "legendary"
                        ? "bg-gradient-to-r from-yellow-400 to-orange-500 text-white"
                        : badge.rarity === "epic"
                        ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                        : badge.rarity === "rare"
                        ? "bg-gradient-to-r from-blue-500 to-cyan-500 text-white"
                        : badge.rarity === "uncommon"
                        ? "bg-gradient-to-r from-green-500 to-teal-500 text-white"
                        : badge.rarity === "common"
                        ? "bg-gradient-to-r from-gray-500 to-gray-400 text-white"
                        : "bg-white/10 text-white/50"
                    }
                  `}
                            >
                              {badge.rarity.charAt(0).toUpperCase() +
                                badge.rarity.slice(1)}
                            </span>
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )
              )}

              {(!userData.badges || userData.badges.length === 0) && (
                <motion.div
                  className="col-span-2 relative overflow-hidden"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 animate-pulse" />
                  <div className="relative bg-white/5 rounded-lg p-8 text-center">
                    <motion.i
                      className="fas fa-award text-5xl text-white/30 mb-4 block"
                      animate={{
                        rotateY: [0, 180, 360],
                        scale: [1, 1.1, 1],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        repeatType: "reverse",
                      }}
                    />
                    <p className="text-white/50 text-lg">
                      Your badge collection awaits! Keep engaging with Negomi to
                      unlock special achievements.
                    </p>
                  </div>
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}

// Reusable components
function StatCard({ icon, title, value, subtitle, gradient, variants }: any) {
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
        {subtitle && <p className="text-sm text-white/60">{subtitle}</p>}
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
