"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import { getDiscordLoginUrl } from "../utils/auth";
import { useUser } from "../contexts/UserContext";
import { API_BASE_URL } from "../config";

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
  const [activeSection, setActiveSection] = useState("");
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
    // Remove scroll check for non-home pages to make transitions instant
    if (!path.startsWith("/#")) {
      return pathname === path;
    }

    // Home page and section checks remain the same
    if (path === "/") {
      return pathname === "/" && isAtTop && !activeSection;
    }

    if (path.startsWith("/#") && pathname === "/") {
      return activeSection === path.substring(2);
    }

    return false;
  };

  // Generate unique layoutId based on current active section/page
  const getLayoutId = () => {
    if (pathname === "/") {
      return activeSection ? `section-${activeSection}` : "home";
    }
    return pathname.replace("/", "page-");
  };

  useEffect(() => {
    const handleScroll = () => {
      if (pathname !== "/") {
        setActiveSection("");
        return;
      }

      // Check if we're at the top of the page
      if (window.scrollY < 100) {
        setActiveSection("");
        return;
      }

      const sections = ["features", "setup"];
      const viewportMiddle = window.innerHeight / 2;

      // Find the section closest to the middle of the viewport
      let closestSection = "";
      let closestDistance = Infinity;

      sections.forEach((section) => {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          const distance = Math.abs(
            rect.top + rect.height / 2 - viewportMiddle
          );

          if (distance < closestDistance) {
            closestDistance = distance;
            closestSection = section;
          }
        }
      });

      setActiveSection(closestSection);
    };

    // Run once immediately to set initial state
    handleScroll();

    // Add smooth scroll behavior
    const handleNavClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const href = target.getAttribute("href");

      if (href?.startsWith("/#")) {
        e.preventDefault();
        const sectionId = href.replace("/#", "");
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: "smooth" });
        }
      }
    };

    document.querySelectorAll('a[href^="/#"]').forEach((link) => {
      link.addEventListener("click", handleNavClick as any);
    });

    // Throttle scroll event for better performance
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      document.querySelectorAll('a[href^="/#"]').forEach((link) => {
        link.removeEventListener("click", handleNavClick as any);
      });
    };
  }, [pathname, activeSection]); // Add pathname as dependency

  // Add click outside handler
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

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("isOwner"); // Clear the cached owner status
    window.location.reload();
  };

  useEffect(() => {
    const checkOwnerStatus = async () => {
      // Check if we already have the owner status in localStorage
      const cachedOwnerStatus = localStorage.getItem('isOwner');
      
      if (user && cachedOwnerStatus === null) {
        try {
          const response = await fetch(
            `${API_BASE_URL}/admin/is_owner`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: user.id }),
              credentials: "include",
            }
          );
          const data = await response.json();
          console.log("Owner status:", data.is_owner);
          setIsOwner(data.is_owner);
          // Cache the result
          localStorage.setItem('isOwner', data.is_owner.toString());
        } catch (error) {
          console.error("Error checking owner status:", error);
          setIsOwner(false);
          localStorage.setItem('isOwner', 'false');
        }
      } else if (cachedOwnerStatus !== null) {
        setIsOwner(cachedOwnerStatus === 'true');
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
    if (path.startsWith("/#") && pathname !== "/") {
      e.preventDefault();
      const sectionId = path.replace("/#", "");

      // Store the target section in localStorage
      localStorage.setItem("scrollTarget", sectionId);

      // Navigate to home page
      window.location.href = "/";
    }
  };

  // Add effect to handle scroll after navigation
  useEffect(() => {
    if (pathname === "/") {
      const scrollTarget = localStorage.getItem("scrollTarget");
      if (scrollTarget) {
        // Clear the stored target
        localStorage.removeItem("scrollTarget");

        // Small delay to ensure the page is loaded
        setTimeout(() => {
          const element = document.getElementById(scrollTarget);
          if (element) {
            element.scrollIntoView({ behavior: "smooth" });
          }
        }, 500); // Increased delay for more reliability
      }
    }
  }, [pathname]);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed w-full bg-white/10 backdrop-blur-lg z-50"
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
                  {item.label}
                  {isActive(item.path) && (
                    <motion.div
                      layoutId="navbar-indicator"
                      className="absolute inset-0 rounded-md bg-white/20 -z-10"
                      initial={false}
                      transition={{
                        type: "spring",
                        bounce: 0.15,
                        duration: 0.5,
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
                href={getDiscordLoginUrl()}
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
