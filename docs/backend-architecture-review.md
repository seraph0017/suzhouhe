# Backend Architecture Review
## Enterprise AI Manga/Video Production Pipeline System

**Document Version:** 1.0
**Review Date:** 2026-03-01
**Reviewer:** Backend Architecture Team
**Status:** Draft for Review

---

## Executive Summary

This document provides a comprehensive backend architecture review of the AI Manga/Video Production Pipeline System PRD. The review covers database schema, API architecture, authentication/authorization, service layer design, AI integration, file storage, audit logging, security, and scalability considerations.

### Overall Assessment

| Aspect | Status | Risk Level |
|--------|--------|------------|
| Core Data Model | **Approved with Recommendations** | Low |
| API Design | **Approved** | Low |
| Authentication & Authorization | **Approved with Recommendations** | Low |
| Service Layer Architecture | **Requires Clarification** | Medium |
| AI Integration | **Approved with Recommendations** | Medium |
| File Storage | **Approved with Recommendations** | Low |
| Audit Logging | **Approved with Recommendations** | Low |
| Security | **Requires Clarification** | Medium |
| Scalability | **Approved with Recommendations** | Medium |

### Critical Gaps Requiring PM Clarification

| ID | Gap | Impact | Recommended Action |
|----|-----|--------|-------------------|
| GAP-001 | User authentication mechanism not specified | P0 | Clarify if built-in auth or SSO/OAuth required |
| GAP-002 | BGM generation/storage requirements unclear | P1 | Define BGM source (AI generation vs. library) |
| GAP-003 | Video generation async handling not detailed | P1 | Define polling vs. webhook callback preference |
| GAP-004 | File size limits and storage quotas undefined | P1 | Define per-project and per-user storage limits |

---

## 1. Database Schema Review

### 1.1 Current Schema Assessment

The PRD provides a solid foundation with proper use of:
- UUID primary keys for all tables
- JSONB for flexible configuration storage
- Foreign key constraints for referential integrity
- Timestamp tracking (created_at, updated_at)
- Proper normalization for core entities

### 1.2 Recommended Schema Optimizations

#### 1.2.1 Missing Tables

The following tables are missing from the PRD schema:

```sql
-- 1. Project Member Assignment (Many-to-Many)
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- TEAM_LEAD, TEAM_MEMBER
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);
CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);

-- 2. Task Assignment (for dashboard "My Tasks")
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
    assigned_to UUID REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    task_type VARCHAR(50) NOT NULL, -- STORYBOARD, MATERIAL_GEN, FIRST_AUDIT, SECOND_AUDIT
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED, BLOCKED
    priority VARCHAR(20) DEFAULT 'NORMAL', -- LOW, NORMAL, HIGH, URGENT
    due_date TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_project ON tasks(project_id);

-- 3. Generation Jobs (for async job tracking)
CREATE TABLE generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    panel_id UUID REFERENCES storyboard_panels(id),
    job_type VARCHAR(50) NOT NULL, -- IMAGE, AUDIO, VIDEO, BGM
    status VARCHAR(50) DEFAULT 'QUEUED', -- QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    model_config_id UUID REFERENCES model_configs(id),
    request_params JSONB NOT NULL,
    result_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    webhook_url VARCHAR(500), -- For callback on completion
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_generation_jobs_status ON generation_jobs(status);
CREATE INDEX idx_generation_jobs_panel ON generation_jobs(panel_id);
CREATE INDEX idx_generation_jobs_project ON generation_jobs(project_id);

-- 4. Asset Library (BGM, stock images, templates)
CREATE TABLE asset_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- BGM, IMAGE_TEMPLATE, TRANSITION, SUBTITLE_STYLE
    name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    metadata JSONB, -- Duration, mood tags, instruments for BGM
    tags TEXT[], -- Searchable tags
    is_public BOOLEAN DEFAULT false, -- Shared across projects
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_asset_library_category ON asset_library(category);
CREATE INDEX idx_asset_library_tags ON asset_library USING GIN(tags);

-- 5. Version History (for rollback capability)
CREATE TABLE script_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID NOT NULL REFERENCES scripts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content JSONB NOT NULL,
    change_summary TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_script_versions_script ON script_versions(script_id);
CREATE UNIQUE INDEX idx_script_versions_unique ON script_versions(script_id, version_number);

-- 6. Notifications (for dashboard alerts)
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- TASK_ASSIGNED, AUDIT_PENDING, GENERATION_COMPLETE, ERROR
    title VARCHAR(255) NOT NULL,
    message TEXT,
    related_entity_type VARCHAR(50), -- PROJECT, CHAPTER, TASK
    related_entity_id UUID,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = false;

-- 7. API Quota Tracking (per project)
CREATE TABLE api_quota_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    model_category VARCHAR(50) NOT NULL, -- LLM, IMAGE, VIDEO, TTS
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    quota_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, model_category, period_start)
);
```

#### 1.2.2 Index Optimization Recommendations

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_chapters_script_status ON chapters(script_id, status);
CREATE INDEX idx_storyboard_panels_chapter_seq ON storyboard_panels(chapter_id, sequence_number);
CREATE INDEX idx_generated_assets_panel_selected ON generated_images(panel_id, is_selected);
CREATE INDEX idx_audit_logs_chapter_type ON audit_logs(chapter_id, audit_type);

-- Partial indexes for filtered queries
CREATE INDEX idx_projects_active ON projects(id) WHERE status = 'ACTIVE';
CREATE INDEX idx_tasks_pending ON tasks(id) WHERE status IN ('PENDING', 'IN_PROGRESS');
CREATE INDEX idx_scripts_locked ON scripts(id) WHERE status = 'LOCKED';

