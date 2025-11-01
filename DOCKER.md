# Docker 部署指南

本文档介绍如何使用 Docker Compose 部署 LangGraph Reflection 应用。

## 前置要求

- Docker 已安装并运行
- Docker Compose 已安装（Docker Desktop 自带）
- 已配置 Azure OpenAI 凭证

## 快速开始

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Azure OpenAI 凭证
# AZURE_OPENAI_API_KEY=your-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 2. 启动应用

```bash
# 使用启动脚本（推荐）
./start.sh

# 或手动启动
docker compose up -d
```

### 3. 访问应用

启动成功后，可以通过以下地址访问：

- **API**: http://localhost:2024
- **API 文档**: http://localhost:2024/docs
- **LangGraph Studio**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### 4. 停止应用

```bash
# 使用停止脚本
./stop.sh

# 或手动停止
docker compose down
```

## 常用命令

### 查看日志

```bash
# 实时查看日志
docker compose logs -f

# 查看最近 100 行日志
docker compose logs --tail=100
```

### 查看容器状态

```bash
docker compose ps
```

### 进入容器

```bash
docker compose exec langgraph-app bash
```

### 重启服务

```bash
docker compose restart
```

### 重新构建镜像

```bash
# 重新构建并启动
docker compose up -d --build

# 或使用脚本
./stop.sh
./start.sh
```

## 文件说明

- `Dockerfile`: Docker 镜像构建文件
- `docker-compose.yml`: Docker Compose 配置文件
- `requirements.txt`: Python 依赖列表
- `.dockerignore`: Docker 构建时忽略的文件
- `start.sh`: 启动脚本
- `stop.sh`: 停止脚本

## 开发模式

docker-compose.yml 中配置了卷挂载，可以直接修改源代码：

- `./src:/app/src` - 源代码目录
- `./examples:/app/examples` - 示例代码目录
- `./langgraph.json:/app/langgraph.json` - 配置文件

修改代码后，需要重启容器才能生效：

```bash
docker compose restart
```

## 生产部署

生产环境部署时，建议：

1. 移除或注释掉卷挂载（volumes）
2. 使用环境变量或密钥管理服务来管理敏感信息
3. 配置合适的资源限制
4. 启用日志收集和监控

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker compose logs langgraph-app

# 检查 .env 文件配置
cat .env
```

### 端口被占用

如果 2024 端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:2024"  # 改为其他端口
```

### 镜像构建失败

```bash
# 清理缓存后重新构建
docker compose build --no-cache
```

### 依赖安装问题

检查 `requirements.txt` 中的依赖是否都正确，可能需要更新 pip：

```dockerfile
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
```

