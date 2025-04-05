"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import { useUser } from "../contexts/UserContext";
import { useBackendCheck } from "../hooks/useBackendCheck";

interface User {
  id: string;
  username: string;
  avatar: string | null | undefined;
  global_name?: string | null;
}

export default function Navbar() {
  const { user } = useUser();
  const { error: backendError } = useBackendCheck();
  const [isOwner, setIsOwner] = useState<boolean>(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const hasMounted = useRef(false);

  const profileRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  const isDashboard = pathname.includes("/dashboard");
  const isAdminPage = pathname.includes("/admin");

  // Navigation items definition
  const baseNavItems = [
    { path: "/", label: "Home" },
    { path: "/dashboard", label: "Dashboard" },
    { path: "/commands", label: "Commands" },
    { path: "/statistics", label: "Statistics" },
  ];

  const navItems = (!backendError && isOwner)
    ? [...baseNavItems, { path: "/admin", label: "Admin" }]
    : baseNavItems;

  // Check if we're on the current page
  const isActive = useCallback(
    (path: string) => {
      if (path === "/") {
        return pathname === "/";
      }
      return pathname.startsWith(path);
    },
    [pathname]
  );

  // Handle scroll effects
  useEffect(() => {
    hasMounted.current = true;
    const handleScroll = () => {
      if (hasMounted.current) {
        setIsScrolled(window.scrollY > 20);
      }
    };

    handleScroll(); // Initial check
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      hasMounted.current = false;
    };
  }, []);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target as Node)
      ) {
        setIsProfileOpen(false);
      }
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        !(
          event.target instanceof Element &&
          event.target.matches(
            'button[name="Hamburger Menu"], button[name="Hamburger Menu"] *'
          )
        )
      ) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close mobile menu on navigation change
  useEffect(() => {
    setIsMenuOpen(false);
  }, [pathname]);

  // Check owner status
  useEffect(() => {
    const checkOwnerStatus = async () => {
      if (!user || backendError) {
        setIsOwner(false);
        return;
      }

      try {
        const response = await fetch("/api/v1/admin/is_owner", {
          credentials: "include",
        });

        if (!response.ok) throw new Error("Failed to fetch owner status");

        const data = await response.json();
        setIsOwner(Boolean(data.is_owner));
        localStorage.setItem("isOwner", String(data.is_owner));
      } catch (error) {
        console.error("Error checking owner status:", error);
        setIsOwner(false);
        localStorage.setItem("isOwner", "false");
      }
    };

    checkOwnerStatus();
  }, [user, backendError]);

  // Handle logout
  const handleLogout = async () => {
    try {
      const response = await fetch("/api/v1/auth/discord/logout", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Logout failed");
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear storage and redirect regardless of success/failure
      localStorage.clear();
      window.location.href = "/";
    }
  };

  // Get avatar URL
  const getAvatarUrl = (user: User) => {
    if (backendError) return "/default-avatar.png";
    const format = user.avatar?.startsWith("a_") ? "gif" : "png";
    return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${format}?size=1024`;
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{
        y: 0,
        backgroundColor: isAdminPage
          ? "rgba(17, 24, 39, 1)"
          : isDashboard
          ? "rgba(255, 255, 255, 0.1)"
          : hasMounted.current && isScrolled
          ? "rgba(255, 255, 255, 0.1)"
          : "rgba(255, 255, 255, 0)",
      }}
      transition={{ duration: 0.3 }}
      className="fixed w-full z-50 backdrop-blur-lg"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div
            className="flex items-center"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <Link href="/" className="text-white font-bold text-xl">
              Negomi
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-4">
              {navItems.map((item) => (
                <Link key={item.path} href={item.path}>
                  <motion.div
                    className={`relative px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
              group hover:text-white flex items-center ${
                isActive(item.path) ? "text-white" : "text-gray-300"
              }`}
                    whileHover={{ scale: 1.05 }}
                    transition={{
                      type: "spring",
                      stiffness: 400,
                      damping: 17,
                    }}
                  >
                    <span className="relative z-10 pointer-events-none">
                      {item.label}
                      <motion.span
                        className="absolute -bottom-1 left-0 w-full h-[2px] bg-white/70 rounded-full pointer-events-none"
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: isActive(item.path) ? 1 : 0 }}
                        transition={{ duration: 0.2 }}
                      />
                    </span>

                    <AnimatePresence>
                      {isActive(item.path) && (
                        <motion.div
                          className="absolute inset-0 rounded-lg bg-gradient-to-r from-white/20 to-white/10"
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          transition={{ duration: 0.2 }}
                          style={{
                            boxShadow: "0 0 20px rgba(255, 255, 255, 0.1)",
                          }}
                        />
                      )}
                    </AnimatePresence>

                    <motion.div
                      className="absolute inset-0 rounded-lg bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity"
                      initial={false}
                      whileHover={{
                        opacity: 1,
                        boxShadow: "0 0 20px rgba(255, 255, 255, 0.15)",
                      }}
                    />
                  </motion.div>
                </Link>
              ))}
            </div>
          </div>

          {/* Right side: Profile & Mobile menu button */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="relative" ref={profileRef}>
                <motion.div
                  className="flex items-center space-x-3 cursor-pointer group"
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ type: "spring", stiffness: 400, damping: 17 }}
                >
                  <div className="flex items-center space-x-2">
                    <motion.svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="text-gray-300 group-hover:text-white transition-colors hidden md:inline"
                      animate={{ rotate: isProfileOpen ? 180 : 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <path d="M6 9l6 6 6-6" />
                    </motion.svg>
                    <span className="text-white hidden md:inline text-sm">
                      {user.global_name || user.username}
                    </span>
                  </div>
                  <div className="h-8 w-8 rounded-full overflow-hidden ring-2 ring-white/30 hover:ring-white/60 transition-all">
                    {backendError ? (
                      <div className="bg-gray-600 w-full h-full" />
                    ) : (
                      <img
                        src={getAvatarUrl(user)}
                        alt="Avatar"
                        className="h-full w-full object-cover"
                      />
                    )}
                  </div>
                </motion.div>

                <AnimatePresence>
                  {isProfileOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{
                        type: "spring",
                        stiffness: 400,
                        damping: 25,
                      }}
                      className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white/10 backdrop-blur-lg ring-1 ring-white/10 overflow-hidden"
                    >
                      <div className="py-1">
                        {/* Show username in dropdown on mobile */}
                        <div className="block md:hidden px-4 py-2 text-sm text-white border-b border-white/10">
                          {user.global_name || user.username}
                        </div>
                        <button
                          onClick={handleLogout}
                          className="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10 transition-colors"
                        >
                          Logout
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <div className="relative group">
                <Link
                  href={backendError ? "#" : "/api/v1/auth/discord/login"}
                  className={`text-sm md:text-base font-medium transition-colors ${
                    backendError
                      ? "text-gray-500 cursor-not-allowed"
                      : "text-white hover:text-gray-200"
                  }`}
                  onClick={(e) => backendError && e.preventDefault()}
                >
                  Login
                </Link>
                {backendError && (
                  <div
                    className="absolute -top-1 left-1/2 transform -translate-x-1/2 -translate-y-full 
                  opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"
                  >
                    <div className="bg-black/80 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                      Login unavailable - Bot is offline
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Mobile Menu Button */}
            <motion.button
              name="Hamburger Menu"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-white/20 focus:outline-none"
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              <svg
                className="h-6 w-6"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 24 24"
              >
                <motion.path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  animate={{
                    d: isMenuOpen
                      ? "M6 18L18 6M6 6l12 12"
                      : "M4 6h16M4 12h16M4 18h16",
                  }}
                  transition={{ duration: 0.2 }}
                />
              </svg>
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            ref={menuRef}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 30,
              opacity: { duration: 0.2 },
            }}
            className="md:hidden overflow-hidden"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white/5">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200
                    ${
                      isActive(item.path)
                        ? "text-white bg-white/20"
                        : "text-gray-300 hover:text-white hover:bg-white/10"
                    }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