-- Full-text search index for script content
CREATE INDEX idx_scripts_content_search ON scripts USING GIN(to_tsvector('simple', content));
```

#### 1.2.3 Schema Issues and Recommendations

| Issue | Current State | Recommendation | Priority |
|-------|---------------|----------------|----------|
| **Soft Delete** | No soft delete mechanism | Add `deleted_at TIMESTAMP` to all main tables for audit compliance | P1 |
| **Optimistic Locking** | No concurrency control | Add `row_version INTEGER` to tables with frequent updates (scripts, chapters, panels) | P1 |
| **Status Enum** | VARCHAR for status fields | Use PostgreSQL ENUM types for status consistency | P2 |
| **Audit Log Partitioning** | Single audit_logs table | Partition `system_audit_logs` by month for performance | P1 (post-MVP) |
| **Cascading Deletes** | Inconsistent ON DELETE | Standardize: ON DELETE CASCADE for child entities, SET NULL for optional refs | P1 |

### 1.3 Data Model Questions for PM

| Question | Context | Impact |
|----------|---------|--------|
| Q1: What is the expected data retention policy? | Audit logs, version history grow unbounded | Storage cost, database performance |
| Q2: Can a user belong to multiple projects with different roles? | Current schema supports it via project_members | Affects permission design |
| Q3: Should BGM/assets be shareable across projects? | Asset library design | Data isolation requirements |
| Q4: What's the expected scale? (scripts/project, chapters/script, panels/chapter) | Affects indexing and partitioning strategy | Performance planning |

---

## 2. API Architecture

### 2.1 RESTful Design Assessment

The PRD follows good RESTful conventions:
- Resource-based URLs (`/api/v1/projects`, `/api/v1/scripts`)
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Consistent response format with success/error structure
- URL versioning (`/api/v1/`)

### 2.2 Recommended API Enhancements

#### 2.2.1 Standardized Request/Response Schemas

```python
# Pydantic models for API contracts

# Base response envelope
class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[APIError] = None
    meta: ResponseMeta

class ResponseMeta(BaseModel):
    request_id: str
    timestamp: datetime
    pagination: Optional[PaginationInfo] = None

class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Pagination
class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None

# Cursor-based pagination request
class PaginatedRequest(BaseModel):
    cursor: Optional[str] = None
    page_size: int = 20
```

#### 2.2.2 Missing API Endpoints

The following endpoints should be added:

```
# Task Management (for dashboard)
GET    /api/v1/tasks                      # List user's tasks
GET    /api/v1/tasks/{id}                 # Get task details
POST   /api/v1/tasks/{id}/start           # Start task
POST   /api/v1/tasks/{id}/complete        # Complete task
PUT    /api/v1/tasks/{id}/assign          # Reassign task (Team Lead only)

# Generation Jobs
GET    /api/v1/jobs                       # List generation jobs
GET    /api/v1/jobs/{id}                  # Get job status
POST   /api/v1/jobs/{id}/cancel           # Cancel running job
POST   /api/v1/jobs/{id}/retry            # Retry failed job

# Notifications
GET    /api/v1/notifications              # List user notifications
PUT    /api/v1/notifications/{id}/read    # Mark as read
PUT    /api/v1/notifications/read-all     # Mark all as read
GET    /api/v1/notifications/unread-count # Get unread count

# Asset Library
GET    /api/v1/assets                     # List assets
POST   /api/v1/assets                     # Upload asset
GET    /api/v1/assets/{id}                # Get asset details
DELETE /api/v1/assets/{id}                # Delete asset
GET    /api/v1/assets/categories          # List asset categories

# Project Members
GET    /api/v1/projects/{id}/members      # List project members
POST   /api/v1/projects/{id}/members      # Add member
DELETE /api/v1/projects/{id}/members/{userId} # Remove member
PUT    /api/v1/projects/{id}/members/{userId}/role # Update role
```

#### 2.2.3 Rate Limiting Strategy

```python
# Rate limiting configuration
RATE_LIMITS = {
    # Per-user limits
    "authenticated_user": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
    },
    # Per-endpoint limits (more restrictive)
    "generation_endpoints": {
        "requests_per_minute": 10,
        "concurrent_jobs": 5,
    },
    "auth_endpoints": {
        "requests_per_minute": 5,  # Prevent brute force
    },
    # Per-project API quota (for external AI services)
    "api_quota": {
        "llm_calls_per_day": 1000,
        "image_generations_per_day": 500,
        "video_generations_per_day": 50,
        "tts_generations_per_day": 500,
    }
}

# Rate limit response headers
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 45
# X-RateLimit-Reset: 1677686400
```

#### 2.2.4 Error Code Standardization

```python
# Standardized error codes
ERROR_CODES = {
    # Authentication (401)
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Token expired",
    "AUTH_003": "Token revoked",
    "AUTH_004": "User not found",

    # Authorization (403)
    "AUTHZ_001": "Insufficient permissions",
    "AUTHZ_002": "Project access denied",
    "AUTHZ_003": "Resource not owned by user",

    # Validation (400)
    "VAL_001": "Invalid request body",
    "VAL_002": "Required field missing",
    "VAL_003": "Invalid field format",
    "VAL_004": "Business rule violation",

    # Not Found (404)
    "NOT_FOUND_001": "Resource not found",
    "NOT_FOUND_002": "Project not found",
    "NOT_FOUND_003": "Chapter not found",

    # Conflict (409)
    "CONFLICT_001": "Resource already exists",
    "CONFLICT_002": "Script already locked",
    "CONFLICT_003": "Chapter already in audit",

    # AI Service (502/504)
    "AI_001": "AI service unavailable",
    "AI_002": "AI generation timeout",
    "AI_003": "AI quota exceeded",
    "AI_004": "Invalid AI response format",

    # Internal (500)
    "INTERNAL_001": "Unexpected error",
    "INTERNAL_002": "Database error",
    "INTERNAL_003": "File upload failed",
}
```

### 2.3 API Versioning Strategy

| Aspect | Recommendation |
|--------|----------------|
| **Version Format** | URL prefix: `/api/v1/`, `/api/v2/` |
| **Deprecation Policy** | 6 months notice before sunsetting |
| **Breaking Changes** | New major version required |
| **Non-Breaking Changes** | Additive changes allowed in current version |
| **Sunset Header** | `Sunset: Sat, 01 Sep 2026 00:00:00 GMT` |

---

## 3. Authentication & Authorization

### 3.1 JWT Implementation Design

```python
# JWT Token Structure

class JWTPayload(BaseModel):
    sub: str  # User ID
    email: str
    name: str
    role: str  # ADMIN, TEAM_LEAD, TEAM_MEMBER
    projects: List[str]  # Project IDs user has access to
    iat: datetime  # Issued at
    exp: datetime  # Expiration
    jti: str  # JWT ID (for revocation tracking)

# Token Configuration
JWT_CONFIG = {
    "access_token_expiry": timedelta(minutes=30),
    "refresh_token_expiry": timedelta(days=7),
    "algorithm": "HS256",
    "issuer": "manga-pipeline-api",
    "audience": "manga-pipeline-client",
}

