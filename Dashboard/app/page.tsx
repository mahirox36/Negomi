"use client"

import Navbar from "./components/Navbar"
import Hero from "./components/Hero"
import Features from "./components/Features"
import QuickStart from "./components/QuickStart"
import Footer from "./components/Footer"
import Stars from "./components/Stars"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-900 to-purple-900 relative">
      <div className="fixed inset-0 bg-purple-950/50" /> {/* Dark overlay for better star visibility */}
      <Stars className="fixed inset-0 z-[2]" />
      <main className="relative z-[1]">
        <Navbar/>
        <Hero />
        <Features />
        <QuickStart />
      </main>
      <Footer />
    </div>
  )
}