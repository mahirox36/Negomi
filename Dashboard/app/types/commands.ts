export type CommandType = 'slash' | 'user' | 'message'
export type CommandCategory = string

export interface Command {
  name: string
  description: string
  usage: string
  type: CommandType
  category: CommandCategory
  admin_only: boolean
  guild_only: boolean
  guild_installed: boolean
  user_installed: boolean
  permissions: string[]
  cooldown: number | null
  examples: string[]
}
