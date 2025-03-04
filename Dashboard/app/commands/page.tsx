"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Command } from "../types/commands";
import { API_BASE_URL } from '../config';
import CommandCard from "../components/CommandCard";
import PageWrapper from "../components/PageWrapper";

export type FilterType = "all" | "admin" | "user" | "guild";

export default function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([]);
  // const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<FilterType>("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCommands();
  }, []);

  const fetchCommands = async () => {
    try {
      const apiUrl = `${API_BASE_URL}/commands`;

      const response = await fetch(apiUrl);
      const data = await response.json();
      setCommands(Array.isArray(data.commands) ? data.commands : []);
    } catch (error) {
      console.error("Error fetching commands:", error);
      setCommands([]);
    } finally {
      setLoading(false);
    }
  };

  const organizeCategoriesAndCommands = () => {
    const processedCommands = commands.map((cmd) => ({
      ...cmd,
      category:
        commands.filter((c) => c.category === cmd.category).length === 1
          ? "Other"
          : cmd.category,
    }));

    const filteredCommands = processedCommands.filter((cmd) => {
      const searchMatch =
        !searchTerm ||
        cmd.name.toLowerCase().includes(searchTerm.toLowerCase());
      const filterMatch =
        selectedFilter === "all" ||
        (selectedFilter === "admin" && cmd.admin_only) ||
        (selectedFilter === "guild" && cmd.guild_installed) ||
        (selectedFilter === "user" && cmd.user_installed);

      return searchMatch && filterMatch;
    });

    const sortedCategories = Array.from(
      new Set(filteredCommands.map((cmd) => cmd.category))
    ).sort((a, b) => {
      if (a === "Other") return 1;
      if (b === "Other") return -1;
      return a.localeCompare(b);
    });

    return { processedCommands: filteredCommands, sortedCategories };
  };

  const { processedCommands, sortedCategories } =
    organizeCategoriesAndCommands();

  const filterButtons: FilterType[] = ["all", "admin", "user", "guild"];

  return (
    <PageWrapper loading={loading} loadingMessage="Loading commands...">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-5xl font-extrabold text-white text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500"
        >
          Command List
        </motion.h1>

        <motion.div
          className="flex flex-col md:flex-row gap-6 mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="md:w-2/3"
          >
            <input
              type="text"
              placeholder="Search commands..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full p-4 rounded-xl bg-white/10 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-violet-500 backdrop-blur-lg"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="md:w-1/3 flex gap-2"
          >
            {filterButtons.map((filter) => (
              <button
                key={filter}
                onClick={() => setSelectedFilter(filter)}
                className={`flex-1 p-3 rounded-xl transition-all duration-300 ${
                  selectedFilter === filter
                    ? "bg-violet-600 text-white font-bold"
                    : "bg-white/10 text-white/80 hover:bg-white/20"
                }`}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
              </button>
            ))}
          </motion.div>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div
            key={selectedFilter + searchTerm}
            className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {sortedCategories.map((category) => {
              const categoryCommands = processedCommands.filter(
                (cmd) => cmd.category === category
              );

              if (categoryCommands.length === 0) return null;

              return (
                <motion.div
                  key={category}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  className="bg-white/10 backdrop-blur-lg rounded-xl p-8 flex flex-col"
                >
                  <motion.h2
                    className="text-2xl font-bold text-white mb-4"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {category}
                  </motion.h2>
                  <motion.div
                    className="space-y-3 flex-grow"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <AnimatePresence mode="popLayout">
                      {categoryCommands.map((command) => (
                        <CommandCard key={command.name} command={command} />
                      ))}
                    </AnimatePresence>
                  </motion.div>
                </motion.div>
              );
            })}
          </motion.div>
        </AnimatePresence>
      </main>
    </PageWrapper>
  );
}
