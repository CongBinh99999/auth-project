# syntax=docker/dockerfile:1

# Ảnh này chỉ để chạy thử console. Sửa code console thì dùng `npm run dev`
# ở máy để có hot reload.
FROM node:24-slim AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build


# dist là file tĩnh thuần, runtime không cần node.
FROM nginx:alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
