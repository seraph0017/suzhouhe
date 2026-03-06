# AI Manga/Video Production Pipeline - 项目完整清单

> 生成时间：2026-03-01
> 项目状态：前端页面开发完成，后端 API 基础功能完成

---

## 一、前端文件清单

### 页面组件（17 个）

#### 认证与通用（3 个）
| 文件 | 路径 | 功能 |
|------|------|------|
| `Login.vue` | `/auth/Login.vue` | 登录页面 |
| `NotFound.vue` | `/common/NotFound.vue` | 404 页面 |
| `Dashboard.vue` | `/Dashboard.vue` | 通用仪表盘 |

#### 管理后台（4 个）
| 文件 | 路径 | 功能 |
|------|------|------|
| `Dashboard.vue` | `/admin/Dashboard.vue` | 管理后台仪表盘 |
| `UserManagement.vue` | `/admin/UserManagement.vue` | 用户管理 |
| `ProjectManagement.vue` | `/admin/ProjectManagement.vue` | 项目管理 |
| `ModelConfig.vue` | `/admin/ModelConfig.vue` | AI 模型配置 |

#### 组长工作台（3 个）
| 文件 | 路径 | 功能 |
|------|------|------|
| `Dashboard.vue` | `/lead/Dashboard.vue` | 组长仪表盘 |
| `ScriptEditor.vue` | `/lead/ScriptEditor.vue` | 剧本编辑器 |
| `FinalAudit.vue` | `/lead/FinalAudit.vue` | 终审工作台 |

#### 组员工作台（5 个）
| 文件 | 路径 | 功能 |
|------|------|------|
| `Dashboard.vue` | `/member/Dashboard.vue` | 组员仪表盘 |
| `ChapterBreakdown.vue` | `/member/ChapterBreakdown.vue` | 章节拆解 |
| `StoryboardEditor.vue` | `/member/StoryboardEditor.vue` | 分镜编辑 |
| `MaterialSelection.vue` | `/member/MaterialSelection.vue` | 素材选择 |
| `FirstAudit.vue` | `/member/FirstAudit.vue` | 一审工作台 |
| `VideoComposition.vue` | `/member/VideoComposition.vue` | 视频合成 |

#### 项目页面（1 个）
| 文件 | 路径 | 功能 |
|------|------|------|
| `ProjectDetail.vue` | `/projects/ProjectDetail.vue` | 项目详情 |

### 布局组件（3 个）
| 文件 | 路径 | 功能 |
|------|------|------|
| `AuthLayout.vue` | `/layouts/AuthLayout.vue` | 认证页布局 |
| `MainLayout.vue` | `/layouts/MainLayout.vue` | 主应用布局 |
| `AppHeader.vue` | `/components/AppHeader.vue` | 应用头部 |

### 路由配置
| 文件 | 路径 |
|------|------|
| `index.ts` | `/router/index.ts` |

### 状态管理（3 个 Stores）
| 文件 | 路径 | 功能 |
|------|------|------|
| `auth.ts` | `/stores/auth.ts` | 认证状态 |
| `project.ts` | `/stores/project.ts` | 项目状态 |
| `pipeline.ts` | `/stores/pipeline.ts` | 流水线状态 |

### API 客户端
| 文件 | 路径 | 功能 |
|------|------|------|
| `api.ts` | `/services/api.ts` | Axios 封装 + API 服务 |

### 类型定义
| 文件 | 路径 | 功能 |
|------|------|------|
| `index.ts` | `/types/index.ts` | TypeScript 类型定义 |

### 工具函数
| 文件 | 路径 | 功能 |
|------|------|------|
| `format.ts` | `/utils/format.ts` | 格式化函数 |

---

## 二、后端文件清单

### API 路由（13 个模块）
| 文件 | 端点前缀 | 功能 |
|------|----------|------|
| `auth.py` | `/api/auth` | 认证（登录/刷新/登出） |
| `users.py` | `/api/users` | 用户 CRUD |
| `projects.py` | `/api/projects` | 项目 CRUD + 成员管理 |
| `scripts.py` | `/api/scripts` | 剧本 CRUD + AI 生成 + 锁定 |
| `chapters.py` | `/api/chapters` | 章节 CRUD + AI 生成 + 重排序 |
| `storyboards.py` | `/api/storyboards` | 分镜 CRUD + AI 生成 + 画面生成 |
| `assets.py` | `/api/assets` | 素材 CRUD |
| `reviews.py` | `/api/reviews` | 审核（通过/驳回） |
| `models.py` | `/api/models` | AI 模型配置 |
| `pipeline.py` | `/api/pipeline` | 流水线状态 + 触发 |
| `storage.py` | `/api/storage` | 文件上传/访问 |
| `providers.py` | `/api/providers` | AI 提供商测试 |
| `websocket.py` | `/ws` | WebSocket 连接 |

