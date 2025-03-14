"use client";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Features from "./components/Features";
import QuickStart from "./components/QuickStart";
import Footer from "./components/Footer";
import Stars from "./components/Stars";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-950 to-purple-950 relative overflow-hidden">
      <Stars className="fixed inset-0 z-0 w-screen h-screen" />
      <div className="fixed inset-0 bg-purple-950/50 z-10" />
      <div className="relative z-20">
        <main>
          <Navbar />
          <Hero />
          <Features />
          <QuickStart />
        </main>
        <Footer />
      </div>
    </div>
  );
}