# Token Storage Recommendation
# - Access token: Memory (frontend), HttpOnly cookie (backend session)
# - Refresh token: HttpOnly, Secure cookie with SameSite=Strict
```

### 3.2 RBAC Permission Matrix

| Resource | Action | Admin | Team Lead | Team Member |
|----------|--------|-------|-----------|-------------|
| **Users** | Create/Update/Delete | ✓ | - | - |
| **Users** | List (all) | ✓ | - | - |
| **Projects** | Create/Archive | ✓ | - | - |
| **Projects** | View assigned | ✓ | ✓ | ✓ |
| **Project Members** | Add/Remove | ✓ | ✓ (own project) | - |
| **Model Config** | Create/Update/Delete | ✓ | ✓ (own project) | - |
| **Model Config** | View | ✓ | ✓ (own project) | ✓ (own project) |
| **Scripts** | Create/Update | ✓ | ✓ | ✓ (assigned) |
| **Scripts** | Lock/Unlock | - | ✓ | - |
| **Chapters** | Create/Update | ✓ | ✓ | ✓ (assigned) |
| **Chapters** | Reorder/Split/Merge | - | ✓ | ✓ (assigned) |
| **Storyboards** | Create/Update | ✓ | ✓ | ✓ (assigned) |
| **Storyboards** | Lock | - | ✓ | ✓ (assigned) |
| **Generation Jobs** | Create | ✓ | ✓ | ✓ (assigned) |
| **Generation Jobs** | Cancel/Retry | ✓ | ✓ | ✓ (own) |
| **Audits (First)** | Perform | ✓ | ✓ | ✓ (assigned) |
| **Audits (Second)** | Perform | ✓ | ✓ | - |
| **Assets** | Upload/Update | ✓ | ✓ | ✓ (own) |
| **Assets** | Delete | ✓ | ✓ | ✓ (own) |
| **Audit Logs** | View | ✓ | ✓ (own project) | ✓ (own tasks) |

### 3.3 Permission Middleware Implementation

```python
# FastAPI dependency injection for permissions

from enum import Enum
from functools import wraps

class Permission(str, Enum):
    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_VIEW = "project:view"
    PROJECT_EDIT = "project:edit"
    PROJECT_DELETE = "project:delete"

    # Script permissions
    SCRIPT_CREATE = "script:create"
    SCRIPT_VIEW = "script:view"
    SCRIPT_EDIT = "script:edit"
    SCRIPT_LOCK = "script:lock"

    # Audit permissions
    AUDIT_FIRST = "audit:first"
    AUDIT_SECOND = "audit:second"

    # Generation permissions
    GENERATION_CREATE = "generation:create"
    GENERATION_CANCEL = "generation:cancel"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    "ADMIN": set(Permission),  # All permissions
    "TEAM_LEAD": {
        Permission.PROJECT_VIEW,
        Permission.PROJECT_EDIT,
        Permission.SCRIPT_CREATE,
        Permission.SCRIPT_VIEW,
        Permission.SCRIPT_EDIT,
        Permission.SCRIPT_LOCK,
        Permission.AUDIT_FIRST,
        Permission.AUDIT_SECOND,
        Permission.GENERATION_CREATE,
        Permission.GENERATION_CANCEL,
    },
    "TEAM_MEMBER": {
        Permission.PROJECT_VIEW,
        Permission.SCRIPT_CREATE,
        Permission.SCRIPT_VIEW,
        Permission.SCRIPT_EDIT,
        Permission.AUDIT_FIRST,
        Permission.GENERATION_CREATE,
    },
}

# Dependency injection
async def require_permission(permission: Permission, project_id: Optional[str] = None):
    async def dependency(current_user: User = Depends(get_current_user)):
        if permission not in ROLE_PERMISSIONS.get(current_user.role, set()):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        if project_id:
            has_project_access = await check_project_access(current_user.id, project_id)
            if not has_project_access:
                raise HTTPException(status_code=403, detail="Project access denied")

        return current_user
    return dependency

# Usage in routes
@router.post("/scripts")
async def create_script(
    script_data: ScriptCreate,
    user: User = Depends(require_permission(Permission.SCRIPT_CREATE))
):
    ...
```

### 3.4 Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │     API     │     │   Auth      │     │   Redis     │
│             │     │   Gateway   │     │   Service   │     │  (Blocklist)│
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │ 1. POST /login    │                   │                   │
       │ ────────────────> │                   │                   │
       │                   │                   │                   │
       │                   │ 2. Validate creds  │                   │
       │                   │ ────────────────> │                   │
       │                   │                   │                   │
       │                   │ 3. JWT + Refresh  │                   │
       │                   │ <──────────────── │                   │
       │                   │                   │                   │
       │ 4. Tokens         │                   │                   │
       │ <──────────────── │                   │                   │
       │                   │                   │                   │
       │ 5. Request + Bearer │                  │                   │
       │ ────────────────> │                   │                   │
       │                   │                   │                   │
       │                   │ 6. Verify JWT     │                   │
       │                   │ 7. Check blocklist│                   │
       │                   │ ───────────────────────────────────> │
       │                   │                   │                   │
       │                   │ 8. Valid          │                   │
       │                   │ <─────────────────────────────────── │
       │                   │                   │                   │
       │ 9. Response       │                   │                   │
       │ <──────────────── │                   │                   │
       │                   │                   │                   │
```

### 3.5 Authentication Gaps

| Gap | Recommendation | Priority |
|-----|----------------|----------|
| **Password Policy** | Define minimum requirements (8+ chars, complexity) | P0 |
| **MFA Support** | Consider TOTP for Admin accounts | P2 |
| **Session Management** | Define concurrent session limits | P1 |
| **Password Reset** | Add forgot password flow | P1 |
| **Account Lockout** | Define failed login threshold | P0 |

---

## 4. Service Layer Design

### 4.1 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API Layer (FastAPI)                               │
│  - Request validation (Pydantic)                                             │
│  - Authentication/Authorization                                              │
│  - Response serialization                                                    │
│  - Error handling                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Service Layer                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  ScriptService  │  │ ChapterService  │  │ PipelineService │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   AuditService  │  │  AssetService   │  │  TaskService    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌───────────────────────┐ ┌─────────────────┐ ┌─────────────────────────────┐
│    Repository Layer   │ │  Job Queue      │ │  External Service           │
│  - Database access    │ │  (ARQ/Celery)   │ │  Adapters                   │
│  - Query building     │ │  - Async tasks  │ │  - LLM Providers            │
│  - Transaction mgmt   │ │  - Retry logic  │ │  - Image Gen APIs           │
│  - ORM (SQLAlchemy)   │ │  - Scheduling   │ │  - Video Gen APIs           │
└───────────────────────┘ └─────────────────┘ │  - TTS Providers            │
                                               └─────────────────────────────┘
