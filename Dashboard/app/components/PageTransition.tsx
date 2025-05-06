'use client';

import { ReactNode } from "react";
import { motion } from "framer-motion";

const PageTransition = ({ children }: { children: ReactNode }) => {
  return (
    <motion.div
      initial={{ opacity: 0, filter: "blur(10px)" }}
      animate={{ 
        opacity: 1, 
        filter: "blur(0px)",
      }}
      exit={{ 
        opacity: 0, 
        filter: "blur(10px)",
        scale: 0.98 
      }}
      transition={{
        duration: 0.4,
        ease: [0.4, 0, 0.2, 1]
      }}
    >
      {children}
    </motion.div>
  );
};

export default PageTransition;
