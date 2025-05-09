"use client";

import AdminSidebar from "../../components/AdminSidebar";
import Link from "next/link";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950">
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
