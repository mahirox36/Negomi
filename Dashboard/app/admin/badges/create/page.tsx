"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { BadgeForm } from "@/components/badge/BadgeForm";
import toast from "react-hot-toast";
import { themeConfig } from "@/lib/theme";

export default function CreateBadgePage() {
  const router = useRouter();

  const handleSubmit = async (formData: any, requirements: any[]) => {
    try {
      console.log("Form data to submit:", formData); // Debug log
      
      const badgeData = {
        ...formData,
        requirements: requirements.map((req) => ({
          ...req,
          value: req.value,
        })),
      };

      console.log("Badge data payload:", badgeData); // Debug log to verify icon_url is included
      
      const response = await fetch("/api/v1/admin/badges/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(badgeData),
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        console.error("Server error response:", error); // Debug log for the error
        throw new Error(error.detail || "Failed to create badge");
      }

      toast.success("Badge created successfully!");
      router.push("/admin/badges");
    } catch (error) {
      console.error("Error creating badge:", error);  
      toast.error(error instanceof Error ? error.message : "Failed to create badge");
    }
  };

  return (
    <div className="container mx-auto p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
      >
        <h1 className={`text-4xl font-bold mb-8 bg-gradient-to-r ${themeConfig.blue.gradient} bg-clip-text text-transparent`}>
          Create Badge
        </h1>
        <BadgeForm onSubmit={handleSubmit} />
      </motion.div>
    </div>
  );
}
