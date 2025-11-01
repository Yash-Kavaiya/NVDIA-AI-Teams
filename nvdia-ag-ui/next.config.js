/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // Required for Docker deployment
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // API routes configuration
  async rewrites() {
    return [
      {
        source: '/api/copilotkit',
        destination: process.env.NEXT_PUBLIC_AGENT_URL
          ? `${process.env.NEXT_PUBLIC_AGENT_URL}/copilotkit`
          : 'http://localhost:8000/copilotkit',
      },
    ];
  },
}

module.exports = nextConfig
