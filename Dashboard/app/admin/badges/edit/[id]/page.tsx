"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { BadgeForm } from "@/app/components/badge/BadgeForm";
import { motion } from "framer-motion";
import { themeConfig } from "@/app/lib/theme";
import toast from "react-hot-toast";
import LoadingScreen from "@/app/components/LoadingScreen";

export default function EditBadgePage() {
  const params = useParams();
  const router = useRouter();
  const [badgeData, setBadgeData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBadge = async () => {
      try {
        const response = await fetch(`/api/v1/admin/badges/${params.id}`);
        
        if (!response.ok) {
          throw new Error("Failed to fetch badge");
        }
        
        const data = await response.json();
        setBadgeData(data);
      } catch (error) {
        console.error("Error fetching badge:", error);
        setError(error instanceof Error ? error.message : "Failed to load badge");
      } finally {
        setLoading(false);
      }
    };

    fetchBadge();
  }, [params.id]);

  const handleSubmit = async (formData: any, requirements: any[]) => {
    try {
      console.log("Submitting form data:", formData); // Debug log
      
      const badgeData = {
        ...formData,
        requirements: requirements.map((req) => ({
          ...req,
          value: req.value,
        })),
      };

      // Ensure icon_url is included in the payload
      if (!badgeData.icon_url) {
        throw new Error("Badge icon URL is required");
      }

      console.log("Badge data to update:", badgeData); // Debug log
      
      const response = await fetch(`/api/v1/admin/badges/update/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(badgeData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Server error:", errorData);
        throw new Error(errorData.detail || "Failed to update badge");
      }

      toast.success("Badge updated successfully!");
      router.push("/admin/badges");
    } catch (error) {
      console.error("Error updating badge:", error);
      toast.error(error instanceof Error ? error.message : "Failed to update badge");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingScreen/>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-500/20 border border-red-500/30 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-red-400 mb-2">Error</h2>
          <p className="text-white/80">{error}</p>
          <button 
            onClick={() => router.push("/admin/badges")}
            className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
      >
        <h1 className={`text-4xl font-bold mb-8 bg-gradient-to-r ${themeConfig.blue.gradient} bg-clip-text text-transparent`}>
          Edit Badge
        </h1>
        
        <BadgeForm 
          onSubmit={handleSubmit}
          initialData={badgeData}
          isEditMode={true}
          theme="blue"
        />
      </motion.div>
    </div>
  );
}
