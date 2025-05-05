"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { FaPlus, FaTrash } from "react-icons/fa";
import { ThemeType, themeConfig } from "@/app/lib/theme";

interface Requirement {
  type: string;
  comparison: string;
  value: string;
}

interface RequirementSectionProps {
  requirements: Requirement[];
  setRequirements: (requirements: Requirement[]) => void;
  theme?: ThemeType;
}

const comparisonMap: Record<string, string> = {
  "==": "Equal to",
  ">": "Greater than",
  "<": "Less than",
  ">=": "Greater than or equal",
  "<=": "Less than or equal",
  "!=": "Not equal",
};

export function RequirementSection({
  requirements,
  setRequirements,
  theme = "blue",
}: RequirementSectionProps) {
  const [requirementTypes, setRequirementTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRequirements = async () => {
      try {
        setLoading(true);
        const response = await axios.get("/api/v1/layout/badges/requirements");
        setRequirementTypes(response.data.sort());
      } catch (error) {
        console.error("Failed to fetch requirements:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRequirements();
  }, []);

  const addRequirement = () => {
    setRequirements([
      ...requirements,
      { type: "", comparison: "==", value: "" },
    ]);
  };

  const updateRequirement = (
    index: number,
    field: keyof Requirement,
    value: string
  ) => {
    const newReqs = [...requirements];
    if (field === "type") {
      value = value.replace(/\s+/g, "_");
    }
    if (field === "value") {
      // Remove any non-numeric characters if the type suggests a numeric value
      if (["MESSAGES", "LEVEL", "EXPERIENCE"].includes(newReqs[index].type)) {
        value = value.replace(/[^\d.-]/g, "");
      }
    }
    newReqs[index] = { ...newReqs[index], [field]: value };
    setRequirements(newReqs);
  };

  const removeRequirement = (index: number) => {
    setRequirements(requirements.filter((_, i) => i !== index));
  };

  const currentTheme = themeConfig[theme];

  const selectStyles = `
    w-full p-2.5 bg-slate-800/50 border border-slate-700/50 rounded-lg 
    ${currentTheme.focus} focus:ring-2 focus:ring-opacity-20
    text-white cursor-pointer transition-all duration-200
    appearance-none bg-[url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%3E%3Ctitle%3Edown-arrow%3C%2Ftitle%3E%3Cg%20fill%3D%22%23ffffff%22%3E%3Cpath%20d%3D%22M10.293%2C3.293%2C6%2C7.586%2C1.707%2C3.293A1%2C1%2C0%2C0%2C0%2C.293%2C4.707l5%2C5a1%2C1%2C0%2C0%2C0%2C1.414%2C0l5-5a1%2C1%2C0%2C1%2C0-1.414-1.414Z%22%20fill%3D%22%23ffffff%22%3E%3C%2Fpath%3E%3C%2Fg%3E%3C%2Fsvg%3E')]
    bg-no-repeat bg-[length:12px] bg-[center_right_1rem]
    hover:bg-slate-700/50
  `;

  const optionStyles = `
    bg-slate-800 text-white
    hover:bg-slate-700
    [&:not(:last-child)]:border-b [&:not(:last-child)]:border-slate-700/50
    transition-colors duration-150
  `;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-slate-200">Requirements</h2>
        <button
          type="button"
          onClick={addRequirement}
          className={`px-4 py-2 ${currentTheme.primary} ${currentTheme.primaryHover} rounded-lg transition-colors flex items-center gap-2`}
        >
          <FaPlus className="text-sm" />
          <span>Add Requirement</span>
        </button>
      </div>

      <div className="space-y-4">
        {requirements.map((req, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-lg space-y-4"
          >
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1 block">
                  Type
                </label>
                <select
                  value={req.type}
                  onChange={(e) =>
                    updateRequirement(index, "type", e.target.value)
                  }
                  className={selectStyles}
                  required
                  disabled={loading}
                >
                  <option value="" className={optionStyles} disabled>
                    Select type
                  </option>
                  {requirementTypes.map((type) => (
                    <option key={type} value={type} className={optionStyles}>
                      {type
                        .replace(/_/g, " ")
                        .toLowerCase()
                        .split(" ")
                        .map(
                          (word) => word.charAt(0).toUpperCase() + word.slice(1)
                        )
                        .join(" ")}
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
                  onChange={(e) =>
                    updateRequirement(index, "comparison", e.target.value)
                  }
                  className={selectStyles}
                  required
                >
                  <option value="" className={optionStyles} disabled>
                    Select comparison
                  </option>
                  {Object.entries(comparisonMap).map(([value, label]) => (
                    <option key={value} value={value} className={optionStyles}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1 block">
                  Value
                </label>
                <input
                  type={
                    ["MESSAGES", "LEVEL", "EXPERIENCE"].includes(req.type)
                      ? "number"
                      : "text"
                  }
                  value={req.value}
                  onChange={(e) =>
                    updateRequirement(index, "value", e.target.value)
                  }
                  className={`w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg ${currentTheme.focus} focus:ring-1 text-white`}
                  required
                  min={
                    ["MESSAGES", "LEVEL", "EXPERIENCE"].includes(req.type)
                      ? "0"
                      : undefined
                  }
                  step={["EXPERIENCE"].includes(req.type) ? "0.01" : "1"}
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => removeRequirement(index)}
                className={`px-3 py-1 ${currentTheme.danger} ${currentTheme.dangerHover} ${currentTheme.dangerText} rounded transition-colors flex items-center gap-2`}
              >
                <FaTrash className="text-sm" />
                <span>Remove</span>
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
