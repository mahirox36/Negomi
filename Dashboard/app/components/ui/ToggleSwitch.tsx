import { ThemeType, themeConfig } from '@/app/lib/theme';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  description?: string;
  theme?: ThemeType;
}

export function ToggleSwitch({ 
  checked, 
  onChange, 
  label, 
  description, 
  theme = 'blue' 
}: ToggleSwitchProps) {
  const currentTheme = themeConfig[theme];

  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex flex-col">
        <span className="text-sm font-medium text-slate-200">{label}</span>
        {description && (
          <span className="text-xs text-slate-400">{description}</span>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors 
          ${currentTheme.focus} focus:ring-2 focus:ring-opacity-20 focus:ring-offset-2 focus:ring-offset-slate-900
          ${checked ? currentTheme.toggle : 'bg-slate-700'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${checked ? 'translate-x-6' : 'translate-x-1'}`}
        />
      </button>
    </div>
  );
}
