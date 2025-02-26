import { motion } from 'framer-motion'

type TagType = 'slash' | 'member' | 'message' | 'guild' | 'user' | 'admin'

const tagStyles = {
  slash: 'bg-blue-500/20 text-blue-300 border border-blue-500/20',
  member: 'bg-green-500/20 text-green-300 border border-green-500/20',
  message: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/20',
  guild: 'bg-purple-500/20 text-purple-300 border border-purple-500/20',
  user: 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/20',
  admin: 'bg-red-500/20 text-red-300 border border-red-500/20',
}

export default function CommandTag({ type }: { type: TagType }) {
  return (
    <motion.span
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`px-2 py-1 rounded-md text-xs font-medium ${tagStyles[type]}`}
    >
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </motion.span>
  )
}