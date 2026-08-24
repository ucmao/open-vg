# ----------------------------------------------------------------------------
# 1. Build Stage
# ----------------------------------------------------------------------------
FROM node:24-alpine AS builder

WORKDIR /app

# Accept build arguments
ARG NUXT_PUBLIC_API_BASE_URL
ENV NUXT_PUBLIC_API_BASE_URL=$NUXT_PUBLIC_API_BASE_URL

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ----------------------------------------------------------------------------
# 2. Runner Stage
# ----------------------------------------------------------------------------
FROM node:24-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3001

COPY --from=builder --chown=node:node /app/.output ./.output

USER node

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["node", "-e", "fetch('http://127.0.0.1:3001/robots.txt').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"]

CMD ["node", ".output/server/index.mjs"]
