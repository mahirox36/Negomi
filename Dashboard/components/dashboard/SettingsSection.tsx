import { ReactNode } from 'react';

interface SettingsSectionProps {
  title: string;
  description?: string;
  icon?: string;
  iconBgColor?: string;
  iconColor?: string;
  children: ReactNode;
}

export default function SettingsSection({
  title,
  description,
  icon = "fa-cog",
  iconBgColor = "bg-white/10",
  iconColor = "text-white/90",
  children
}: SettingsSectionProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className={`w-10 h-10 flex items-center justify-center ${iconBgColor} rounded-lg`}>
          <i className={`fas ${icon} text-xl ${iconColor}`}></i>
        </div>
        <div>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          {description && (
            <p className="text-sm text-white/70 mt-1">
              {description}
            </p>
          )}
        </div>
      </div>

      <div className="bg-white/5 rounded-lg p-5 space-y-5">
        {children}
      </div>
    </div>
  );
}