```

### 4.2 Pipeline Orchestration Design

The 8-step pipeline requires careful orchestration. Recommended approach:

```python
# Pipeline state machine
class PipelineState(str, Enum):
    SCRIPT_BASE = "SCRIPT_BASE"
    SCRIPT_REFINEMENT = "SCRIPT_REFINEMENT"
    CHAPTER_BREAKDOWN = "CHAPTER_BREAKDOWN"
    STORYBOARD_CREATION = "STORYBOARD_CREATION"
    FIRST_AUDIT = "FIRST_AUDIT"
    MATERIAL_GENERATION = "MATERIAL_GENERATION"
    VIDEO_GENERATION = "VIDEO_GENERATION"
    SMART_COMPOSITION = "SMART_COMPOSITION"
    CHAPTER_ASSEMBLY = "CHAPTER_ASSEMBLY"
    SECOND_AUDIT = "SECOND_AUDIT"
    PUBLISHED = "PUBLISHED"

# Pipeline transitions
PIPELINE_TRANSITIONS = {
    PipelineState.SCRIPT_BASE: [PipelineState.SCRIPT_REFINEMENT],
    PipelineState.SCRIPT_REFINEMENT: [PipelineState.CHAPTER_BREAKDOWN],
    PipelineState.CHAPTER_BREAKDOWN: [PipelineState.STORYBOARD_CREATION],
    PipelineState.STORYBOARD_CREATION: [PipelineState.FIRST_AUDIT],
    PipelineState.FIRST_AUDIT: [
        PipelineState.MATERIAL_GENERATION,  # Approved
        PipelineState.STORYBOARD_CREATION,  # Rejected - back to storyboard
    ],
    PipelineState.MATERIAL_GENERATION: [PipelineState.VIDEO_GENERATION],
    PipelineState.VIDEO_GENERATION: [PipelineState.SMART_COMPOSITION],
    PipelineState.SMART_COMPOSITION: [PipelineState.CHAPTER_ASSEMBLY],
    PipelineState.CHAPTER_ASSEMBLY: [PipelineState.SECOND_AUDIT],
    PipelineState.SECOND_AUDIT: [
        PipelineState.PUBLISHED,  # Approved
        PipelineState.MATERIAL_GENERATION,  # Rejected - materials
        PipelineState.VIDEO_GENERATION,  # Rejected - video
        PipelineState.SMART_COMPOSITION,  # Minor edit
    ],
}

# Saga pattern for cross-service transactions
class PipelineSaga:
    """
    Manages distributed transactions across pipeline steps.
    Each step has a compensating action for rollback.
    """

    async def execute_step(self, step: PipelineStep, context: PipelineContext):
        try:
            result = await step.execute(context)
            context.compensations.append(step.compensate)
            return result
        except StepExecutionError as e:
            # Execute compensations in reverse order
            for compensation in reversed(context.compensations):
                await compensation()
            raise
```

### 4.3 Async Task Handling

```python
# Background job configuration using ARQ (async Redis queue)

class WorkerSettings:
    functions = [
        generate_images_job,
        generate_audio_job,
        generate_video_job,
        generate_bgm_job,
        compose_chapter_job,
        render_chapter_job,
    ]
    redis_settings = RedisSettings(host='redis', port=6379)
    job_timeout = 600  # 10 minutes max
    max_tries = 3
    retry_delay = 5  # seconds

# Job definitions
async def generate_images_job(ctx, panel_ids: List[str], config: dict):
    """Background job for image generation."""
    job_id = ctx['job_id']

    # Update job status
    await update_job_status(job_id, 'RUNNING')

    try:
        for panel_id in panel_ids:
            result = await image_provider.generate(
                prompt=await get_panel_prompt(panel_id),
                **config
            )
            await store_generated_images(panel_id, result.images)

        await update_job_status(job_id, 'COMPLETED')

    except Exception as e:
        await update_job_status(job_id, 'FAILED', str(e))
        raise

# Job progression with callbacks
async def on_job_complete(job_id: str):
    """Webhook handler for job completion."""
    job = await get_job(job_id)

    if job.status == 'COMPLETED':
        # Auto-trigger next step if configured
        if job.job_type == 'IMAGE':
            # Optionally auto-start audio generation
            pass
        elif job.job_type == 'VIDEO':
            # Notify user, move to next step
            await send_notification(job.assigned_to, 'Generation complete')

    elif job.status == 'FAILED':
        # Notify user of failure
        await send_notification(job.assigned_to, 'Generation failed', job.error_message)
