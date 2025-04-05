"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter, useParams } from "next/navigation";
import { BadgeForm } from "@/app/components/badge/BadgeForm";
import { themeConfig } from "@/app/lib/theme";

export default function EditServerBadgePage() {
  const params = useParams();
  const serverId = params.id;
  const badgeId = params.badgeId;
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [initialData, setInitialData] = useState(null);

  useEffect(() => {
    const fetchBadge = async () => {
      try {
        const response = await fetch(
          `/api/v1/guilds/${serverId}/badges/${badgeId}`,
          {
            credentials: "include",
          }
        );
        if (!response.ok) throw new Error("Failed to fetch badge");
        const data = await response.json();
        setInitialData(data);
      } catch (error) {
        console.error("Error fetching badge:", error);
        router.push(`/dashboard/server/${serverId}/badges`);
      } finally {
        setLoading(false);
      }
    };
    fetchBadge();
  }, [serverId, badgeId, router]);

  const handleSubmit = async (formData: any, requirements: any[]) => {
    try {
      const response = await fetch(
        `/api/v1/guilds/${serverId}/badges/${badgeId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...formData, requirements }),
          credentials: "include",
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update badge");
      }

      router.push(`/dashboard/server/${serverId}/badges`);
    } catch (error) {
      console.error("Error updating badge:", error);
      alert(error instanceof Error ? error.message : "Failed to update badge");
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="text-center text-slate-300">Loading...</div>
      </div>
    );
  }

  return (
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
        >
          <h1 className={`text-4xl font-bold mb-8 bg-gradient-to-r ${themeConfig.purple.gradient} bg-clip-text text-transparent`}>
            Edit Server Badge
          </h1>

          <BadgeForm
            onSubmit={handleSubmit}
            initialData={initialData}
            isEditMode={true}
            theme="purple"
          />
        </motion.div>
      </div>
  );
}
