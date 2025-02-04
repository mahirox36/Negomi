"use client"

import { motion } from "framer-motion"

export default function Features() {
  const features = [
    {
      icon: "🛡️",
      title: "Advanced Moderation",
      description:
        "Comprehensive moderator management system with role hierarchy, token authentication, and automated security features.",
    },
    {
      icon: "🎭",
      title: "Custom Roles",
      description:
        "Let members create and customize their own roles. Perfect for communities and servers with boosters!",
    },
    {
      icon: "🔊",
      title: "Temporary Voice",
      description:
        "Dynamic voice channels with full user control - customize names, limits, privacy settings and more.",
    },
    {
      icon: "🤖",
      title: "AI Integration",
      description:
        "Engage with an intelligent AI assistant that can help manage your server and interact with members.",
    },
    {
      icon: "👋",
      title: "Welcome System",
      description: "Greet new members with customizable welcome messages and beautifully generated welcome images.",
    },
    {
      icon: "💾",
      title: "Backup System",
      description:
        "Comprehensive server backups including channels, roles, permissions and more for complete peace of mind.",
    },
  ]

  return (
    <div className="py-24 bg-gradient-to-b from-purple-600 to-indigo-900" id="features">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-4">Powerful Features</h2>
          <p className="text-xl text-indigo-200">Everything you need to manage your Discord server</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
              className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-filter backdrop-blur-lg"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-indigo-200">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

