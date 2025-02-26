const DISCORD_API_BASE_URL = 'https://discord.com/api';
const CLIENT_ID = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID;
const CLIENT_SECRET = process.env.NEXT_PUBLIC_DISCORD_CLIENT_SECRET;
const REDIRECT_URI = process.env.NEXT_PUBLIC_DISCORD_REDIRECT_URI;
const SCOPE = 'identify guilds';

export const getDiscordLoginUrl = () => {
    return `${DISCORD_API_BASE_URL}/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=${SCOPE}`;
};

export const handleDiscordCallback = async (code: string) => {
    if (!CLIENT_ID || !CLIENT_SECRET || !REDIRECT_URI) {
        throw new Error('Missing required environment variables');
    }
    const data = {
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: REDIRECT_URI,
    };

    const tokenResponse = await fetch(`${DISCORD_API_BASE_URL}/oauth2/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data),
    });

    const tokenData = await tokenResponse.json();
    if (!tokenData.access_token) {
        throw new Error('Failed to get access token');
    }

    // Get user info
    const userResponse = await fetch(`${DISCORD_API_BASE_URL}/users/@me`, {
        headers: {
            Authorization: `Bearer ${tokenData.access_token}`,
        },
    });
    const userInfo = await userResponse.json();

    // Get guilds info
    const guildsResponse = await fetch(`${DISCORD_API_BASE_URL}/users/@me/guilds`, {
        headers: {
            Authorization: `Bearer ${tokenData.access_token}`,
        },
    });
    const guildsInfo = await guildsResponse.json();

    return {
        user: userInfo,
        guilds: guildsInfo,
        accessToken: tokenData.access_token,
    };
};

export interface Guild {
  id: string;
  name: string;
  icon: string | null;
  owner: boolean;
  permissions: string;
}

export async function fetchUserGuilds(): Promise<Guild[]> {
  const accessToken = localStorage.getItem('accessToken');
  if (!accessToken) {
    throw new Error('No access token found');
  }

  const response = await fetch('https://discord.com/api/v10/users/@me/guilds', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch guilds');
  }

  return response.json();
}
