export type ThemeType = 'blue' | 'purple';

export const themeConfig = {
  blue: {
    primary: 'bg-blue-500',
    primaryHover: 'hover:bg-blue-600',
    focus: 'focus:border-blue-400 focus:ring-blue-400',
    danger: 'bg-red-500/20',
    dangerHover: 'hover:bg-red-500/30',
    dangerText: 'text-red-300',
    gradient: 'bg-gradient-to-r from-blue-500 to-cyan-500',
    gradientHover: 'hover:from-blue-600 hover:to-cyan-600',
    dragActive: 'border-blue-500 bg-blue-500/10',
    dragHover: 'hover:border-blue-400',
    toggle: 'bg-blue-500'
  },
  purple: {
    primary: 'bg-purple-500',
    primaryHover: 'hover:bg-purple-600',
    focus: 'focus:border-indigo-400 focus:ring-indigo-400',
    danger: 'bg-pink-500/20',
    dangerHover: 'hover:bg-pink-500/30',
    dangerText: 'text-pink-300',
    gradient: 'bg-gradient-to-r from-purple-500 to-pink-500',
    gradientHover: 'hover:from-purple-600 hover:to-pink-600',
    dragActive: 'border-purple-500 bg-purple-500/10',
    dragHover: 'hover:border-indigo-400',
    toggle: 'bg-purple-500'
  }
} as const;