```

### 4.4 Service Layer Questions

| Question | Options | Recommendation |
|----------|---------|----------------|
| **Task Queue** | Celery vs ARQ vs Redis Queue | **ARQ** - Async native, lighter weight |
| **Transaction Pattern** | Database transactions vs Saga | **Saga** for pipeline, **DB TX** for single service |
| **Event Communication** | Direct calls vs Event bus | **Direct** for MVP, **Event bus** for scale |
| **Caching Strategy** | Per-service vs Centralized | **Centralized Redis** with clear key namespaces |

---

## 5. AI Integration Architecture

### 5.1 Provider Abstraction Layer

```python
# Abstract base class for all AI providers
from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Base interface for all AI service providers."""

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Test API credentials."""
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Execute generation request."""
        pass

    @abstractmethod
    async def get_quota_usage(self) -> QuotaInfo:
        """Get current quota usage."""
        pass

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """List available models."""
        pass

# Concrete implementations
class OpenAIProvider(AIProvider):
    """OpenAI GPT integration."""

    async def generate(self, request: LLMRequest) -> LLMResult:
        # Implementation using openai package
        pass

class StabilityAIProvider(AIProvider):
    """Stable Diffusion image generation."""

    async def generate(self, request: ImageRequest) -> ImageResult:
        # Implementation using stability-sdk
        pass

class HeyGenProvider(AIProvider):
    """HeyGen lip-sync video generation."""

    async def generate(self, request: VideoRequest) -> VideoResult:
        # Implementation using HeyGen API
        pass

class AzureTTSProvider(AIProvider):
    """Azure Text-to-Speech."""

    async def generate(self, request: TTSRequest) -> TTSResult:
        # Implementation using azure-cognitiveservices-speech
        pass
```

### 5.2 Provider Factory Pattern

```python
# Factory for dynamic provider selection
class ProviderFactory:
    _providers: Dict[str, Type[AIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "stability": StabilityAIProvider,
        "midjourney": MidjourneyProvider,
        "heygen": HeyGenProvider,
        "d-id": DIDProvider,
        "azure_tts": AzureTTSProvider,
        "elevenlabs": ElevenLabsProvider,
    }

    @classmethod
    def create(cls, provider_name: str, config: ModelConfig) -> AIProvider:
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class(config)

# Usage
async def get_image_provider(config_id: str) -> AIProvider:
    config = await get_model_config(config_id)
    return ProviderFactory.create(config.provider, config)
```

### 5.3 Fallback Mechanism Design

```python
# Circuit breaker pattern for AI service failures
from circuitbreaker import circuit

class AIGenerationService:
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    @circuit(failure_threshold=5, recovery_timeout=60)
    async def generate_with_fallback(
        self,
        request: GenerationRequest,
        primary_provider: str,
        fallback_providers: List[str]
    ) -> GenerationResult:
        """
        Attempt generation with primary provider,
        fall back to alternatives on failure.
        """
        providers_to_try = [primary_provider] + fallback_providers

        for provider_name in providers_to_try:
            try:
                provider = ProviderFactory.create(provider_name, config)
                result = await provider.generate(request)
                return result
            except ProviderError as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue

        raise GenerationExhaustedError(
            "All providers failed to generate content"
        )

# Fallback configuration per category
FALLBACK_CONFIG = {
    "LLM": {
        "primary": "openai",
        "fallbacks": ["anthropic", "google_gemini"],
    },
    "IMAGE": {
        "primary": "stability",
        "fallbacks": ["midjourney", "dall-e"],
    },
    "VIDEO": {
        "primary": "heygen",
        "fallbacks": ["d-id", "sadtalker"],
    },
    "TTS": {
        "primary": "azure_tts",
        "fallbacks": ["elevenlabs", "google_tts"],
    },
}
```

### 5.4 Hot-Swap Configuration Storage

```python
# Runtime configuration model
class ModelConfig(BaseModel):
    id: str
    project_id: Optional[str]  # None = global default
    category: ModelCategory  # LLM, IMAGE, VIDEO, TTS
    provider: str
    credentials: EncryptedDict  # Custom type for encryption
    default_model: str
    parameters: Dict[str, Any]
    is_active: bool
    rate_limit: Optional[int]  # Requests per minute
    quota_limit: Optional[int]  # Daily limit

# Configuration caching with Redis
class ConfigCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes

    async def get_config(self, config_id: str) -> ModelConfig:
        cached = await self.redis.get(f"config:{config_id}")
        if cached:
            return ModelConfig.parse_raw(cached)

        config = await db.get_config(config_id)
        await self.redis.setex(
            f"config:{config_id}",
            self.cache_ttl,
            config.json()
        )
        return config

    async def invalidate(self, config_id: str):
        await self.redis.delete(f"config:{config_id}")
```

### 5.5 AI Integration Questions for PM

| Question | Impact |
|----------|--------|
| **Q1: Which specific providers are required at launch?** | Determines initial implementation scope |
| **Q2: Should users be able to bring their own API keys?** | Affects billing and quota design |
| **Q3: What's the budget for AI API costs per project?** | Informs quota limits and warnings |
| **Q4: How should failed generations be billed?** | Some APIs charge even on failure |
| **Q5: Any compliance requirements for data residency?** | Affects provider selection (EU vs US) |

---

## 6. File Storage Strategy

### 6.1 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          File Storage Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   MinIO     │     │    CDN      │     │   Local     │                   │
│  │  (Primary)  │────>│  (Optional) │     │  (Thumbs)   │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│        │                                                        │           │
│        │ Buckets                                                │           │
│        ▼                                                        │           │
│  ┌────────────────────────────────────────────────────────────┐ │           │
│  │  /{project-id}/                                            │ │           │
│  │    /scripts/                                               │ │           │
│  │    /chapters/{chapter-id}/                                 │ │           │
│  │      /storyboards/                                         │ │           │
│  │      /generated/                                           │ │           │
│  │        /images/{panel-id}/                                 │ │           │
│  │        /audio/{panel-id}/                                  │ │           │
│  │        /video/{panel-id}/                                  │ │           │
│  │      /composed/                                            │ │           │
│  │      /final/                                               │ │           │
│  │    /assets/                                                │ │           │
│  │      /bgm/                                                 │ │           │
│  │      /templates/                                           │ │           │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 File Organization Schema

```python
# File path convention
def generate_file_path(
    project_id: str,
    chapter_id: str,
    file_type: str,
    panel_id: Optional[str] = None,
    file_name: Optional[str] = None
) -> str:
    """Generate standardized file path."""
    base = f"{project_id}/chapters/{chapter_id}"

    if file_type == "storyboard":
        return f"{base}/storyboards/{file_name or 'storyboard.json'}"

    elif file_type == "image":
        if not panel_id:
            raise ValueError("panel_id required for images")
        return f"{base}/generated/images/{panel_id}/{uuid4()}.png"

    elif file_type == "audio":
        if not panel_id:
            raise ValueError("panel_id required for audio")
        return f"{base}/generated/audio/{panel_id}/{uuid4()}.wav"

    elif file_type == "video":
        if not panel_id:
            raise ValueError("panel_id required for video")
        return f"{base}/generated/video/{panel_id}/{uuid4()}.mp4"

    elif file_type == "composed":
        return f"{base}/composed/{file_name or 'composed.mp4'}"

    elif file_type == "final":
        return f"{base}/final/chapter_final.mp4"

# Thumbnail generation
def generate_thumbnail_path(original_path: str) -> str:
    """Generate thumbnail path from original file path."""
    directory, filename = os.path.split(original_path)
    name, ext = os.path.splitext(filename)
    return f"{directory}/thumbs/{name}_thumb.jpg"
```

### 6.3 MinIO Configuration

```python
# MinIO client setup
from minio import Minio
from minio.error import S3Error

class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=True
        )

    async def upload_file(
        self,
        file_content: bytes,
        object_path: str,
        content_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Upload file to MinIO."""
        try:
            self.client.put_object(
                bucket_name="manga-pipeline",
                object_name=object_path,
                data=io.BytesIO(file_content),
                length=len(file_content),
                content_type=content_type,
                metadata=metadata
            )
            return f"https://{os.getenv('MINIO_ENDPOINT')}/manga-pipeline/{object_path}"
        except S3Error as e:
            logger.error(f"Upload failed: {e}")
            raise StorageError(f"Failed to upload file: {e}")

    async def generate_presigned_url(
        self,
        object_path: str,
        expires_in: int = 3600
    ) -> str:
        """Generate time-limited access URL."""
        return self.client.presigned_get_object(
            bucket_name="manga-pipeline",
            object_name=object_path,
            expires=timedelta(seconds=expires_in)
        )

    async def delete_file(self, object_path: str):
        """Delete file from storage."""
        self.client.remove_object("manga-pipeline", object_path)
