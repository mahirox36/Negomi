"use client";

import { AnimatePresence, motion } from "framer-motion";
import { User, Guild } from "../types/discord";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

interface SidebarProps {
  user?: User;
  guilds?: Guild[];
}

export default function Sidebar({ guilds }: SidebarProps) {
  const [joinedGuilds, setJoinedGuilds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const adminGuilds =
    guilds?.filter(
      (g) =>
        g.permissions && (BigInt(g.permissions) & BigInt(0x8)) === BigInt(0x8)
    ) || [];

  // Fetch joined guilds
  useEffect(() => {
    const fetchJoinedGuilds = async () => {
      if (adminGuilds.length > 0) {
        setIsLoading(true);
        try {
          const res = await fetch("/api/v1/guilds/filter_joined", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ guilds: adminGuilds.map((g) => g.id) }),
            credentials: "include",
          });
          const data = await res.json();
          setJoinedGuilds(data);
        } catch (error) {
          console.error("Failed to fetch joined guilds:", error);
        } finally {
          setIsLoading(false);
        }
      } else {
        setJoinedGuilds([]);
        setIsLoading(false);
      }
    };

    fetchJoinedGuilds();
  }, [guilds]); // Depend on the original guilds prop instead

  // Close mobile menu on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        !target.closest(".sidebar-content") &&
        !target.closest(".mobile-menu-button")
      ) {
        setIsMobileMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getGuildIcon = (guild: Guild) => {
    if (!guild.icon) {
      const canvas = document.createElement("canvas");
      canvas.width = 100;
      canvas.height = 100;
      const ctx = canvas.getContext("2d");
      if (!ctx) return "/default-guild-icon.png";

      // Generate background color
      const hashCode = guild.name
        .split("")
        .reduce((acc, char) => char.charCodeAt(0) + ((acc << 5) - acc), 0);
      const hue = Math.abs(hashCode % 360);
      const backgroundColor = `hsl(${hue}, 70%, 60%)`;
      ctx.fillStyle = backgroundColor;
      ctx.fillRect(0, 0, 100, 100);

      // Calculate brightness of background color
      const l = 60; // lightness from HSL color
      // Use white text for dark backgrounds, black text for light backgrounds
      const textColor = l > 50 ? "#000000" : "#ffffff";

      // Get initials
      const initials = guild.name
        .split(" ")
        .map((word) => word[0])
        .join("")
        .substring(0, 2)
        .toUpperCase();

      // Add text with calculated color
      ctx.fillStyle = textColor;
      ctx.font = "40px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(initials, 51, 55);

      return canvas.toDataURL();
    }
    // Check if the icon hash starts with 'a_' which indicates it's an animated icon (GIF)
    if (guild.icon.startsWith("a_")) {
      return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.gif`;
    }
    return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`;
  };

  // Separate guilds into joined and not joined
  const joinedGuildsList = adminGuilds.filter((guild) =>
    joinedGuilds.includes(guild.id)
  );
  const notJoinedGuildsList = adminGuilds.filter(
    (guild) => !joinedGuilds.includes(guild.id)
  );

  return (
    <div className="lg:w-72">
      {/* Enhanced Mobile Menu Button */}
      <motion.button
        className="lg:hidden fixed top-20 left-4 z-50 p-3 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 backdrop-blur-xl border border-white/20 shadow-xl mobile-menu-button overflow-hidden"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        whileTap={{ scale: 0.95 }}
        whileHover={{ scale: 1.05 }}
      >
        {/* Animated background */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-blue-500/30"
          animate={{
            opacity: isMobileMenuOpen ? 1 : 0,
            scale: isMobileMenuOpen ? 1 : 0.8,
          }}
          transition={{ duration: 0.3 }}
        />

        {/* Icon container */}
        <motion.div
          className="relative w-6 h-6 flex items-center justify-center"
          animate={{ rotate: isMobileMenuOpen ? 180 : 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <AnimatePresence mode="wait">
            {isMobileMenuOpen ? (
              <motion.i
                key="close"
                className="fas fa-times text-white text-lg"
                initial={{ opacity: 0, rotate: -90 }}
                animate={{ opacity: 1, rotate: 0 }}
                exit={{ opacity: 0, rotate: 90 }}
                transition={{ duration: 0.2 }}
              />
            ) : (
              <motion.i
                key="menu"
                className="fas fa-bars text-white text-lg"
                initial={{ opacity: 0, rotate: 90 }}
                animate={{ opacity: 1, rotate: 0 }}
                exit={{ opacity: 0, rotate: -90 }}
                transition={{ duration: 0.2 }}
              />
            )}
          </AnimatePresence>
        </motion.div>

        {/* Ripple effect */}
        <motion.div
          className="absolute inset-0 rounded-2xl"
          animate={{
            background: isMobileMenuOpen
              ? "radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%)"
              : "radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%)",
          }}
          transition={{ duration: 0.3 }}
        />
      </motion.button>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Enhanced Mobile Sidebar */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            className="lg:hidden sidebar-content fixed left-0 top-0 bottom-0 w-80 backdrop-blur-xl border-r border-white/20 shadow-2xl z-50 overflow-hidden"
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 30,
              opacity: { duration: 0.2 },
            }}
          >
            {/* Animated background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-blue-500/5 to-emerald-500/10 opacity-50" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/20 via-transparent to-blue-500/20" />

            <div className="relative h-full overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent pt-20 px-6">
              <motion.div
                className="space-y-6"
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <div className="mb-8">
                  <motion.h3
                    className="text-white/90 text-lg font-bold mb-6 px-2 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent"
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    Your Servers
                  </motion.h3>

                  {isLoading ? (
                    <motion.div
                      className="text-white/70 text-center py-8 flex flex-col items-center gap-4"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <motion.div
                        className="w-8 h-8 border-2 border-purple-500/30 border-t-purple-500 rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                      />
                      <span className="font-medium">Loading servers...</span>
                    </motion.div>
                  ) : (
                    <>
                      {/* Joined servers */}
                      <div className="space-y-3">
                        {joinedGuildsList.map((guild, index) => (
                          <motion.div
                            key={guild.id}
                            initial={{ x: -30, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{
                              delay: 0.4 + index * 0.1,
                              type: "spring",
                              stiffness: 300,
                            }}
                          >
                            <Link
                              href={`/dashboard/server/${guild.id}/overview`}
                              className="flex items-center space-x-4 p-4 rounded-xl hover:bg-white/10 text-white group transition-all border border-transparent hover:border-white/20 bg-white/5 backdrop-blur-sm"
                              onClick={() => setIsMobileMenuOpen(false)}
                            >
                              <motion.div
                                whileHover={{ scale: 1.1, rotate: 5 }}
                                whileTap={{ scale: 0.95 }}
                                className="relative"
                              >
                                <Image
                                  src={getGuildIcon(guild)}
                                  alt={guild.name}
                                  width={48}
                                  height={48}
                                  className="rounded-2xl shadow-lg border-2 border-white/20"
                                />
                              </motion.div>
                              <div className="flex-1 min-w-0">
                                <span className="block font-semibold truncate group-hover:text-purple-300 transition-colors">
                                  {guild.name}
                                </span>
                              </div>
                              <motion.i
                                className="fas fa-chevron-right text-white/30 group-hover:text-white/60 transition-colors"
                                whileHover={{ x: 2 }}
                              />
                            </Link>
                          </motion.div>
                        ))}
                      </div>

                      {/* Not joined servers */}
                      {notJoinedGuildsList.length > 0 && (
                        <motion.div
                          className="mt-8 pt-6 border-t border-white/20"
                          initial={{ y: 20, opacity: 0 }}
                          animate={{ y: 0, opacity: 1 }}
                          transition={{ delay: 0.6 }}
                        >
                          <h4 className="text-white/80 text-sm font-bold mb-4 px-2 uppercase tracking-wider bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
                            Available Servers
                          </h4>
                          <div className="space-y-3">
                            {notJoinedGuildsList.map((guild, index) => (
                              <motion.div
                                key={guild.id}
                                initial={{ x: -30, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{
                                  delay: 0.7 + index * 0.1,
                                  type: "spring",
                                  stiffness: 300,
                                }}
                              >
                                <motion.a
                                  href={`/api/v1/auth/bot/invite?guild_id=${guild.id}`}
                                  className="flex items-center space-x-4 p-4 rounded-xl hover:bg-white/10 text-white/70 hover:text-white group transition-all border border-white/10 hover:border-emerald-500/30 bg-white/5 backdrop-blur-sm relative overflow-hidden"
                                  whileHover={{ scale: 1.02 }}
                                  whileTap={{ scale: 0.98 }}
                                >
                                  {/* Hover effect background */}
                                  <motion.div
                                    className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                                    initial={false}
                                  />

                                  <motion.div
                                    whileHover={{ scale: 1.1 }}
                                    className="relative"
                                  >
                                    <Image
                                      src={getGuildIcon(guild)}
                                      alt={guild.name}
                                      width={48}
                                      height={48}
                                      className="rounded-2xl opacity-70 group-hover:opacity-100 transition-opacity shadow-lg border-2 border-white/10 group-hover:border-emerald-500/30"
                                    />
                                    <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-gradient-to-tl from-emerald-500 to-indigo-500 rounded-full border border-slate-900 flex items-center justify-center">
                                      <i className="fas fa-plus text-white text-xs" />
                                    </div>
                                  </motion.div>

                                  <div className="flex-1 min-w-0">
                                    <span className="block font-semibold truncate group-hover:text-emerald-300 transition-colors">
                                      {guild.name}
                                    </span>
                                    <span className="text-white/50 text-sm font-medium group-hover:text-white/70 transition-colors">
                                      Click to add bot
                                    </span>
                                  </div>

                                  <span className="text-xs bg-gradient-to-r from-pink-500/30 to-purple-600/50 border border-pink-500/30 px-3 py-1.5 rounded-full text-pink-300 font-bold group-hover:from-pink-500/30 group-hover:to-purple-600/50 transition-all">
                                  Add
                                </span>
                                </motion.a>
                              </motion.div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </>
                  )}
                </div>
              </motion.div>

              {/* Bottom gradient fade */}
              <div className="h-20 bg-gradient-to-t from-slate-900/50 to-transparent pointer-events-none" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enhanced Desktop Sidebar */}
      <motion.div
        className="hidden lg:block sidebar-content fixed left-0 top-16 bottom-0 w-72 backdrop-blur-xl border-r border-white/10 shadow-2xl overflow-hidden"
        initial={{ x: -50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
        {/* Background effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 via-blue-500/3 to-purple-500/5" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/10 via-transparent to-blue-500/10" />

        <div className="relative h-full overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent pt-6 px-6">
          <div className="space-y-6">
            <div className="mb-8">
              <h3 className="text-sm font-bold mb-4 px-2 uppercase tracking-wider bg-gradient-to-r from-pink-200/90 via-purple-300/90 to-purple-500/90 bg-clip-text text-transparent">
                Your Servers
              </h3>

              {isLoading ? (
                <div className="text-white/70 text-center py-6 flex flex-col items-center gap-3">
                  <motion.div
                    className="w-6 h-6 border-2 border-purple-500/30 border-t-purple-500 rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  />
                  <span className="text-sm font-medium">
                    Loading servers...
                  </span>
                </div>
              ) : (
                <>
                  {/* Joined servers */}
                  <div className="space-y-2">
                    {joinedGuildsList.map((guild, index) => (
                      <motion.div
                        key={guild.id}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <Link
                          href={`/dashboard/server/${guild.id}/overview`}
                          className="flex items-center space-x-3 p-3 rounded-xl hover:bg-white/10 text-white group transition-all border border-transparent hover:border-white/20 bg-white/5"
                        >
                          <motion.div
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            className="relative"
                          >
                            <Image
                              src={getGuildIcon(guild)}
                              alt={guild.name}
                              width={40}
                              height={40}
                              className="rounded-xl shadow-md border-2 border-white/20"
                            />
                          </motion.div>
                          <div className="flex-1 min-w-0">
                            <span className="block font-semibold truncate text-sm group-hover:text-purple-300 transition-colors">
                              {guild.name}
                            </span>
                          </div>
                          <motion.i
                            className="fas fa-chevron-right text-xs text-white/30 group-hover:text-white/60 transition-colors"
                            whileHover={{ x: 1 }}
                          />
                        </Link>
                      </motion.div>
                    ))}
                  </div>

                  {/* Not joined servers */}
                  {notJoinedGuildsList.length > 0 && (
                    <div className="mt-6 pt-4 border-t border-white/20">
                      <h4 className="text-xs font-bold mb-3 px-2 uppercase tracking-wider bg-gradient-to-r from-pink-400/90 to-purple-500/90 bg-clip-text text-transparent">
                        Available Servers
                      </h4>
                      <div className="space-y-2">
                        {notJoinedGuildsList.map((guild, index) => (
                          <motion.div
                            key={guild.id}
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.3 + index * 0.1 }}
                          >
                            <motion.a
                              href={`/api/v1/auth/bot/invite?guild_id=${guild.id}`}
                              className="flex items-center space-x-3 p-3 rounded-xl hover:bg-white/10 text-white/70 hover:text-white group transition-all border border-white/10 hover:border-pink-500/30 bg-white/5 relative overflow-hidden"
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                            >
                              <motion.div
                                className="absolute inset-0 bg-gradient-to-r from-pink-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                                initial={false}
                              />

                              <motion.div
                                whileHover={{ scale: 1.1 }}
                                className="relative"
                              >
                                <Image
                                  src={getGuildIcon(guild)}
                                  alt={guild.name}
                                  width={40}
                                  height={40}
                                  className="rounded-xl opacity-70 group-hover:opacity-100 transition-opacity shadow-md border-2 border-white/10 group-hover:border-pink-500/30"
                                />
                                <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-gradient-to-tl from-emerald-500 to-indigo-500 rounded-full border border-slate-900 flex items-center justify-center">
                                  <i className="fas fa-plus text-white text-xs" />
                                </div>
                              </motion.div>

                              <div className="flex-1 min-w-0">
                                <span className="block font-semibold truncate text-sm group-hover:text-pink-400 transition-colors">
                                  {guild.name}
                                </span>
                                <span className="text-white/50 text-xs font-medium group-hover:text-white/70 transition-colors">
                                  Add bot
                                </span>
                              </div>

                              <motion.div
                                className="flex items-center"
                                whileHover={{ scale: 1.1 }}
                              >
                                <span className="text-xs bg-gradient-to-r from-pink-500/30 to-purple-600/50 border border-pink-500/30 px-2 py-1 rounded-lg text-pink-300 font-bold group-hover:from-pink-500/30 group-hover:to-purple-600/50 transition-all">
                                  Add
                                </span>
                              </motion.div>
                            </motion.a>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
// Enhanced debounce function with better TypeScript support
function debounce<T extends (...args: any[]) => any>(func: T, wait: number) {
  let timeoutId: NodeJS.Timeout;

  const debouncedFunc = (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    return new Promise<ReturnType<T>>((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await func(...args);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, wait);
    });
  };

  debouncedFunc.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  };

  debouncedFunc.flush = async (...args: Parameters<T>) => {
    debouncedFunc.cancel();
    return await func(...args);
  };

  return debouncedFunc;
}
