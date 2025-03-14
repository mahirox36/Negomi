"use client"

import Navbar from "./components/Navbar"
import Hero from "./components/Hero"
import Features from "./components/Features"
import QuickStart from "./components/QuickStart"
import Footer from "./components/Footer"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-500 via-purple-600 to-purple-900">
      <main className="relative">
        <Navbar/>
        <Hero />
        <Features />
        <QuickStart />
      </main>
      <Footer />
    </div>
  )
}