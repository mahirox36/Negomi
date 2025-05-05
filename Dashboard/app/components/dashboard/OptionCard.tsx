import { ReactNode } from 'react';

interface OptionCardProps {
  title: string;
  description?: string;
  icon?: string;
  iconColor?: string;
  selected: boolean;
  borderColor?: string;
  bgColor?: string;
  onClick: () => void;
}

export default function OptionCard({
  title,
  description,
  icon,
  iconColor = "text-indigo-300",
  selected,
  borderColor = "border-indigo-500",
  bgColor = "bg-indigo-500/10",
  onClick
}: OptionCardProps) {
  return (
    <div 
      className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200
        ${selected ? 
          `${borderColor} ${bgColor}` : 
          'border-white/10 hover:border-white/30 bg-white/5'
        }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-center h-12 mb-3">
        <i className={`fas ${icon} text-2xl ${iconColor}`}></i>
      </div>
      <h3 className="text-center font-medium text-white">{title}</h3>
      {description && (
        <p className="text-center text-xs text-white/60 mt-1">
          {description}
        </p>
      )}
    </div>
  );
}