# 🌾 智农兴乡 ZhinongXingxiang

> 赋能乡村振兴的 AIGC 智慧农业全栈解决方案。
> 通过大模型 RAG 技术解决农技普及痛点，提供**病虫害智能诊断、农业政策问答、精准农业管理**服务。

**技术栈：** FastAPI · PostgreSQL · Redis · ChromaDB · Next.js 15 · Capacitor Android

---

## 目录

1. [项目结构](#-项目结构)
2. [快速启动（Docker Compose）](#-快速启动docker-compose)
3. [服务器手动部署](#-服务器手动部署)
   - [3.1 环境准备](#31-环境准备)
   - [3.2 后端部署](#32-后端部署)
   - [3.3 前端部署](#33-前端部署)
   - [3.4 Nginx 反向代理](#34-nginx-反向代理)
4. [知识库数据导入](#-知识库数据导入)
5. [APK 打包](#-apk-打包)
   - [5.1 前置要求](#51-前置要求)
   - [5.2 构建静态前端](#52-构建静态前端)
   - [5.3 同步到 Android 工程](#53-同步到-android-工程)
   - [5.4 用 Android Studio 打包 APK](#54-用-android-studio-打包-apk)
   - [5.5 命令行打包（可选）](#55-命令行打包可选)
6. [环境变量说明](#-环境变量说明)
7. [常见问题](#-常见问题)

---

## 📁 项目结构

```
ZhinongXingxiang/
├── backend/               # FastAPI 后端
│   ├── app/               # 业务代码（routers / models / rag / services）
│   ├── data/              # 种子知识库 knowledge.jsonl
│   ├── scripts/           # 工具脚本（知识库导入等）
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # Next.js 15 前端
│   ├── app/               # App Router 页面与组件
│   ├── capacitor.config.ts
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml     # 一键启动全栈
└── docs/                  # 文档（演示文稿、计划书等）
```

---

## 🚀 快速启动（Docker Compose）

> 适合本地开发或单机服务器快速验证。需要安装 Docker（≥ 24）和 Docker Compose（≥ 2.20）。

### 第一步：克隆仓库

```bash
git clone https://github.com/Andrewrover-01/ZhinongXingxiang.git
cd ZhinongXingxiang
```

### 第二步：配置后端环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，至少填写以下必填项：

```dotenv
# LLM（二选一）
QWEN_API_KEY=sk-xxxxxxxx          # 通义千问（推荐）
# OPENAI_API_KEY=sk-xxxxxxxx      # 或 OpenAI

# 生产环境务必修改此密钥（随机 64 位字符串）
SECRET_KEY=change-me-in-production-use-a-random-64-char-string
```

### 第三步：一键启动

```bash
docker compose up -d --build
```

> 首次构建约需 3–5 分钟，后续重启仅需数秒。

启动后访问：

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 交互文档 | http://localhost:8000/docs |

### 第四步：导入知识库（首次）

容器启动完成后，执行一次知识库数据导入：

```bash
docker compose exec backend python scripts/ingest_knowledge.py
```

### 常用管理命令

```bash
# 查看日志
docker compose logs -f backend

# 停止服务
docker compose down

# 停止并清除数据卷（慎用）
docker compose down -v
```

---

## 🛠 服务器手动部署

> 适合有独立 Linux 服务器（Ubuntu 22.04 / Debian 12 推荐）且不使用 Docker 的场景。

### 3.1 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget build-essential

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 安装 Node.js 20 (使用 nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# 安装 PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-client-16

# 安装 Redis 7
sudo apt install -y redis-server
sudo systemctl enable redis-server && sudo systemctl start redis-server
```

#### 初始化 PostgreSQL

```bash
sudo -u postgres psql <<'EOF'
CREATE USER zhinong WITH PASSWORD 'your_strong_password';
CREATE DATABASE zhinong OWNER zhinong;
\q
EOF
```

### 3.2 后端部署

```bash
# 克隆仓库
git clone https://github.com/Andrewrover-01/ZhinongXingxiang.git
cd ZhinongXingxiang/backend

# 创建并激活虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
```

编辑 `.env`：

```dotenv
DATABASE_URL=postgresql+psycopg2://zhinong:your_strong_password@localhost:5432/zhinong
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<用 python -c "import secrets; print(secrets.token_hex(32))" 生成>
QWEN_API_KEY=sk-xxxxxxxx
CHROMA_PERSIST_DIR=/home/<user>/zhinong_chroma
UPLOAD_DIR=/home/<user>/zhinong_uploads
CORS_ORIGINS=["https://yourdomain.com"]
```

```bash
# 创建上传目录
mkdir -p ~/zhinong_uploads ~/zhinong_chroma

# 导入知识库
python scripts/ingest_knowledge.py

# 测试启动（验证配置正确）
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### 配置 systemd 服务（后台运行）

```bash
sudo tee /etc/systemd/system/zhinong-backend.service > /dev/null <<EOF
[Unit]
Description=ZhinongXingxiang FastAPI Backend
After=network.target postgresql.service redis.service

[Service]
User=$(whoami)
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zhinong-backend
sudo systemctl start zhinong-backend
sudo systemctl status zhinong-backend
```

### 3.3 前端部署

```bash
cd ../frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
```

编辑 `.env.local`：

```dotenv
# 填写服务器后端的公网地址或域名
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

```bash
# 构建生产版本（standalone 模式，适合服务器部署）
npm run build

# 测试启动
node .next/standalone/server.js
```

#### 配置 systemd 服务

```bash
sudo tee /etc/systemd/system/zhinong-frontend.service > /dev/null <<EOF
[Unit]
Description=ZhinongXingxiang Next.js Frontend
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$(pwd)/.next/standalone
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=HOSTNAME=127.0.0.1
ExecStart=$(which node) server.js
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zhinong-frontend
sudo systemctl start zhinong-frontend
```

### 3.4 Nginx 反向代理

```bash
sudo apt install -y nginx
sudo tee /etc/nginx/sites-available/zhinong > /dev/null <<'EOF'
server {
    listen 80;
    server_name yourdomain.com;

    # 前端
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # SSE 流式响应需要关闭缓冲
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/zhinong /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

> 💡 **配置 HTTPS（推荐）：** 安装 Certbot 申请免费 SSL 证书：
> ```bash
> sudo apt install -y certbot python3-certbot-nginx
> sudo certbot --nginx -d yourdomain.com
> ```

---

## 📚 知识库数据导入

知识库种子数据位于 `backend/data/knowledge.jsonl`，每行一条 JSON 记录。

```bash
# 进入 backend 目录并激活虚拟环境（手动部署时）
cd backend && source .venv/bin/activate

# 完整导入（首次）
python scripts/ingest_knowledge.py

# 指定文件路径
python scripts/ingest_knowledge.py --file data/knowledge.jsonl

# 跳过已存在的条目（增量更新）
python scripts/ingest_knowledge.py --skip-existing

# 试运行（不写入数据库，仅验证格式）
python scripts/ingest_knowledge.py --dry-run
```

**Docker Compose 环境下：**

```bash
docker compose exec backend python scripts/ingest_knowledge.py --skip-existing
```

---

## 📱 APK 打包

> 前端通过 [Capacitor](https://capacitorjs.com/) 打包为 Android 原生 APP。
> APK 内嵌静态 Web 页面，通过 HTTP API 与后端通信。

### 5.1 前置要求

| 工具 | 版本要求 | 安装方式 |
|------|----------|----------|
| Node.js | ≥ 20 | nvm / 官网 |
| JDK | 17 或 21 | `sudo apt install openjdk-17-jdk` |
| Android Studio | 最新稳定版 | [developer.android.com](https://developer.android.com/studio) |
| Android SDK | API Level ≥ 33 | 通过 Android Studio SDK Manager 安装 |
| ANDROID_HOME | 已设置 | 见下方说明 |

**配置 ANDROID_HOME（Linux / macOS）：**

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
source ~/.bashrc
```

### 5.2 构建静态前端

APK 内嵌的是 Next.js 的**静态导出（`output: "export"`）**，需单独构建：

```bash
cd frontend

# 安装依赖（若尚未安装）
npm install

# 配置 APK 内访问的后端地址（改为服务器真实地址）
# 编辑 .env.local：
echo "NEXT_PUBLIC_API_URL=https://api.yourdomain.com" > .env.local
```

> ⚠️ `NEXT_PUBLIC_API_URL` 必须填写**外网可访问的后端地址**（不能是 localhost），
> 因为 Android 设备运行时无法访问开发机的 localhost。

```bash
# 构建静态资源（生成 out/ 目录）
npm run build:capacitor
```

构建完成后，`frontend/out/` 目录即为 APK 内嵌的静态页面。

### 5.3 同步到 Android 工程

```bash
# 一步完成：构建静态资源 + 同步到 android/ 工程
npm run cap:sync

# 等价于分步执行：
# npm run build:capacitor        # 生成 out/
# npx cap sync android           # 复制 out/ 到 android 工程 + 更新插件
```

> 首次执行 `cap sync` 时，Capacitor 会自动在 `frontend/android/` 目录下生成完整的 Android Gradle 工程。

### 5.4 用 Android Studio 打包 APK

```bash
# 用 Android Studio 打开 android/ 工程
npm run cap:open
# 或：
npx cap open android
```

在 Android Studio 中：

1. 等待 Gradle Sync 完成（首次约 5–10 分钟，需下载依赖）
2. 菜单 **Build → Generate Signed App Bundle / APK**
3. 选择 **APK**，点击 **Next**
4. 选择或新建签名密钥（Keystore）：
   - Key store path：选择 `.jks` 文件，或点击 **Create new** 创建
   - 填写密钥别名、密码等信息
5. 选择构建类型：
   - **debug**：用于测试，无需签名配置
   - **release**：用于正式发布，需要签名
6. 点击 **Finish**，等待构建完成
7. APK 文件路径：`android/app/build/outputs/apk/release/app-release.apk`

### 5.5 命令行打包（可选）

如需在 CI / 服务器环境下无界面打包：

```bash
# 进入 Android 工程目录
cd frontend/android

# 构建 debug APK（无需签名）
./gradlew assembleDebug

# 构建 release APK（需配置签名）
./gradlew assembleRelease \
  -Pandroid.injected.signing.store.file=/path/to/keystore.jks \
  -Pandroid.injected.signing.store.password=STORE_PASS \
  -Pandroid.injected.signing.key.alias=KEY_ALIAS \
  -Pandroid.injected.signing.key.password=KEY_PASS
```

**APK 输出路径：**

```
frontend/android/app/build/outputs/apk/debug/app-debug.apk
frontend/android/app/build/outputs/apk/release/app-release.apk
```

---

## ⚙️ 环境变量说明

### 后端（`backend/.env`）

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | ✅ | `sqlite:///./zhinong.db` | 数据库连接串（生产环境用 PostgreSQL） |
| `REDIS_URL` | ✅ | `redis://localhost:6379/0` | Redis 连接串 |
| `SECRET_KEY` | ✅ | — | JWT 签名密钥，生产环境必须修改 |
| `QWEN_API_KEY` | ✅* | — | 通义千问 API Key（与 OPENAI_API_KEY 二选一） |
| `OPENAI_API_KEY` | ✅* | — | OpenAI API Key（与 QWEN_API_KEY 二选一） |
| `ALGORITHM` | | `HS256` | JWT 算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | `10080` | Token 有效期（分钟），默认 7 天 |
| `UPLOAD_DIR` | | `./uploads` | 图片上传目录 |
| `CHROMA_PERSIST_DIR` | | `./chroma_data` | ChromaDB 向量库持久化目录 |
| `CACHE_TTL` | | `3600` | Redis 缓存 TTL（秒） |
| `CORS_ORIGINS` | | `["http://localhost:3000"]` | 允许的前端跨域地址（JSON 数组） |

### 前端（`frontend/.env.local`）

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `NEXT_PUBLIC_API_URL` | ✅ | 后端 API 地址，如 `https://api.yourdomain.com` |

---

## ❓ 常见问题

**Q: Docker Compose 启动后后端报 `connection refused` 连接数据库失败？**

A: PostgreSQL 容器需要初始化时间。后端容器已配置 `depends_on: condition: service_healthy`，一般会自动等待。若仍失败，执行 `docker compose restart backend` 重启后端即可。

---

**Q: 知识库导入时报 `ChromaDB` 相关错误？**

A: 确保 `CHROMA_PERSIST_DIR` 目录有写权限，且磁盘空间充足（向量库首次建立约占 500MB）。

---

**Q: APK 安装到手机后无法连接后端（空白页 / 请求失败）？**

A: 检查以下几点：
1. `NEXT_PUBLIC_API_URL` 必须是**公网 IP 或域名**，不能是 `localhost`
2. 服务器防火墙开放了 `8000` 端口（或通过 Nginx 代理的 `80/443`）
3. 若服务器仅有 HTTP（无 HTTPS），需在 `capacitor.config.ts` 中确认 `allowMixedContent: true`

---

**Q: Android Studio Gradle Sync 失败，提示下载超时？**

A: 网络问题。可在 `frontend/android/gradle.properties` 中添加代理配置，或使用镜像源（阿里云 Maven 镜像）：

```properties
# android/gradle.properties
org.gradle.jvmargs=-Xmx2048m
# 配置网络代理（如需要）
systemProp.https.proxyHost=127.0.0.1
systemProp.https.proxyPort=7890
```

---

**Q: 生产环境如何更新部署？**

```bash
# Docker Compose 方式
git pull
docker compose up -d --build

# 手动部署方式
git pull
# 后端
cd backend && source .venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart zhinong-backend
# 前端
cd ../frontend && npm install && npm run build
sudo systemctl restart zhinong-frontend
```

