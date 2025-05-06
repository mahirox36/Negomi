"use client";

import Hero from "./components/Hero";
import Features from "./components/Features";
import QuickStart from "./components/QuickStart";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-950 to-purple-950 relative overflow-hidden">
      <div className="relative">
        <main>
          <Hero />
          <Features />
          <QuickStart />
        </main>
        <Footer />
      </div>
    </div>
  );
}
