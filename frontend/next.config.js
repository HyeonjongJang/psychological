/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Only use rewrites for local development
    // In production, the frontend calls the backend directly via NEXT_PUBLIC_API_URL
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Skip rewrites if using external API URL (production)
    if (process.env.NEXT_PUBLIC_API_URL) {
      return [];
    }

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
