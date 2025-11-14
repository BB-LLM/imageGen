# Docker 部署指南

## 快速开始

使用 `docker-compose.yml` 可以一键部署包含PostgreSQL数据库和应用服务的完整系统。

**重要：** 所有 Docker 相关文件已移至 `docker/` 文件夹，请在 `docker/` 目录下执行命令。

```bash
# 1. 进入 docker 目录
cd docker

# 2. 创建 .env 文件（在项目根目录或 docker 目录）
cat > ../.env << EOF
# 数据库配置
POSTGRES_USER=mvpdbuser
POSTGRES_PASSWORD=mvpdbpw
POSTGRES_DB=mvpdb
POSTGRES_PORT=5432

# Wan API配置（必需）
DASHSCOPE_API_KEY=your-dashscope-api-key

# 应用配置
API_PORT=8000
DEBUG=false
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=1
EOF

# 3. 启动服务（会自动初始化数据库和创建Soul角色）
docker-compose up -d

# 4. 查看日志（确认初始化完成）
docker-compose logs -f soul-app
```

**注意：** 如果本地已有服务占用 8000 或 5432 端口，项目已包含 `docker-compose.override.yml` 配置，Docker 会自动使用：
- 应用端口：`8001`（而非 8000）
- 数据库端口：`5433`（而非 5432）

这样 Docker 和本地服务可以同时运行，互不干扰。

**容器启动时会自动执行：**
- 等待数据库就绪
- 初始化数据库表（`init_db.py`）
- 创建Soul角色（`create_soul.py`）
- 启动应用服务器

**访问地址：**
- 前端页面: http://localhost:8001（如果使用 override 配置则为 8001，否则为 8000）
- Wan视频生成页面: http://localhost:8001/wan-video
- API文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/healthz

**端口说明：**
- 如果本地已有服务占用 8000/5432 端口，`docker-compose.override.yml` 会自动让 Docker 使用 8001/5433
- 如果端口未被占用，可以删除 `docker-compose.override.yml` 使用默认端口

---

## 使用外部数据库

如果数据库已经在另一个Docker容器中运行，可以手动构建和运行应用容器：

```bash
# 1. 构建镜像（在项目根目录）
docker build -f docker/Dockerfile -t soul-app:latest .

# 2. 创建 .env 文件
cat > .env << EOF
# 数据库配置（使用外部数据库）
# 如果数据库在另一个Docker容器中，使用容器名或服务名
DATABASE_URL=postgresql://mvpdbuser:mvpdbpw@postgres-container:5432/mvpdb

# 如果数据库在宿主机：
# Linux: DATABASE_URL=postgresql://mvpdbuser:mvpdbpw@172.17.0.1:5432/mvpdb
# Mac/Windows: DATABASE_URL=postgresql://mvpdbuser:mvpdbpw@host.docker.internal:5432/mvpdb

# Wan API配置（必需）
DASHSCOPE_API_KEY=your-dashscope-api-key

# 应用配置
API_PORT=8000
DEBUG=false
LOG_LEVEL=INFO
EOF

# 3. 创建数据目录
mkdir -p generated_images generated_videos

# 4. 运行容器（会自动初始化数据库和创建Soul角色）
docker run -d \
  --name soul-app \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/generated_images:/app/generated_images \
  -v $(pwd)/generated_videos:/app/generated_videos \
  --add-host=host.docker.internal:host-gateway \
  soul-app:latest

# 5. 查看日志
docker logs -f soul-app
```

**连接到外部数据库网络：**
```bash
# 将应用容器加入数据库网络
docker network connect <database-network-name> soul-app
```

---

## 数据持久化

生成的数据（图像和视频）通过volume挂载到宿主机：

- `../generated_images` → `/app/generated_images`
- `../generated_videos` → `/app/generated_videos`

即使容器删除，数据也会保留在宿主机上。

---

## 数据库连接配置

### 场景1：数据库在另一个Docker容器中（同一网络）

```env
DATABASE_URL=postgresql://user:password@postgres-container:5432/dbname
```

### 场景2：数据库在另一个Docker容器中（不同网络）

```bash
# 方法1：将应用容器加入数据库网络
docker network connect <database-network> soul-app
```

### 场景3：数据库在宿主机

```env
# Linux
DATABASE_URL=postgresql://user:password@172.17.0.1:5432/dbname

# Mac/Windows
DATABASE_URL=postgresql://user:password@host.docker.internal:5432/dbname
```

---

## 常用命令

```bash
# 进入 docker 目录
cd docker

# 查看日志
docker-compose logs -f soul-app
# 或
docker logs -f soul-app

# 停止服务
docker-compose down
# 或
docker stop soul-app

# 重启服务
docker-compose restart soul-app
# 或
docker restart soul-app

# 进入容器
docker-compose exec soul-app bash
# 或
docker exec -it soul-app bash

# 查看容器状态
docker-compose ps
# 或
docker ps

# 删除容器和数据（谨慎使用）
docker-compose down -v
```

---

## 生产环境建议

1. **使用环境变量文件**：不要将敏感信息（如API密钥）硬编码
2. **数据备份**：定期备份 `generated_images` 和 `generated_videos` 目录
3. **数据库备份**：定期备份PostgreSQL数据
4. **资源限制**：在docker-compose.yml中添加资源限制
5. **日志管理**：配置日志轮转和集中日志收集
6. **健康检查**：容器已包含健康检查，可配合监控系统使用

---

## 故障排查

### 无法连接数据库

1. 检查数据库容器是否运行：`docker ps | grep postgres`
2. 检查网络连接：`docker network ls`
3. 测试连接：`docker exec soul-app python -c "from app.data.dal import get_db; next(get_db())"`

### 数据目录权限问题

```bash
# 确保目录有写权限
chmod -R 755 generated_images generated_videos
```

### 查看详细日志

```bash
cd docker
docker-compose logs --tail=100 soul-app
```

---

## 文件结构说明

所有 Docker 相关文件已移至 `docker/` 文件夹：

```
docker/
├── Dockerfile                    # Docker 镜像构建文件
├── docker-compose.yml            # Docker Compose 主配置
├── docker-compose.override.yml   # Docker Compose 覆盖配置（本地开发用）
├── docker-entrypoint.sh          # 容器启动脚本
├── .dockerignore                 # Docker 构建忽略文件
└── DOCKER_DEPLOY.md             # 本部署文档
```

**使用方式：**
- 在 `docker/` 目录下执行 `docker-compose` 命令
- 或在项目根目录使用 `docker-compose -f docker/docker-compose.yml` 命令

