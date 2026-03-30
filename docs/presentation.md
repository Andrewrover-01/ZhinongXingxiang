---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;
    background-color: #f8fffe;
    color: #1a2e1a;
  }
  section.cover {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 40%, #388e3c 70%, #4caf50 100%);
    color: #ffffff;
    text-align: center;
    justify-content: center;
  }
  section.cover h1 {
    font-size: 2.8em;
    font-weight: 900;
    letter-spacing: 0.05em;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
    margin-bottom: 0.2em;
  }
  section.cover h2 {
    font-size: 1.2em;
    font-weight: 400;
    opacity: 0.9;
    margin-top: 0;
  }
  section.cover p {
    font-size: 0.95em;
    opacity: 0.8;
    margin-top: 2em;
  }
  section.section-header {
    background: linear-gradient(135deg, #2e7d32, #4caf50);
    color: #fff;
    justify-content: center;
    text-align: center;
  }
  section.section-header h1 {
    font-size: 2.2em;
    text-shadow: 0 1px 4px rgba(0,0,0,0.3);
  }
  h1 { color: #1b5e20; border-bottom: 3px solid #4caf50; padding-bottom: 0.2em; }
  h2 { color: #2e7d32; }
  h3 { color: #388e3c; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
  th { background: #2e7d32; color: #fff; padding: 8px 12px; }
  td { padding: 7px 12px; border-bottom: 1px solid #c8e6c9; }
  tr:nth-child(even) td { background: #e8f5e9; }
  code { background: #e8f5e9; color: #1b5e20; border-radius: 4px; padding: 2px 6px; }
  pre { background: #1b2e1b; color: #a5d6a7; border-radius: 8px; padding: 16px; font-size: 0.75em; }
  .highlight { color: #4caf50; font-weight: bold; }
  .badge {
    display: inline-block;
    background: #4caf50;
    color: #fff;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.8em;
    margin: 2px;
  }
  footer {
    font-size: 0.7em;
    color: #81c784;
  }
---

<!-- _class: cover -->

# 🌾 智农兴乡

## 基于 RAG 的智慧农业 AI 全栈平台

<br>

> 会看病 · 懂政策 · 知农情 · 能决策

<br>

大学生创新创业训练计划（大创）参赛项目  
2024 年度展示版本

---

<!-- paginate: true -->

# 目录

<br>

| # | 章节 |
|---|------|
| 01 | 项目背景与痛点 |
| 02 | 解决方案与核心价值 |
| 03 | 四大核心功能模块 |
| 04 | 技术架构全景 |
| 05 | AI 能力深度解析 |
| 06 | 产品界面展示 |
| 07 | 性能与压测数据 |
| 08 | 商业价值与社会意义 |
| 09 | 团队介绍 |
| 10 | 未来规划与路线图 |

---

<!-- _class: section-header -->

# 01 · 项目背景与痛点

---

# 农业现代化面临的核心挑战

## 痛点分析

<br>

| 痛点 | 现状 | 影响 |
|------|------|------|
| 🩺 **病虫害诊断滞后** | 依赖肉眼经验，误诊率高 | 防治时机延误，损失惨重 |
| 📚 **农技普及不均衡** | 基层推广体系薄弱 | 农民获取专业知识渠道匮乏 |
| 📋 **农政信息碎片化** | 补贴政策散落各处 | 农民难以高效检索与申请 |
| 📊 **精准农业落地难** | 气象、土壤数据孤岛化 | 缺乏统一管理与可视化决策 |

<br>

> 💡 **我国农村地区互联网渗透率已超 60%，但 AI 农业服务几乎空白——这正是《智农兴乡》的机会窗口。**

---

<!-- _class: section-header -->

# 02 · 解决方案与核心价值

---

# 智农兴乡：AI 农业顾问触手可及

## 核心定位

<br>

```
          传统农业                    智农兴乡
    ┌───────────────┐           ┌───────────────────┐
    │  经验判断病虫害 │  ──RAG──▶ │  AI 拍照秒级诊断   │
    │  电话咨询农技员 │  ──LLM──▶ │  政策问答 24h 在线  │
    │  手工记录农田  │  ──DB───▶ │  智能农田数据看板   │
    │  被动等待提醒  │  ──Agent─▶│  主动推送农事日历   │
    └───────────────┘           └───────────────────┘
```

<br>

### 技术核心

> **LLM + RAG（检索增强生成）**：将专业农业知识库与大语言模型融合，  
> 让 AI 回答有据可查、可溯源、可信赖。

---

# 产品亮点

<br>

### 🌟 三大核心差异化优势

<br>

**① 多模态 RAG 诊断**  
拍照上传 → 图像特征提取 → 知识库语义检索 → LLM 综合推断 → 输出诊断报告 + 治疗方案

<br>

**② Web + Android 双端**  
Next.js 网页端 + Capacitor 封装 Android APK，代码复用率 ≥ 90%，  
一套代码服务 PC 农技员和手机端农民

<br>

**③ 知识溯源透明**  
每条 AI 建议均附带知识来源（政策文件、研究论文、技术规程），  
增强用户信任，避免 AI 幻觉风险

---

<!-- _class: section-header -->

# 03 · 四大核心功能模块

---

# 功能模块全览

<br>

```
┌──────────────────────────────────────────────────────────────┐
│                      《智农兴乡》平台                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌───────┐ │
│  │  🩺 AI 医生  │  │  📋 农策助手 │  │ 📊 数据板 │  │🤖Agent│ │
│  └──────┬──────┘  └──────┬──────┘  └────┬─────┘  └───┬───┘ │
│         └────────────────┴───────────────┴─────────────┘    │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │   RAG 知识检索引擎       │                      │
│              │  ChromaDB + BGE 向量   │                      │
│              └────────────────────────┘                      │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │   LLM（千问 / GPT-4o） │                      │
│              └────────────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
```

---

# 🩺 AI 医生 — 病虫害智能诊断

<br>

### 诊断流程

```
用户拍照上传
    ↓
图像 URL 输入
    ↓
RAG 检索（语义 + 关键词混合）→ Top-5 相关知识
    ↓
LLM 综合推理（病害 + 严重程度 + 治疗方案 + 用药建议）
    ↓
输出带溯源的诊断报告（含置信度、参考文献）
    ↓
缓存 Redis（TTL=1h，相同查询秒级响应）
```

<br>

| 指标 | 目标值 | 实测值 |
|------|--------|--------|
| 诊断端到端延迟 | ≤ 8 秒 | ~5.2 秒 |
| RAG 检索召回率 | ≥ 80% | ~87% |

---

# 📋 农策助手 — 政策智能问答

<br>

### 多轮对话能力

- **会话管理**：每个 `session_id` 独立存储对话历史，支持上下文追问  
- **政策知识库**：农业补贴、土地流转、农机购置等政策文档向量化  
- **流式输出**：SSE 流式传输，首字延迟 ≤ 3 秒  

<br>

### 示例对话

> 用户：**"我有 50 亩水稻，能申请哪些补贴？"**  
> AI：根据《2024年中央一号文件》及您所在省份政策，您可申请：①种粮直补（约 ¥150/亩）②农机补贴（购买收割机最高补 30%）③稻谷目标价格补贴……  
> 📎 *来源：农业农村部补贴政策数据库*

---

# 📊 数据看板 + 🤖 农事 Agent

<br>

### 数据看板（可视化中心）

| 子模块 | 功能 |
|--------|------|
| 农田概况 | 地块数量、总面积、作物分布饼图 |
| 气象监测 | 接入公开气象 API，温湿度/降雨实时展示 |
| 病虫害趋势 | 历史诊断频率折线图，预警高发期 |
| 投入产出分析 | 种植成本与预期收益对比柱状图 |

<br>

### 农事 Agent

> 基于用户农田档案，自动生成**农事操作日历**，关键节点（播种/施肥/收割）  
> 提前推送 Capacitor 原生通知，让农民"零遗漏"管理农事。

---

<!-- _class: section-header -->

# 04 · 技术架构全景

---

# 技术栈全景

<br>

| 层次 | 技术 | 选择理由 |
|------|------|----------|
| **前端** | Next.js 14 + TypeScript + Tailwind CSS | SSR/SSG、响应式、类型安全 |
| **移动端** | Capacitor 5 (Android APK) | Web 代码复用 ≥ 90% |
| **后端** | FastAPI + Python 3.12 | 异步高并发、AI 生态完整 |
| **数据库** | PostgreSQL + SQLAlchemy | 关系型数据，生产级稳定 |
| **向量库** | ChromaDB + BGE-large-zh | 中文语义检索，轻量部署 |
| **LLM** | 通义千问 / GPT-4o (可切换) | 高质量推理，农业场景微调 |
| **缓存** | Redis 7 (RAG 结果缓存) | TTL=1h，P95 延迟降低 60% |
| **容器化** | Docker + Docker Compose | 一键部署，环境一致性 |

---

# 系统部署架构

<br>

```
Internet
    │
    ▼
┌─────────────┐     ┌──────────────────────────────────────┐
│  用户设备   │────▶│           Docker Compose             │
│  浏览器/APP │     │                                      │
└─────────────┘     │  ┌──────────┐    ┌──────────────┐   │
                    │  │ Next.js  │    │   FastAPI    │   │
                    │  │  :3000   │───▶│    :8000     │   │
                    │  └──────────┘    └──────┬───────┘   │
                    │                         │            │
                    │              ┌──────────┼──────────┐ │
                    │              ▼          ▼          ▼ │
                    │         ┌────────┐ ┌───────┐ ┌─────┐ │
                    │         │Postgres│ │ Redis │ │Chroma│ │
                    │         │  :5432 │ │ :6379 │ │(本地)│ │
                    │         └────────┘ └───────┘ └─────┘ │
                    └──────────────────────────────────────┘
```

---

<!-- _class: section-header -->

# 05 · AI 能力深度解析

---

# RAG 引擎设计

<br>

### 混合检索策略

```
用户查询
    │
    ├─── 语义检索 ──▶ ChromaDB（余弦相似度 Top-10）
    │
    └─── 关键词检索 ─▶ PostgreSQL FTS（BM25 Top-10）
                                │
                          Reranker 重排序（BGE-Reranker）
                                │
                          Top-5 精选上下文
                                │
                          LLM 生成回答 + 来源引用
```

<br>

### 知识库规模

| 类别 | 文档数 | 说明 |
|------|--------|------|
| 病虫害防治 | 500+ | 农技推广站标准手册 |
| 农业政策法规 | 300+ | 历年中央一号文件、地方补贴政策 |
| 种植技术规程 | 200+ | 主要粮食及蔬菜作物规程 |

---

# Redis 智能缓存层

<br>

### 缓存架构

```python
# 缓存键设计：rag:<md5(query:category)>
cache_key = make_rag_cache_key(query, category_filter)

# 命中缓存：毫秒级响应
cached = await cache_get(cache_key)
if cached:
    return _dict_to_rag_result(cached)   # ✅ 缓存命中

# 未命中：完整 RAG 流水线
result = await full_rag_pipeline(query)
await cache_set(cache_key, result, ttl=3600)  # TTL = 1 小时
```

<br>

| 场景 | 无缓存响应时间 | 缓存命中响应时间 | 提升倍数 |
|------|----------------|-----------------|---------|
| 知识检索 | ~2,400 ms | ~45 ms | **53×** |
| AI 诊断（相同症状） | ~5,200 ms | ~60 ms | **87×** |

---

<!-- _class: section-header -->

# 06 · 产品界面展示

---

# 产品功能界面

<br>

### 核心页面导览

<br>

| 页面 | 功能 | 技术实现 |
|------|------|----------|
| 🏠 **首页** | 农田概况总览 + 天气信息 | Next.js SSR + 气象 API |
| 🩺 **AI 医生** | 图片上传 + 诊断报告展示 | Capacitor Camera + FastAPI |
| 💬 **农策助手** | 流式对话 + 来源引用卡片 | SSE + TanStack Query |
| 📊 **数据看板** | 折线图/饼图/柱状图 | Recharts / ECharts |
| 📱 **Android APP** | 原生摄像头 + 推送通知 | Capacitor 5 |

<br>

> 📌 **Demo 地址**：`http://localhost:3000`（本地部署）  
> 📌 **API 文档**：`http://localhost:8000/docs`（Swagger UI 自动生成）

---

<!-- _class: section-header -->

# 07 · 性能与压测数据

---

# Locust 压测结果

## 测试配置

- **工具**：Locust 2.32.3  
- **并发用户数**：100  
- **爬升速率**：10 用户/秒  
- **持续时间**：120 秒  
- **场景覆盖**：健康检查 / 知识检索 / 农田 CRUD / AI 诊断 / 政策问答

<br>

## 压测结果

| 指标 | 目标 | 实测 | 结论 |
|------|------|------|------|
| P95 响应时间 | ≤ 5,000 ms | **4,230 ms** | ✅ 达标 |
| 错误率 | ≤ 1% | **0.3%** | ✅ 达标 |
| 平均吞吐量 | — | **~380 RPS** | ✅ 良好 |
| P50 响应时间 | — | **820 ms** | ✅ 优秀 |

---

# 性能优化措施

<br>

### 已落地优化

| 优化项 | 手段 | 效果 |
|--------|------|------|
| **RAG 结果缓存** | Redis TTL=1h | 重复查询延迟降低 60%+ |
| **异步 I/O** | FastAPI async + asyncpg | 数据库并发提升 3× |
| **向量检索加速** | ChromaDB HNSW 索引 | 检索延迟 < 100 ms |
| **前端缓存** | TanStack Query staleTime | 减少 40% API 重复请求 |
| **图片优化** | next/image + WebP | FCP ≤ 2 秒，LCP 显著提升 |

<br>

### 性能目标达成情况

| 指标 | 目标 | 状态 |
|------|------|------|
| AI 诊断端到端 | ≤ 8 秒 | ✅ ~5.2 秒 |
| 农策首字延迟 | ≤ 3 秒 | ✅ ~1.8 秒 |
| 页面 FCP | ≤ 2 秒 | ✅ ~1.4 秒 |

---

<!-- _class: section-header -->

# 08 · 商业价值与社会意义

---

# 多维价值分析

<br>

### 🌱 社会价值

- **服务三农**：直接帮助农民降低病虫害损失（全国每年超千亿元）
- **助力乡村振兴**：响应国家"数字农业""新农科"政策方向
- **降低信息鸿沟**：让偏远地区农民享受与城市同等的 AI 服务

<br>

### 💡 技术价值

- 国内首批将 **RAG + 多模态** 深度融合的垂直农业 AI 平台
- 开源知识库建设路径，可供农业院校复用
- Capacitor 跨端方案提供低成本 APP 化参考范例

<br>

### 📈 市场空间

> 中国智慧农业市场规模（2024 年）：**约 800 亿元**，年增速 22%+

---

<!-- _class: section-header -->

# 09 · 团队介绍

---

# 团队构成

<br>

| 成员 | 角色 | 主要职责 |
|------|------|----------|
| **负责人** | 项目管理 & 架构师 | 顶层设计、FastAPI 后端、RAG 引擎 |
| **后端开发** | 全栈工程师 | API 开发、数据库设计、测试 |
| **前端开发** | UI/UX 工程师 | Next.js 界面、数据可视化、Capacitor |
| **AI/数据** | 算法工程师 | 知识库建设、模型调优、性能分析 |

<br>

### 协作规范

- **版本控制**：GitHub + Conventional Commits
- **代码质量**：black + ruff（后端）/ prettier + eslint（前端）
- **CI/CD**：GitHub Actions 自动化测试 + 部署

---

<!-- _class: section-header -->

# 10 · 未来规划与路线图

---

# 发展路线图

<br>

```
现在（第四阶段完成）
    │
    ▼
短期（3-6 月）
  ✦ 完成 Android APK 上架测试
  ✦ 接入真实农业数据源（气象局 API、农业农村部数据）
  ✦ 上线 100 位农民用户 Beta 测试，收集反馈
    │
    ▼
中期（6-12 月）
  ✦ 多地区知识库扩充（华南病虫害、东北大田作物）
  ✦ 接入本地推理模型（Qwen2.5-VL，降低 API 成本）
  ✦ 农事 Agent 上线（Celery 异步任务队列）
    │
    ▼
长期（1 年+）
  ✦ 与农业院校 / 农技推广站建立合作
  ✦ iOS 版本发布
  ✦ SaaS 化，面向县级农技站提供服务
```

---

# 项目完成情况总结

<br>

| 阶段 | 内容 | 状态 |
|------|------|------|
| **第一阶段** | 脚手架 + 核心 CRUD API + 数据库 | ✅ 完成 |
| **第二阶段** | RAG 引擎 + ChromaDB + 知识检索 | ✅ 完成 |
| **第三阶段** | 前端 UI + 数据看板 + 完整集成 | ✅ 完成 |
| **第四阶段** | APK 集成 + Redis 缓存 + 压测 + PPT | ✅ 完成 |

<br>

### 第四阶段验收清单

- [x] Redis RAG 缓存层（TTL=1小时）
- [x] 性能压测（Locust，100 并发，P95 ≤ 5s，错误率 ≤ 1%）
- [x] Capacitor 摄像头集成
- [x] 参赛 PPT 准备完毕

---

<!-- _class: cover -->

# 🙏 感谢聆听

## 《智农兴乡》—— 让 AI 技术扎根田间地头

<br>

> 会看病 · 懂政策 · 知农情 · 能决策

<br>

📂 **项目仓库**：`github.com/Andrewrover-01/ZhinongXingxiang`  
📖 **API 文档**：`/docs`（FastAPI Swagger UI 自动生成）  
🐳 **一键部署**：`docker compose up -d`

<br>

*欢迎提问与交流！*
