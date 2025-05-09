import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num);
}

export function formatDate(date: number): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
}

export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d`;
  if (hours > 0) return `${hours}h`;
  if (minutes > 0) return `${minutes}m`;
  return `${seconds}s`;
}


export const formatPercentage = (value: number, total: number): string => {
  return `${((value / total) * 100).toFixed(1)}%`;
};

export const getTimeOfDay = (hour: number): string => {
  if (hour >= 5 && hour < 12) return "morning";
  if (hour >= 12 && hour < 17) return "afternoon";
  if (hour >= 17 && hour < 21) return "evening";
  return "night";
};

export const getMostActiveTime = (hourlyData: Record<string, number>): string => {
  const maxHour = Object.entries(hourlyData)
    .reduce((a, b) => (a[1] > b[1] ? a : b))[0];
  return getTimeOfDay(parseInt(maxHour));
};

export const getActivityHeatmap = (hourlyData: Record<string, number>): number[] => {
  const hours = Array(24).fill(0);
  Object.entries(hourlyData).forEach(([hour, count]) => {
    hours[parseInt(hour)] = count;
  });
  return hours;
};