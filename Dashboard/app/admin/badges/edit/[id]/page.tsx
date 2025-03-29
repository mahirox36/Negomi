"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { use } from "react";

export default function EditBadgePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    icon_url: "",
    rarity: 1,
    hidden: false,
  });
  const requirementTypes = [
    "message_count",
    "message_sent",
    "command_use",
    "reaction_received",
    "reaction_given",
    "gif_sent",
    "gif_count",
    "content_length",
    "emoji_used",
    "custom_emoji_used",
    "attachment_sent",
    "attachment_count",
    "mention_count",
    "unique_mention_count",
    "link_shared",
    "content_match",
    "channel_activity",
    "time_based",
    "specific_user_interaction",
    "inactive_duration",
    "unique_emoji_count",
    "specific_emoji",
    "all_commands",
    "message_edit_count",
    "message_delete_count",
  ];

  const comparisonTypes = [
    "equal",
    "greater",
    "less",
    "greater_equal",
    "less_equal",
  ];
  const addRequirement = () => {
    setRequirements([...requirements, { type: "", comparison: "", value: "" }]);
  };
  const [requirements, setRequirements] = useState<
    Array<{
      type: string;
      comparison: string;
      value: string;
      specific_value?: string;
    }>
  >([]);

  // Fetch badge data on load
  useEffect(() => {
    const fetchBadge = async () => {
      try {
        const response = await fetch(`/api/v1/admin/badges/${id}`, {
          credentials: "include",
        });
        if (!response.ok) throw new Error("Failed to fetch badge");
        const data = await response.json();
        setFormData(data);
        setRequirements(data.requirements);
      } catch (error) {
        console.error("Error fetching badge:", error);
        router.push("/admin/badges");
      } finally {
        setLoading(false);
      }
    };
    fetchBadge();
  }, [id, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/v1/admin/badges/${id}/edit`, {
        method: "POST",
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
        className="bg-slate-900/50 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-slate-800"
      >
        <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          Edit Badge
        </h1>

        {/* Use the same form structure as create page but with edit functionality */}
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="space-y-6">
            {/* Basic Info Section */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">
                Badge Name
              </label>
              <input
                type="text"
                placeholder="Enter badge name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition-all text-white"
              />
            </div>

            {/* Description field */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">
                Description
              </label>
              <textarea
                placeholder="Enter badge description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="w-full p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition-all min-h-[100px] text-white"
              />
            </div>

            {/* Icon URL field */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">
                Icon URL
              </label>
              <input
                type="url"
                placeholder="Enter icon URL"
                value={formData.icon_url}
                onChange={(e) =>
                  setFormData({ ...formData, icon_url: e.target.value })
                }
                className="w-full p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition-all text-white"
              />
            </div>

            {/* Rarity and Visibility */}
            <div className="grid grid-cols-2 gap-6">
              {/* ...existing rarity and visibility fields with updated colors... */}
            </div>
          </div>

          {/* Requirements Section */}
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-slate-200">
                Requirements
              </h2>
              <button
                type="button"
                onClick={addRequirement}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors flex items-center space-x-2"
              >
                <span>Add Requirement</span>
                <i className="fas fa-plus text-sm" />
              </button>
            </div>

            <div className="space-y-4">
              {requirements.map((req, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-lg space-y-4"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-slate-300 mb-1 block">
                        Type
                      </label>
                      <select
                        value={req.type}
                        onChange={(e) => {
                          const newReqs = [...requirements];
                          newReqs[index] = { ...req, type: e.target.value };
                          setRequirements(newReqs);
                        }}
                        className="w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 text-white"
                      >
                        <option value="" disabled>
                          Select type
                        </option>
                        {requirementTypes.map((type) => (
                          <option key={type} value={type}>
                            {type.replace(/_/g, " ")}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-slate-300 mb-1 block">
                        Comparison
                      </label>
                      <select
                        value={req.comparison}
                        onChange={(e) => {
                          const newReqs = [...requirements];
                          newReqs[index] = {
                            ...req,
                            comparison: e.target.value,
                          };
                          setRequirements(newReqs);
                        }}
                        className="w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 text-white"
                      >
                        <option value="" disabled>
                          Select comparison
                        </option>
                        {comparisonTypes.map((comp) => (
                          <option key={comp} value={comp}>
                            {comp.replace(/_/g, " ")}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-1 block">
                      Value
                    </label>
                    <input
                      type="number"
                      value={req.value}
                      onChange={(e) => {
                        const newReqs = [...requirements];
                        newReqs[index] = { ...req, value: e.target.value };
                        setRequirements(newReqs);
                      }}
                      className="w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 text-white"
                    />
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={() => {
                        setRequirements(
                          requirements.filter((_, i) => i !== index)
                        );
                      }}
                      className="px-3 py-1 bg-red-500/20 text-red-300 hover:bg-red-500/30 rounded transition-colors flex items-center space-x-2"
                    >
                      <i className="fas fa-trash-alt" />
                      <span>Remove</span>
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            className="w-full p-4 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 rounded-lg font-semibold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] text-white"
          >
            Edit Badge
          </button>
        </form>
      </motion.div>
    </div>
  );
}
