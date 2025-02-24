"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { usePathname } from "next/navigation"
import DiscordLoginButton from "./DiscordLoginButton"

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const [activeSection, setActiveSection] = useState("")
  const [isAtTop, setIsAtTop] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsAtTop(window.scrollY < 100)
    }

    // Initial check
    handleScroll()

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const isActive = (path: string) => {
    // Remove scroll check for non-home pages to make transitions instant
    if (!path.startsWith('/#')) {
      return pathname === path;
    }

    // Home page and section checks remain the same
    if (path === '/') {
      return pathname === '/' && isAtTop && !activeSection;
    }
    
    if (path.startsWith('/#') && pathname === '/') {
      return activeSection === path.substring(2);
    }

    return false;
  }

  // Generate unique layoutId based on current active section/page
  const getLayoutId = () => {
    if (pathname === '/') {
      return activeSection ? `section-${activeSection}` : 'home';
    }
    return pathname.replace('/', 'page-');
  }

  useEffect(() => {
    const handleScroll = () => {
      if (pathname !== '/') {
        setActiveSection("")
        return
      }

      // Check if we're at the top of the page
      if (window.scrollY < 100) {
        setActiveSection("");
        return;
      }

      const sections = ['features', 'setup']
      const viewportMiddle = window.innerHeight / 2

      // Find the section closest to the middle of the viewport
      let closestSection = ''
      let closestDistance = Infinity

      sections.forEach(section => {
        const element = document.getElementById(section)
        if (element) {
          const rect = element.getBoundingClientRect()
          const distance = Math.abs(rect.top + rect.height / 2 - viewportMiddle)
          
          if (distance < closestDistance) {
            closestDistance = distance
            closestSection = section
          }
        }
      })
      
      setActiveSection(closestSection)
    }

    // Run once immediately to set initial state
    handleScroll()

    // Add smooth scroll behavior
    const handleNavClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      const href = target.getAttribute('href')
      
      if (href?.startsWith('/#')) {
        e.preventDefault()
        const sectionId = href.replace('/#', '')
        const element = document.getElementById(sectionId)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
        }
      }
    }

    document.querySelectorAll('a[href^="/#"]').forEach(link => {
      link.addEventListener('click', handleNavClick as any)
    })

    // Throttle scroll event for better performance
    let ticking = false
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll()
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      document.querySelectorAll('a[href^="/#"]').forEach(link => {
        link.removeEventListener('click', handleNavClick as any)
      })
    }
  }, [pathname, activeSection]) // Add pathname as dependency

  useEffect(() => {
    // Check if user is authenticated (you'll need to implement this based on your auth setup)
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/status')
        const data = await response.json()
        setIsAuthenticated(data.authenticated)
      } catch (error) {
        console.error('Error checking auth status:', error)
      }
    }
    
    checkAuth()
  }, [])

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/commands', label: 'Commands' },
    { path: '/statistics', label: 'Statistics' },
    { path: '/dashboard', label: 'Dashboard', requiresAuth: true }, // Added statistics route
  ]

  const handleNavigation = (e: React.MouseEvent<HTMLAnchorElement>, path: string) => {
    if (path.startsWith('/#') && pathname !== '/') {
      e.preventDefault()
      const sectionId = path.replace('/#', '')
      
      // Store the target section in localStorage
      localStorage.setItem('scrollTarget', sectionId)
      
      // Navigate to home page
      window.location.href = '/'
    }
  }

  // Add effect to handle scroll after navigation
  useEffect(() => {
    if (pathname === '/') {
      const scrollTarget = localStorage.getItem('scrollTarget')
      if (scrollTarget) {
        // Clear the stored target
        localStorage.removeItem('scrollTarget')
        
        // Small delay to ensure the page is loaded
        setTimeout(() => {
          const element = document.getElementById(scrollTarget)
          if (element) {
            element.scrollIntoView({ behavior: 'smooth' })
          }
        }, 500) // Increased delay for more reliability
      }
    }
  }, [pathname])

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed w-full bg-white/10 backdrop-blur-lg z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <motion.div
            className="flex items-center"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link href="/" className="text-white font-bold text-xl">
              Negomi
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-4 relative">
              {navItems.map((item) => {
                if (item.requiresAuth && !isAuthenticated) return null
                return (
                  <Link
                    key={item.path}
                    href={item.path}
                    onClick={(e) => handleNavigation(e, item.path)}
                    className={`relative px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200
                      ${isActive(item.path) 
                        ? 'text-white' 
                        : 'text-gray-300 hover:text-white'
                      }`}
                  >
                    {item.label}
                    {isActive(item.path) && (
                      <motion.div
                        layoutId="navbar-indicator"
                        className="absolute inset-0 rounded-md bg-white/20 -z-10"
                        initial={false}
                        transition={{ 
                          type: "spring",
                          bounce: 0.15,
                          duration: 0.5
                        }}
                      />
                    )}
                  </Link>
                )
              })}
              {!isAuthenticated && <DiscordLoginButton />}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-white/20 focus:outline-none"
          >
            <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth="2" 
                d={isOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
              />
            </svg>
          </motion.button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden overflow-hidden"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navItems.map((item) => {
                if (item.requiresAuth && !isAuthenticated) return null
                return (
                  <Link
                    key={item.path}
                    href={item.path}
                    onClick={(e) => {
                      setIsOpen(false)
                      handleNavigation(e, item.path)
                    }}
                    className={`block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200
                      ${isActive(item.path)
                        ? 'text-white bg-white/20'
                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                      }`}
                  >
                    {item.label}
                  </Link>
                )
              })}
              {!isAuthenticated && (
                <div className="px-3 py-2">
                  <DiscordLoginButton />
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}

