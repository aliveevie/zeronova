FROM node:20-alpine AS build
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile || npm install

# Copy source
COPY . .

# Build args for Vite env vars (API is proxied via nginx, so leave empty)
ARG VITE_PRIVY_APP_ID=placeholder-dev-id
ARG VITE_API_BASE_URL=
ARG VITE_WS_BASE_URL=

ENV VITE_PRIVY_APP_ID=$VITE_PRIVY_APP_ID
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL

RUN npm run build

# Production image
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
