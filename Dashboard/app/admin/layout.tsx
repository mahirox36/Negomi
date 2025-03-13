"use client";

import AdminSidebar from "../components/AdminSidebar";
import Link from "next/link";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Admin Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/50 backdrop-blur-lg border-b border-slate-800">
        <div className="px-4 mx-auto">
          <div className="flex items-center justify-between h-16">
            <Link href="/admin" className="flex items-center space-x-3">
              <img src="/logo.png" alt="Logo" className="w-8 h-8" />
              <span className="text-xl font-bold text-white">Admin Panel</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Layout */}
      <div className="flex pt-16 min-h-screen">
        <AdminSidebar />
        <main className="flex-1 p-8 bg-slate-950">
          {children}
        </main>
      </div>
    </div>
  );
}
