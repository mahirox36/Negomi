"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function Hero() {
  // Floating animation variant
  const floatingAnimation = {
    initial: { y: 20, opacity: 0 },
    animate: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 1,
        ease: "easeOut",
      },
    },
  };

  // Stagger children animation
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  // Text reveal animation
  const textReveal = {
    hidden: { y: 20, opacity: 0 },
    show: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.8,
        ease: [0.43, 0.13, 0.23, 0.96],
      },
    },
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-pink-500 to-purple-600"
        animate={{
          background: [
            "linear-gradient(to bottom right, #ec4899, #9333ea)",
            "linear-gradient(to bottom right, #8b5cf6, #6366f1)",
            "linear-gradient(to bottom right, #ec4899, #9333ea)",
          ],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          repeatType: "reverse",
        }}
      />

      {/* Animated particles */}
      <div className="absolute inset-0 z-0">
        {[...Array(50)].map((_, i) => {
          // Generate deterministic values using the index
          const duration = 2 + (i % 3);
          const delay = (i * 0.1) % 2;
          const left = ((i * 17) % 100);
          const top = ((i * 23) % 100);
          
          return (
            <motion.div
              key={i}
              className="star"
              initial={{ scale: 0, opacity: 0 }}
              animate={{
                scale: [0, 1, 0],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: duration,
                repeat: Infinity,
                delay: delay,
              }}
              style={{
                left: `${left}%`,
                top: `${top}%`,
              }}
            />
          );
        })}
      </div>

      {/* Content container */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="relative z-10 text-center px-4"
      >
        {/* Title with improved padding and unified text */}
        <motion.div className="overflow-hidden">
          <motion.h1
            className="text-6xl md:text-8xl font-extrabold text-white mb-6 relative p-8" // Increased padding from p-4 to p-8
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.8,
              ease: [0, 0.71, 0.2, 1.01],
              scale: {
                type: "spring",
                damping: 5,
                stiffness: 100,
                restDelta: 0.001,
              },
            }}
          >
            <motion.span
              className="inline-block px-2 no-select" // Added horizontal padding
              animate={{ rotate: [0, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 5 }}
              style={{ transformOrigin: "center" }} // Ensure rotation happens from center
            >
              Negomi
            </motion.span>
          </motion.h1>
        </motion.div>

        {/* Description with stagger effect */}
        <motion.p
          variants={textReveal}
          className="text-xl md:text-2xl text-indigo-200 mb-8 max-w-2xl mx-auto"
        >
          Your all-in-one Discord bot for moderation, community engagement, and
          server management.
        </motion.p>

        {/* Buttons container with side-by-side layout */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          {/* Discord Button with hover effect */}
          <motion.div variants={floatingAnimation}>
            <Link
              href="https://discord.com/oauth2/authorize?client_id=1304926952552923156"
              className="group relative inline-flex items-center justify-center"
            >
              <motion.div
                className="absolute -inset-0.5 rounded-full bg-gradient-to-r from-pink-600 to-purple-600 opacity-75 blur-sm"
                animate={{
                  scale: [1, 1.05, 1],
                  opacity: [0.75, 0.85, 0.75],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  repeatType: "reverse",
                }}
              />
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="no-select relative px-8 py-4 bg-white rounded-full font-bold text-lg text-purple-600 transition-colors duration-200 hover:text-purple-700"
              >
                Add to Discord
              </motion.div>
            </Link>
          </motion.div>

          {/* Dashboard Button with cosmic style */}
          <motion.div variants={floatingAnimation}>
            <Link
              href="/dashboard"
              className="relative inline-flex items-center justify-center"
            >
              <motion.div
                className="absolute -inset-1 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-75 blur-md z-0"
                animate={{
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="no-select relative px-8 py-4 bg-transparent backdrop-blur-sm border-2 border-white/50 rounded-full font-bold text-lg transition-all duration-200"
              >
                <span className="relative z-10 text-white">
                  ✨ Open Dashboard ✨
                </span>
                <motion.div
                  className="absolute inset-0 rounded-full"
                  animate={{
                    boxShadow: [
                      "0 0 20px rgba(255, 255, 255, 0.3)",
                      "0 0 40px rgba(255, 255, 255, 0.6)",
                      "0 0 20px rgba(255, 255, 255, 0.3)",
                    ],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />
              </motion.div>
            </Link>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