```

### 6.4 CDN Considerations

| Consideration | Recommendation |
|---------------|----------------|
| **When to Use CDN** | If serving media to external users or geographically distributed team |
| **CDN Strategy** | Pull-based from MinIO origin |
| **Cache Invalidation** | Versioned file names (UUID-based), long cache TTL |
| **Cost Optimization** | Only CDN-ify final chapter videos, not intermediate assets |

### 6.5 File Storage Recommendations

| Aspect | Recommendation |
|--------|----------------|
| **Max File Size** | Images: 10MB, Audio: 50MB, Video: 500MB |
| **Storage Quota** | Per-project: 100GB default, configurable by Admin |
| **File Retention** | Keep all versions for audit trail; implement lifecycle policy for temp files |
| **Backup Strategy** | Daily snapshots to cold storage |
| **Cleanup Policy** | Archive projects inactive >90 days |

---

## 7. Audit Logging Implementation

### 7.1 Audit Log Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Audit Logging Flow                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   API       │     │   Audit     │     │  Database   │                   │
│  │   Layer     │────>│  Middleware │────>│  (Primary)  │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                            │                     │                          │
│                            │                     │                          │
│                            ▼                     ▼                          │
│                     ┌─────────────┐     ┌─────────────┐                     │
│                     │   Redis     │     │   Async     │                     │
│                     │   (Buffer)  │     │   Writer    │                     │
│                     └─────────────┘     └─────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                     ┌─────────────┐                        │
│                                     │  Cold Store │                        │
│                                     │  (S3/Glacier)│                       │
│                                     └─────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Audit Log Implementation

```python
# Audit log middleware
from fastapi import Request
from contextlib import asynccontextmanager

class AuditLogger:
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.buffer_key = "audit_log_buffer"

    async def log(
        self,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        previous_state: Optional[Dict] = None,
        current_state: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        request: Optional[Request] = None
    ):
        """Record audit log entry."""
        log_entry = {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "previous_state": previous_state,
            "current_state": current_state,
            "metadata": metadata,
            "ip_address": request.client.host if request else None,
            "user_agent": request.headers.get("user-agent") if request else None,
        }

        # Buffer to Redis for batch write
        await self.redis.lpush(self.buffer_key, json.dumps(log_entry))

        # Also write directly for critical actions
        if action in ["LOGIN", "LOGOUT", "ROLE_CHANGE", "AUDIT_DECISION"]:
            await self._flush_to_db(log_entry)

    async def flush_buffer(self):
        """Periodically flush Redis buffer to database."""
        while True:
            entries = await self.redis.lrange(self.buffer_key, 0, 99)
            if not entries:
                await asyncio.sleep(60)  # Wait if empty
                continue

            await self.redis.ltrim(self.buffer_key, len(entries), -1)

            bulk_entries = [json.loads(e) for e in entries]
            await self._bulk_insert(bulk_entries)

