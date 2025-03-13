'use client';

import { User, Guild } from '../types/discord';
import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

interface SidebarProps {
  user?: User;
  guilds?: Guild[];
}

export default function Sidebar({ guilds }: SidebarProps) {
  const [joinedGuilds, setJoinedGuilds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const adminGuilds = guilds?.filter(g => g.permissions && (BigInt(g.permissions) & BigInt(0x8)) === BigInt(0x8)) || [];

  // Fetch joined guilds
  useEffect(() => {
    const fetchJoinedGuilds = async () => {
      if (adminGuilds.length > 0) {
        setIsLoading(true);
        try {
          const res = await fetch("/api/guilds/filter_joined", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ guilds: adminGuilds.map(g => g.id) }),
          });
          const data = await res.json();
          setJoinedGuilds(data);
        } catch (error) {
          console.error("Failed to fetch joined guilds:", error);
        } finally {
          setIsLoading(false);
        }
      } else {
        setJoinedGuilds([]);
        setIsLoading(false);
      }
    };

    fetchJoinedGuilds();
  }, [guilds]); // Depend on the original guilds prop instead

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
    // Check if the icon hash starts with 'a_' which indicates it's an animated icon (GIF)
    if (guild.icon.startsWith('a_')) {
      return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.gif`;
    }
    return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`;
  };

  // Separate guilds into joined and not joined
  const joinedGuildsList = adminGuilds.filter(guild => joinedGuilds.includes(guild.id));
  const notJoinedGuildsList = adminGuilds.filter(guild => !joinedGuilds.includes(guild.id));

  return (
    <div className="w-64 bg-white/5 backdrop-blur-lg min-h-screen pt-20 px-4">
      <div className="space-y-4">
        <div className="mb-8">
          <h3 className="text-white text-sm font-semibold mb-2">Servers</h3>
          
          {isLoading ? (
            <div className="text-white/70 text-center py-2">Loading servers...</div>
          ) : (
            <>
              {/* Joined servers */}
              {joinedGuildsList.map(guild => (
                <Link
                  href={`/dashboard/server/${guild.id}/overview`}
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
              
              {/* Not joined servers */}
              {notJoinedGuildsList.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/20">
                  <h4 className="text-white/70 text-xs font-medium mb-2">Available Servers</h4>
                  {notJoinedGuildsList.map(guild => (
                    <a
                      href={`/api/auth/bot/invite?guild_id=${guild.id}`}
                      key={guild.id}
                      className="flex items-center space-x-2 p-2 rounded hover:bg-white/10 text-white/60 hover:text-white"
                    >
                      <Image
                        src={getGuildIcon(guild)}
                        alt={guild.name}
                        width={32}
                        height={32}
                        className="rounded-full opacity-70"
                      />
                      <span className="truncate">{guild.name}</span>
                      <span className="text-xs bg-white/20 px-1.5 py-0.5 rounded text-white/80 ml-auto">Add</span>
                    </a>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function debounce<T extends (...args: any[]) => any>(func: T, wait: number) {
  let timeoutId: NodeJS.Timeout;
  const debouncedFunc = (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    return new Promise<ReturnType<T>>((resolve) => {
      timeoutId = setTimeout(() => {
        resolve(func(...args));
      }, wait);
    });
  };
  debouncedFunc.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  };
  return debouncedFunc;
}

