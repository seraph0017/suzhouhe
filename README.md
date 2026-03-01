# AI Manga/Video Production Pipeline System

企业级 AI 漫剧生成流水线系统 - 多角色协作、全流程可配置、双节点审核

**GitHub:** [github.com/seraph0017/suzhouhe](https://github.com/seraph0017/suzhouhe)

## 🎯 项目状态

**当前阶段:** Phase 5 - AI 功能联调 ✅

**总体进度:** 约 80% 完成

---

## 🚀 快速开始

### 前置条件

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Redis (用于 ARQ 和 WebSocket)

### 1. 启动基础设施

```bash
# 启动 PostgreSQL 和 MinIO
docker-compose up -d

# 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. 设置后端

```bash
cd backend

# 创建 Conda 环境
conda create -n suzhou python=3.11 -y
conda activate suzhou

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API 密钥

# 初始化数据库
python scripts/seed_db.py

# 配置 AI Provider
python scripts/configure_providers.py

# 测试 Provider 连接
python scripts/test_providers.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动 ARQ Worker (新终端)
arq arq_settings.WorkerSettings
```

### 3. 设置前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- **前端:** http://localhost:5173
- **后端 API:** http://localhost:8000
- **API 文档:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws/notifications

---

## 👥 默认测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| Admin | admin@example.com | admin123 |
| Team Lead | lead@example.com | lead123 |
| Team Member | member@example.com | member123 |

---

## 📁 项目结构

```
suzhou/
├── frontend/                 # Vue 3 前端应用
│   ├── src/
│   │   ├── views/           # 20+ 页面组件
│   │   ├── stores/          # 4 个 Pinia Store
│   │   ├── services/        # API + WebSocket
│   │   ├── router/          # 路由配置
│   │   ├── layouts/         # 布局组件
│   │   ├── types/           # TypeScript 类型
│   │   └── App.vue
│   └── package.json
│
├── backend/                  # FastAPI 后端服务
│   ├── app/
│   │   ├── api/             # 11 个路由模块
│   │   ├── models/          # 14 个 SQLAlchemy 模型
│   │   ├── schemas/         # 9 个 Pydantic Schemas
│   │   ├── services/        # 业务服务
│   │   │   ├── ai/          # AI Provider 实现
│   │   │   ├── ai_service.py# AI 服务集成层
│   │   │   ├── worker.py    # ARQ Worker 任务
│   │   │   └── storage.py   # MinIO 存储
│   │   ├── middleware/      # 认证中间件
│   │   └── utils/           # 工具函数
│   ├── alembic/             # 数据库迁移
│   ├── scripts/             # 工具脚本
│   └── requirements.txt
│
├── docs/                     # 文档
│   ├── PRD.md               # 产品需求
│   ├── test-plan.md         # 测试计划 (225+ 用例)
│   ├── backend-architecture-final.md
│   ├── frontend-architecture-final.md
│   └── phase[1-5]-completion-report.md
│
├── docker-compose.yml        # Docker 配置
└── CLAUDE.md                 # 项目指南
```

---

## 🎬 8 步双审流水线

```
┌─────────────────────────────────────────────────────────────┐
│  1. 剧本基座 ─→ 2. 剧本精调 ─→ 3. 章节拆解 ─→ 4. 分镜创作    │
│      │                          │                          │
│      ▼                          ▼                          ▼
│   LLM 生成                   自动生成                   AI 生成
│   手动上传                   手动调整                   手动编辑
│                                                             │
│      │                          │                          │
│      ▼                          ▼                          ▼
│  5. 素材生成 ←── 一审 ── 6. 视频生成 ─→ 7. 智能合成 ─→ 8. 章节封装
│      │         (组员)              │                        │
│      ▼                             ▼                        ▼
│   图片/TTS                      口型同步                  BGM/ 字幕
│                                                             │
│                           二审 (终审)
│                            (组长)
│                              │
│                              ▼
│                         交付导出
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Vite |
| **UI 组件** | Element Plus |
| **状态管理** | Pinia |
| **路由** | Vue Router |
| **后端** | Python 3.11 + FastAPI |
| **数据库** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 |
| **认证** | JWT (python-jose) |
| **任务队列** | ARQ + Redis |
| **对象存储** | MinIO (S3-compatible) |
| **AI Provider** | OpenAI / Anthropic / Runway |
| **实时通信** | WebSocket |

---

## 📊 项目统计

| 类别 | 数量 |
|------|------|
| 前端页面组件 | 20+ |
| 后端 API 端点 | 60+ |
| 数据库表 | 14 |
| Pinia Stores | 4 |
| AI Provider 实现 | 5 |
| ARQ Worker 任务 | 9 |
| 测试用例 | 225+ |
| 代码行数 | ~10,000+ |

---

## 🔑 AI Provider 配置

### 支持的 Provider

| 类型 | Provider | 模型 | 状态 |
|------|----------|------|------|
| LLM | OpenAI | gpt-4 | ✅ |
| LLM | Anthropic | claude-sonnet-4 | ✅ |
| Image | OpenAI | dall-e-3 | ✅ |
| TTS | OpenAI | tts-1 | ✅ |
| Video | Runway | gen2 | ⏳ |

### 配置 API 密钥

编辑 `backend/.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key

# Runway
RUNWAY_API_KEY=your-key
```

---

## 📝 测试命令

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

---

## 📖 文档

| 文档 | 描述 |
|------|------|
| [PRD.md](PRD.md) | 产品需求文档 |
| [test-plan.md](docs/test-plan.md) | 测试计划 (225+ 用例) |
| [backend-architecture-final.md](docs/backend-architecture-final.md) | 后端架构 |
| [frontend-architecture-final.md](docs/frontend-architecture-final.md) | 前端架构 |
| [phase5-ai-integration-report.md](docs/phase5-ai-integration-report.md) | Phase 5 报告 |

---

## ⏭️ 后续工作

### Phase 6: 测试与优化 (预计 1-2 周)
- [ ] 运行 225+ 测试用例
- [ ] Bug 修复
- [ ] 性能优化
- [ ] 安全审计

### Phase 7: 真实 API 联调 (预计 2-3 周)
- [ ] 配置真实 API 密钥
- [ ] LLM 剧本生成联调
- [ ] 图片生成联调
- [ ] TTS 语音合成联调
- [ ] 视频生成对接

### Phase 8: 部署准备 (预计 1 周)
- [ ] 生产环境配置
- [ ] CI/CD 设置
- [ ] 监控日志
- [ ] 用户文档

---

## 🎯 项目亮点

1. **8 步双审流水线** - 完整的企业级生产流程
2. **角色权限系统** - Admin/Team Lead/Team Member 三级权限
3. **AI Provider 抽象层** - 热插拔 AI 服务配置
4. **实时进度推送** - WebSocket 实时任务进度
5. **抽卡制素材生成** - 多选项供用户选择
6. **口型同步验证** - 视频生成质量检测
7. **MinIO 对象存储** - S3 兼容的文件管理

---

## 📄 许可证

MIT License

---

**最后更新:** 2026-03-01
