# 回响前端 - Docker 镜像
# 阶段1: 构建
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖（使用淘宝镜像）
RUN npm config set registry https://registry.npmmirror.com && npm install

# 复制源代码
COPY . .

# 构建（生产环境变量在构建时注入）
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# 阶段2: 生产镜像（使用 nginx 提供静态文件）
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置（用于前端路由）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
