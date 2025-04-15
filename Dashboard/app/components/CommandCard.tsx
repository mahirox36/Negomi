import { motion } from "framer-motion";
import { Command } from "../types/commands";
import { ViewMode } from "../commands/page";

interface CommandCardProps {
  command: Command;
  viewMode: ViewMode;
  onClick: () => void;
}

const badgeColors: Record<string, string> = {
  admin: "bg-red-500/20 text-red-400",
  developer: "bg-yellow-500/20 text-yellow-400",
  fun: "bg-purple-500/20 text-purple-400",
  utility: "bg-blue-500/20 text-blue-400",
  moderation: "bg-green-500/20 text-green-400",
  music: "bg-pink-500/20 text-pink-400",
};

export default function CommandCard({ command, viewMode, onClick }: CommandCardProps) {
  const badgeColor = badgeColors[command.category.toLowerCase()] || "bg-gray-500/20 text-gray-400";

  if (viewMode === "compact") {
    return (
      <motion.button
        layout
        onClick={onClick}
        className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/5 transition-colors flex items-center gap-3"
      >
        <span className="text-white font-medium">/{command.name}</span>
        <span className="text-white/60 text-sm flex-1 truncate">{command.description}</span>
      </motion.button>
    );
  }

  if (viewMode === "list") {
    return (
      <motion.div
        layout
        className="bg-white/5 rounded-lg overflow-hidden hover:bg-white/10 transition-colors cursor-pointer"
        onClick={onClick}
      >
        <div className="p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg text-white font-medium">/{command.name}</h3>
                <span className={`px-2 py-0.5 rounded-full text-xs ${badgeColor}`}>
                  {command.category}
                </span>
              </div>
              <p className="text-white/60">{command.description}</p>
            </div>
            <div className="flex flex-col items-end">
              {command.usage && (
                <span className="text-white/40 text-sm">
                  {command.usage} uses
                </span>
              )}
              {command.cooldown && (
                <span className="text-white/40 text-sm">
                  {command.cooldown}s cooldown
                </span>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      layout
      className="bg-white/5 rounded-lg overflow-hidden hover:bg-white/10 transition-colors cursor-pointer"
      onClick={onClick}
    >
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg text-white font-medium">/{command.name}</h3>
          <span className={`px-2 py-0.5 rounded-full text-xs ${badgeColor}`}>
            {command.category}
          </span>
        </div>
        <p className="text-white/60 text-sm mb-4">{command.description}</p>
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-white/40">
            <i className="fas fa-chart-bar" />
            {command.usage || 0} uses
          </div>
          {command.cooldown && (
            <div className="flex items-center gap-2 text-white/40">
              <i className="fas fa-clock" />
              {command.cooldown}s
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}