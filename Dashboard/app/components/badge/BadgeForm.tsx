"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { BadgeRarity } from "./BadgeRarity";
import { RequirementSection } from "./RequirementSection";
import { ToggleSwitch } from "@/app/components/ui/ToggleSwitch";
import { ThemeType, themeConfig } from '@/app/lib/theme';

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
        
        const { url } = await uploadRes.json();
        await onSubmit({ ...formData, icon_url: url }, requirements);
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

  const inputStyles = `
    w-full p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg 
    ${currentTheme.focus} focus:ring-2 focus:ring-opacity-20
    transition-all text-white
  `;

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div className="space-y-6">
        <input
          type="text"
          placeholder="Badge Name"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className={inputStyles}
        />

        <textarea
          placeholder="Badge Description"
          required
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className={`${inputStyles} min-h-[100px]`}
        />

        <div className="space-y-2">
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-lg p-6 cursor-pointer transition-all
              ${isDragging ? currentTheme.dragActive : `border-slate-700 ${currentTheme.dragHover}`}
              ${preview ? 'h-[200px]' : 'h-[120px]'}`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png, image/gif, image/jpeg, image/webp"
              onChange={handleFileChange}
              className="hidden"
            />
            
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
          {fileError && <p className="text-red-500 text-sm">{fileError}</p>}
        </div>

        <div className="grid grid-cols-2 gap-6">
          <BadgeRarity
            value={formData.rarity}
            onChange={(rarity) => setFormData({ ...formData, rarity })}
          />
          
          <div className="space-y-2">
            <ToggleSwitch
              checked={formData.hidden}
              onChange={(hidden) => setFormData({ ...formData, hidden })}
              label="Hidden Badge"
              description="Hidden badges are not visible until unlocked"
              theme={theme}
            />
          </div>
        </div>
      </div>

      <RequirementSection
        requirements={requirements}
        setRequirements={setRequirements}
        theme={theme}
      />

      <button
        type="submit"
        disabled={loading}
        className={`w-full p-4 ${currentTheme.gradient} ${currentTheme.gradientHover} 
          rounded-lg font-semibold text-lg 
          transition-all transform hover:scale-[1.02] active:scale-[0.98] 
          text-white disabled:opacity-50`}
      >
        {loading ? (isEditMode ? "Updating..." : "Creating...") : (isEditMode ? "Update Badge" : "Create Badge")}
      </button>
    </form>
  );
}
