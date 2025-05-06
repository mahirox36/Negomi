"use client"

import { motion } from "framer-motion"
import Stars from "./Stars"

export default function QuickStart() {
  const steps = [
    { number: "01", title: "Invite Bot", description: "Add Negomi to your server with just a few clicks" },
    {
      number: "02",
      title: "Setup Features",
      description: "Use /setup commands to configure moderator roles, welcome messages, and more",
    },
    { number: "03", title: "Enjoy!", description: "Experience enhanced server management and community engagement" },
  ]

  return (
    <div className="relative py-24 overflow-hidden" id="setup">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-indigo-800 via-purple-900 to-purple-950 z-[1]" />
      
      {/* Stars layer */}
      <Stars className="absolute inset-0 z-[2]" />

      <div className="relative z-[3] max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-4">Quick Start Guide</h2>
          <p className="text-xl text-indigo-200">Get started in minutes</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2}}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
              className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-filter backdrop-blur-lg"
            >
              <div className="text-4xl font-bold text-indigo-300 mb-4">{step.number}</div>
              <h3 className="text-xl font-semibold text-white mb-2">{step.title}</h3>
              <p className="text-indigo-200">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

