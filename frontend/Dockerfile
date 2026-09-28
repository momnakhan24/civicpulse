# ---- Builder stage ----
FROM node:22-alpine AS builder

WORKDIR /app

# Cache-friendly layer order: deps before source
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- Final stage ----
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Run as the non-root "nginx" user (uid 101, already present in the base image).
# Listening on 8080 instead of 80 means we don't need root to bind the port.
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
