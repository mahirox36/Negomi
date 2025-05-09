import { InputHTMLAttributes } from 'react';

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: string;
  variant?: 'default' | 'glass';
}

export default function TextInput({ 
  label, 
  error, 
  icon,
  variant = 'default',
  className = '',
  ...props 
}: TextInputProps) {
  const baseClasses = `w-full px-4 py-2.5 rounded-lg transition-all duration-200 outline-none
    focus:ring-2 ring-offset-2 ring-offset-[#1a1b1e] font-medium
    disabled:opacity-50 disabled:cursor-not-allowed`;
    
  const variants = {
    default: `bg-white/10 border border-white/20 text-white 
      focus:border-white/40 focus:ring-white/20`,
    glass: `backdrop-blur-md bg-white/5 border border-white/10 text-white/90
      focus:border-white/20 focus:ring-white/10 shadow-lg`
  };

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-white/70">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/50">
            <i className={icon}></i>
          </div>
        )}
        <input
          {...props}
          className={`${baseClasses} ${variants[variant]} ${icon ? 'pl-10' : ''} ${className}`}
        />
      </div>
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  );
}
