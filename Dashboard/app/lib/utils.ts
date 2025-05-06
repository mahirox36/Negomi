import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
};

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toLocaleString();
};

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