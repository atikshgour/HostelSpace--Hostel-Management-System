// Owner: Atiksh Gour | US-20 | Shared session/CSRF proxy
const backend = process.env.DJANGO_API_ORIGIN || 'http://127.0.0.1:8000';
const config = {
  output: 'standalone', poweredByHeader: false, devIndicators: false,
  skipTrailingSlashRedirect: true,
  async rewrites() { return [{ source: '/api/:path*', destination: `${backend}/api/:path*/` }]; },
};
export default config;
