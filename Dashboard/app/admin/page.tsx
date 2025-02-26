"use client"
import { useState } from 'react';
import { motion } from 'framer-motion';

const requirementTypes = [
  "message_count", "message_sent", "command_use", "reaction_received",
  "reaction_given", "gif_sent", "gif_count", "content_length",
  "emoji_used", "custom_emoji_used", "attachment_sent", "attachment_count",
  "mention_count", "unique_mention_count", "link_shared", "content_match",
  "channel_activity", "time_based", "specific_user_interaction",
  "inactive_duration", "unique_emoji_count", "specific_emoji",
  "all_commands", "message_edit_count", "message_delete_count"
];

const comparisonTypes = [
  "equal", "greater", "less", "greater_equal", "less_equal"
];

export default function AdminPage() {
  const [requirements, setRequirements] = useState([{
    type: "message_count",
    value: 0,
    comparison: "greater_equal",
    specific_value: ""
  }]);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    icon_url: "",
    rarity: 1,
    hidden: false
  });

  const addRequirement = () => {
    setRequirements([...requirements, {
      type: "message_count",
      value: 0,
      comparison: "greater_equal",
      specific_value: ""
    }]);
  };

  const removeRequirement = (index: number) => {
    setRequirements(requirements.filter((_, i) => i !== index));
  };

  const updateRequirement = (index: number, field: string, value: string | number) => {
    const newRequirements = [...requirements];
    newRequirements[index] = { ...newRequirements[index], [field]: value };
    setRequirements(newRequirements);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const badgeData = {
        ...formData,
        requirements: requirements.map(req => ({
          ...req,
          value: Number(req.value) // Ensure value is a number
        }))
      };

      const response = await fetch('http://localhost:25400/api/admin/create_badge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(badgeData),
        credentials: 'include',
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create badge');
      }
      
      alert('Badge created successfully!');
      // Reset form
      setFormData({
        name: "",
        description: "",
        icon_url: "",
        rarity: 1,
        hidden: false
      });
      setRequirements([{
        type: "message_count",
        value: 0,
        comparison: "greater_equal",
        specific_value: ""
      }]);
    } catch (error) {
      console.error('Error creating badge:', error);
      alert(error instanceof Error ? error.message : 'Failed to create badge');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-900 to-indigo-900 text-white p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-xl"
      >
        <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Create Badge
        </h1>
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-purple-200">Badge Name</label>
              <input
                type="text"
                placeholder="Enter badge name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full p-3 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-purple-200">Description</label>
              <textarea
                placeholder="Enter badge description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full p-3 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all min-h-[100px]"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-purple-200">Icon URL</label>
              <input
                type="url"
                placeholder="Enter icon URL"
                value={formData.icon_url}
                onChange={(e) => setFormData({...formData, icon_url: e.target.value})}
                className="w-full p-3 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all"
              />
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-purple-200">Rarity Level</label>
                <input
                  type="number"
                  placeholder="1-5"
                  min="1"
                  max="5"
                  value={formData.rarity}
                  onChange={(e) => setFormData({...formData, rarity: parseInt(e.target.value)})}
                  className="w-full p-3 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-purple-200">Visibility</label>
                <label className="flex items-center space-x-3 p-3 bg-white/5 border border-purple-500/30 rounded-lg cursor-pointer hover:bg-white/10 transition-all">
                  <input
                    type="checkbox"
                    checked={formData.hidden}
                    onChange={(e) => setFormData({...formData, hidden: e.target.checked})}
                    className="form-checkbox h-5 w-5 text-purple-500 rounded border-purple-400"
                  />
                  <span className="text-sm text-purple-200">Hidden Badge</span>
                </label>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-purple-200">Requirements</h2>
              <button
                type="button"
                onClick={addRequirement}
                className="px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors flex items-center space-x-2"
              >
                <span>Add Requirement</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              {requirements.map((req, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-4 bg-white/5 border border-purple-500/30 rounded-lg space-y-4"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-purple-200 mb-1 block">Type</label>
                      <select
                        value={req.type}
                        onChange={(e) => updateRequirement(index, 'type', e.target.value)}
                        className="w-full p-2 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400"
                      >
                        {requirementTypes.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-purple-200 mb-1 block">Comparison</label>
                      <select
                        value={req.comparison}
                        onChange={(e) => updateRequirement(index, 'comparison', e.target.value)}
                        className="w-full p-2 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400"
                      >
                        {comparisonTypes.map(comp => (
                          <option key={comp} value={comp}>{comp}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-purple-200 mb-1 block">Value</label>
                      <input
                        type="number"
                        value={req.value}
                        onChange={(e) => updateRequirement(index, 'value', parseInt(e.target.value))}
                        className="w-full p-2 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-purple-200 mb-1 block">Specific Value</label>
                      <input
                        type="text"
                        value={req.specific_value}
                        onChange={(e) => updateRequirement(index, 'specific_value', e.target.value)}
                        placeholder="Optional"
                        className="w-full p-2 bg-white/5 border border-purple-500/30 rounded-lg focus:border-purple-400"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={() => removeRequirement(index)}
                      className="px-4 py-2 bg-red-500/20 text-red-300 hover:bg-red-500/30 rounded-lg transition-colors flex items-center space-x-2"
                    >
                      <span>Remove</span>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            className="w-full p-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg font-semibold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98]"
          >
            Create Badge
          </button>
        </form>
      </motion.div>
    </div>
  );
}
