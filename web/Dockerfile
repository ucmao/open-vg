# ----------------------------------------------------------------------------
# 1. Build Stage
# ----------------------------------------------------------------------------
FROM node:18-alpine AS builder

WORKDIR /app

# Accept build arguments
ARG NUXT_PUBLIC_API_BASE_URL
ENV NUXT_PUBLIC_API_BASE_URL=$NUXT_PUBLIC_API_BASE_URL

COPY package*.json ./
RUN npm ci || npm install

COPY . .
RUN npm run build

# ----------------------------------------------------------------------------
# 2. Runner Stage
# ----------------------------------------------------------------------------
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

COPY --from=builder /app/.output ./.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
