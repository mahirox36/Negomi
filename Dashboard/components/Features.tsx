"use client";

import { motion } from "framer-motion";
import Stars from "./Stars";

export default function Features() {
  const features = [
    {
      icon: "🎭",
      title: "Custom Roles",
      description:
        "Create and customize unique roles with advanced permissions and appearance settings for your community members.",
    },
    {
      icon: "🌀",
      title: "Reaction Roles",
      description:
        "Let members assign roles to themselves by reacting to messages with emojis — easy, fun, and interactive!",
    },
    {
      icon: "🎉",
      title: "Auto Role",
      description:
        "Automatically assign roles to new members when they join, making onboarding smooth and welcoming.",
    },
    {
      icon: "🔊",
      title: "Temporary Voice",
      description:
        "Create dynamic voice channels with customizable names, user limits, privacy settings, and full member control.",
    },
    {
      icon: "🤖",
      title: "AI Integration",
      description:
        "Intelligent AI assistant that enhances server management and provides engaging member interactions and support.",
    },
    {
      icon: "💾",
      title: "Comprehensive Backup",
      description:
        "Complete server backup solution covering channels, roles, permissions, and settings for maximum data protection.",
    },
    {
      icon: "🎯",
      title: "Achievement System",
      description:
        "Built-in achievement system that rewards member participation and engagement with predefined ranks.",
    },
    {
      icon: "⏳",
      title: "Time Capsule",
      description:
        "Schedule and store messages for future delivery with customizable timing and delivery options.",
    },
    {
      icon: "🎮",
      title: "Fun Commands",
      description:
        "Extensive collection of interactive commands and mini-games to boost community engagement and activity.",
    },
  ];

  return (
    <div className="relative py-24 overflow-hidden" id="features">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-purple-800 via-purple-700 to-indigo-800 z-[1]" />

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
          <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-4">
            Powerful Features
          </h2>
          <p className="text-xl text-indigo-200">
            Everything you need to manage your Discord server
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }} // Removed index * 0.1 delay
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
              className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-filter backdrop-blur-lg"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-indigo-200">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
