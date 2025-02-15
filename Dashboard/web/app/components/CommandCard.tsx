import { motion } from 'framer-motion'
import CommandTag from './CommandTag'
import type { Command } from '../commands/page'

export default function CommandCard({ command }: { command: Command }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      whileHover={{ 
        scale: 1.02,
        backgroundColor: "rgba(255, 255, 255, 0.15)",
        transition: { duration: 0.1 }
      }}
      className="bg-white/5 rounded-lg p-4 transition-all"
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-white">{command.name}</h3>
        <div className="flex gap-2">
          {command.admin_only && <CommandTag type="admin" />}
          {command.user_installed && <CommandTag type="user" />}
          {command.guild_installed && <CommandTag type="guild" />}
          <CommandTag type={command.type} />
        </div>
      </div>
      <p className="text-gray-300 text-sm mb-2">{command.description}</p>
      <p className="text-gray-400 text-xs">
        Usage: <span className="font-mono bg-black/20 px-2 py-0.5 rounded">{command.usage}</span>
      </p>
    </motion.div>
  )
}