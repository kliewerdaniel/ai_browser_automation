/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      // Proxy API requests to the Flask backend
      {
        source: '/api/flask/:path*',
        destination: 'http://localhost:5001/api/:path*',
      },
    ];
  },
  // Enable TypeScript and specific image domains if needed
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
