interface ToggleSwitchProps {
  enabled: boolean;
  onChange: (value: boolean) => void;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

export default function ToggleSwitch({ 
  enabled, 
  onChange,
  size = 'md',
  disabled = false 
}: ToggleSwitchProps) {
  const sizes = {
    sm: 'w-10 h-6',
    md: 'w-14 h-8',
    lg: 'w-16 h-9'
  };

  const thumbSizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-7 h-7'
  };

  return (
    <div
      onClick={() => !disabled && onChange(!enabled)}
      className={`${sizes[size]} rounded-full transition-colors duration-200 cursor-pointer relative
        ${enabled ? "bg-emerald-500" : "bg-white/20"}
        ${disabled ? "opacity-50 cursor-not-allowed" : ""}
      `}
    >
      <div
        className={`${thumbSizes[size]} absolute rounded-full bg-white top-1 transition-transform duration-200
          ${enabled ? "translate-x-[calc(100%+0.25rem)]" : "translate-x-1"}
        `}
      />
    </div>
  );
}
