"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { FiServer } from "react-icons/fi"

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl mx-auto text-center"
      >
        <FiServer className="w-16 h-16 mx-auto mb-6 text-primary" />
        <h1 className="text-4xl font-bold mb-4">Welcome to Your Dashboard</h1>
        <p className="text-muted-foreground mb-8">
          Select a server from the sidebar to get started managing your Discord community.
        </p>
      </motion.div>
    </div>
  )
}
