# ============================================================
# Campus Byte Frontend — Multi-stage Docker Build
# Stage 1: Build React/Vite app
# Stage 2: Serve with nginx (SPA + API proxy to backend:8000)
# ============================================================

# --- Stage 1: Builder ---
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (cache layer)
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

# Copy source and build
COPY . .
RUN npm run build

# --- Stage 2: Nginx server ---
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
