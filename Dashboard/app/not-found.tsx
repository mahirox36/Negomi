"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function NotFound() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center">
      <div className="text-center text-white p-8">
        <h1 className="text-9xl font-bold mb-4">404</h1>
        <h2 className="text-2xl mb-6">Page Not Found</h2>
        <p className="mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <motion.div
              initial="initial"
              animate="animate"
              variants={{
                initial: { y: 20, opacity: 0 },
                animate: {
                  y: 0,
                  opacity: 1,
                  transition: {
                    duration: 1,
                    ease: "easeOut",
                  },
                },
              }}
              className="mt-8"
            >
              <Link
                href="/"
                className="group relative inline-block"
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
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative px-8 py-4 bg-white rounded-full font-bold text-lg text-purple-600 hover:text-purple-700 transition-colors duration-200"
                >
                  Back to homepage
                </motion.button>
              </Link>
            </motion.div>
      </div>
    </main>
  );
}
