import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  RiDashboardFill, 
  RiSettings4Fill, 
  RiShieldFill,
  RiUserAddFill,
  RiSpamFill,
  RiFileListFill
} from 'react-icons/ri';

interface ServerSidebarProps {
  serverId: string;
}

export default function ServerSidebar({ serverId }: ServerSidebarProps) {
  const pathname = usePathname();

  const menuItems = [
    {
      section: 'General Settings',
      items: [
        { name: 'Overview', href: `/dashboard/server/${serverId}`, icon: RiDashboardFill },
        { name: 'Basic Settings', href: `/dashboard/server/${serverId}/settings`, icon: RiSettings4Fill },
        { name: 'Permissions', href: `/dashboard/server/${serverId}/permissions`, icon: RiShieldFill },
      ]
    },
    {
      section: 'Features',
      items: [
        { name: 'Welcome Messages', href: `/dashboard/server/${serverId}/welcome`, icon: RiUserAddFill },
        { name: 'Auto Moderation', href: `/dashboard/server/${serverId}/automod`, icon: RiSpamFill },
        { name: 'Logging', href: `/dashboard/server/${serverId}/logging`, icon: RiFileListFill },
      ]
    }
  ];

  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-white/5 backdrop-blur-lg min-h-[calc(100vh-4rem)] sticky top-16 px-4 py-6" // Updated positioning
    >
      <div className="space-y-8">
        {menuItems.map((section) => (
          <motion.div 
            key={section.section}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <h3 className="text-white/70 text-sm font-semibold mb-2 px-2">
              {section.section}
            </h3>
            <div className="space-y-1">
              {section.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                
                return (
                  <Link key={item.href} href={item.href}>
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
