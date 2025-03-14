"use client"

import { motion } from "framer-motion"
import { useState, useEffect } from "react"

export default function Footer() {
  const [ownerPfp, setOwnerPfp] = useState("");

  useEffect(() => {
    fetch('/api/owner_pfp_url')
      .then(res => res.json())
      .then(data => setOwnerPfp(data.url))
      .catch(err => console.error('Failed to load owner pfp:', err));
  }, []);

  const fadeInUpVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <footer className="relative mt-36">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-950 to-purple-950 pointer-events-none" />
      
      {/* Wave divider */}
      <div className="absolute top-0 left-0 right-0 overflow-hidden -translate-y-[99%]">
        <svg 
          viewBox="0 0 1200 120" 
          preserveAspectRatio="none" 
          className="relative block w-full h-[150px]"
          style={{ transform: 'rotateY(180deg)' }}
        >
          <path 
            d="M985.66,92.83C906.67,72,823.78,31,743.84,14.19c-82.26-17.34-168.06-16.33-250.45.39-57.84,11.73-114,31.07-172,41.86A600.21,600.21,0,0,1,0,27.35V120H1200V95.8C1132.19,118.92,1055.71,111.31,985.66,92.83Z" 
            className="fill-purple-950"
          />
        </svg>
      </div>
      
      {/* Footer background */}
      <div className="relative bg-gradient-to-b from-purple-950 to-purple-950 pt-16 pb-12 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
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
                <div className="h-10 w-10 rounded-full overflow-hidden mr-3">
                  {ownerPfp ? (
                    <img src={ownerPfp} alt="Owner" className="w-full h-full object-cover" />
                  ) : (
                    <div className="bg-indigo-500 w-full h-full animate-pulse" />
                  )}
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
              className="space-y-3 sm:space-y-0"
            >
              <h3 className="text-lg font-semibold text-white mb-4">Quick Links</h3>
              <ul className="space-y-3">
                <li>
                  <a href="#features" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Features
                  </a>
                </li>
                <li>
                  <a href="#statistics" className="text-indigo-200 hover:text-white transition duration-300 flex items-center">
                    <span className="mr-2">→</span> Statistics
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
              className="space-y-3 sm:space-y-0"
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
          </div>
          
          <hr className="border-purple-700/50 mb-8" />
          
          <motion.div
            initial="hidden"
            whileInView="visible"
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            variants={fadeInUpVariants}
            className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0"
          >
            <div className="text-white/90 text-center sm:text-left">© 2025 Negomi Bot. All rights reserved.</div>
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

