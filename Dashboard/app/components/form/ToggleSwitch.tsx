import { ThemeType, themeConfig } from '@/app/lib/theme';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  theme?: ThemeType;
  size?: 'sm' | 'md' | 'lg';
}

const sizeConfig = {
  sm: {
    container: 'h-4 w-8',
    knob: 'h-3 w-3',
    translate: { on: 'translate-x-5', off: 'translate-x-1' },
  },
  md: {
    container: 'h-6 w-11',
    knob: 'h-4 w-4',
    translate: { on: 'translate-x-6', off: 'translate-x-1' },
  },
  lg: {
    container: 'h-8 w-16',
    knob: 'h-6 w-6',
    translate: { on: 'translate-x-9', off: 'translate-x-2' },
  },
};

export function ToggleSwitch({ 
  checked, 
  onChange, 
  label = '', 
  description, 
  disabled = false,
  theme = 'blue',
  size = 'lg',
}: ToggleSwitchProps) {
  const currentTheme = themeConfig[theme];
  const sizeProps = sizeConfig[size];

  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex flex-col">
        {label && (
          <span className="text-sm font-medium text-slate-200">{label}</span>
        )}
        {description && (
          <span className="text-xs text-slate-400">{description}</span>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        disabled={disabled}
        className={`relative inline-flex items-center rounded-full transition-colors
          ${sizeProps.container}
          ${currentTheme.focus} focus:ring-2 focus:ring-opacity-20 focus:ring-offset-2 focus:ring-offset-slate-900
          ${checked ? currentTheme.toggle : 'bg-slate-700'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <span
          className={`inline-block rounded-full bg-white transition-transform
            ${sizeProps.knob}
            ${checked ? sizeProps.translate.on : sizeProps.translate.off}
          `}
        />
      </button>
    </div>
  );
}
