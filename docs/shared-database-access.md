# One shared HostelSpace instance on a local network

Run **one** Docker Compose stack on a server reachable by the other computers. All browsers then use the same Next.js frontend, Django API and PostgreSQL volume. Do not start a separate Compose stack on each computer: each stack creates its own `postgres_data` volume and its own database.

1. On the server, set `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY` in `.env` as usual.
2. Set `FRONTEND_BIND_ADDRESS=0.0.0.0`, `DJANGO_ALLOWED_HOSTS=<server-LAN-IP>,api`, and `DJANGO_CSRF_TRUSTED_ORIGINS=http://<server-LAN-IP>:3000`. Use the server's actual LAN IP without angle brackets. If clients use a DNS name, include that exact name in both settings instead.
3. Start the stack with `docker compose up --build`. Allow inbound TCP 3000 on the server's local firewall. Keep PostgreSQL and the Django API unexposed to the other computers; the frontend proxies `/api/` to the API inside Compose.
4. On every computer, open `http://<server-LAN-IP>:3000`. Sign in separately. Each request reads the same PostgreSQL database. Refresh a page or use its refresh button to see changes made elsewhere; currently open pages do not receive live push updates.

This is a local network development setup. For internet access, configure HTTPS, a stable hostname, production Django settings and a reviewed deployment before exposing the service.
