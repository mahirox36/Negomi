/** @type {import('next').NextConfig} */
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
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:25400/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
