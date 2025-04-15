"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Fuse from 'fuse.js';
import { Command } from "../types/commands";
import CommandCard from "../components/CommandCard";
import PageWrapper from "../components/PageWrapper";
import axios from "axios";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs";

export type FilterType = "all" | "admin" | "user" | "guild";
export type ViewMode = "grid" | "list" | "compact";
export type SortType = "name" | "category" | "popularity" | "newest";

const sortOptions: { label: string; value: SortType }[] = [
  { label: "Name", value: "name" },
  { label: "Category", value: "category" },
  { label: "Most Used", value: "popularity" },
  { label: "Newest", value: "newest" }
];

export default function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<FilterType>("all");
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [sortBy, setSortBy] = useState<SortType>("category");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedCommand, setSelectedCommand] = useState<Command | null>(null);

  const fuse = useMemo(() => new Fuse(commands, {
    keys: ['name', 'description', 'category'],
    threshold: 0.4,
    shouldSort: true
  }), [commands]);

  useEffect(() => {
    fetchCommands();
  }, []);

  const fetchCommands = async () => {
    try {
      const [commandsRes, statsRes] = await Promise.all([
        axios.get("/api/v1/bot/commands", { withCredentials: true }),
        axios.get("/api/v1/bot/command-stats", { withCredentials: true })
      ]);

      const commandsWithStats = commandsRes.data.map((cmd: Command) => ({
        ...cmd,
        usage: statsRes.data[cmd.name] || 0,
        lastUsed: statsRes.data[`${cmd.name}_last_used`] || null
      }));

      setCommands(commandsWithStats);
    } catch (error) {
      console.error("Error fetching commands:", error);
      setCommands([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedCommands = useMemo(() => {
    let result = [...commands];

    // Apply search
    if (searchTerm) {
      result = fuse.search(searchTerm).map(({ item }) => item);
    }

    // Apply filters
    result = result.filter(cmd => {
      if (selectedFilter === "all") return true;
      if (selectedFilter === "admin") return cmd.admin_only;
      if (selectedFilter === "guild") return cmd.guild_installed;
      if (selectedFilter === "user") return cmd.user_installed;
      return true;
    });

    // Apply sorting
    result.sort((a, b) => {
      switch (sortBy) {
        case "name":
          return a.name.localeCompare(b.name);
        case "category":
          return a.category.localeCompare(b.category);
        case "popularity":
          return (b.usage || 0) - (a.usage || 0);
        case "newest":
          return new Date(b.lastUsed || 0).getTime() - new Date(a.lastUsed || 0).getTime();
        default:
          return 0;
      }
    });

    return result;
  }, [commands, searchTerm, selectedFilter, sortBy, fuse]);

  const categories = useMemo(() => {
    const cats = new Set(filteredAndSortedCommands.map(cmd => cmd.category));
    return Array.from(cats).sort();
  }, [filteredAndSortedCommands]);

  const commandsByCategory = useMemo(() => {
    return categories.reduce((acc, category) => {
      acc[category] = filteredAndSortedCommands.filter(cmd => cmd.category === category);
      return acc;
    }, {} as Record<string, Command[]>);
  }, [categories, filteredAndSortedCommands]);

  return (
    <PageWrapper loading={loading} loadingMessage="Loading commands...">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white text-center mb-2">
            Command List
          </h1>
          <p className="text-white/60 text-center">
            Browse and search through {commands.length} available commands
          </p>
        </motion.div>

        {/* Search and Filters */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:col-span-6"
          >
            <div className="relative">
              <input
                type="text"
                placeholder="Search commands..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-4 pl-12 rounded-xl bg-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 backdrop-blur-lg"
              />
              <i className="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:col-span-4"
          >
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortType)}
              className="w-full p-4 rounded-xl bg-white/10 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 backdrop-blur-lg"
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value} className="bg-gray-800">
                  {option.label}
                </option>
              ))}
            </select>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:col-span-2 flex gap-2"
          >
            {["grid", "list", "compact"].map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode as ViewMode)}
                className={`flex-1 p-3 rounded-xl transition-all duration-300 ${
                  viewMode === mode
                    ? "bg-violet-600 text-white"
                    : "bg-white/10 text-white/60 hover:bg-white/20"
                }`}
              >
                <i className={`fas fa-${mode === "grid" ? "grid" : mode === "list" ? "list" : "list-ul"}`} />
              </button>
            ))}
          </motion.div>
        </div>

        {/* Filter Pills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap gap-2 mb-8"
        >
          {["all", "admin", "user", "guild"].map((filter) => (
            <button
              key={filter}
              onClick={() => setSelectedFilter(filter as FilterType)}
              className={`px-4 py-2 rounded-full transition-all duration-300 ${
                selectedFilter === filter
                  ? "bg-violet-600 text-white"
                  : "bg-white/10 text-white/60 hover:bg-white/20"
              }`}
            >
              <i className={`fas fa-${
                filter === "all" ? "globe" :
                filter === "admin" ? "shield" :
                filter === "user" ? "user" : "server"
              } mr-2`} />
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </motion.div>

        {/* Command Categories */}
        <AnimatePresence mode="wait">
          <motion.div
            key={`${selectedFilter}-${searchTerm}-${viewMode}-${sortBy}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className={`grid gap-6 ${
              viewMode === "grid"
                ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                : "grid-cols-1"
            }`}
          >
            {categories.map((category) => (
              <motion.div
                key={category}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-white/10 backdrop-blur-lg rounded-xl overflow-hidden"
              >
                <div className="p-4 bg-white/5">
                  <h2 className="text-lg font-semibold text-white">
                    {category}
                    <span className="ml-2 text-sm text-white/60">
                      {commandsByCategory[category].length} commands
                    </span>
                  </h2>
                </div>
                <div className={`p-4 ${viewMode === "compact" ? "space-y-1" : "space-y-4"}`}>
                  <AnimatePresence mode="popLayout">
                    {commandsByCategory[category].map((command) => (
                      <CommandCard
                        key={command.name}
                        command={command}
                        viewMode={viewMode}
                        onClick={() => setSelectedCommand(command)}
                      />
                    ))}
                  </AnimatePresence>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>

        {/* Command Detail Modal */}
        <AnimatePresence>
          {selectedCommand && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
              onClick={() => setSelectedCommand(null)}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-gray-900 rounded-xl p-6 max-w-2xl w-full mx-4 overflow-auto max-h-[90vh]"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold text-white">
                    /{selectedCommand.name}
                  </h2>
                  <button
                    onClick={() => setSelectedCommand(null)}
                    className="text-white/60 hover:text-white"
                  >
                    <i className="fas fa-times" />
                  </button>
                </div>
                <div className="prose prose-invert max-w-none">
                  <p className="text-lg text-white/80 mb-4">
                    {selectedCommand.description}
                  </p>
                  {selectedCommand.options && selectedCommand.options.length > 0 && (
                    <>
                      <h3 className="text-lg font-semibold text-white mt-4 mb-2">
                        Options
                      </h3>
                      <div className="space-y-2">
                        {selectedCommand.options.map((option) => (
                          <div
                            key={option.name}
                            className="bg-white/5 rounded-lg p-3"
                          >
                            <div className="flex items-start justify-between">
                              <div>
                                <span className="font-mono text-violet-400">
                                  {option.name}
                                </span>
                                {option.required && (
                                  <span className="ml-2 text-xs text-red-400">
                                    Required
                                  </span>
                                )}
                              </div>
                              <span className="text-sm text-white/60">
                                {option.type}
                              </span>
                            </div>
                            <p className="text-sm text-white/80 mt-1">
                              {option.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                  <div className="mt-4 flex items-center gap-4 text-sm text-white/60">
                    <div>
                      <i className="fas fa-clock mr-2" />
                      Cooldown: {selectedCommand.cooldown || "None"}
                    </div>
                    <div>
                      <i className="fas fa-chart-bar mr-2" />
                      Used {selectedCommand.usage || 0} times
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </PageWrapper>
  );
}
