# 《智农兴乡》项目问题与风险清单

> 本文档由代码审查自动生成，记录项目中发现的所有安全漏洞、Bug 及潜在风险，并标注修复状态。

---

## 目录

1. [严重安全漏洞（Critical）](#1-严重安全漏洞critical)
2. [高危风险（High）](#2-高危风险high)
3. [中危风险（Medium）](#3-中危风险medium)
4. [低危风险（Low）](#4-低危风险low)
5. [代码质量问题](#5-代码质量问题)
6. [配置与运维风险](#6-配置与运维风险)
7. [修复汇总](#7-修复汇总)

---

## 1. 严重安全漏洞（Critical）

### 🔴 [FIXED] CRIT-001：文件下载路径穿越（Path Traversal）

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/upload.py` |
| **类型** | 路径穿越（CWE-22） |
| **状态** | ✅ 已修复 |

**问题描述：**  
`GET /upload/images/{filename}` 接口直接将用户提供的 `filename` 参数拼接到文件路径，未做任何校验：

```python
# 修复前（漏洞代码）
file_path = Path(settings.UPLOAD_DIR) / "images" / filename
```

攻击者可构造如下请求，读取服务器上的任意文件：
```
GET /api/v1/upload/images/../../../../etc/passwd
GET /api/v1/upload/images/..%2F..%2Fapp%2Fcore%2Fconfig.py
```

**修复方案：**  
- 用正则表达式验证文件名格式（UUID + 合法扩展名）
- 使用 `Path.resolve()` 对比路径是否仍在 `UPLOAD_DIR` 内

---

### 🔴 [FIXED] CRIT-002：知识库文档缺少所有权校验（Authorization Bypass）

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/knowledge.py` |
| **类型** | 越权访问（CWE-285） |
| **状态** | ✅ 已修复 |

**问题描述：**  
`PUT /knowledge/{id}` 和 `DELETE /knowledge/{id}` 接口虽然要求登录，但未校验操作者是否是文档的创建者，任何已登录用户均可修改或删除他人上传的文档：

```python
# 修复前（漏洞代码）——直接操作，无所有权验证
def update_doc(...):
    doc = update_knowledge(db, doc_id, data, vs=vs)
    ...

def delete_doc(...):
    ok = delete_knowledge(db, doc_id, vs=vs)
    ...
```

**修复方案：**  
在执行写操作前，先查询文档并验证 `doc.upload_by == current_user.id`，不匹配则返回 403。

---

### 🔴 [FIXED] CRIT-003：诊断接口缺少输入校验，存在 SSRF 风险

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/schemas/rag.py` |
| **类型** | SSRF（CWE-918）、Prompt Injection |
| **状态** | ✅ 已修复 |

**问题描述：**  
`DiagnoseRequest.image_url` 字段无任何格式验证，攻击者可提交内网地址触发 SSRF，或利用 `description` 字段（无长度限制）进行提示词注入：

```python
# 修复前（漏洞代码）
class DiagnoseRequest(BaseModel):
    image_url: str = Field(...)          # 无校验，可传 file://, ftp://, 内网 IP
    description: Optional[str] = Field(None)  # 无长度限制
```

**修复方案：**  
- `image_url` 仅允许 `/upload/images/` 相对路径或 `http(s)://` URL，最长 500 字符
- `description` 最长 1000 字符
- `crop_type` 最长 100 字符（已有）

---

## 2. 高危风险（High）

### 🟠 [FIXED] HIGH-001：认证缺失时返回错误状态码（401 vs 403）

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/deps.py` |
| **类型** | 错误 HTTP 状态码（HTTP 语义错误） |
| **状态** | ✅ 已修复 |

**问题描述：**  
FastAPI 内置的 `HTTPBearer` 在请求头不含 Authorization 字段时返回 **403 Forbidden**，而按 RFC 7235 规范，缺少凭据时应返回 **401 Unauthorized**（并携带 `WWW-Authenticate` 头）。

**影响：**  
- 客户端无法区分"没有权限"（403）与"未登录"（401），影响自动重定向到登录页的逻辑
- 测试用例断言失败

**修复方案：**  
自定义 `_HTTPBearer401` 类，捕获 `HTTPBearer` 抛出的 403，改为抛出 401。

---

### 🟠 HIGH-002：JWT Token 存储在 localStorage（XSS 风险）

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/lib/api.ts`, `frontend/app/(auth)/login/page.tsx`, `frontend/app/(auth)/register/page.tsx` |
| **类型** | 凭据泄露（CWE-312） |
| **状态** | ⚠️ 未修复（需架构层面改动） |

**问题描述：**  
登录成功后，Token 存入 `localStorage`：

```typescript
localStorage.setItem("access_token", res.access_token);
```

任何能注入 JavaScript 代码的 XSS 漏洞（包括第三方 npm 包中的供应链攻击）都可以通过 `localStorage.getItem("access_token")` 窃取 Token。

**建议修复方案：**  
后端改为在登录响应中设置 `HttpOnly; Secure; SameSite=Strict` 的 Cookie，前端不再手动存储 Token。需前后端协同改造。

---

### 🟠 [FIXED] HIGH-003：CORS 配置过度宽松（`allow_methods=["*"]`）

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/main.py` |
| **类型** | CORS 配置不当（CWE-942） |
| **状态** | ✅ 已修复 |

**问题描述：**  
CORS 配置允许所有 HTTP 方法和所有请求头：

```python
# 修复前
allow_methods=["*"],   # 允许 TRACE、CONNECT 等危险方法
allow_headers=["*"],   # 允许任意请求头注入
```

**修复方案：**  
改为显式白名单：
```python
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
allow_headers=["Content-Type", "Authorization"],
```

---

### 🟠 HIGH-004：Token 有效期过长（7 天）

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/core/config.py` |
| **类型** | 会话管理不当（CWE-613） |
| **状态** | ✅ 已修复 |

**问题描述：**  
`ACCESS_TOKEN_EXPIRE_MINUTES = 10080`（7 天），Token 一旦泄露，攻击者可在 7 天内不受限制地使用。

**修复方案：**  
改为 `60` 分钟（1 小时），生产环境建议配合 Refresh Token 机制实现无感续期。

---

### 🟠 HIGH-005：缺少接口限流（Rate Limiting）

| 字段 | 内容 |
|------|------|
| **文件** | 全部 API 路由 |
| **类型** | 资源耗尽（CWE-770） |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
以下高成本接口无任何限流措施，可被恶意用户批量调用：
- `POST /auth/login`（暴力破解密码）
- `POST /auth/register`（注册垃圾账号）
- `POST /ai-doctor/diagnose`（消耗 LLM API 配额）
- `POST /policy/chat`（消耗 LLM API 配额）

**建议修复方案：**  
使用 `slowapi` 或在 Nginx/Traefik 层配置限流规则。

---

### 🟠 HIGH-006：SSE 流式响应异常被静默吞噬

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/policy.py`, `backend/app/routers/ai_doctor.py` |
| **类型** | 不当的错误处理（CWE-390） |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
SSE 事件生成器中的异常被 `except` 捕获后仅记录日志，客户端收不到任何错误信号，连接会被静默关闭：

```python
async def _event_generator():
    try:
        async for chunk in run_policy_chat_stream(...):
            yield {"data": chunk}
    except Exception as exc:
        _log.warning("SSE stream error: %s", exc)  # 客户端无感知
```

**建议修复方案：**  
捕获异常后向客户端发送 `{"data": "[ERROR]"}` 信号，让前端能够正确处理错误状态。

---

### 🟠 [FIXED] HIGH-007：前端流式响应未处理 `res.body` 为 null 的情况

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/lib/api.ts` |
| **类型** | 空指针异常（CWE-476） |
| **状态** | ✅ 已修复 |

**问题描述：**  
`streamDiagnose` 和 `streamPolicyChat` 函数使用非空断言操作符 `!` 访问 `res.body`，当服务端返回空响应体时将抛出未处理异常：

```typescript
// 修复前
const reader = res.body!.getReader();  // res.body 可能为 null
```

**修复方案：**  
添加 `null` 检查，为 `null` 时向流控制器传递错误：
```typescript
if (!res.body) {
  controller.error(new Error("Empty response body"));
  return;
}
const reader = res.body.getReader();
```

---

### 🟠 HIGH-008：知识库搜索/列表接口无需认证

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/knowledge.py` |
| **类型** | 未授权访问 |
| **状态** | ⚠️ 未修复（需业务确认） |

**问题描述：**  
`GET /knowledge/`（列表）和 `GET /knowledge/search`（搜索）无需登录即可访问，内部知识库内容可被公开爬取。

**建议：**  
如果知识库属于内部资产，应添加 `current_user: User = Depends(get_current_user)` 依赖。

---

## 3. 中危风险（Medium）

### 🟡 MED-001：弱默认 SECRET_KEY

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/core/config.py` |
| **状态** | ⚠️ 已通过注释提示，需生产部署时手动覆盖 |

**问题描述：**  
默认 `SECRET_KEY = "dev-secret-key-change-in-production"` 在代码仓库中明文可见，若生产部署时未通过环境变量覆盖，所有 JWT Token 的签名密钥将被攻击者获知，可伪造任意 Token。

**建议修复方案：**  
生产部署前，必须在 `.env` 文件或 CI/CD 的 Secrets 管理中设置随机密钥：
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

---

### 🟡 MED-002：缺少全局 React Error Boundary

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/app/layout.tsx` |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
前端没有配置全局 Error Boundary，任何一个组件抛出未捕获的 JavaScript 错误都会导致整个应用白屏，用户体验极差且不利于错误上报。

---

### 🟡 MED-003：文件上传缺少 Magic Bytes 校验

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/upload.py` |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
当前仅通过 `Content-Type` 请求头校验文件类型，攻击者可将 `.php` 或 `.exe` 文件的 `Content-Type` 伪造为 `image/jpeg` 来绕过限制。

**建议修复方案：**  
使用 `python-magic` 库读取文件前几个字节（Magic Bytes）验证真实文件类型。

---

### 🟡 MED-004：政策聊天历史不分页，存在内存溢出风险

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/services/rag_service.py` |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
`get_session_messages` 一次性从数据库加载会话的**全部**历史消息，无分页限制：
```python
return (...).all()  # 可能返回数万条消息
```

**建议修复方案：**  
增加 `offset` / `limit` 参数，默认最多返回最近 50 条。

---

### 🟡 MED-005：前端错误信息直接暴露服务端详情

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/app/(auth)/login/page.tsx`, `frontend/app/(auth)/register/page.tsx` |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
服务端返回的错误详情（`response.data.detail`）直接显示给用户，可能泄露内部系统信息（如数据库错误、字段约束信息）：
```typescript
const msg = err?.response?.data?.detail;
setError(msg ?? "登录失败，请重试");
```

**建议修复方案：**  
根据 HTTP 状态码返回固定的用户友好提示，不透传服务端原始错误。

---

### 🟡 MED-006：前端路由缺乏客户端保护

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/app/` 各页面 |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
所有受保护页面（`/farmland`、`/ai-doctor`、`/policy` 等）没有客户端路由守卫，未登录用户可直接访问这些页面 URL（虽然 API 会返回 401，但页面框架会渲染，UI 出现异常）。

**建议修复方案：**  
在 `middleware.ts`（Next.js 路由中间件）中检查 Token 存在性，未登录用户重定向到 `/login`。

---

### 🟡 MED-007：知识库类别（category）缺少枚举验证

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/routers/knowledge.py`, `backend/app/schemas/knowledge.py` |
| **状态** | ✅ 已修复 |

**问题描述：**  
`category` 查询参数和请求体字段原为自由字符串，不合法的值可进入数据库和向量数据库，破坏数据一致性。

**修复方案：**  
新增 `KnowledgeCategory` 枚举类（`disease | policy | technique | pest | weather`），创建/更新/搜索接口统一使用该枚举作为类型约束。

---

### 🟡 MED-008：Redis 连接未配置密码认证

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/core/cache.py`, `backend/.env.example` |
| **状态** | ⚠️ 未修复 |

**问题描述：**  
默认 Redis 连接地址为 `redis://localhost:6379/0`，无密码，在生产环境中 Redis 可能被未授权访问，攻击者可读取/清除 RAG 缓存。

**建议：**  
生产部署时在 `REDIS_URL` 中包含密码：`redis://:yourpassword@host:6379/0`。

---

## 4. 低危风险（Low）

### 🟢 LOW-001：Dockerfile 以 root 用户运行

| 字段 | 内容 |
|------|------|
| **文件** | `backend/Dockerfile` |
| **状态** | ⚠️ 未修复 |

容器进程以 root 权限运行，容器逃逸风险较高。建议创建非特权用户并以其身份运行应用。

---

### 🟢 LOW-002：推送通知 Token 未上报至后端

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/lib/notifications.ts` |
| **状态** | ⚠️ TODO 未完成 |

设备推送 Token 注册后只打印到控制台，未发送至后端，导致推送通知功能实际不可用。

---

### 🟢 LOW-003：生产环境使用 SQLite

| 字段 | 内容 |
|------|------|
| **文件** | `backend/app/core/config.py` |
| **状态** | ⚠️ 未修复 |

默认数据库为 `sqlite:///./zhinong.db`，SQLite 不支持并发写入，在生产环境下高并发访问会导致数据损坏或性能下降。建议生产使用 PostgreSQL。

---

### 🟢 LOW-004：前端图片域名硬编码 localhost

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/next.config.ts` |
| **状态** | ⚠️ 未修复 |

`remotePatterns` 只配置了 `localhost:8000`，生产环境切换域名后 `next/image` 会拒绝加载图片。

---

### 🟢 LOW-005：缺少 Content Security Policy（CSP）

| 字段 | 内容 |
|------|------|
| **文件** | `frontend/next.config.ts` |
| **状态** | ⚠️ 未修复 |

已配置多个安全响应头（`X-Frame-Options`、`X-XSS-Protection` 等），但缺少 `Content-Security-Policy`，无法有效阻止 XSS 和数据注入攻击。

---

### 🟢 LOW-006：依赖包缺少安全扫描流程

| 字段 | 内容 |
|------|------|
| **文件** | `backend/requirements.txt`, `frontend/package.json` |
| **状态** | ⚠️ 未修复 |

CI/CD 流程中无 `pip-audit` / `npm audit` 扫描步骤，已知漏洞的依赖版本可能在不知情的情况下被引入。

---

## 5. 代码质量问题

| 编号 | 描述 | 位置 | 严重性 |
|------|------|------|--------|
| BUG-001 | 流式诊断切换 Tab 时未中止请求，可能引发竞态条件 | `frontend/app/ai-doctor/page.tsx` | Medium |
| BUG-002 | `URL.createObjectURL(file)` 未检查文件大小，超大图片会撑爆内存 | `frontend/app/ai-doctor/page.tsx` | Medium |
| BUG-003 | 表单 mutation 错误信息直接暴露 `response.data.detail` | `frontend/app/farmland/page.tsx` | Low |
| BUG-004 | `parseFloat()` 用于仪表盘数字处理时可能出现 NaN，未做防御 | `frontend/app/dashboard/page.tsx` | Low |
| BUG-005 | `main.py` 中 import 语句重复（`asynccontextmanager`、`Path` 等被导入两次） | `backend/app/main.py` | Low |

---

## 6. 配置与运维风险

| 编号 | 描述 | 位置 | 严重性 |
|------|------|------|--------|
| OPS-001 | 未配置结构化日志（无 request_id、user_id 追踪） | 后端全局 | Medium |
| OPS-002 | 无错误监控（未集成 Sentry 或 OpenTelemetry） | 前后端 | Medium |
| OPS-003 | 无健康检查的数据库连通性探测（`/health` 仅返回 ok，不检查 DB/Redis） | `backend/app/main.py` | Low |
| OPS-004 | ChromaDB 向量数据库无备份策略 | `chroma_data/` | Medium |
| OPS-005 | 无密钥轮换机制，API Key 泄露后无法快速失效 | `.env` 配置 | Medium |

---

## 7. 修复汇总

| 编号 | 描述 | 状态 | 修改文件 |
|------|------|------|----------|
| CRIT-001 | 路径穿越漏洞 | ✅ 已修复 | `backend/app/routers/upload.py` |
| CRIT-002 | 知识库越权访问 | ✅ 已修复 | `backend/app/routers/knowledge.py` |
| CRIT-003 | 诊断接口 SSRF + Prompt Injection | ✅ 已修复 | `backend/app/schemas/rag.py` |
| HIGH-001 | 认证失败返回 403 而非 401 | ✅ 已修复 | `backend/app/routers/deps.py` |
| HIGH-003 | CORS 过度宽松 | ✅ 已修复 | `backend/app/main.py` |
| HIGH-004 | Token 有效期 7 天 | ✅ 已修复 | `backend/app/core/config.py` |
| HIGH-007 | 前端 `res.body!` 非空断言 | ✅ 已修复 | `frontend/lib/api.ts` |
| MED-007 | 知识库 category 无枚举校验 | ✅ 已修复 | `backend/app/schemas/knowledge.py`, `backend/app/routers/knowledge.py` |
| HIGH-002 | JWT 存储在 localStorage | ⚠️ 未修复（需架构改造） | - |
| HIGH-005 | 缺少接口限流 | ⚠️ 未修复 | - |
| HIGH-006 | SSE 异常静默吞噬 | ⚠️ 未修复 | - |
| HIGH-008 | 知识库接口无认证 | ⚠️ 待业务确认 | - |
| MED-001 | 弱默认 SECRET_KEY | ⚠️ 需生产部署时覆盖 | - |
| MED-002 | 缺少 React Error Boundary | ⚠️ 未修复 | - |
| MED-003 | 文件上传无 Magic Bytes 校验 | ⚠️ 未修复 | - |
| MED-004 | 聊天历史不分页 | ⚠️ 未修复 | - |
| MED-005 | 服务端错误信息直接暴露 | ⚠️ 未修复 | - |
| MED-006 | 前端路由缺乏保护 | ⚠️ 未修复 | - |
| MED-008 | Redis 无密码认证 | ⚠️ 未修复 | - |

---

*最后更新：2026-03-30*
