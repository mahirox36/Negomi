'use client';

import { User, Guild } from '../types/discord';
import Image from 'next/image';
import Link from 'next/link';

interface SidebarProps {
  user?: User;
  guilds?: Guild[];
}

export default function Sidebar({ user, guilds }: SidebarProps) {
  const adminGuilds = guilds?.filter(g => (BigInt(g.permissions) & BigInt(0x8)) === BigInt(0x8)) || [];

const getGuildIcon = (guild: Guild) => {
    if (!guild.icon) {
        const canvas = document.createElement('canvas');
        canvas.width = 100;
        canvas.height = 100;
        const ctx = canvas.getContext('2d');
        if (!ctx) return '/default-guild-icon.png';

        // Generate background color
        const hashCode = guild.name.split('')
            .reduce((acc, char) => char.charCodeAt(0) + ((acc << 5) - acc), 0);
        const hue = Math.abs(hashCode % 360);
        const backgroundColor = `hsl(${hue}, 70%, 60%)`;
        ctx.fillStyle = backgroundColor;
        ctx.fillRect(0, 0, 100, 100);

        // Calculate brightness of background color
        const l = 60; // lightness from HSL color
        // Use white text for dark backgrounds, black text for light backgrounds
        const textColor = l > 50 ? '#000000' : '#ffffff';

        // Get initials
        const initials = guild.name
            .split(' ')
            .map(word => word[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();

        // Add text with calculated color
        ctx.fillStyle = textColor;
        ctx.font = '40px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(initials, 51, 55);

        return canvas.toDataURL();
    }
    return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`;
};

  return (
    <div className="w-64 bg-white/5 backdrop-blur-lg min-h-screen pt-20 px-4">
      <div className="space-y-4">
        <div className="mb-8">
          <h3 className="text-white text-sm font-semibold mb-2">Servers</h3>
          {adminGuilds.map(guild => (
            <Link
              href={`/dashboard/server/${guild.id}`}
              key={guild.id}
              className="flex items-center space-x-2 p-2 rounded hover:bg-white/10 text-white"
            >
              <Image
                src={getGuildIcon(guild)}
                alt={guild.name}
                width={32}
                height={32}
                className="rounded-full"
              />
              <span className="truncate">{guild.name}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
