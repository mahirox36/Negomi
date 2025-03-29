"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { FaPlus, FaTrash } from "react-icons/fa";

interface Requirement {
  type: string;
  comparison: string;
  value: string;
}

interface RequirementSectionProps {
  requirements: Requirement[];
  setRequirements: (requirements: Requirement[]) => void;
}

const comparisonMap: Record<string, string> = {
  "==": "EQUAL",
  ">": "GREATER",
  "<": "LESS",
  ">=": "GREATER_EQUAL",
  "<=": "LESS_EQUAL",
  "!=": "NOT_EQUAL"
};

export function RequirementSection({
  requirements,
  setRequirements,
}: RequirementSectionProps) {
  const [requirementTypes, setRequirementTypes] = useState<string[]>([]);

  useEffect(() => {
    const fetchRequirements = async () => {
      const response = await axios.get("/api/v1/layout/badges/requirements");
      setRequirementTypes(response.data);
    };
    fetchRequirements();
  }, []);

  const addRequirement = () => {
    setRequirements([...requirements, { type: "", comparison: "", value: "" }]);
  };

  const updateRequirement = (
    index: number,
    field: keyof Requirement,
    value: string
  ) => {
    const newReqs = [...requirements];
    if (field === 'type') {
      value = value.toUpperCase();
    }
    newReqs[index] = { ...newReqs[index], [field]: value };
    setRequirements(newReqs);
  };

  const removeRequirement = (index: number) => {
    setRequirements(requirements.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-slate-200">Requirements</h2>
        <button
          type="button"
          onClick={addRequirement}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors flex items-center gap-2"
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
                  className="w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 text-white"
                  required
                >
                  <option value="">Select type</option>
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
                  onChange={(e) =>
                    updateRequirement(index, "comparison", e.target.value)
                  }
                  className="w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 text-white"
                  required
                >
                  <option value="">Select comparison</option>
                  {Object.keys(comparisonMap).map((comp) => (
                    <option key={comp} value={comp}>
                      {comparisonMap[comp]}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-300 mb-1 block">
                  Value
                </label>
                <input
                  type="text"
                  value={req.value}
                  onChange={(e) =>
                    updateRequirement(index, "value", e.target.value)
                  }
                  className="w-full p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:border-blue-400 text-white"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => removeRequirement(index)}
                className="px-3 py-1 bg-red-500/20 text-red-300 hover:bg-red-500/30 rounded transition-colors flex items-center gap-2"
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
