"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Navbar from "../components/Navbar"
import Footer from "../components/Footer"

type Command = {
  name: string
  description: string
  usage: string
  type: string
  category: string
  admin_only: boolean
  permissions: string[]
  guild_only: boolean
  cooldown: number | null
  examples: string[]
}

export default function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'admin' | 'slash' | 'user'>('all')
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    fetchCommands()
  }, [])

  const fetchCommands = async () => {
    try {
      const response = await fetch("/api/get_commands")
      const data = await response.json()
      
      // Check if data is an array, if not, use empty array
      setCommands(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error("Error fetching commands:", error)
      setCommands([])
    }
  }

  const organizeCategoriesAndCommands = () => {
    // Move single-command categories to "Other"
    const processedCommands = commands.map(cmd => ({
      ...cmd,
      category: commands.filter(c => c.category === cmd.category).length === 1 ? "Other" : cmd.category
    }));

    // Filter and sort categories based on current filters
    const filteredCommands = processedCommands.filter(cmd => {
      const searchMatch = !searchTerm || cmd.name.toLowerCase().includes(searchTerm.toLowerCase());
      const filterMatch = selectedFilter === 'all' 
        || (selectedFilter === 'admin' && cmd.admin_only)
        || (selectedFilter === 'slash' && cmd.type === 'slash')
        || (selectedFilter === 'user' && !cmd.admin_only && cmd.type !== 'slash'); // Fixed user filter
      
      return searchMatch && filterMatch;
    });

    // Get categories that have visible commands
    const sortedCategories = Array.from(new Set(filteredCommands.map(cmd => cmd.category)))
      .sort((a, b) => {
        if (a === "Other") return 1;
        if (b === "Other") return -1;
        return a.localeCompare(b);
      });

    return { processedCommands: filteredCommands, sortedCategories };
  };

  const { processedCommands, sortedCategories } = organizeCategoriesAndCommands();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-5xl font-extrabold text-white text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500"
        >
          Command List
        </motion.h1>

        {/* Enhanced Search and Filter Section */}
        <motion.div 
          className="flex flex-col md:flex-row gap-6 mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Search Bar */}
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

          {/* Filter Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5}}
            className="md:w-1/3 flex gap-2"
          >
            {['all', 'admin', 'slash', 'user'].map((filter) => (
              <button
                key={filter}
                onClick={() => setSelectedFilter(filter as any)}
                className={`flex-1 p-3 rounded-xl transition-all duration-300 ${
                  selectedFilter === filter
                    ? 'bg-violet-600 text-white font-bold'
                    : 'bg-white/10 text-white/80 hover:bg-white/20'
                }`}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
              </button>
            ))}
          </motion.div>
        </motion.div>

        {/* Enhanced Categories Grid */}
        <AnimatePresence mode="wait">
          <motion.div 
            key={selectedFilter + searchTerm} // Force re-render on filter change
            className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {sortedCategories.map((category, categoryIndex) => {
              const categoryCommands = processedCommands.filter(cmd => cmd.category === category);
              
              if (categoryCommands.length === 0) return null;

              return (
                <motion.div
                  key={category}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3}}
                  className="bg-white/10 backdrop-blur-lg rounded-xl p-8 flex flex-col" // Added flex-col
                >
                  <motion.h2 
                    className="text-2xl font-bold text-white mb-4" // Reduced margin
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {category}
                  </motion.h2>
                  <motion.div 
                    className="space-y-3 flex-grow" // Reduced space and added flex-grow
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <AnimatePresence mode="popLayout">
                      {categoryCommands.map((command, cmdIndex) => (
                        <motion.div
                          key={command.name}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          transition={{ 
                            duration: 0.2,
                          }}
                          whileHover={{ 
                            scale: 1.02,
                            backgroundColor: "rgba(255, 255, 255, 0.15)",
                            transition: { duration: 0.1 } // Faster hover transition
                          }}
                          className="bg-white/5 rounded-lg p-4 transition-all" // Reduced padding
                        >
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-lg font-semibold text-white">{command.name}</h3>
                            <div className="flex gap-2">
                              {command.admin_only && (
                                <span className="px-2 py-1 rounded-md text-xs font-medium bg-red-500/20 text-red-300 border border-red-500/20">
                                  Admin
                                </span>
                              )}
                              <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                                command.type === 'slash'
                                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/20'
                                  : 'bg-green-500/20 text-green-300 border border-green-500/20'
                              }`}>
                                {command.type}
                              </span>
                            </div>
                          </div>
                          <p className="text-gray-300 text-sm mb-2">{command.description}</p>
                          <p className="text-gray-400 text-xs">
                            Usage: <span className="font-mono bg-black/20 px-2 py-0.5 rounded">{command.usage}</span>
                          </p>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </motion.div>
                </motion.div>
              );
            })}
          </motion.div>
        </AnimatePresence>
      </main>
      <Footer />
    </div>
  )
}

