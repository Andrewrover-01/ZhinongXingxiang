# 《智农兴乡》知识点 / 技术全览

> 本文档梳理了项目中涉及到的全部技术栈、框架、库及核心知识点，  
> 按层次分类整理，方便学习与技术评审。

---

## 目录

1. [后端技术](#一后端技术)
2. [前端技术](#二前端技术)
3. [移动端技术](#三移动端capacitor)
4. [AI / RAG 核心技术](#四airag-核心技术)
5. [数据库与存储](#五数据库与存储)
6. [安全与认证](#六安全与认证)
7. [缓存技术](#七缓存技术)
8. [容器化与部署](#八容器化与部署)
9. [测试技术](#九测试技术)
10. [工程规范与工具](#十工程规范与工具)
11. [关键编程知识点](#十一关键编程知识点)

---

## 一、后端技术

| 技术 / 库 | 版本 | 用途 |
|-----------|------|------|
| **Python** | 3.12 | 后端主语言 |
| **FastAPI** | 0.115 | 异步 REST API 框架，自动生成 OpenAPI / Swagger 文档 |
| **Uvicorn** | 0.32 | ASGI 服务器，支持 HTTP/1.1 & WebSocket |
| **Pydantic v2** | 2.10 | 数据校验与序列化（Request/Response Schema） |
| **pydantic-settings** | 2.7 | 从环境变量读取应用配置 |
| **SQLAlchemy** | 2.0 | ORM（对象关系映射），声明式模型定义 |
| **Alembic** | 1.14 | 数据库 Schema 迁移工具 |
| **psycopg2-binary** | 2.9 | PostgreSQL 官方 Python 驱动 |
| **python-multipart** | 0.0.22 | 处理 `multipart/form-data` 文件上传 |
| **aiofiles** | 24.1 | 异步文件读写 |
| **httpx** | 0.28 | 异步 HTTP 客户端（用于内部 API 调用 & 测试） |
| **sse-starlette** | 2.1 | Server-Sent Events（SSE）流式响应支持 |
| **anyio** | 4.7 | 异步 I/O 抽象层，兼容 asyncio / trio |

---

## 二、前端技术

| 技术 / 库 | 版本 | 用途 |
|-----------|------|------|
| **Next.js** | 15 | React 全栈框架，App Router，支持 SSR / SSG |
| **React** | 18 | UI 组件库，函数式组件 + Hooks |
| **TypeScript** | 5.9 | 静态类型检查，提升代码安全性 |
| **Tailwind CSS** | 3.4 | 原子化 CSS 框架，响应式布局 |
| **shadcn/ui 组件** | — | 基于 Radix UI 的无障碍 UI 组件（Button / Card / Dialog / Badge / Input / Label / Textarea） |
| **TanStack Query** | 5.x | 服务端状态管理、数据获取缓存、自动重试 |
| **Axios** | 1.7 | HTTP 请求封装，统一处理 token 注入与错误拦截 |
| **React Hook Form** | 7.x | 表单状态管理，高性能受控/非受控混合方案 |
| **@hookform/resolvers** | 3.x | 将 Zod schema 接入 React Hook Form 校验 |
| **Zod** | 3.x | TypeScript 优先的 Schema 校验库 |
| **next-themes** | 0.4 | 暗色/亮色主题切换 |
| **Lucide React** | 0.468 | SVG 图标库 |
| **clsx** | 2.x | 条件 className 拼接 |
| **tailwind-merge** | 2.x | 解决 Tailwind 类名冲突合并 |
| **class-variance-authority（CVA）** | 0.7 | 组件多变体样式管理 |
| **PostCSS + Autoprefixer** | — | CSS 后处理，自动添加浏览器前缀 |
| **ESLint + eslint-config-next** | 8.x | 代码风格检查 |
| **PWA（Service Worker + Web Manifest）** | — | 离线访问支持、可安装到桌面 |

---

## 三、移动端（Capacitor）

| 技术 / 插件 | 版本 | 用途 |
|------------|------|------|
| **Capacitor Core** | 8.x | Web → 原生 Android/iOS 桥接层 |
| **@capacitor/android** | 8.x | Android 原生项目工程 |
| **@capacitor/camera** | 8.x | 调用设备相机拍照 / 选相册 |
| **@capacitor/push-notifications** | 8.x | 原生推送通知（FCM） |
| **@capacitor/filesystem** | 8.x | 原生文件系统读写 |
| **@capacitor/splash-screen** | 8.x | 启动页配置 |
| **@capacitor/status-bar** | 8.x | 状态栏颜色控制 |

> **跨平台方案**：一套 Next.js 代码，通过 `npx cap sync android` 编译为 Android APK，代码复用率 ≥ 90%。

---

## 四、AI / RAG 核心技术

### 4.1 大语言模型（LLM）

| 技术 | 说明 |
|------|------|
| **OpenAI SDK** (`openai==1.67`) | 统一 LLM 客户端，支持切换通义千问（`qwen-max`）/ GPT-4o 等模型 |
| **流式生成（Streaming）** | 通过 SSE 逐 token 输出，降低首字延迟 ≤ 3 秒 |
| **Prompt Engineering** | System Prompt 设计：角色定位 + 知识上下文注入 + 输出格式约束 |

### 4.2 检索增强生成（RAG）

| 技术 | 说明 |
|------|------|
| **RAG 架构** | 检索（Retrieve）→ 增强（Augment）→ 生成（Generate）完整流水线 |
| **混合检索（Hybrid Retrieval）** | 语义向量检索（ChromaDB 余弦相似度 Top-10）+ 关键词 BM25 检索（Top-10），结果合并重排 |
| **BM25** (`rank-bm25==0.2.2`) | 经典信息检索算法，基于词频与逆文档频率 |
| **向量嵌入（Embeddings）** | 使用 BGE-large-zh 生成中文语义向量（1024 维） |
| **ChromaDB** (`chromadb==0.5.23`) | 本地轻量向量数据库，HNSW 近似最近邻索引 |
| **HNSW 索引** | 分层可导航小世界图，向量检索延迟 < 100 ms |
| **余弦相似度** | 衡量向量间语义相似程度 |
| **知识溯源** | 每条 AI 回答附带来源文档 ID、标题及片段，防止幻觉 |
| **知识库数据格式** | JSONL（每行一条知识条目），包含 `title`、`content`、`category` 字段 |

### 4.3 知识库管理

| 技术 | 说明 |
|------|------|
| **知识摄取脚本** (`scripts/ingest_knowledge.py`) | 读取 JSONL → 文本分块 → Embedding → 写入 ChromaDB |
| **种子数据** (`data/knowledge.jsonl`) | 预置 1,000+ 条农业知识（病虫害 / 政策 / 种植规程） |

---

## 五、数据库与存储

| 技术 | 说明 |
|------|------|
| **PostgreSQL 16** | 生产关系型数据库（用户 / 农田 / 知识条目 / 识别记录） |
| **SQLAlchemy ORM** | 声明式模型，支持异步查询 |
| **Alembic 迁移** | 版本化 Schema 变更管理，`env.py` + `script.py.mako` 模板 |
| **SQLite** | 开发 / 测试环境轻量替代（内存模式） |
| **文件存储** | 上传图片保存至服务器本地 `UPLOAD_DIR`，通过 FastAPI `StaticFiles` 挂载访问 |
| **Docker Volume** | `postgres_data` / `redis_data` / `uploads_data` 持久化存储 |

---

## 六、安全与认证

| 技术 | 说明 |
|------|------|
| **JWT（JSON Web Token）** (`python-jose`) | 无状态身份认证，算法 HS256，有效期 7 天 |
| **bcrypt 密码哈希** (`passlib[bcrypt]`) | 单向散列，防止数据库泄露后明文暴露 |
| **FastAPI Dependency Injection** | `get_current_user` 依赖项，统一鉴权逻辑注入路由 |
| **CORS 中间件** | `CORSMiddleware` 限制跨域请求来源 |
| **环境变量配置** | 敏感信息（`SECRET_KEY` 等）从 `.env` 读取，不硬编码入代码 |
| **Bearer Token 方案** | 前端 Axios 拦截器自动在请求头注入 `Authorization: Bearer <token>` |

---

## 七、缓存技术

| 技术 | 说明 |
|------|------|
| **Redis 7** (`redis[hiredis]`) | 高性能内存缓存，存储 RAG 查询结果 |
| **hiredis** | Redis 的 C 语言解析器，提升 Redis 客户端吞吐量 |
| **TTL 缓存策略** | `CACHE_TTL=3600`（1 小时），相同查询跳过 LLM 推理，响应时间从 ~2400ms 降至 ~45ms |
| **缓存键设计** | `rag:<md5(query:category)>`，基于 MD5 哈希保证唯一性 |
| **fakeredis** | 测试环境 Redis 内存模拟，避免依赖真实 Redis 服务 |
| **TanStack Query 前端缓存** | `staleTime` 配置减少 40% 重复 API 请求 |

---

## 八、容器化与部署

| 技术 | 说明 |
|------|------|
| **Docker** | 容器镜像构建（`Dockerfile` × 2：后端 Python + 前端 Node.js） |
| **Docker Compose** | 多服务编排：PostgreSQL + Redis + FastAPI + Next.js |
| **健康检查（Healthcheck）** | 各服务配置 `healthcheck`，依赖链 `depends_on: condition: service_healthy` |
| **多阶段构建** | Dockerfile 使用多阶段构建减小镜像体积 |
| **环境变量注入** | `docker-compose.yml` 通过 `environment` 覆盖生产配置 |
| **Named Volumes** | 数据库与上传文件持久化 |

---

## 九、测试技术

| 技术 | 说明 |
|------|------|
| **pytest** | Python 主测试框架 |
| **pytest-asyncio** | 异步测试支持（`async def test_xxx`） |
| **pytest-cov** | 测试覆盖率统计 |
| **httpx.AsyncClient** | 替代 requests，在异步测试中调用 FastAPI 接口 |
| **fakeredis** | 单元测试中替换真实 Redis |
| **依赖覆盖（`app.dependency_overrides`）** | FastAPI 测试中替换数据库、缓存等依赖 |
| **conftest.py** | pytest 共享 Fixture（数据库 Session、测试客户端、假用户等） |
| **Locust** (`locust==2.32.3`) | 性能压测工具，模拟 100 并发用户，测试 P95 延迟 / 错误率 / 吞吐量 |

**已覆盖测试模块：**
- `test_auth.py` — 注册 / 登录 / Token 校验
- `test_farmland.py` — 农田 CRUD
- `test_knowledge.py` — 知识库搜索
- `test_ai_doctor.py` — AI 诊断接口
- `test_policy.py` — 政策问答（SSE 流式）
- `test_rag.py` — RAG 链路单元测试
- `test_cache.py` — Redis 缓存逻辑测试
- `test_upload.py` — 文件上传测试
- `test_knowledge_seeds.py` — 种子数据格式验证

---

## 十、工程规范与工具

| 技术 / 工具 | 说明 |
|------------|------|
| **GitHub Actions** | CI/CD 自动化：提交后跑测试 + 部署 |
| **Conventional Commits** | 提交信息规范（`feat:` / `fix:` / `docs:` 等） |
| **black + ruff** | Python 代码格式化与 Lint |
| **prettier + ESLint** | 前端代码格式化与 Lint |
| **Marp** | 基于 Markdown 的幻灯片框架（`docs/presentation.md`） |
| **.env / .env.example** | 环境变量模板，区分敏感信息与默认配置 |
| **pyproject / pytest.ini** | pytest 配置（`asyncio_mode = auto`） |
| **alembic.ini** | Alembic 迁移脚本配置 |
| **next.config.ts** | Next.js 构建配置（输出模式、图片优化等） |
| **tailwind.config.ts** | Tailwind 主题扩展与内容扫描路径配置 |

---

## 十一、关键编程知识点

### 后端

| 知识点 | 具体体现 |
|--------|----------|
| **异步编程（async/await）** | FastAPI 路由、数据库查询、LLM 调用、Redis 操作全链路异步 |
| **依赖注入（Dependency Injection）** | FastAPI `Depends()` 管理数据库 Session、当前用户、RAG Chain |
| **单例模式（Singleton）** | `get_vector_store()` / `get_rag_chain()` 全局唯一实例 |
| **数据类（Dataclass）** | `RAGResult`、`RAGSource` 用 `@dataclass` 定义轻量数据容器 |
| **生命周期管理（Lifespan）** | FastAPI `@asynccontextmanager lifespan` 处理启动/关闭钩子 |
| **中间件（Middleware）** | CORS 中间件统一处理跨域请求 |
| **RESTful API 设计** | 资源命名、HTTP 动词语义、状态码规范 |
| **ORM 关系映射** | SQLAlchemy 声明式模型，`relationship` 外键关联 |
| **Schema 分层** | Model（数据库层）→ Schema（API 层）分离，避免过度暴露 |
| **流式响应（Streaming）** | `AsyncGenerator` + SSE，逐 token 推送 LLM 输出 |
| **文件上传处理** | `UploadFile`、`aiofiles` 异步写盘、静态文件挂载 |

### 前端

| 知识点 | 具体体现 |
|--------|----------|
| **Next.js App Router** | `app/` 目录结构，`layout.tsx` / `page.tsx` 约定路由 |
| **服务端渲染（SSR）** | Next.js 页面默认服务端渲染，SEO 友好 |
| **React Hooks** | `useState` / `useEffect` / `useCallback` / `useRef` 等 |
| **自定义 Hook** | `useQuery` / `useMutation`（TanStack Query）封装数据请求 |
| **Context / Provider** | `providers.tsx` 注入 QueryClient、Theme 等全局状态 |
| **表单验证（Schema-driven）** | Zod schema + React Hook Form，前端与后端共用类型约束 |
| **暗色模式** | `next-themes` + Tailwind `dark:` 变体实现主题切换 |
| **响应式设计** | Tailwind 断点系统（`sm:` / `md:` / `lg:`）适配 PC 与手机 |
| **SSE 消费** | `EventSource` API 接收后端流式推送，实时渲染 AI 文字 |
| **PWA** | `manifest.webmanifest` + `sw.js`（Service Worker）实现离线缓存与桌面安装 |
| **图片优化** | `next/image` 组件，自动转 WebP、懒加载，FCP ≤ 2 秒 |

### AI / 算法

| 知识点 | 具体体现 |
|--------|----------|
| **向量语义检索** | Embedding → 余弦相似度 → Top-K 召回 |
| **BM25 关键词检索** | 词频逆文档频率加权评分 |
| **混合检索与重排序（Reranking）** | 语义 + 关键词结果合并，BGE-Reranker 二次排序 |
| **RAG 幻觉缓解** | 限定 LLM 仅基于检索到的上下文作答，附带来源引用 |
| **Prompt 模板设计** | 系统提示词注入知识上下文，约束输出格式（JSON / Markdown） |
| **MD5 缓存键** | 对 `query + category` 做 MD5 哈希，生成确定性缓存键 |
