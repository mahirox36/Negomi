"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import { useUser } from "../contexts/UserContext";

interface User {
  id: string;
  username: string;
  avatar: string;
  global_name?: string;
}

export default function Navbar() {
  const { user } = useUser();
  const [isOwner, setIsOwner] = useState<boolean | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const [isAtTop, setIsAtTop] = useState(true);

  useEffect(() => {
    const handleScroll = () => {
      setIsAtTop(window.scrollY < 100);
    };

    // Initial check
    handleScroll();

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const isActive = (path: string) => {
    return pathname === path;
  };

  // Generate unique layoutId based on current page
  const getLayoutId = () => {
    return pathname.replace("/", "page-");
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target as Node)
      ) {
        setIsProfileOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/auth/discord/logout", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Logout failed");
      }

      // Clear local storage
      localStorage.clear();

      // Force page reload to clear all state
      window.location.href = "/";
    } catch (error) {
      console.error("Logout error:", error);
      // Still clear storage and redirect on error
      localStorage.clear();
      window.location.href = "/";
    }
  };

  useEffect(() => {
    const checkOwnerStatus = async () => {
      // Check if we already have the owner status in localStorage
      const cachedOwnerStatus = localStorage.getItem("isOwner");

      if (user && cachedOwnerStatus === null) {
        try {
          const response = await fetch("/api/admin/is_owner", {
            credentials: "include",
          });
          const data = await response.json();
          console.log("Owner status:", data.is_owner);
          setIsOwner(data.is_owner);
          // Cache the result
          localStorage.setItem("isOwner", data.is_owner.toString());
        } catch (error) {
          console.error("Error checking owner status:", error);
          setIsOwner(false);
          localStorage.setItem("isOwner", "false");
        }
      } else if (cachedOwnerStatus !== null) {
        setIsOwner(cachedOwnerStatus === "true");
      }
    };

    checkOwnerStatus();
  }, [user]);

  const baseNavItems = [
    { path: "/", label: "Home" },
    { path: "/dashboard", label: "Dashboard" },
    { path: "/commands", label: "Commands" },
    { path: "/statistics", label: "Statistics" },
  ];

  const navItems = isOwner
    ? [...baseNavItems, { path: "/admin", label: "Admin" }]
    : baseNavItems;

  const handleNavigation = (
    e: React.MouseEvent<HTMLAnchorElement>,
    path: string
  ) => {
    // No special handling needed anymore
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed w-full bg-white/10 backdrop-blur-lg"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 no-select">
        <div className="flex items-center justify-between h-16">
          <motion.div
            className="flex items-center"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link href="/" className="text-white font-bold text-xl">
              Negomi
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4 relative">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  onClick={(e) => handleNavigation(e, item.path)}
                  className={`relative px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200
                    ${
                      isActive(item.path)
                        ? "text-white"
                        : "text-gray-300 hover:text-white"
                    }`}
                >
                  <span className="relative z-10">{item.label}</span>
                  {isActive(item.path) && (
                    <motion.div
                      layoutId="navbar-indicator"
                      className="absolute inset-x-0 top-0 h-full rounded-md bg-white/20"
                      initial={false}
                      transition={{
                        type: "spring",
                        bounce: 0.15,
                        duration: 0.5,
                        layout: {
                          axis: "x"
                        }
                      }}
                    />
                  )}
                </Link>
              ))}
            </div>
          </div>

          {/* Profile Section - Now visible on both desktop and mobile */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="relative" ref={profileRef}>
                <motion.div
                  className="flex items-center space-x-4 cursor-pointer group"
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
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
                    <span className="text-white hidden md:inline">
                      {user.global_name || user.username}
                    </span>
                  </div>
                  <img
                    src={`https://cdn.discordapp.com/avatars/${user.id}/${
                      user.avatar
                    }.${user.avatar?.startsWith("a_") ? "gif" : "png"}`}
                    alt="Avatar"
                    className="w-8 h-8 rounded-full"
                  />
                </motion.div>

                <AnimatePresence>
                  {isProfileOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute md:right-0 -right-4 mt-2 w-48 rounded-md shadow-lg bg-white/10 backdrop-blur-lg ring-1 ring-black ring-opacity-5"
                    >
                      <div className="py-1">
                        {/* Show username in dropdown on mobile */}
                        <div className="block md:hidden px-4 py-2 text-sm text-white border-b border-white/10">
                          {user.global_name || user.username}
                        </div>
                        <button
                          onClick={handleLogout}
                          className="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/20"
                        >
                          Logout
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link
                href="/api/auth/discord/login"
                className="text-white text-sm md:text-base"
              >
                Login
              </Link>
            )}

            {/* Mobile Menu Button - Now after profile section */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-white/20 focus:outline-none"
            >
              <svg
                className="h-6 w-6"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d={
                    isOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"
                  }
                />
              </svg>
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Menu - Navigation links only */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden overflow-hidden"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  onClick={(e) => {
                    setIsOpen(false);
                    handleNavigation(e, item.path);
                  }}
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
