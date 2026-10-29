# Owner: Atiksh (authorized foundation) | US-19/20 | Sprint 1
FROM node:22-bookworm-slim AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
RUN npm ci
COPY app ./app
COPY src/app/globals.css ./src/app/globals.css
COPY src/features/complaints/api.js src/features/complaints/ComplaintManagePanel.jsx ./src/features/complaints/
COPY src/features/mess/api.js src/features/mess/MessPanel.jsx src/features/mess/MessManageForm.jsx ./src/features/mess/
COPY next.config.mjs postcss.config.mjs jsconfig.json ./
ARG DJANGO_API_URL=http://api:8000
ENV DJANGO_API_URL=$DJANGO_API_URL
RUN npm run build

FROM node:22-bookworm-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node", "server.js"]
