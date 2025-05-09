"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { BadgeForm } from "@/components/badge/BadgeForm";
import { useLayout } from "@/providers/LayoutProvider";
import toast from "react-hot-toast";

export default function EditServerBadgePage() {
  const params = useParams();
  // Ensure params are always strings
  const serverId = Array.isArray(params.id) ? params.id[0] : params.id;
  const badgeId = Array.isArray(params.badgeId) ? params.badgeId[0] : params.badgeId;
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [initialData, setInitialData] = useState(null);
  const { setCurrentPath, setServerId } = useLayout();

  useEffect(() => {
    setCurrentPath("badges");
    setServerId(serverId as string);
  }, [serverId, setCurrentPath, setServerId]);

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
        toast.error("Failed to load badge");
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

      toast.success("Badge updated successfully");
      router.push(`/dashboard/server/${serverId}/badges`);
    } catch (error) {
      console.error("Error updating badge:", error);
      toast.error(error instanceof Error ? error.message : "Failed to update badge");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <i className="fas fa-circle-notch fa-spin text-3xl text-indigo-400" />
      </div>
    );
  }

  if (!initialData) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <p className="text-lg text-white/80 mb-4">Badge not found or failed to load.</p>
        <button
          onClick={() => router.push(`/dashboard/server/${serverId}/badges`)}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <BadgeForm
        onSubmit={handleSubmit}
        initialData={initialData}
        isEditMode={true}
        theme="purple"
      />
    </div>
  );
}