# Decorator for automatic audit logging
def audit_log(action: str, entity_type: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract context from function arguments
            audit_logger = kwargs.get('audit_logger')
            user = kwargs.get('current_user')
            entity = kwargs.get('entity')

            if audit_logger and user:
                # Capture state before
                previous_state = entity.dict() if entity else None

                result = await func(*args, **kwargs)

                # Capture state after
                current_state = result.dict() if result else None

                await audit_logger.log(
                    user_id=user.id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=str(entity.id) if entity else None,
                    previous_state=previous_state,
                    current_state=current_state,
                )

                return result
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@audit_log(action="SCRIPT_UPDATE", entity_type="SCRIPT")
async def update_script(
    script_id: str,
    data: ScriptUpdate,
    current_user: User,
    audit_logger: AuditLogger
):
    ...
```

### 7.3 Version History Implementation

```python
# Version history service
class VersionService:
    """Manage entity versioning and rollback."""

    async def create_version(
        self,
        entity_type: str,
        entity_id: str,
        content: Dict,
        user_id: str,
        change_summary: Optional[str] = None
    ) -> str:
        """Create new version entry."""
        version = {
            "id": str(uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version_number": await self._get_next_version(entity_type, entity_id),
            "content": content,
            "change_summary": change_summary,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
        }

        await self.db.execute(
            """
            INSERT INTO version_history (...)
            VALUES (:id, :entity_type, :entity_id, :version_number,
                    :content, :change_summary, :created_by, :created_at)
            """,
            version
        )

        return version["id"]

    async def get_versions(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get version history for entity."""
        return await self.db.fetch_all(
            """
            SELECT * FROM version_history
            WHERE entity_type = :entity_type AND entity_id = :entity_id
            ORDER BY version_number DESC
            LIMIT :limit
            """,
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )

    async def rollback(
        self,
        entity_type: str,
        entity_id: str,
        target_version: int,
        user_id: str
    ):
        """Rollback entity to target version."""
        # Fetch target version content
        target = await self.db.fetch_one(
            """
            SELECT content FROM version_history
            WHERE entity_type = :entity_type
            AND entity_id = :entity_id
            AND version_number = :version
            """,
            entity_type=entity_type,
            entity_id=entity_id,
            version=target_version
        )

        if not target:
            raise NotFoundError("Target version not found")

        # Create new version as copy of target (preserving history)
        await self.create_version(
            entity_type=entity_type,
            entity_id=entity_id,
            content=target["content"],
            user_id=user_id,
            change_summary=f"Rollback to version {target_version}"
        )
```

### 7.4 Audit Log Retention Policy

| Log Type | Hot Storage | Warm Storage | Cold Storage |
|----------|-------------|--------------|--------------|
| System Audit Logs | 30 days | 90 days | 2 years |
| User Audit Logs | 30 days | 90 days | 2 years |
| Generation Job Logs | 7 days | 30 days | 90 days |
| Version History | All current | - | Archive on project archive |

---

## 8. Security Considerations

### 8.1 Input Validation Strategy

```python
# Pydantic validators for common patterns

from pydantic import validator, Field
import re

class ScriptCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Dict[str, Any]

    @validator('title')
    def validate_title(cls, v):
        # Prevent XSS and injection
        v = html.escape(v)
        if not re.match(r'^[\w\s\-_\u4e00-\u9fff]+$', v):
            raise ValueError('Title contains invalid characters')
        return v

    @validator('content')
    def validate_script_content(cls, v):
        # Validate script structure
        if 'scenes' not in v:
            raise ValueError('Script must contain scenes')
        if not isinstance(v['scenes'], list):
            raise ValueError('Scenes must be a list')
        if len(v['scenes']) < 1:
            raise ValueError('Script must have at least one scene')
        if len(v['scenes']) > 1000:
            raise ValueError('Script exceeds maximum scene count')

        # Validate each scene
        for scene in v['scenes']:
            if 'description' not in scene:
                raise ValueError('Each scene must have description')
            if len(scene.get('description', '')) > 50000:
                raise ValueError('Scene description too long')

        return v

# Global input sanitization middleware
class SanitizationMiddleware:
    async def __call__(self, request: Request, call_next):
        # Log request for audit
        body = await request.body()

        # Check for SQL injection patterns
        if self._contains_sql_injection(body.decode()):
            logger.warning(f"SQL injection attempt detected: {request.client.host}")
            raise HTTPException(status_code=400, detail="Invalid request")

        return await call_next(request)

    def _contains_sql_injection(self, content: str) -> bool:
        patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
            r"(--|;|\/\*|\*\/)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        ]
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
```

### 8.2 Database Security

```python
# SQLAlchemy with parameterized queries (prevents SQL injection)

from sqlalchemy import text

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # SAFE: Parameterized query
    async def get_user_by_id(self, user_id: str):
        result = await self.session.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {"id": user_id}
        )
        return result.scalar_one_or_none()

    # SAFE: ORM query
    async def get_user_by_email(self, email: str):
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    # DANGEROUS: String formatting (DON'T DO THIS)
    # async def get_user_bad(self, user_id: str):
    #     result = await self.session.execute(
    #         text(f"SELECT * FROM users WHERE id = '{user_id}'")
    #     )
    #     return result.scalar_one_or_none()
```

### 8.3 API Security Best Practices

| Security Measure | Implementation |
|-----------------|----------------|
| **HTTPS Only** | Enforce TLS 1.3, HSTS header |
| **CORS** | Whitelist specific frontend origins |
| **CSRF Protection** | Double-submit cookie pattern |
| **Security Headers** | X-Content-Type-Options, X-Frame-Options, CSP |
| **Request Size Limit** | 10MB max body size |
| **Timeout** | 30s request timeout |
| **Logging** | Sanitize PII from logs |

```python
# Security headers middleware
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 8.4 API Key Encryption

```python
# Encryption for stored API keys
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        self.cipher = Fernet(self.key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Usage in model config
class ModelConfig(BaseModel):
    # ...
    credentials: Dict[str, str]

    @validator('credentials', pre=True)
    def encrypt_credentials(cls, v):
        if 'api_key' in v:
            v['api_key'] = encryption_service.encrypt(v['api_key'])
        return v

    def get_decrypted_credentials(self) -> Dict[str, str]:
        decrypted = self.credentials.copy()
        if 'api_key' in decrypted:
            decrypted['api_key'] = encryption_service.decrypt(decrypted['api_key'])
        return decrypted
```

### 8.5 Security Checklist

| Item | Status | Notes |
|------|--------|-------|
| Password hashing (bcrypt/argon2) | Required | Use bcrypt with cost factor 12 |
| Rate limiting on auth endpoints | Required | 5 attempts/minute |
| Account lockout after failed attempts | Required | Lock for 15 minutes after 5 failures |
| Session invalidation on logout | Required | Add token to blocklist |
| Audit logging for security events | Required | Login, logout, role changes |
| Input validation | Required | All user inputs |
| Output encoding | Required | Prevent XSS |
| Error message sanitization | Required | No stack traces to clients |

---

## 9. Scalability Planning

### 9.1 Database Connection Pooling

```python
# SQLAlchemy async connection pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/manga_pipeline"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Number of connections to keep open
    max_overflow=40,  # Additional connections under load
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=1800,  # Recycle connections after 30 min
    pool_pre_ping=True,  # Verify connection before use
    echo=False  # SQL logging
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### 9.2 Caching Strategy

```python
# Redis caching layers

class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes

    # Cache key namespace convention
    def _key(self, namespace: str, identifier: str) -> str:
        return f"manga:{namespace}:{identifier}"

    # Model configuration cache
    async def get_model_config(self, config_id: str) -> Optional[ModelConfig]:
        key = self._key("config", config_id)
        data = await self.redis.get(key)
        if data:
            return ModelConfig.parse_raw(data)
        return None

    async def set_model_config(self, config: ModelConfig, ttl: int = 300):
        key = self._key("config", config.id)
        await self.redis.setex(key, ttl, config.json())

    # User permission cache
    async def get_user_permissions(self, user_id: str, project_id: str) -> Set[str]:
        key = self._key("perms", f"{user_id}:{project_id}")
        data = await self.redis.smembers(key)
        return set(data) if data else set()

    # Dashboard data cache (per user)
    async def get_dashboard_summary(self, user_id: str) -> Optional[Dict]:
        key = self._key("dashboard", user_id)
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    # Cache invalidation on write
    async def invalidate_project_cache(self, project_id: str):
        pattern = self._key("*", f"*{project_id}*")
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

### 9.3 Read Replica Strategy

```python
# Read/write separation for database scaling

class DatabaseRouter:
    """Route queries to appropriate database replica."""

    WRITE_OPERATIONS = {'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP'}

    def __init__(self, primary_engine, replica_engines: List):
        self.primary = primary_engine
        self.replicas = replica_engines
        self.replica_index = 0

    def get_engine(self, operation: str):
        """Get appropriate engine based on operation type."""
        if operation in self.WRITE_OPERATIONS:
            return self.primary

        # Round-robin read replicas
        engine = self.replicas[self.replica_index]
        self.replica_index = (self.replica_index + 1) % len(self.replicas)
        return engine

# Session routing
async def get_db_session(operation: str = "READ"):
    engine = db_router.get_engine(operation)
    async with sessionmaker(bind=engine)() as session:
        yield session
```

### 9.4 Horizontal Scaling Considerations

| Component | Scaling Strategy | Notes |
|-----------|-----------------|-------|
| **API Servers** | Stateless, horizontal | Behind load balancer |
| **Background Workers** | Horizontal scaling | Queue-based distribution |
| **Redis** | Vertical or Cluster | For large deployments |
| **PostgreSQL** | Read replicas first | Sharding if needed later |
| **MinIO** | Horizontal (distributed) | Built-in distribution |

### 9.5 Performance Targets

| Metric | Target | Monitoring |
|--------|--------|------------|
| API P95 Latency | < 500ms | Prometheus/Grafana |
| Database Query P95 | < 100ms | pg_stat_statements |
| Cache Hit Ratio | > 80% | Redis stats |
| Queue Processing Time | < 30s | ARQ dashboard |
| Video Generation | < 5 min | Job monitoring |

---

## 10. Technical Risk Assessment

### 10.1 Risk Matrix

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| **AI API Downtime** | Medium | High | Multi-provider fallback, queue buffering | Backend |
| **Video Generation Failure** | Medium | High | Retry with backoff, manual override | Backend |
| **Database Performance** | Low | Medium | Indexing, caching, read replicas | Backend |
| **File Storage Overflow** | Medium | Medium | Quota enforcement, cleanup policy | DevOps |
| **Concurrent Edit Conflicts** | Medium | Low | Optimistic locking, merge conflict UI | Frontend |
| **AI Generation Cost Overage** | Medium | Medium | Quota tracking, alerts, hard limits | Backend |
| **Lip-Sync Quality Issues** | High | Medium | Provider selection, quality threshold | Product |
| **User Adoption (Complexity)** | Medium | High | Guided workflows, tutorials | Product |

### 10.2 Detailed Risk Analysis

#### Risk 1: AI API Downtime

**Description:** External AI service providers (OpenAI, Stability, HeyGen) may experience outages.

**Impact:**
- Pipeline execution blocked
- User productivity loss
- Potential data inconsistency if partial generation

**Mitigation:**
1. Implement provider fallback chain (primary → secondary → tertiary)
2. Queue jobs during outage, process when recovered
3. Graceful degradation messaging to users
4. Circuit breaker to prevent cascading failures

```python
# Circuit breaker implementation
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60, expected_exception=AIProviderError)
async def call_ai_provider(provider, request):
    return await provider.generate(request)
```

#### Risk 2: Video Generation Failure

**Description:** Lip-sync video generation may fail due to:
- Face detection failure on certain art styles
- Audio/video duration mismatch
- Provider-specific format issues

**Impact:**
- Pipeline blocked at Step 6
- Manual intervention required

**Mitigation:**
1. Pre-validation of image before submission (face detection test)
2. Automatic retry with adjusted parameters
3. Fallback to simpler animation method
4. Manual upload option for edge cases

#### Risk 3: Database Performance Under Load

**Description:** As project count and asset volume grows, database queries may slow down.

**Impact:**
- Slow API responses
- Dashboard loading delays

**Mitigation:**
1. Proper indexing strategy (see Section 1.2.2)
2. Query optimization with EXPLAIN ANALYZE
3. Read replica scaling
4. Connection pool tuning
5. Archive old/completed projects

#### Risk 4: AI Generation Cost Overage

**Description:** Uncontrolled AI API usage may exceed budget.

**Impact:**
- Unexpected costs
- Quota exhaustion blocking production

**Mitigation:**
1. Per-project quota tracking
2. Warning at 80% quota usage
3. Hard limit enforcement
4. Cost estimation before generation
5. Batch generation discounts

```python
# Quota check before generation
async def check_quota(project_id: str, model_category: str) -> bool:
    usage = await get_quota_usage(project_id, model_category)
    if usage.usage_count >= usage.quota_limit:
        raise QuotaExceededError(f"Quota exceeded for {model_category}")
    if usage.usage_count >= usage.quota_limit * 0.8:
        await send_warning_notification(project_id, model_category)
    return True
```

### 10.3 Disaster Recovery Plan

| Scenario | Recovery Procedure | RTO | RPO |
|----------|-------------------|-----|-----|
| Database failure | Failover to replica, restore from backup | 15 min | 5 min |
| File storage failure | MinIO distributed recovery, S3 restore | 30 min | 1 hour |
| Complete region failure | DNS failover to secondary region | 1 hour | 24 hour |
| AI provider permanent failure | Switch to backup provider, update configs | 1 hour | 0 |

---

## 11. Recommendations Summary

### 11.1 Immediate Actions (Pre-Development)

| Priority | Action | Rationale |
|----------|--------|-----------|
| P0 | Clarify authentication requirements with PM | Core to all API design |
| P0 | Define BGM source and storage requirements | Affects asset model |
| P0 | Confirm AI providers for launch | Determines adapter implementation |
| P1 | Finalize schema with missing tables | Required for development |
| P1 | Define file storage quotas and limits | Infrastructure planning |

### 11.2 Phase 1 (MVP)

| Component | Recommendation |
|-----------|----------------|
| **Database** | PostgreSQL 16 with recommended schema |
| **Cache** | Redis 7 for sessions, caching, job queue |
| **File Storage** | MinIO self-hosted (or S3 for simplicity) |
| **Job Queue** | ARQ (async Redis queue) |
| **Authentication** | JWT with refresh tokens |
| **AI Integration** | Provider abstraction with fallback |

### 11.3 Phase 2 (Post-MVP)

| Enhancement | Benefit |
|-------------|---------|
| Read replicas | Scale read-heavy operations |
| CDN for media | Faster global delivery |
| Audit log partitioning | Improved query performance |
| Event bus (NATS/Kafka) | Decoupled service communication |
| Metrics dashboard | Operational visibility |

---

## Appendix A: Open Questions for PM

| ID | Question | Priority | Impact |
|----|----------|----------|--------|
| Q1 | What authentication method is required? (Built-in, SSO, OAuth) | P0 | Affects auth design |
| Q2 | Should users be able to bring their own AI API keys? | P1 | Affects billing model |
| Q3 | What is the target launch date? | P0 | Affects scope decisions |
| Q4 | What are the budget constraints for AI API costs? | P1 | Affects quota design |
| Q5 | Are there specific compliance requirements? (GDPR, etc.) | P1 | Affects data handling |
| Q6 | What languages beyond Chinese need support? | P2 | Affects TTS/UI |
| Q7 | Should BGM be AI-generated or licensed library? | P1 | Affects asset design |
| Q8 | What is the expected team size per project? | P2 | Affects scaling |

---

## Appendix B: Technology Stack Recommendation

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend Framework** | FastAPI (Python 3.11+) | Async native, auto-docs, Pydantic |
| **Database** | PostgreSQL 16 | JSONB support, proven reliability |
| **Cache/Queue** | Redis 7 | Versatile, well-supported |
| **ORM** | SQLAlchemy 2.0 (async) | Mature, feature-rich |
| **Job Queue** | ARQ | Async-native, Redis-based |
| **File Storage** | MinIO | S3-compatible, self-hostable |
| **Authentication** | PyJWT + passlib | Standard, well-maintained |
| **Validation** | Pydantic V2 | Integrated with FastAPI |
| **Testing** | pytest + httpx | Comprehensive testing |
| **Monitoring** | Prometheus + Grafana | Industry standard |

---

**Document End**

*Review completed by: Backend Architecture Team*
*Next Steps: PM review and clarification of open questions*
