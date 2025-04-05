"use client";

import { motion } from "framer-motion";

export default function ErrorPage() {
  return (
    <div className="container mx-auto h-screen flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/50 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-slate-800 text-center"
      >
        <h1 className="text-4xl font-bold mb-4 text-red-400">
          Service Unavailable
        </h1>
        <p className="text-slate-300">
          The bot appears to be offline. Please try again later.
        </p>
      </motion.div>
    </div>
  );
}
