"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { BadgeRarity } from "./BadgeRarity";
import { RequirementSection } from "./RequirementSection";
import { ToggleSwitch } from "@/components/form/ToggleSwitch";
import { ThemeType, themeConfig } from '@/lib/theme';
import SettingsSection from "@/components/dashboard/SettingsSection";

interface BadgeFormData {
  name: string;
  description: string;
  icon_url: string;
  rarity: number;
  hidden: boolean;
}

interface BadgeFormProps {
  onSubmit: (data: BadgeFormData, requirements: any[]) => Promise<void>;
  initialData?: any;
  isEditMode?: boolean;
  theme?: ThemeType;
}

const rarityMap: Record<string, number> = {
  'common': 1,
  'uncommon': 2,
  'rare': 3,
  'epic': 4,
  'legendary': 5
};

const comparisonMap: Record<string, string> = {
  'EQUAL': '==',
  'GREATER': '>',
  'LESS': '<',
  'GREATER_EQUAL': '>=',
  'LESS_EQUAL': '<=',
  'NOT_EQUAL': '!='
};

export function BadgeForm({ onSubmit, initialData, isEditMode = false, theme = 'blue' }: BadgeFormProps) {
  const [formData, setFormData] = useState<BadgeFormData>(() => {
    if (initialData) {
      return {
        name: initialData.name || "",
        description: initialData.description || "",
        icon_url: initialData.icon_url || "",
        rarity: initialData.rarity ? rarityMap[initialData.rarity.toLowerCase()] : 1,
        hidden: initialData.hidden || false,
      };
    }
    return {
      name: "",
      description: "",
      icon_url: "",
      rarity: 1,
      hidden: false,
    };
  });

  const [requirements, setRequirements] = useState<Array<{ type: string; comparison: string; value: string }>>(() => {
    if (initialData?.requirements) {
      return initialData.requirements.map((req: any) => ({
        type: req.type.toLowerCase(),
        comparison: comparisonMap[req.comparison] || '==',
        value: req.value
      }));
    }
    return [];
  });

  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string>("");
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialData?.icon_url) {
      setPreview(initialData.icon_url);
    }
  }, [initialData]);

  const validateFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setFileError("Please upload an image file");
      return false;
    }
    if (file.size > 3 * 1024 * 1024) { // 3MB limit
      setFileError("File size must be less than 3MB");
      return false;
    }
    setFileError("");
    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement> | File) => {
    const file = 'target' in e ? e.target.files?.[0] : e;
    if (file && validateFile(file)) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileChange(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (selectedFile) {
        const uploadFormData = new FormData();
        uploadFormData.append('file', selectedFile);
        
        const uploadRes = await fetch('/api/v1/bot/upload', {
          method: 'POST',
          body: uploadFormData,
        });
        
        if (!uploadRes.ok) throw new Error('Failed to upload image');
        
        const { data } = await uploadRes.json();
        await onSubmit({ ...formData, icon_url: data.url }, requirements);
      } else {
        await onSubmit(formData, requirements);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const currentTheme = themeConfig[theme];

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
            <i className="fas fa-medal text-2xl text-white/90"></i>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
              {isEditMode ? "Edit Badge" : "Create Badge"}
            </h1>
            <p className="text-lg text-white/70 mt-1">
              {isEditMode ? "Modify badge settings and requirements" : "Configure a new badge for your server"}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10">
        <div className="p-6 space-y-8">
          <SettingsSection
            title="Badge Information"
            description="Basic information about the badge"
            icon="fa-info-circle"
            iconBgColor="bg-indigo-500/20"
            iconColor="text-indigo-300"
          >
            <div className="space-y-6">
              <input
                type="text"
                placeholder="Badge Name"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-20 transition-all text-white"
              />

              <textarea
                placeholder="Badge Description"
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-20 transition-all text-white min-h-[100px]"
              />

              <div className="space-y-2">
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                  className={`relative border-2 border-dashed rounded-lg p-6 cursor-pointer transition-all
                    ${isDragging ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-700 hover:border-indigo-500/50 hover:bg-indigo-500/5'}
                    ${preview ? 'h-[200px]' : 'h-[120px]'}`}
                >
                  {preview ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <img src={preview} alt="Preview" className="max-h-full max-w-full object-contain rounded"/>
                      <div className="absolute inset-0 bg-black/50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                        <p className="text-white text-sm">Click to change image</p>
                      </div>
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400">
                      <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="text-sm">Drop an image here or click to upload</p>
                      <p className="text-xs mt-1">Maximum size: 3MB</p>
                    </div>
                  )}
                </div>
                {fileError && (
                  <p className="text-rose-500 text-sm flex items-center gap-2">
                    <i className="fas fa-exclamation-circle" />
                    {fileError}
                  </p>
                )}
              </div>
            </div>
          </SettingsSection>

          <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
            <SettingsSection
              title="Badge Properties"
              description="Configure badge visibility and rarity"
              icon="fa-cog"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-300"
            >
              <div className="space-y-6">
                <BadgeRarity
                  value={formData.rarity}
                  onChange={(rarity) => setFormData({ ...formData, rarity })}
                />
                
                <ToggleSwitch
                  checked={formData.hidden}
                  onChange={(hidden) => setFormData({ ...formData, hidden })}
                  label="Hidden Badge"
                  description="Hidden badges are not visible until unlocked"
                  theme="purple"
                />
              </div>
            </SettingsSection>

            <SettingsSection
              title="Requirements"
              description="Set conditions for earning this badge"
              icon="fa-list-check"
              iconBgColor="bg-indigo-500/20"
              iconColor="text-indigo-300"
            >
              <RequirementSection
                requirements={requirements}
                setRequirements={setRequirements}
                theme={theme}
              />
            </SettingsSection>
          </div>
        </div>

        <div className="px-6 py-4 border-t border-white/10">
          <button
            type="submit"
            disabled={loading}
            className="w-full p-4 bg-gradient-to-br from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 
              rounded-lg font-semibold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] 
              text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <i className="fas fa-circle-notch fa-spin" />
                {isEditMode ? "Updating..." : "Creating..."}
              </>
            ) : (
              <>
                <i className={`fas ${isEditMode ? 'fa-save' : 'fa-plus'}`} />
                {isEditMode ? "Update Badge" : "Create Badge"}
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