### 数据模型（10 个）
| 文件 | 模型名 | 功能 |
|------|--------|------|
| `user.py` | `User` | 用户（含角色） |
| `project.py` | `Project` | 项目 |
| `script.py` | `Script` | 剧本（含版本控制） |
| `chapter.py` | `Chapter` | 章节 |
| `storyboard.py` | `Storyboard` | 分镜 |
| `asset.py` | `Asset` | 素材 |
| `review.py` | `Review` | 审核记录 |
| `audit_log.py` | `AuditLog` | 审计日志 |
| `model_provider.py` | `ModelProvider` | AI 模型配置 |
| `generation_job.py` | `GenerationJob` | 生成任务 |

### Pydantic Schemas（9 个）
| 文件 | Schema 名 | 功能 |
|------|-----------|------|
| `user.py` | `UserCreate/UserResponse` | 用户请求/响应 |
| `project.py` | `ProjectCreate/ProjectResponse` | 项目请求/响应 |
| `script.py` | `ScriptCreate/ScriptResponse` | 剧本请求/响应 |
| `chapter.py` | `ChapterCreate/ChapterResponse` | 章节请求/响应 |
| `storyboard.py` | `StoryboardCreate/StoryboardResponse` | 分镜请求/响应 |
| `asset.py` | `AssetCreate/AssetResponse` | 素材请求/响应 |
| `review.py` | `ReviewCreate/ReviewResponse` | 审核请求/响应 |
| `model.py` | `ModelCreate/ModelResponse` | 模型请求/响应 |
| `token.py` | `TokenResponse` | Token 响应 |

### 业务服务
| 文件 | 服务名 | 功能 |
|------|--------|------|
| `ai_service.py` | `AIService` | AI 服务抽象层 |
| `ai/openai.py` | `OpenAIService` | OpenAI 兼容接口 |
| `ai/anthropic.py` | `AnthropicService` | Anthropic 接口 |
| `worker.py` | `Worker` | 异步任务（ARQ） |
| `storage.py` | `StorageService` | 存储服务 |
| `websocket.py` | `WebSocketManager` | WebSocket 管理 |

### 中间件
| 文件 | 中间件名 | 功能 |
|------|----------|------|
| `auth.py` | `AuthMiddleware` | JWT 认证中间件 |

### 工具函数
| 文件 | 功能 |
|------|------|
| `security.py` | 密码哈希、JWT 生成/验证 |
| `audit_logger.py` | 审计日志记录 |

### 配置
| 文件 | 功能 |
|------|------|
| `config.py` | 应用配置（使用 pydantic-settings） |
| `database.py` | 数据库连接、会话管理 |

---

## 三、API 端点统计

### 认证模块 (4 个)
- `POST /api/auth/login` - 登录
- `POST /api/auth/refresh` - 刷新 Token
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户

### 用户管理 (5 个)
- `GET /api/users` - 用户列表
- `GET /api/users/{id}` - 用户详情
- `POST /api/users` - 创建用户
- `PUT /api/users/{id}` - 更新用户
- `DELETE /api/users/{id}` - 删除用户

### 项目管理 (7 个)
- `GET /api/projects` - 项目列表
- `GET /api/projects/{id}` - 项目详情
- `POST /api/projects` - 创建项目
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目
- `GET /api/projects/{id}/members` - 成员列表
- `POST /api/projects/{id}/members` - 添加成员
- `DELETE /api/projects/{id}/members/{user_id}` - 移除成员

### 剧本管理 (9 个)
- `GET /api/scripts` - 剧本列表
- `GET /api/scripts/{id}` - 剧本详情
- `POST /api/scripts` - 创建剧本
- `PUT /api/scripts/{id}` - 更新剧本
- `DELETE /api/scripts/{id}` - 删除剧本
- `POST /api/scripts/generate` - AI 生成剧本
- `POST /api/scripts/{id}/lock` - 锁定剧本
- `POST /api/scripts/{id}/unlock` - 解锁剧本

### 章节管理 (7 个)
- `GET /api/chapters` - 章节列表
- `GET /api/chapters/{id}` - 章节详情
- `POST /api/chapters` - 创建章节
- `PUT /api/chapters/{id}` - 更新章节
- `DELETE /api/chapters/{id}` - 删除章节
- `POST /api/chapters/reorder` - 调整顺序
- `POST /api/chapters/generate` - AI 生成章节

### 分镜管理 (9 个)
- `GET /api/storyboards` - 分镜列表
- `GET /api/storyboards/{id}` - 分镜详情
- `POST /api/storyboards` - 创建分镜
- `PUT /api/storyboards/{id}` - 更新分镜
- `DELETE /api/storyboards/{id}` - 删除分镜
- `POST /api/storyboards/generate` - AI 生成分镜
- `POST /api/storyboards/{id}/generate-image` - AI 生成画面
- `POST /api/storyboards/{id}/lock` - 锁定分镜

### 素材管理 (3 个)
- `GET /api/assets` - 素材列表
- `POST /api/assets` - 创建素材
- `DELETE /api/assets/{id}` - 删除素材

