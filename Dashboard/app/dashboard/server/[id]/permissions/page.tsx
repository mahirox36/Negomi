'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import ServerLayout from '../../../../components/ServerLayout';
import { RiShieldFill, RiAddLine } from 'react-icons/ri';

interface Permission {
  role: string;
  commands: string[];
}

export default function Permissions() {
  const params = useParams();
  const [permissions, setPermissions] = useState<Permission[]>([
    { role: '@everyone', commands: ['help', 'ping'] },
    { role: 'Moderator', commands: ['ban', 'kick', 'mute'] },
  ]);

  return (
    <ServerLayout serverId={params.id as string}>
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold text-white mb-6 flex items-center gap-2"
        >
          <RiShieldFill className="w-6 h-6" />
          Permissions
        </motion.h1>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          {permissions.map((perm, index) => (
            <motion.div
              key={perm.role}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/5 rounded-lg p-4"
            >
              <h3 className="text-white font-semibold mb-2">{perm.role}</h3>
              <div className="flex flex-wrap gap-2">
                {perm.commands.map((command) => (
                  <span
                    key={command}
                    className="px-2 py-1 bg-white/10 rounded text-sm text-white"
                  >
                    {command}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
          >
            <RiAddLine className="w-5 h-5" />
            Add Role Permission
          </motion.button>
        </motion.div>
      </div>
    </ServerLayout>
  );
}
