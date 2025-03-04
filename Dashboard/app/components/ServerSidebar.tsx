'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { useLayout } from '@/providers/LayoutProvider';
import * as Icons from 'react-icons/ri';

interface ServerSidebarProps {
  serverId: string;
}

const iconMap: Record<string, string> = {
  'fa-solid fa-gauge': 'RiDashboardFill',
  'fa-solid fa-cog': 'RiSettings4Fill',
  'fa-solid fa-robot': 'RiRobotFill',
  'fa-solid fa-user-plus': 'RiUserAddFill',
  'fa-solid fa-hdd': 'RiHardDriveFill',
  'fa-solid fa-user-tag': 'RiUserSettingsFill',
  'fa-solid fa-headset': 'RiHeadphoneFill',
  'fa-solid fa-gift': 'RiGiftFill',
  'fa-solid fa-trophy': 'RiTrophyFill',
  'fa-solid fa-medal': 'RiMedalFill'
};

export default function ServerSidebar({ serverId }: ServerSidebarProps) {
  const pathname = usePathname();
  const { serverSidebar, fetchServerSidebar } = useLayout();

  useEffect(() => {
    fetchServerSidebar();
  }, [fetchServerSidebar]);

  if (!serverSidebar) return null;

  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-white/5 backdrop-blur-lg min-h-[calc(100vh-4rem)] sticky top-16 px-4 py-6"
    >
      <div className="space-y-8">
        {Object.entries(serverSidebar).map(([section, items]) => (
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
                const pagePath = item.name.toLowerCase().replace(/\s+/g, '-');
                const isActive = pathname === `/dashboard/server/${serverId}/${pagePath}`;
                const iconName = iconMap[item.icon] || 'RiSettings4Fill';
                const Icon = Icons[iconName as keyof typeof Icons] || Icons.RiSettings4Fill;
                
                return (
                  <Link 
                    key={item.name} 
                    href={`/dashboard/server/${serverId}/${pagePath}`}
                  >
                    <motion.div
                      className={`flex items-center px-2 py-2 rounded-lg transition-colors relative ${
                        isActive
                          ? 'text-white'
                          : 'text-white/60 hover:text-white'
                      }`}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {item.name}
                      {isActive && (
                        <motion.div
                          layoutId="sidebar-active"
                          className="absolute inset-0 bg-white/10 rounded-lg -z-10"
                          initial={false}
                          transition={{
                            type: "spring",
                            stiffness: 380,
                            damping: 30
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
