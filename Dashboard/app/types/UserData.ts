export interface UserDataDashboard {
  guildsCount: number;
  adminGuildsCount: number;
  totalMessages: number;
  commandsUsed: number;
  level: number;
  xp: number;
  activityStreak: number;
  longestStreak: number;
  messageStats: {
    totalCharacters: number;
    totalWords: number;
    totalAttachments: number;
    totalMentions: number;
    totalEmojis: number;
    totalReplies: number;
    averageDailyMessages: number;
  };
  attachmentStats: {
    images: number;
    videos: number;
    audio: number;
    other: number;
  };
  commandStats: {
    totalCommands: number;
    favoriteCommands: [string, number][];
  };
  reactionStats: {
    given: number;
    received: number;
  };
  milestoneProgress: {
    currentLevel: number;
    xpToNextLevel: number;
    totalXpGained: number;
    achievements: string[];
  };
  badges: Array<{
    id: number;
    name: string;
    description: string;
    icon_url: string;
    emoji: string;
    created_at: string;
    guild_id: string;
    rarity: string;
    hidden: boolean;
    requirements: Array<{
      type: string;
      comparison: string;
      value: number;
    }>;
    obtained_at: string; // ISO 8601 format
  } | null>;
}
