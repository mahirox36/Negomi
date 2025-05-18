/** @type {import('next').NextConfig} */
import createNextIntlPlugin from 'next-intl/plugin';

const nextConfig = {
  assetPrefix: "",
  staticPageGenerationTimeout: 1000,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    const apiBaseUrl = process.env.API_BASE_URL || 'http://localhost:25400';
    return [
      {
        source: '/api/:path*',
        destination: `${apiBaseUrl}/api/:path*`,
      },
    ];
  },
  reactStrictMode: true,
};

const withNextIntl = createNextIntlPlugin();
export default withNextIntl(nextConfig);
