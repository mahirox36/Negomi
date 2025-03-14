"use client"

import { motion } from "framer-motion"
import { useState } from "react"

export default function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      // Here you would typically send this to your API
      console.log("Subscribed with:", email);
      setSubscribed(true);
      setEmail("");
    }
  };

  const fadeInUpVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <footer className="relative mt-16">
      {/* Gradient overlay for smooth transition */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-purple-900/60 pointer-events-none" />
      
      {/* Wave divider */}
      <div className="absolute top-0 left-0 right-0 overflow-hidden -translate-y-full">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="fill-purple-900/30 w-full h-16">
          <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V120H0V56.44Z"></path>
        </svg>
      </div>
      
      <div className="relative bg-purple-900/30 backdrop-blur-lg pt-16 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 mb-16">
            {/* Logo and brand info */}
            <motion.div 
              initial="hidden"
              whileInView="visible"
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              variants={fadeInUpVariants}
              className="col-span-1 md:col-span-2 lg:col-span-1"
            >
              <div className="flex items-center mb-4">
                <div className="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-xl">N</span>
                </div>
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-300">
                  Negomi
                </span>
              </div>
              <p className="text-indigo-200 mb-6">
                The ultimate companion for your Discord server. Powered by cutting-edge AI technology to enhance your community experience.
              </p>
            </motion.div>

            {/* Quick links */}
            <motion.div
              initial="hidden"
              whileInView="visible"
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              variants={fadeInUpVariants}
            >
              <h3 className="text-lg font-semibold text-white mb-4">Quick Links</h3>
              <ul className="space-y-3">
                <li>
                  <a href="#features" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Features
                  </a>
                </li>
                <li>
                  <a href="#pricing" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Pricing
                  </a>
                </li>
                <li>
                  <a href="#faq" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> FAQ
                  </a>
                </li>
                <li>
                  <a href="/commands" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Commands
                  </a>
                </li>
              </ul>
            </motion.div>

            {/* Legal links */}
            <motion.div
              initial="hidden"
              whileInView="visible"
              transition={{ duration: 0.5, delay: 0.3 }}
              viewport={{ once: true }}
              variants={fadeInUpVariants}
            >
              <h3 className="text-lg font-semibold text-white mb-4">Legal</h3>
              <ul className="space-y-3">
                <li>
                  <a href="/terms-of-service" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Terms of Service
                  </a>
                </li>
                <li>
                  <a href="/privacy-policy" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="/cookie-policy" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Cookie Policy
                  </a>
                </li>
              </ul>
            </motion.div>

            {/* Newsletter */}
            <motion.div
              initial="hidden"
              whileInView="visible"
              transition={{ duration: 0.5, delay: 0.4 }}
              viewport={{ once: true }}
              variants={fadeInUpVariants}
            >
              <h3 className="text-lg font-semibold text-white mb-4">Stay Updated</h3>
              <p className="text-indigo-200 mb-4">Subscribe to our newsletter for the latest features and updates.</p>
              
              {!subscribed ? (
                <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
                  <input 
                    type="email" 
                    placeholder="Enter your email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="px-4 py-2 rounded bg-purple-800/50 border border-purple-700 text-white placeholder-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                  <button 
                    type="submit" 
                    className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded text-white font-medium transition-colors duration-300"
                  >
                    Subscribe
                  </button>
                </form>
              ) : (
                <div className="bg-indigo-900/50 border border-indigo-700 rounded p-3 text-indigo-200">
                  Thanks for subscribing! 🎉
                </div>
              )}
            </motion.div>
          </div>
          
          <hr className="border-purple-700/50 mb-8" />
          
          <motion.div
            initial="hidden"
            whileInView="visible"
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            variants={fadeInUpVariants}
            className="flex flex-col md:flex-row justify-between items-center"
          >
            <div className="text-white/90 mb-6 md:mb-0">© 2025 Negomi Bot. All rights reserved.</div>
            <div className="flex flex-wrap gap-4 justify-center">
              <a 
                href="https://discord.gg/HC2bryKU5Y" 
                className="text-indigo-200 hover:text-white/90 transition duration-300 flex items-center bg-purple-800/30 hover:bg-purple-800/50 px-4 py-2 rounded-full"
              >
                <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                </svg>
                Support Server
              </a>
              <a 
                href="https://github.com/mahirox36/Negomi" 
                className="text-indigo-200 hover:text-white/90 transition duration-300 flex items-center bg-purple-800/30 hover:bg-purple-800/50 px-4 py-2 rounded-full"
              >
                <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                  />
                </svg>
                GitHub
              </a>
              <a 
                href="/twitter" 
                className="text-indigo-200 hover:text-white/90 transition duration-300 flex items-center bg-purple-800/30 hover:bg-purple-800/50 px-4 py-2 rounded-full"
              >
                <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
                Twitter
              </a>
            </div>
          </motion.div>
        </div>
      </div>
    </footer>
  )
}