### 审核管理 (4 个)
- `GET /api/reviews/pending` - 待审核列表
- `POST /api/reviews/{id}/approve` - 通过审核
- `POST /api/reviews/{id}/reject` - 驳回审核

### 模型配置 (7 个)
- `GET /api/models` - 模型列表
- `GET /api/models/{id}` - 模型详情
- `POST /api/models` - 创建模型
- `PUT /api/models/{id}` - 更新模型
- `DELETE /api/models/{id}` - 删除模型
- `POST /api/models/{id}/set-default` - 设为默认
- `POST /api/models/{id}/health-check` - 健康检测

### 流水线 (2 个)
- `GET /api/pipeline/status` - 流水线状态
- `POST /api/pipeline/trigger` - 触发流水线

### 存储 (2 个)
- `POST /api/storage/upload` - 文件上传
- `GET /api/storage/{filename}` - 文件访问

### AI 提供商 (2 个)
- `GET /api/providers` - 提供商列表
- `POST /api/providers/test` - 测试连接

---

## 四、数据库表清单

| 表名 | 对应模型 | 记录数（初始） |
|------|----------|----------------|
| `users` | User | 3（默认账号） |
| `projects` | Project | 0 |
| `scripts` | Script | 0 |
| `chapters` | Chapter | 0 |
| `storyboards` | Storyboard | 0 |
| `assets` | Asset | 0 |
| `reviews` | Review | 0 |
| `audit_logs` | AuditLog | 0 |
| `model_providers` | ModelProvider | 0 |
| `generation_jobs` | GenerationJob | 0 |
| `project_members` | ProjectMember | 0 |

---

## 五、默认账号

| 角色 | 邮箱 | 密码 | 权限 |
|------|------|------|------|
| Admin | admin@example.com | admin123 | 系统配置、用户管理、模型配置 |
| Team Lead | lead@example.com | lead123 | 项目管理、剧本创作、终审 |
| Team Member | member@example.com | member123 | 任务执行、一审、素材选择 |

---

## 六、环境变量配置

### 后端 (.env)
```env
# 应用配置
APP_NAME="AI Manga Pipeline"
DEBUG=True
SECRET_KEY="your-secret-key-here"

# 数据库
DATABASE_URL="postgresql://user:password@localhost:5432/manga_db"

# Redis
REDIS_URL="redis://localhost:6379"

# JWT
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 存储
STORAGE_TYPE="local"
STORAGE_PATH="./uploads"

# 允许的源
ALLOWED_ORIGINS="http://localhost:5173"
```

### 前端 (.env)
```env
VITE_API_BASE_URL="/api"
```

---

## 七、技术栈总结

### 前端
- **框架**: Vue 3.4 + TypeScript
- **构建工具**: Vite 5.2
- **UI 组件库**: Element Plus 2.6
- **状态管理**: Pinia 2.1 + pinia-plugin-persistedstate
- **路由**: Vue Router 4.3
- **HTTP 客户端**: Axios 1.6
- **样式**: SCSS
- **代码规范**: ESLint + Prettier

### 后端
- **框架**: FastAPI
- **语言**: Python 3.13
- **ORM**: SQLAlchemy 2.0
- **验证**: Pydantic V2
- **数据库**: PostgreSQL 16
- **缓存/队列**: Redis 7 (ARQ)
- **认证**: JWT (python-jose)
- **迁移**: Alembic

---

## 八、文件统计

| 类型 | 数量 |
|------|------|
| 前端 Vue 组件 | 17 个页面 + 3 个布局 |
| 前端 TypeScript 文件 | 10+ 个 |
| 后端 Python 文件 | 40+ 个 |
| API 端点 | 60+ 个 |
| 数据库表 | 11 个 |
| 文档文件 | 10+ 个 |

---

## 九、Git 提交历史

| 阶段 | 提交数 | 主要内容 |
|------|--------|----------|
| Phase 1 | 10+ | 项目初始化、基础架构 |
| Phase 2 | 15+ | 数据库模型、API 基础 |
| Phase 3 | 20+ | 前端页面开发 |
| Phase 4 | 10+ | API 集成、完善功能 |

---

## 十、下一步工作

### 高优先级
1. [ ] 完善 AI 服务集成（图片多选项、BGM 生成）
2. [ ] 实现 WebSocket 实时通知
3. [ ] 完善 ARQ 任务队列处理
4. [ ] 实现视频唇型同步功能

### 中优先级
1. [ ] 前端性能优化（虚拟滚动、懒加载）
2. [ ] 添加前端单元测试
3. [ ] E2E 测试（Playwright）
4. [ ] PWA 支持

### 低优先级
1. [ ] 国际化支持
2. [ ] 深色主题
3. [ ] 移动端适配

---

**文档生成时间**: 2026-03-01
**项目状态**: ✅ 前端页面开发完成，后端 API 基础功能完成
