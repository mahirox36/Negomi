"use client";

import { useEffect, useState } from "react";
import { useBackendCheck } from "../hooks/useBackendCheck";
import DashboardLayout from "../components/DashboardLayout";
import { User, Guild } from "../types/discord";
import { UserDataDashboard } from "../types/UserData";
import LoadingScreen from "../components/LoadingScreen";
import { useRouter } from "next/navigation";

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
        // router.push("/api/v1/auth/discord/login");
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

  // Only render dashboard if we have a user
  if (!user) {
    return null;
  }

  const getGuildIcon = (guild: Guild) => {
    if (!guild.icon) return "/default-guild-icon.png";
    return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`;
  };

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
                  src={`https://cdn.discordapp.com/avatars/${user.id}/${
                    user.avatar
                  }.${user.avatar?.startsWith("a_") ? "gif" : "png"}`}
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
            <p className="text-3xl text-white font-bold">{userData?.guildsCount}</p>
          </div>
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-white text-lg font-semibold mb-2">
              Total Messages
            </h3>
            <p className="text-3xl text-white font-bold">{userData?.totalMessages}</p>
          </div>
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-white text-lg font-semibold mb-2">
              Commands Used
            </h3>
            <p className="text-3xl text-white font-bold">{userData?.commandsUsed}</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
