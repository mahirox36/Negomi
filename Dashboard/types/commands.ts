export type CommandType = 'slash' | 'user' | 'message'
export type CommandCategory = string

export interface CommandOption {
  name: string;
  description: string;
  type: string;
  required: boolean;
  choices?: Array<{
    name: string;
    value: string | number;
  }>;
}

export interface Command {
  name: string;
  description: string;
  category: string;
  cooldown?: number;
  admin_only?: boolean;
  guild_installed?: boolean;
  user_installed?: boolean;
  options?: CommandOption[];
  usage?: number;
  lastUsed?: number;
}
