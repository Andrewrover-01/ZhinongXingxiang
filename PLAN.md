# 《智农兴乡》阶段性开发计划书

> 项目类型：大学生创新创业训练计划（大创）  
> 项目定位：基于 RAG 的智慧农业全栈平台  
> 发展理念：融合「新农科」建设与「人工智能+」战略，以 AI 技术赋能农业现代化，助力乡村振兴

---

## 目录

1. [项目背景与愿景](#一项目背景与愿景)
2. [功能架构设计](#二功能架构设计)
3. [技术选型与理由](#三技术选型与理由)
4. [数据库模型设计](#四数据库模型设计)
5. [分阶段开发目标](#五分阶段开发目标)
6. [团队分工与协作](#六团队分工与协作)
7. [风险评估与应对](#七风险评估与应对)

---

## 一、项目背景与愿景

### 1.1 背景

在「新农科」建设和「人工智能+」行动的双重驱动下，农业生产正经历从传统经验驱动向数据智能驱动的历史性转变。然而，我国广大农村地区仍面临以下核心痛点：

- **农技普及不均衡**：基层农技推广体系薄弱，农民获取专业知识渠道匮乏。
- **病虫害诊断滞后**：依赖肉眼经验判断，误诊率高，防治时机延误。
- **农政信息碎片化**：补贴政策、种植规程散落多处，农民难以高效获取。
- **精准农业落地难**：气象、土壤、产量等多源数据缺乏统一管理与可视化。

### 1.2 愿景

《智农兴乡》致力于构建一个"**会看病、懂政策、知农情、能决策**"的智慧农业 AI 平台，将大语言模型（LLM）与检索增强生成（RAG）技术深度融合，通过移动端 APP 和 Web 端双入口，让每一位农民都能享受到触手可及的 AI 农业顾问服务。

---

## 二、功能架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    《智农兴乡》平台                           │
│  ┌───────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │  AI 医生  │  │ 农策助手  │  │ 数据看板 │  │ 农事Agent│  │
│  └─────┬─────┘  └─────┬─────┘  └────┬─────┘  └────┬─────┘  │
│        └──────────────┴──────────────┴──────────────┘        │
│                        ▼                                      │
│              ┌──────────────────┐                            │
│              │  RAG 知识引擎    │                            │
│              │  ChromaDB + LLM  │                            │
│              └────────┬─────────┘                            │
│                       ▼                                       │
│              ┌──────────────────┐                            │
│              │  FastAPI 后端    │                            │
│              └────────┬─────────┘                            │
│         ┌─────────────┴──────────────┐                       │
│         ▼                            ▼                        │
│  ┌─────────────┐             ┌──────────────┐               │
│  │ Next.js Web │             │Capacitor APP │               │
│  └─────────────┘             └──────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心功能模块

#### 2.2.1 AI 医生（病虫害智能诊断）

**功能定位**：农作物"私人医生"，通过图文多模态输入，快速诊断病虫害并给出防治方案。

| 子功能 | 说明 |
|--------|------|
| 图像上传识别 | 支持拍照/相册选图，调用视觉模型分析病症 |
| 多模态问诊 | 结合图片 + 文字描述，提升诊断精准度 |
| RAG 方案检索 | 从农业知识库中检索最优防治方案 |
| 历史记录管理 | 记录每次诊断结果，支持回溯分析 |
| 防治药品推荐 | 依据病症推荐适配农药，标注用量与注意事项 |

**技术流程**：
```
用户上传图片
    ↓
视觉模型（如 GPT-4V / 本地多模态模型）提取图像特征
    ↓
特征向量化 → ChromaDB 检索相似案例
    ↓
LLM + 检索结果 生成诊断报告
    ↓
返回：病害名称 + 严重程度 + 防治方案 + 药品建议
```

#### 2.2.2 农策助手（农业政策智能问答）

**功能定位**：政策"翻译官"，将复杂的农业政策、补贴信息转化为农民可理解的问答形式。

| 子功能 | 说明 |
|--------|------|
| 政策问答 | 自然语言提问，RAG 检索政策原文并生成通俗解答 |
| 补贴计算器 | 根据农田面积、作物类型计算可申请补贴金额 |
| 种植规程查询 | 检索特定作物的标准化种植技术规程 |
| 政策推送订阅 | 根据用户画像推送相关最新政策 |

#### 2.2.3 数据看板（农业数据可视化）

**功能定位**：农情"仪表盘"，整合多源农业数据，提供可视化洞察。

| 子功能 | 说明 |
|--------|------|
| 农田概况 | 地块数量、总面积、作物分布统计 |
| 气象监测 | 接入气象 API，展示温湿度、降雨量、风速等 |
| 病虫害趋势 | 本地区历史病虫害发生频率与趋势图 |
| 产量预测 | 基于历史数据与气象条件的产量预测模型 |
| 投入产出分析 | 种植成本与收益的对比分析 |

#### 2.2.4 农事 Agent（自主农业决策助手）

**功能定位**：农业"参谋长"，结合用户农田实际情况，主动规划农事活动并执行工具调用。

| 子功能 | 说明 |
|--------|------|
| 农事日历生成 | 依据作物种类与生长周期，自动生成农事操作日历 |
| 浇水施肥建议 | 结合土壤数据与气象预报，给出精准灌溉施肥建议 |
| 工具调用能力 | 调用天气 API、病虫害数据库、补贴查询等外部工具 |
| 多轮对话规划 | 支持与农民多轮交互，逐步细化农事方案 |
| 任务提醒推送 | 关键农事节点（播种、施肥、收割）提前推送提醒 |

---

## 三、技术选型与理由

### 3.1 后端框架：FastAPI

**选择理由**：

| 维度 | 说明 |
|------|------|
| **性能** | 基于 Starlette + Pydantic，异步处理能力强，适合高并发的 AI 推理请求 |
| **AI 生态** | Python 原生支持所有主流 AI/ML 库（LangChain、OpenAI SDK、PyTorch 等） |
| **类型安全** | Pydantic 数据验证自动生成 JSON Schema，与前端类型系统无缝集成 |
| **自动文档** | 内置 Swagger UI 与 ReDoc，便于接口调试与团队协作 |
| **RAG 集成** | 与 LangChain、LlamaIndex 等 RAG 框架深度兼容 |
| **学习成本** | 语法简洁，适合大创项目团队快速上手 |

```python
# 示例：FastAPI + LangChain RAG 接口
from fastapi import FastAPI
from langchain.chains import RetrievalQA

app = FastAPI()

@app.post("/api/ai-doctor/diagnose")
async def diagnose(image_url: str, description: str):
    # 多模态 RAG 诊断逻辑
    result = await rag_chain.ainvoke({
        "image": image_url,
        "query": description
    })
    return {"diagnosis": result}
```

### 3.2 前端框架：Next.js

**选择理由**：

| 维度 | 说明 |
|------|------|
| **SSR/SSG** | 服务端渲染提升 SEO 与首屏加载速度，适合数据看板场景 |
| **全栈能力** | API Routes 支持轻量后端逻辑，减少架构复杂度 |
| **生态成熟** | React 生态丰富，Tailwind CSS、shadcn/ui 等组件库快速构建 UI |
| **TypeScript** | 原生 TypeScript 支持，提升代码可维护性 |
| **移动适配** | 响应式设计与 Capacitor 无缝集成，实现 Web/APP 代码复用 |
| **图表支持** | 与 Recharts、ECharts 等可视化库兼容，满足数据看板需求 |

### 3.3 向量数据库：ChromaDB

**选择理由**：

| 维度 | 说明 |
|------|------|
| **轻量部署** | 嵌入式运行，无需独立服务，适合大创项目初期快速验证 |
| **Python 原生** | Python SDK 简洁，与 LangChain/LlamaIndex 深度集成 |
| **持久化存储** | 支持本地持久化，农业知识库数据不丢失 |
| **多模态支持** | 支持文本、图像等多种嵌入向量存储，适配 AI 医生图像检索场景 |
| **过滤查询** | 支持元数据过滤，可按作物类型、病害类别精准检索 |
| **免费开源** | 完全开源，无商业授权限制，适合学术项目 |

```python
# 示例：ChromaDB 农业知识库构建
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_data")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-large-zh-v1.5"  # 中文农业语料优化模型
)

collection = client.get_or_create_collection(
    name="agriculture_knowledge",
    embedding_function=ef,
    metadata={"hnsw:space": "cosine"}
)
```

### 3.4 移动端框架：Capacitor

**选择理由**：

| 维度 | 说明 |
|------|------|
| **代码复用** | 将 Next.js Web 代码直接封装为 Android/iOS APP，复用率 ≥ 90% |
| **原生能力** | 访问摄像头、相册、推送通知等原生 API，满足 AI 医生拍照需求 |
| **轻量打包** | 相较于 React Native，构建流程更简单，适合大创项目周期 |
| **APK 输出** | 直接生成 Android APK，便于参赛展示与用户测试 |
| **插件生态** | 丰富的官方插件（Camera、Filesystem、Push Notifications 等） |

### 3.5 技术栈全景

```
┌─────────────────────────────────────────────────────┐
│                   技术栈全景图                        │
│                                                     │
│  移动端        Web 端          后端          数据层  │
│  ┌────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐ │
│  │Capacitor│  │ Next.js  │  │FastAPI  │  │Postgres│ │
│  │Android │  │Tailwind  │  │LangChain│  │SQLite  │ │
│  │  APK   │  │shadcn/ui │  │LlamaIdx │  │ChromaDB│ │
│  └────────┘  └──────────┘  └─────────┘  └────────┘ │
│                    ↕              ↕                  │
│              ┌───────────────────────┐               │
│              │     REST / WebSocket  │               │
│              └───────────────────────┘               │
│                                                     │
│  AI 模型层                    DevOps                │
│  ┌──────────────────────┐  ┌────────────────────┐  │
│  │ OpenAI GPT-4o / 本地 │  │ Docker Compose     │  │
│  │ Qwen-VL (多模态)     │  │ GitHub Actions CI  │  │
│  │ BGE-Large-ZH (向量)  │  │ Nginx 反向代理     │  │
│  └──────────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 四、数据库模型设计

### 4.1 设计原则

- **关系型数据库**（PostgreSQL / SQLite）：存储结构化业务数据（用户、农田、记录）。
- **向量数据库**（ChromaDB）：存储知识库文档的嵌入向量，支持语义检索。
- **对象存储**（本地 / MinIO）：存储用户上传的图片、文档等二进制文件。

### 4.2 用户模型（User）

```sql
-- 用户表
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username    VARCHAR(50)  UNIQUE NOT NULL,
    phone       VARCHAR(20)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name   VARCHAR(50),
    province    VARCHAR(50),          -- 所在省份
    city        VARCHAR(50),          -- 所在市县
    role        VARCHAR(20)  NOT NULL DEFAULT 'farmer',
                                      -- farmer | expert | admin
    avatar_url  VARCHAR(500),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);
```

```python
# Pydantic / SQLAlchemy ORM 模型
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[Optional[str]] = mapped_column(String(50))
    province: Mapped[Optional[str]] = mapped_column(String(50))
    city: Mapped[Optional[str]] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), default="farmer")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    farmlands: Mapped[List["Farmland"]] = relationship(back_populates="owner")
    recognition_records: Mapped[List["RecognitionRecord"]] = relationship(back_populates="user")
```

### 4.3 农田模型（Farmland）

```sql
-- 农田表
CREATE TABLE farmlands (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,               -- 地块名称（如"东头二亩地"）
    area        DECIMAL(10, 2) NOT NULL,             -- 面积（亩）
    location    VARCHAR(200),                        -- 文字地址描述
    latitude    DECIMAL(10, 7),                      -- 纬度
    longitude   DECIMAL(10, 7),                      -- 经度
    soil_type   VARCHAR(50),                         -- 土壤类型（黏土/沙土/壤土等）
    crop_type   VARCHAR(100),                        -- 当前种植作物
    crop_stage  VARCHAR(50),                         -- 作物生长阶段（育苗/分蘖/抽穗等）
    sowing_date DATE,                                -- 播种日期
    notes       TEXT,                                -- 备注信息
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 农田作物历史记录
CREATE TABLE farmland_crop_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmland_id UUID NOT NULL REFERENCES farmlands(id) ON DELETE CASCADE,
    crop_type   VARCHAR(100) NOT NULL,
    sowing_date DATE,
    harvest_date DATE,
    yield_kg    DECIMAL(10, 2),                     -- 产量（公斤）
    notes       TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

```python
class Farmland(Base):
    __tablename__ = "farmlands"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    soil_type: Mapped[Optional[str]] = mapped_column(String(50))
    crop_type: Mapped[Optional[str]] = mapped_column(String(100))
    crop_stage: Mapped[Optional[str]] = mapped_column(String(50))
    sowing_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    owner: Mapped["User"] = relationship(back_populates="farmlands")
    recognition_records: Mapped[List["RecognitionRecord"]] = relationship(back_populates="farmland")
```

### 4.4 知识库模型（KnowledgeBase）

```sql
-- 知识库文档表（元数据）
CREATE TABLE knowledge_documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(200) NOT NULL,
    source      VARCHAR(200),                        -- 来源（农业部官网/教材/论文等）
    category    VARCHAR(50)  NOT NULL,               -- 分类：disease | policy | technique | pest
    crop_types  TEXT[],                              -- 适用作物类型数组
    region      VARCHAR(100),                        -- 适用地区
    content     TEXT         NOT NULL,               -- 原文内容
    summary     TEXT,                                -- AI 生成摘要
    chroma_id   VARCHAR(100) UNIQUE,                 -- ChromaDB 中的文档 ID
    file_url    VARCHAR(500),                        -- 原始文件存储路径
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,      -- 是否经专家审核
    upload_by   UUID REFERENCES users(id),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 知识库分类枚举
-- disease  : 病虫害知识
-- policy   : 农业政策法规
-- technique: 种植技术规程
-- pest     : 农药化肥信息
-- weather  : 气象农事关联
```

```python
class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    crop_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    chroma_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_verified: Mapped[bool] = mapped_column(default=False)
    upload_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 4.5 识别记录模型（RecognitionRecord）

```sql
-- AI 医生识别记录表
CREATE TABLE recognition_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmland_id     UUID REFERENCES farmlands(id) ON DELETE SET NULL,
    image_url       VARCHAR(500)  NOT NULL,          -- 上传图片存储路径
    description     TEXT,                            -- 用户文字描述
    crop_type       VARCHAR(100),                    -- 识别的作物类型
    diagnosis       VARCHAR(200),                    -- 诊断结果（病害名称）
    severity        VARCHAR(20),                     -- 严重程度：mild | moderate | severe
    confidence      DECIMAL(5, 4),                   -- 置信度（0.0000~1.0000）
    treatment_plan  TEXT,                            -- AI 生成防治方案
    medicine_suggest TEXT,                           -- 推荐药品及用量
    rag_sources     JSONB,                           -- 检索到的知识库来源列表
    llm_model       VARCHAR(100),                    -- 使用的 LLM 模型名称
    is_confirmed    BOOLEAN DEFAULT NULL,            -- 用户是否确认诊断结果
    expert_review   TEXT,                            -- 专家复核意见
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 农策助手对话记录表
CREATE TABLE policy_chat_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id  UUID NOT NULL,                       -- 会话 ID（多轮对话归组）
    role        VARCHAR(10) NOT NULL,                -- user | assistant
    content     TEXT        NOT NULL,                -- 消息内容
    rag_sources JSONB,                               -- 检索来源（仅 assistant 消息）
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);
```

```python
class RecognitionRecord(Base):
    __tablename__ = "recognition_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    farmland_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("farmlands.id"))
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    crop_type: Mapped[Optional[str]] = mapped_column(String(100))
    diagnosis: Mapped[Optional[str]] = mapped_column(String(200))
    severity: Mapped[Optional[str]] = mapped_column(String(20))
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    treatment_plan: Mapped[Optional[str]] = mapped_column(Text)
    medicine_suggest: Mapped[Optional[str]] = mapped_column(Text)
    rag_sources: Mapped[Optional[dict]] = mapped_column(JSON)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100))
    is_confirmed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    expert_review: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # 关联
    user: Mapped["User"] = relationship(back_populates="recognition_records")
    farmland: Mapped[Optional["Farmland"]] = relationship(back_populates="recognition_records")
```

### 4.6 E-R 关系图

```
Users ─────────────┬──────── Farmlands
  │  (1:N)         │ (1:N)        │
  │                │              │
  ▼                ▼              ▼
RecognitionRecords           FarmlandCropHistory
  (N:1 farmlands)

Users ──────────── KnowledgeDocuments (上传者)
Users ──────────── PolicyChatHistory (1:N)
```

---

## 五、分阶段开发目标

### 第一阶段：环境搭建与基础 API 开发（第 1-3 周）

**阶段目标**：完成项目脚手架搭建、数据库初始化、核心 CRUD API 开发，形成可演示的基础框架。

#### 1.1 开发任务

**环境搭建**
- [ ] 初始化 Git 仓库，配置 `.gitignore` 与 `README.md`
- [ ] 创建 `backend/` 目录，初始化 FastAPI 项目结构
- [ ] 创建 `frontend/` 目录，初始化 Next.js 14 项目（App Router）
- [ ] 配置 Docker Compose（PostgreSQL + Redis + 后端 + 前端）
- [ ] 搭建 GitHub Actions CI 流水线（代码检查 + 自动测试）

**后端基础**
- [ ] 配置 SQLAlchemy ORM 与 Alembic 数据库迁移
- [ ] 创建四张核心数据表（User / Farmland / KnowledgeDocument / RecognitionRecord）
- [ ] 实现用户注册/登录（JWT 认证，bcrypt 密码加密）
- [ ] 实现农田 CRUD API（增删改查地块信息）
- [ ] 实现图片上传接口（存储到本地 / MinIO）
- [ ] 编写 Pytest 单元测试（覆盖率 ≥ 80%）

**前端基础**
- [ ] 配置 Tailwind CSS + shadcn/ui 组件库
- [ ] 实现用户登录/注册页面
- [ ] 实现农田管理列表页面（含增删改查操作）
- [ ] 配置 Axios / TanStack Query 对接后端 API

#### 1.2 项目目录结构

```
ZhinongXingxiang/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI 入口
│   │   ├── core/
│   │   │   ├── config.py         # 环境变量配置
│   │   │   ├── security.py       # JWT / 密码加密
│   │   │   └── database.py       # 数据库连接
│   │   ├── models/               # SQLAlchemy ORM 模型
│   │   │   ├── user.py
│   │   │   ├── farmland.py
│   │   │   ├── knowledge.py
│   │   │   └── recognition.py
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   ├── routers/              # API 路由
│   │   │   ├── auth.py
│   │   │   ├── farmland.py
│   │   │   ├── ai_doctor.py
│   │   │   ├── policy.py
│   │   │   └── dashboard.py
│   │   ├── services/             # 业务逻辑层
│   │   └── rag/                  # RAG 引擎
│   │       ├── vector_store.py   # ChromaDB 封装
│   │       ├── embeddings.py     # 向量化模型
│   │       └── chains.py         # LangChain 链
│   ├── migrations/               # Alembic 数据库迁移文件
│   ├── tests/                    # Pytest 测试
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/               # 认证相关页面
│   │   ├── dashboard/            # 数据看板
│   │   ├── ai-doctor/            # AI 医生
│   │   ├── policy/               # 农策助手
│   │   └── farmland/             # 农田管理
│   ├── components/               # 共用组件
│   ├── lib/                      # 工具函数 / API 客户端
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── android/                      # Capacitor Android 项目（第四阶段生成）
├── docker-compose.yml
├── .github/workflows/
│   └── ci.yml
├── PLAN.md
└── README.md
```

#### 1.3 阶段验收标准

| 验收项 | 标准 |
|--------|------|
| 数据库迁移 | `alembic upgrade head` 成功建表，无报错 |
| 用户 API | 注册/登录/获取用户信息接口正常工作 |
| 农田 API | 增删改查接口通过 Postman 测试 |
| 前端登录 | 登录页面可正常认证并跳转至农田管理页 |
| 单元测试 | `pytest` 运行通过，覆盖率 ≥ 80% |
| Docker 启动 | `docker compose up` 一键启动全栈服务 |

---

### 第二阶段：RAG 知识库构建与向量检索（第 4-6 周）

**阶段目标**：完成农业知识库的数据采集、向量化入库，实现 RAG 驱动的智能问答与病虫害诊断 API。

#### 2.1 开发任务

**知识库数据采集**
- [ ] 收集农业病虫害图文资料（来源：农业农村部、各省农技推广站）
- [ ] 收集国家农业补贴政策文件（2023-2025 年）
- [ ] 收集主要粮食作物（水稻、小麦、玉米、大豆）种植技术规程
- [ ] 数据清洗：去重、格式统一、Markdown 化处理

**RAG 引擎开发**
- [ ] 封装 ChromaDB 向量存储层（CRUD + 语义检索）
- [ ] 集成中文嵌入模型（`BAAI/bge-large-zh-v1.5`）
- [ ] 实现文档分块策略（RecursiveCharacterTextSplitter，chunk_size=512）
- [ ] 实现知识库批量导入脚本（`scripts/ingest_knowledge.py`）
- [ ] 开发 RAG 检索链（LangChain `RetrievalQA`）
- [ ] 实现混合检索（向量检索 + BM25 关键词检索）

**AI 医生 API**
- [ ] 实现图片预处理接口（压缩/格式转换）
- [ ] 集成多模态 LLM（GPT-4V 或 Qwen-VL）进行图像描述生成
- [ ] 将图像描述与用户文字描述融合后进行 RAG 检索
- [ ] 生成结构化诊断报告（病害名称/严重程度/防治方案）
- [ ] 将诊断结果写入 `recognition_records` 表

**农策助手 API**
- [ ] 实现多轮对话会话管理（`session_id` 关联）
- [ ] 实现政策问答 RAG 链（按 `category=policy` 过滤检索）
- [ ] 实现流式输出接口（SSE / WebSocket）

#### 2.2 RAG 架构详解

```
知识库构建流程：
┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ 原始文档  │ →  │ 文本分块  │ →  │ 向量化嵌入   │ →  │  ChromaDB    │
│ PDF/MD/  │    │ 512字符  │    │ BGE-Large-ZH │    │  持久化存储  │
│ TXT/HTML │    │ 50字重叠 │    │              │    │              │
└──────────┘    └──────────┘    └──────────────┘    └──────────────┘

查询流程：
用户提问
    ↓
问题向量化
    ↓
ChromaDB 语义相似度检索（Top-K=5）
    ↓
BM25 关键词检索（候选去重合并）
    ↓
Reranker 重排序（可选）
    ↓
LLM + 检索结果 → 生成回答
    ↓
返回答案 + 来源文献
```

#### 2.3 阶段验收标准

| 验收项 | 标准 |
|--------|------|
| 知识库规模 | ≥ 500 条农业知识文档成功入库 |
| 向量检索 | Top-5 检索相关度 ≥ 0.75（余弦相似度） |
| AI 医生 | 上传病害图片，10 秒内返回诊断报告 |
| 农策问答 | 政策问题准确率（人工评估）≥ 85% |
| 流式输出 | 农策助手回答支持流式逐字输出 |

---

### 第三阶段：前端 UI 开发与多模态交互（第 7-10 周）

**阶段目标**：完成所有前端页面开发，实现完整的用户交互流程，重点打磨 AI 医生多模态交互体验。

#### 3.1 开发任务

**AI 医生前端**
- [ ] 实现图片拍摄/上传组件（支持拖拽上传 + 相机调用）
- [ ] 实现实时诊断进度展示（骨架屏 + 进度动画）
- [ ] 实现诊断报告卡片（病害信息 + 防治方案 + 置信度可视化）
- [ ] 实现历史诊断记录列表与详情页

**农策助手前端**
- [ ] 实现类 ChatGPT 对话界面（气泡消息 + 打字机效果）
- [ ] 实现会话历史侧边栏（创建/切换/删除对话）
- [ ] 实现来源引用展示（悬浮卡片显示知识库原文）
- [ ] 实现快捷问题模板（常见政策问题一键发送）

**数据看板前端**
- [ ] 实现农田分布概览卡片（面积/数量/作物统计）
- [ ] 实现气象数据图表（折线图：温度/湿度/降雨量）
- [ ] 实现病虫害发生趋势图（柱状图，按月统计）
- [ ] 实现地图组件（可选：农田位置标注，使用高德地图 API）

**农事 Agent 前端**
- [ ] 实现农事日历组件（月视图，颜色标注农事节点）
- [ ] 实现农事建议卡片（浇水/施肥/病害预警）
- [ ] 实现 Agent 对话界面（展示工具调用过程）

**通用 UI 组件**
- [ ] 实现响应式布局（移动端优先，支持 375px ~ 1440px）
- [ ] 实现暗色模式支持
- [ ] 实现国际化（中文简体）
- [ ] 实现 PWA 支持（可离线查看历史诊断记录）

#### 3.2 关键页面线框图

**AI 医生页面**：
```
┌─────────────────────────────┐
│  🌾 AI 医生           ☰ 菜单 │
├─────────────────────────────┤
│  ┌───────────────────────┐  │
│  │   📷 点击上传/拍摄图片  │  │
│  │   支持 JPG PNG 格式    │  │
│  └───────────────────────┘  │
│                             │
│  描述症状（可选）：          │
│  ┌───────────────────────┐  │
│  │ 例：叶片发黄，有褐色斑...│  │
│  └───────────────────────┘  │
│                             │
│  关联农田：[ 东头二亩地 ▼ ] │
│                             │
│  [ 🔍 开始诊断 ]            │
├─────────────────────────────┤
│  诊断结果：                 │
│  ┌───────────────────────┐  │
│  │ 🚨 水稻稻瘟病（叶瘟型）│  │
│  │ 严重程度：中度 ████░░ │  │
│  │ 置信度：92.3%          │  │
│  ├───────────────────────┤  │
│  │ 防治方案：             │  │
│  │ 1. 立即喷施三环唑...   │  │
│  │ 2. 加强田间通风...     │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

#### 3.3 阶段验收标准

| 验收项 | 标准 |
|--------|------|
| 页面完整性 | 全部核心页面开发完成，无空白页面 |
| 移动端适配 | 在 375px 宽度下所有页面布局正常 |
| 交互完整性 | 完整用户流程（注册→管理农田→AI诊断→查看历史）可完整走通 |
| 性能指标 | Lighthouse 移动端评分 ≥ 75 |
| 流式体验 | 农策助手打字机效果流畅，无明显卡顿 |

---

### 第四阶段：Android APK 适配与性能优化（第 11-14 周）

**阶段目标**：通过 Capacitor 将 Web 应用打包为 Android APK，完成原生能力集成，进行全面性能调优，准备参赛展示版本。

#### 4.1 开发任务

**Capacitor 集成**
- [ ] 安装并配置 Capacitor（`@capacitor/core` + `@capacitor/android`）
- [ ] 配置 `capacitor.config.ts`（应用 ID、名称、服务器地址）
- [ ] 集成 `@capacitor/camera` 插件（调用原生摄像头）
- [ ] 集成 `@capacitor/filesystem` 插件（本地图片缓存）
- [ ] 集成 `@capacitor/push-notifications` 插件（农事提醒推送）
- [ ] 集成 `@capacitor/splash-screen` 和 `@capacitor/status-bar`（APP 外观）

**Android 原生适配**
- [ ] 配置 Android Studio 开发环境
- [ ] 适配 Android 深色模式
- [ ] 处理 Android 权限（摄像头权限、网络权限、通知权限）
- [ ] 配置 Android 启动图与应用图标（1024x1024 PNG）
- [ ] 构建 Release APK（签名配置）

**性能优化**
- [ ] **前端优化**：
  - Next.js 图片优化（`next/image` + WebP 格式）
  - 代码分割（`dynamic import`，按路由懒加载）
  - API 响应缓存（TanStack Query `staleTime` 配置）
- [ ] **后端优化**：
  - 数据库查询优化（为高频查询字段添加索引）
  - Redis 缓存（缓存 RAG 检索结果，TTL=1小时）
  - 异步任务队列（Celery + Redis，处理耗时 AI 推理）
- [ ] **RAG 优化**：
  - 嵌入向量缓存（避免重复计算）
  - 批量检索优化（合并相似查询）
  - 模型量化（本地模型 INT8 量化，降低推理延迟）

**测试与质量保障**
- [ ] 编写端到端测试（Playwright，覆盖核心用户路径）
- [x] 完成性能压测（Locust，模拟 100 并发用户）
- [ ] 完成 Android 真机测试（目标：Android 10+ 兼容）
- [ ] 完成 APK 安全扫描

**文档与部署**
- [ ] 编写 API 文档（基于 FastAPI 自动生成 + 补充说明）
- [ ] 编写部署文档（服务器环境配置、Docker 部署流程）
- [ ] 录制演示视频（3-5 分钟功能展示）
- [x] 准备参赛 PPT

#### 4.2 APK 构建流程

```bash
# Step 1: 构建 Next.js 静态资源
cd frontend && npm run build

# Step 2: 同步到 Capacitor
npx cap sync android

# Step 3: 在 Android Studio 中构建 APK
# Build → Generate Signed Bundle/APK → APK

# 或使用命令行构建
cd android && ./gradlew assembleRelease

# 输出路径：android/app/build/outputs/apk/release/app-release.apk
```

#### 4.3 性能目标

| 指标 | 目标值 |
|------|--------|
| AI 医生诊断延迟 | ≤ 8 秒（含图片上传 + 推理） |
| 农策助手首字延迟 | ≤ 3 秒 |
| 页面首次内容绘制（FCP） | ≤ 2 秒 |
| 数据看板数据加载 | ≤ 1.5 秒 |
| APK 安装包大小 | ≤ 30 MB |
| Android APP 冷启动 | ≤ 3 秒 |

#### 4.4 阶段验收标准

| 验收项 | 标准 |
|--------|------|
| APK 可安装 | Release APK 在 Android 10+ 设备上正常安装运行 |
| 摄像头功能 | APP 内可直接调用摄像头拍摄病害图片并完成诊断 |
| 推送通知 | 农事提醒通知在 APP 后台/关闭状态下正常推送 |
| 性能达标 | 所有核心性能指标达到上表目标值 |
| 压测通过 | 100 并发下 API 响应时间 P95 ≤ 5 秒，错误率 ≤ 1% |
| 演示就绪 | 演示视频录制完成，PPT 准备完毕 |

---

## 六、团队分工与协作

### 6.1 推荐分工（4人团队）

| 成员 | 主要职责 |
|------|----------|
| 负责人 | 项目管理、架构设计、后端核心开发、RAG 引擎 |
| 后端开发 | FastAPI API 开发、数据库设计、测试 |
| 前端开发 | Next.js UI 开发、数据可视化、Capacitor 适配 |
| AI/数据 | 知识库建设、模型选型与调优、性能优化 |

### 6.2 开发规范

- **Git 工作流**：`main` 分支保护，功能开发在 `feature/xxx` 分支，PR 合并前需代码审查。
- **代码规范**：后端使用 `black` + `ruff`，前端使用 `prettier` + `eslint`。
- **提交规范**：遵循 Conventional Commits（`feat:` / `fix:` / `docs:` / `chore:`）。
- **接口文档**：后端每个新接口必须同步更新 FastAPI 路由注释（自动生成 Swagger）。

### 6.3 项目里程碑

```
第 1 周  第 3 周  第 6 周  第 10 周  第 14 周
   │        │        │         │          │
   ▼        ▼        ▼         ▼          ▼
[启动]  [基础框架] [RAG上线] [Web完成] [APK发布]
          ↑          ↑          ↑          ↑
       阶段一      阶段二     阶段三     阶段四
       验收        验收        验收        验收
```

---

## 七、风险评估与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| LLM API 费用超支 | 中 | 高 | 优先使用开源模型（Qwen、ChatGLM）部署本地推理；设置 API 调用限额 |
| 知识库质量不足 | 中 | 高 | 与农业院校专家合作审核；优先采用权威官方数据源 |
| ChromaDB 检索精度低 | 低 | 中 | 引入 Reranker 模型（BGE-Reranker）二次排序；调优 chunk 大小 |
| Capacitor APK 兼容性问题 | 中 | 中 | 提前在 Android 模拟器（API 30/31/33）测试；参考 Capacitor 官方兼容性列表 |
| 服务器性能不足 | 低 | 中 | 使用异步推理队列（Celery）削峰；开启 Redis 缓存减少重复计算 |
| 团队进度延误 | 中 | 高 | 每周进行站会；各阶段设置缓冲期（3-5天）；优先保证核心功能完成 |
| 用户数据隐私合规 | 低 | 高 | 实现数据脱敏；不上传用户农田精确坐标到第三方；遵守《个人信息保护法》 |

---

## 附录：快速启动指南

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Android Studio（第四阶段需要）

### 本地开发启动

```bash
# 克隆仓库
git clone https://github.com/Andrewrover-01/ZhinongXingxiang.git
cd ZhinongXingxiang

# 启动后端（方式一：Docker）
docker compose up -d db redis
cd backend && pip install -r requirements.txt
cp .env.example .env   # 配置环境变量（LLM API Key 等）
alembic upgrade head   # 初始化数据库
uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend && npm install && npm run dev

# 访问
# 前端：http://localhost:3000
# 后端 API 文档：http://localhost:8000/docs
```

### 环境变量配置（.env）

```env
# 数据库
DATABASE_URL=postgresql://postgres:password@localhost:5432/zhinong
REDIS_URL=redis://localhost:6379/0

# LLM 配置（二选一）
OPENAI_API_KEY=sk-xxxxxxxx
# QWEN_API_KEY=xxxxxxxx   # 阿里云百炼平台

# 向量数据库
CHROMA_PERSIST_DIR=./chroma_data

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 文件存储
UPLOAD_DIR=./uploads
```

---

> **计划书版本**：v1.0  
> **最后更新**：2026-03-28  
> **项目仓库**：https://github.com/Andrewrover-01/ZhinongXingxiang
