"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const adminSections = {
  "Dashboard": [
    { name: "Overview", icon: "fa-solid fa-gauge", path: "/admin" },
  ],
  "Management": [
    { name: "Badges", icon: "fa-solid fa-certificate", path: "/admin/badges" },
    { name: "Servers", icon: "fa-solid fa-server", path: "/admin/servers" },
  ],
};

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
    <motion.div
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-slate-900/50 backdrop-blur-lg min-h-[calc(100vh-4rem)] sticky top-16 px-4 py-6 border-r border-slate-800"
    >
      <div className="space-y-8">
        {Object.entries(adminSections).map(([section, items]) => (
          <motion.div
            key={section}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <h3 className="text-white/70 text-sm font-semibold mb-2 px-2">
              {section}
            </h3>
            <div className="space-y-1">
              {items.map((item) => {
                const isActive = pathname === item.path;

                return (
                  <Link key={item.name} href={item.path}>
                    <motion.div
                      className={`flex items-center px-2 py-2 rounded-lg transition-colors relative ${
                        isActive
                          ? "text-blue-400"
                          : "text-slate-400 hover:text-white"
                      }`}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="w-5 flex items-center justify-center mr-3">
                        <i className={item.icon} />
                      </div>
                      {item.name}
                      {isActive && (
                        <motion.div
                          layoutId="admin-sidebar-active"
                          className="absolute inset-0 bg-blue-500/10 rounded-lg -z-10"
                          initial={false}
                          transition={{
                            type: "spring",
                            stiffness: 380,
                            damping: 30,
                          }}
                        />
                      )}
                    </motion.div>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
