"use client"

import Navbar from "./components/Navbar"
import Hero from "./components/Hero"
import Features from "./components/Features"
import QuickStart from "./components/QuickStart"
import Footer from "./components/Footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-500 to-purple-600">
      <Navbar/>
      <Hero />
      <Features />
      <QuickStart />
      <Footer />
    </main>
  )
}