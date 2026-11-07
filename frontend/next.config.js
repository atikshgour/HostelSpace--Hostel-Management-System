/** Proxy /api/* to Django so browser sees one origin (session + CSRF friendly). */
const backend = process.env.BACKEND_URL || "http://localhost:8000";

module.exports = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};
