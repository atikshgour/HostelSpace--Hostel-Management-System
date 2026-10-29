// Owner: Atiksh | US-20 foundation | Sprint 1
const nextConfig = {
  output: 'standalone', poweredByHeader: false,
  // Django's canonical endpoints retain their trailing slash through the proxy.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${process.env.DJANGO_API_URL || 'http://127.0.0.1:8000'}/api/:path*/` }];
  },
};
export default nextConfig;
