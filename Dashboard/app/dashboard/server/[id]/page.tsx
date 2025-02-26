'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import LoadingScreen from '../../../components/LoadingScreen';
import { User, Guild } from '../../../types/discord';
import { fetchUserGuilds } from '../../../utils/auth';
import ServerLayout from '../../../components/ServerLayout';
import PageWrapper from '../../../components/PageWrapper';

export default function ServerManagement() {
  const params = useParams();
  const [user, setUser] = useState<User>();
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
      fetchUserGuilds()
        .then(setGuilds)
        .finally(() => setLoading(false));
    }
  }, []);

  if (loading) return <LoadingScreen message='Loading Server'/>;

  const currentGuild = guilds.find(g => g.id === params.id);

  const quickLinks = [
    { name: 'Basic Settings', href: `/dashboard/server/${params.id}/settings`, description: 'Configure basic bot settings and preferences' },
    { name: 'Welcome Messages', href: `/dashboard/server/${params.id}/welcome`, description: 'Set up custom welcome messages for new members' },
    { name: 'Auto Moderation', href: `/dashboard/server/${params.id}/automod`, description: 'Configure automated moderation rules' },
    { name: 'Logging', href: `/dashboard/server/${params.id}/logging`, description: 'Set up event logging channels and filters' },
  ];

  return (
    <ServerLayout serverId={params.id as string}>
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
        <h1 className="text-2xl font-bold text-white mb-2">
          {currentGuild?.name || 'Server'} Overview
        </h1>
        <p className="text-white/70 mb-8">
          Manage your server settings and features from this dashboard
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="block p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
            >
              <h3 className="text-white font-semibold mb-1">{link.name}</h3>
              <p className="text-white/60 text-sm">{link.description}</p>
            </Link>
          ))}
        </div>

        <div className="bg-white/5 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-white mb-4">Server Information</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-white/60">Server ID</span>
              <p className="text-white">{params.id}</p>
            </div>
            <div>
              <span className="text-white/60">Owner</span>
              <p className="text-white">{currentGuild?.owner ? 'Yes' : 'No'}</p>
            </div>
          </div>
        </div>
      </div>
    </ServerLayout>
  );
}
