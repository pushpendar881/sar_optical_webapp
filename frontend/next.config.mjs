/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Enable API proxy in development to avoid CORS issues
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://127.0.0.1:8000/api/:path*', // Use IPv4 explicitly
        },
        {
          source: '/data/:path*', 
          destination: 'http://127.0.0.1:8000/data/:path*', // Use IPv4 explicitly
        },
      ]
    }
    return []
  },
}

export default nextConfig
