"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { use } from "react";
import { BadgeForm } from "@/app/components/badge/BadgeForm";
import { themeConfig } from "@/app/lib/theme";

export default function EditBadgePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [initialData, setInitialData] = useState(null);

  // Fetch badge data on load
  useEffect(() => {
    const fetchBadge = async () => {
      try {
        const response = await fetch(`/api/v1/admin/badges/${id}`, {
          credentials: "include",
        });
        if (!response.ok) throw new Error("Failed to fetch badge");
        const data = await response.json();
        setInitialData(data);
      } catch (error) {
        console.error("Error fetching badge:", error);
        router.push("/admin/badges");
      } finally {
        setLoading(false);
      }
    };
    fetchBadge();
  }, [id, router]);

  const handleSubmit = async (formData: any, requirements: any[]) => {
    try {
      const response = await fetch(`/api/v1/admin/badges/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...formData, requirements }),
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update badge");
      }

      router.push("/admin/badges");
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
        <h1 className={`text-4xl font-bold mb-8 ${themeConfig.blue.gradient} bg-clip-text text-transparent`}>
          Edit Badge
        </h1>

        <BadgeForm
          onSubmit={handleSubmit}
          initialData={initialData}
          isEditMode={true}
        />
      </motion.div>
    </div>
  );
}
