"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function AdminPage() {
  const [stats, setStats] = useState({
    totalBadges: 0,
    totalServers: 0,
    activeUsers: 0,
  });

  useEffect(() => {
    // Fetch stats from API
    const fetchStats = async () => {
      try {
        const response = await fetch("/api/admin/stats", { credentials: "include" });
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="container mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/50 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-slate-800"
      >
        <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          Admin Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard title="Total Badges" value={stats.totalBadges} icon="fa-medal" />
          <StatsCard title="Total Servers" value={stats.totalServers} icon="fa-server" />
          <StatsCard title="Active Users" value={stats.activeUsers} icon="fa-users" />
        </div>
      </motion.div>
    </div>
  );
}

function StatsCard({ title, value, icon }: { title: string; value: number; icon: string }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-6 flex items-center space-x-4 border border-slate-700/50 hover:bg-slate-800/70 transition-colors">
      <div className="bg-blue-500/20 p-4 rounded-lg">
        <i className={`fas ${icon} text-2xl text-blue-400`}></i>
      </div>
      <div>
        <h3 className="text-slate-300 text-sm font-medium">{title}</h3>
        <p className="text-2xl font-bold text-white">{value.toLocaleString()}</p>
      </div>
    </div>
  );
}
