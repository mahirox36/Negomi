import DiscordOAuth2 from 'discord-oauth2';

const oauth = new DiscordOAuth2({
  clientId: process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID,
  clientSecret: process.env.NEXT_PUBLIC_DISCORD_CLIENT_SECRET,
  redirectUri: process.env.NEXT_PUBLIC_DISCORD_REDIRECT_URI,
});

const SCOPE = ['identify', 'guilds'];

export const getDiscordLoginUrl = () => {
  return oauth.generateAuthUrl({
    scope: SCOPE,
  });
};

export const handleDiscordCallback = async (code: string) => {
  if (!process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID || 
      !process.env.NEXT_PUBLIC_DISCORD_CLIENT_SECRET || 
      !process.env.NEXT_PUBLIC_DISCORD_REDIRECT_URI) {
    throw new Error('Missing required environment variables');
  }

  try {
    const tokenData = await oauth.tokenRequest({
      code,
      scope: SCOPE,
      grantType: "authorization_code",
    });

    const user = await oauth.getUser(tokenData.access_token);
    const guilds = await oauth.getUserGuilds(tokenData.access_token);

    return {
      user,
      guilds,
      accessToken: tokenData.access_token,
    };
  } catch (error) {
    console.error('OAuth error:', error);
    throw new Error('Authentication failed');
  }
};

export const fetchUserGuilds = async (): Promise<DiscordOAuth2.PartialGuild[]> => {
  const accessToken = localStorage.getItem('accessToken');
  if (!accessToken) {
    throw new Error('No access token found');
  }

  return oauth.getUserGuilds(accessToken);
};
