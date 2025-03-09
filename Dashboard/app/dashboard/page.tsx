"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "../components/DashboardLayout";
import { User, Guild } from "../types/discord";
import LoadingScreen from "../components/LoadingScreen";

export default function Dashboard() {
  const [user, setUser] = useState<User | undefined>(undefined);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const userResponse = await fetch("/api/auth/user", {
          credentials: "include",
        });
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUser(userData.user);
        } else {
          window.location.href = "/api/auth/discord/login";
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        window.location.href = "/api/auth/discord/login";
      }
    };

    const fetchGuildData = async () => {
      try {
        const guildResponse = await fetch("/api/auth/user/guilds", {
          credentials: "include",
        });
        if (guildResponse.ok) {
          const guildData = await guildResponse.json();
          setGuilds(guildData.guilds);
        }
      } catch (error) {
        console.error("Error fetching guild data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
    fetchGuildData();
  }, []);

  const getGuildIcon = (guild: Guild) => {
    if (!guild.icon) return "/default-guild-icon.png";
    return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`;
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <DashboardLayout user={user} guilds={guilds}>
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 mt-8">
        <h1 className="text-2xl font-bold text-white mb-6">Dashboard</h1>

        {/* User Info */}
        <section className="mb-8">
          <div className="bg-white/5 rounded-lg p-4">
            <div className="flex items-center space-x-4">
              {user?.avatar && (
                <img
                  src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${user.avatar?.startsWith("a_") ? "gif" : "png"}`}
                  alt={user.username}
                  className="w-16 h-16 rounded-full"
                />
              )}
              <div>
                <h2 className="text-xl font-bold text-white">
                  {user?.global_name || user?.username}
                </h2>
                <p className="text-gray-300">#{user?.username}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-white text-lg font-semibold mb-2">
              Total Servers
            </h3>
            <p className="text-3xl text-white font-bold">{guilds.length}</p>
          </div>
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-white text-lg font-semibold mb-2">
              Total Users
            </h3>
            <p className="text-3xl text-white font-bold">0</p>
          </div>
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-white text-lg font-semibold mb-2">
              Commands Used
            </h3>
            <p className="text-3xl text-white font-bold">0</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
