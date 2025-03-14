"use client";

import { motion } from "framer-motion";

export default function Stars({ className = "" }: { className?: string }) {
  return (
    <div className={`${className}`}>
      {[...Array(50)].map((_, i) => {
        const duration = 2 + (i % 3);
        const delay = (i * 0.1) % 2;
        const left = ((i * 17) % 100);
        const top = ((i * 23) % 100);
        const size = ((i % 3) + 2); // Slightly larger stars: 2px, 3px, or 4px
        
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
              ease: "easeInOut",
            }}
            style={{
              left: `${left}%`,
              top: `${top}%`,
              width: `${size}px`,
              height: `${size}px`,
            }}
          />
        );
      })}
    </div>
  );
}
