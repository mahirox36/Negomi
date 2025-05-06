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
export type SortType = "name" | "category";

const sortOptions: { label: string; value: SortType }[] = [
  { label: "Name", value: "name" },
  { label: "Category", value: "category" }
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
      const commandsRes = await axios.get("/api/v1/bot/commands", { withCredentials: true });
      setCommands(commandsRes.data);
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
          className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10 mb-8"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl shadow-inner">
              <i className="fas fa-terminal text-2xl text-white/90"></i>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
                Command List
              </h1>
              <p className="text-lg text-white/70 mt-1">
                Browse and search through {commands.length} available commands
              </p>
            </div>
          </div>
        </motion.div>

        <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 mb-8">
          {/* Search and Filters */}
          <div className="p-6 border-b border-white/10">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
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
                    className="w-full p-4 pl-12 rounded-xl bg-white/5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 border border-white/10"
                  />
                  <i className="fas fa-magnifying-glass absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
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
                  className="w-full p-4 rounded-xl bg-white/5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 border border-white/10"
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
                        ? "bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-lg"
                        : "bg-white/5 text-white/60 hover:bg-white/10 border border-white/10"
                    }`}
                  >
                    <i className={`fas fa-${mode === "grid" ? "table-cells" : mode === "list" ? "bars" : "list"}`} />
                  </button>
                ))}
              </motion.div>
            </div>

            {/* Filter Pills */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-wrap gap-2 mt-4"
            >
              {[
                { type: "all", icon: "globe", label: "All" },
                { type: "admin", icon: "shield", label: "Admin" },
                { type: "user", icon: "user", label: "User" },
                { type: "guild", icon: "server", label: "Server" }
              ].map(({ type, icon, label }) => (
                <button
                  key={type}
                  onClick={() => setSelectedFilter(type as FilterType)}
                  className={`px-4 py-2 rounded-full transition-all duration-300 ${
                    selectedFilter === type
                      ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg"
                      : "bg-white/5 text-white/60 hover:bg-white/10 border border-white/10"
                  }`}
                >
                  <i className={`fas fa-${icon} mr-2`} />
                  {label}
                </button>
              ))}
            </motion.div>
          </div>

          {/* Command Categories */}
          <div className="p-6">
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
                    className="bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-sm rounded-xl overflow-hidden border border-white/10"
                  >
                    <div className="p-4 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-b border-white/10">
                      <h2 className="text-lg font-semibold text-white flex items-center justify-between">
                        {category}
                        <span className="text-sm text-white/60 px-2 py-1 rounded-full bg-white/5">
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
          </div>
        </div>

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
                className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 backdrop-blur-xl rounded-xl p-6 max-w-2xl w-full mx-4 overflow-auto max-h-[90vh] border border-white/10"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-start mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 flex items-center justify-center bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-lg">
                      <i className="fas fa-terminal text-lg text-white/90"></i>
                    </div>
                    <h2 className="text-2xl font-bold text-white bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">
                      /{selectedCommand.name}
                    </h2>
                  </div>
                  <button
                    onClick={() => setSelectedCommand(null)}
                    className="text-white/60 hover:text-white bg-white/5 hover:bg-white/10 rounded-lg p-2 transition-colors"
                  >
                    <i className="fas fa-xmark" />
                  </button>
                </div>
                <div className="prose prose-invert max-w-none">
                  <div className="bg-white/5 rounded-lg p-4 mb-6">
                    <p className="text-lg text-white/80">
                      {selectedCommand.description}
                    </p>
                  </div>
                  {selectedCommand.options && selectedCommand.options.length > 0 && (
                    <>
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <i className="fas fa-sliders text-indigo-400" />
                        Command Options
                      </h3>
                      <div className="space-y-3">
                        {selectedCommand.options.map((option) => (
                          <div
                            key={option.name}
                            className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-lg p-4 border border-white/10"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded">
                                  {option.name}
                                </span>
                                {option.required && (
                                  <span className="text-xs bg-red-500/10 text-red-400 px-2 py-1 rounded">
                                    Required
                                  </span>
                                )}
                              </div>
                              <span className="text-sm text-white/60 bg-white/5 px-2 py-1 rounded">
                                {option.type}
                              </span>
                            </div>
                            <p className="text-sm text-white/80">
                              {option.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                  <div className="mt-6 flex items-center gap-4">
                    <div className="text-sm text-white/60 bg-white/5 px-3 py-2 rounded-lg">
                      <i className="fas fa-clock mr-2" />
                      Cooldown: {selectedCommand.cooldown || "None"}
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
