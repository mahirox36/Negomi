'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import ServerLayout from '../../../../components/ServerLayout';
import { RiSaveLine } from 'react-icons/ri';

export default function BasicSettings() {
  const params = useParams();
  const [prefix, setPrefix] = useState('!');
  const [nickname, setNickname] = useState('Negomi');

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving settings...');
  };

  return (
    <ServerLayout serverId={params.id as string}>
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold text-white mb-6"
        >
          Basic Settings
        </motion.h1>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          <div className="space-y-4">
            <label className="block">
              <span className="text-white">Bot Prefix</span>
              <input
                type="text"
                value={prefix}
                onChange={(e) => setPrefix(e.target.value)}
                className="mt-1 block w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-white focus:border-violet-500 focus:ring focus:ring-violet-500/20"
              />
            </label>

            <label className="block">
              <span className="text-white">Bot Nickname</span>
              <input
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                className="mt-1 block w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-white focus:border-violet-500 focus:ring focus:ring-violet-500/20"
              />
            </label>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors"
          >
            <RiSaveLine className="w-5 h-5" />
            Save Changes
          </motion.button>
        </motion.div>
      </div>
    </ServerLayout>
  );
}
