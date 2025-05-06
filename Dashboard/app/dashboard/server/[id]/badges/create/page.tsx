"use client";

import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import { BadgeForm } from "../../../../../components/badge/BadgeForm";
import toast from "react-hot-toast";
import { themeConfig } from "@/app/lib/theme";

export default function CreateServerBadgePage() {
  const router = useRouter();
  const params = useParams();
  const serverId = params.id;

  const handleSubmit = async (formData: any, requirements: any[]) => {
    try {
      const badgeData = {
        ...formData,
        requirements: requirements.map((req) => ({
          ...req,
          value: req.value,
        })),
      };

      const response = await fetch(`/api/v1/guilds/${serverId}/badges/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(badgeData),
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create badge");
      }

      router.push(`/dashboard/server/${serverId}/badges`);
    } catch (error) {
      console.error("Error creating badge:", error);
      toast.error("Failed to reset settings");
      error instanceof Error ? error.message : "Failed to create badge";
    }
  };

  return (
    <div className="container mx-auto p-6">
      <BadgeForm onSubmit={handleSubmit} theme="purple" />
    </div>
  );
}
