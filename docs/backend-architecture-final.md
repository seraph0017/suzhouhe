# Backend Architecture Final Review
# Enterprise AI Manga/Video Production Pipeline System

**Document Version:** 1.0
**Date:** 2026-03-01
**Author:** Backend Architect
**Status:** APPROVED FOR DEVELOPMENT

---

## Executive Summary

This document provides the final backend architecture specification for the AI Manga/Video Production Pipeline System. All previously identified gaps (GAP-001 through GAP-004) have been addressed in the updated PRD. This architecture document translates the PRD requirements into executable technical specifications.

### Architecture Approval Status

| Item | Status | Notes |
|------|--------|-------|
| Authentication Design | CONFIRMED | JWT with refresh tokens |
| BGM Strategy | CONFIRMED | AI-generated + user upload |
| Async Communication | CONFIRMED | WebSocket + ARQ/Redis |
| Storage Quotas | CONFIRMED | Tier-based limits defined |
| AI Fallback Logic | CONFIRMED | 3 retries + manual failover |
| Export Formats | CONFIRMED | MP4/MOV/WebM support |

---

## 1. Gap Analysis Confirmation

### GAP-001: Storage Quotas and Limits
**Status:** RESOLVED

The PRD Section 7.6 now defines comprehensive storage quotas:

| Tier | Storage | API Calls | Max Chapters | Max Members |
|------|---------|-----------|--------------|-------------|
| Starter | 10 GB | 1,000 | 20 | 5 |
| Professional | 100 GB | 10,000 | 100 | 20 |
| Enterprise | 1 TB | 100,000 | Unlimited | Unlimited |

**Architecture Impact:**
- Added `storage_quota_bytes` to projects table
- Added storage tracking service for quota enforcement
- Implemented automatic cleanup policy (7-day unselected, 30-day cold archive)

---

### GAP-002: WebSocket Real-Time Communication
**Status:** RESOLVED

The PRD Section 7.7 now specifies complete WebSocket protocol:

- Connection handshake with JWT authentication
- Message types: CONNECTION_ACK, PROGRESS_UPDATE, ERROR, TASK_COMPLETE
- Heartbeat mechanism (PING/PONG every 30s)
- Exponential backoff reconnection strategy

**Architecture Impact:**
- WebSocket handler service with connection pooling
- Redis pub/sub for cross-instance message broadcasting
- Message schema validation with Pydantic models

---

### GAP-003: AI Provider Fallback Logic
**Status:** RESOLVED

The PRD Section 7.8 now defines retry and failover:

| Failure Type | Retries | Delay | Timeout |
|--------------|---------|-------|---------|
| Network Error | 3 | Exponential | 30s |
| Rate Limit (429) | 3 | Retry-After header | 30s |
| Server Error (5xx) | 3 | Exponential | 60s |

**Architecture Impact:**
- Provider health check service (5-minute intervals)
- Circuit breaker pattern for degraded providers
- Manual provider switch UI workflow supported by backend

---

### GAP-004: Task Assignment Workflow
**Status:** RESOLVED

The PRD Section 7.9 now specifies assignment modes:

- Auto-assignment: Round-robin with workload balancing
- Manual assignment: Team Lead discretion
- Priority levels: CRITICAL, HIGH, NORMAL, LOW
- Deadline escalation with notifications

**Architecture Impact:**
- Task assignment service with pluggable strategies
- Workload scoring algorithm
- Notification service integration

---

## 2. Database Schema (Complete)

### 2.1 Core Tables

```sql
-- ============================================================================
-- USER MANAGEMENT
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'TEAM_LEAD', 'TEAM_MEMBER')),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- ============================================================================
-- PROJECT MANAGEMENT
-- ============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    team_lead_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ARCHIVED', 'DRAFT')),
    tier VARCHAR(50) DEFAULT 'STARTER' CHECK (tier IN ('STARTER', 'PROFESSIONAL', 'ENTERPRISE')),
    storage_quota_bytes BIGINT DEFAULT 10737418240, -- 10GB default
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_team_lead ON projects(team_lead_id);

CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('TEAM_LEAD', 'TEAM_MEMBER')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

CREATE INDEX idx_project_members_user ON project_members(user_id);
CREATE INDEX idx_project_members_project ON project_members(project_id);

-- Storage tracking per project
CREATE TABLE project_storage_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    total_bytes BIGINT DEFAULT 0,
    image_bytes BIGINT DEFAULT 0,
    audio_bytes BIGINT DEFAULT 0,
    video_bytes BIGINT DEFAULT 0,
    other_bytes BIGINT DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id)
);

-- ============================================================================
-- MODEL CONFIGURATION (Hot-swappable AI providers)
-- ============================================================================

CREATE TABLE model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL CHECK (category IN ('LLM', 'IMAGE', 'VIDEO', 'TTS', 'BGM')),
    provider VARCHAR(100) NOT NULL,
    credentials JSONB NOT NULL, -- Encrypted at application layer
    default_model VARCHAR(100),
    parameters JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 1, -- For failover ordering
    is_active BOOLEAN DEFAULT true,
    health_status VARCHAR(50) DEFAULT 'UNKNOWN' CHECK (health_status IN ('HEALTHY', 'DEGRADED', 'UNAVAILABLE', 'UNKNOWN')),
    last_health_check_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_configs_project ON model_configs(project_id);
CREATE INDEX idx_model_configs_category ON model_configs(category);
CREATE INDEX idx_model_configs_active ON model_configs(is_active);

-- ============================================================================
-- SCRIPT MANAGEMENT
-- ============================================================================

CREATE TABLE scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL, -- Structured: {scenes: [], characters: [], metadata: {}}
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'IN_REVIEW', 'LOCKED', 'PUBLISHED')),
    locked_at TIMESTAMP,
    locked_by UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scripts_project ON scripts(project_id);
CREATE INDEX idx_scripts_status ON scripts(status);
CREATE INDEX idx_scripts_created_by ON scripts(created_by);

-- Script version history for rollback
CREATE TABLE script_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content JSONB NOT NULL,
    change_summary TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_script_versions_script ON script_versions(script_id);
CREATE INDEX idx_script_versions_version ON script_versions(script_id, version);

-- ============================================================================
-- CHAPTER MANAGEMENT
-- ============================================================================

CREATE TABLE chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title VARCHAR(255),
    summary TEXT,
    sequence_order INTEGER NOT NULL,
    estimated_duration_sec INTEGER,
    actual_duration_sec INTEGER,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'CHAPTER_BREAKDOWN', 'STORYBOARD', 'MATERIAL_GEN',
        'VIDEO_GEN', 'COMPOSITION', 'FIRST_AUDIT', 'SECOND_AUDIT',
        'PUBLISHED', 'REJECTED'
    )),
    workflow_step INTEGER DEFAULT 1, -- 1-8 corresponding to pipeline steps
    assigned_to UUID REFERENCES users(id),
    priority VARCHAR(50) DEFAULT 'NORMAL' CHECK (priority IN ('CRITICAL', 'HIGH', 'NORMAL', 'LOW')),
    due_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(script_id, chapter_number)
);

CREATE INDEX idx_chapters_script ON chapters(script_id);
CREATE INDEX idx_chapters_status ON chapters(status);
CREATE INDEX idx_chapters_assigned_to ON chapters(assigned_to);
CREATE INDEX idx_chapters_workflow ON chapters(workflow_step, status);

-- ============================================================================
-- STORYBOARD PANELS
-- ============================================================================

CREATE TABLE storyboard_panels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    image_prompt TEXT NOT NULL,
    camera_direction VARCHAR(100),
    character_pose VARCHAR(100),
    background_description TEXT,
    dialogue TEXT,
    subtitle_text VARCHAR(500),
    estimated_duration_sec DECIMAL(5,2),
    selected_image_id UUID, -- References generated_images
    selected_audio_id UUID, -- References generated_audio
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'GENERATED', 'SELECTED', 'APPROVED', 'REJECTED'
    )),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_storyboard_panels_chapter ON storyboard_panels(chapter_id);
CREATE INDEX idx_storyboard_panels_sequence ON storyboard_panels(chapter_id, sequence_number);
CREATE INDEX idx_storyboard_panels_status ON storyboard_panels(status);

-- ============================================================================
-- GENERATED ASSETS
-- ============================================================================

CREATE TABLE generated_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    panel_id UUID REFERENCES storyboard_panels(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    file_size_bytes BIGINT,
    generation_params JSONB,
    seed INTEGER,
    provider VARCHAR(100),
    model_config_id UUID REFERENCES model_configs(id),
    is_selected BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP -- For auto-cleanup of unselected images
);

CREATE INDEX idx_generated_images_panel ON generated_images(panel_id);
CREATE INDEX idx_generated_images_project ON generated_images(project_id);
CREATE INDEX idx_generated_images_selected ON generated_images(is_selected);
CREATE INDEX idx_generated_images_created ON generated_images(created_at);

CREATE TABLE generated_audio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    panel_id UUID REFERENCES storyboard_panels(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    audio_url VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    duration_sec DECIMAL(8,2),
    voice_id VARCHAR(100),
    generation_params JSONB,
    provider VARCHAR(100),
    model_config_id UUID REFERENCES model_configs(id),
    is_selected BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_generated_audio_panel ON generated_audio(panel_id);
CREATE INDEX idx_generated_audio_project ON generated_audio(project_id);
CREATE INDEX idx_generated_audio_selected ON generated_audio(is_selected);

CREATE TABLE generated_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    panel_id UUID REFERENCES storyboard_panels(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    video_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    file_size_bytes BIGINT,
    duration_sec DECIMAL(8,2),
    generation_params JSONB,
    provider VARCHAR(100),
    model_config_id UUID REFERENCES model_configs(id),
    lip_sync_accuracy VARCHAR(50),
    status VARCHAR(50) DEFAULT 'GENERATING' CHECK (status IN (
        'QUEUED', 'GENERATING', 'COMPLETED', 'FAILED'
    )),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_generated_videos_panel ON generated_videos(panel_id);
CREATE INDEX idx_generated_videos_project ON generated_videos(project_id);
CREATE INDEX idx_generated_videos_status ON generated_videos(status);

-- BGM tracks (AI-generated or user-uploaded)
CREATE TABLE bgm_tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    source VARCHAR(50) CHECK (source IN ('AI_GENERATED', 'USER_UPLOADED', 'LIBRARY')),
    audio_url VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    duration_sec DECIMAL(8,2),
    mood_tags TEXT[], -- ['romantic', 'dreamy', 'tense']
    tempo VARCHAR(50),
    instruments TEXT[],
    is_loop_seamless BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bgm_tracks_project ON bgm_tracks(project_id);
CREATE INDEX idx_bgm_tracks_source ON bgm_tracks(source);
CREATE INDEX idx_bgm_tracks_mood ON bgm_tracks USING GIN(mood_tags);

-- ============================================================================
-- AUDIT SYSTEM
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES chapters(id),
    auditor_id UUID REFERENCES users(id),
    audit_type VARCHAR(50) NOT NULL CHECK (audit_type IN ('FIRST', 'SECOND')),
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED', 'MINOR_EDIT')),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- For second audit
    feedback TEXT,
    rejection_category VARCHAR(100),
    return_to_step INTEGER,
    requires_re_audit BOOLEAN DEFAULT true,
    time_spent_minutes INTEGER,
    approved_panels INTEGER[], -- Panel IDs approved
    rejected_panels INTEGER[], -- Panel IDs rejected
    selection_snapshot JSONB, -- Image/audio selections at audit time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_chapter ON audit_logs(chapter_id);
CREATE INDEX idx_audit_logs_auditor ON audit_logs(auditor_id);
CREATE INDEX idx_audit_logs_type ON audit_logs(audit_type);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- System-wide audit trail
CREATE TABLE system_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    previous_state JSONB,
    current_state JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    metadata JSONB
);

CREATE INDEX idx_system_audit_logs_user ON system_audit_logs(user_id);
CREATE INDEX idx_system_audit_logs_action ON system_audit_logs(action);
CREATE INDEX idx_system_audit_logs_entity ON system_audit_logs(entity_type, entity_id);
CREATE INDEX idx_system_audit_logs_timestamp ON system_audit_logs(timestamp);

-- ============================================================================
-- TASK ASSIGNMENT
-- ============================================================================

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL CHECK (task_type IN (
        'CHAPTER_BREAKDOWN', 'STORYBOARD_CREATE', 'FIRST_AUDIT',
        'MATERIAL_GENERATION', 'VIDEO_GENERATION', 'COMPOSITION', 'SECOND_AUDIT'
    )),
    assignee_id UUID REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    priority VARCHAR(50) DEFAULT 'NORMAL' CHECK (priority IN ('CRITICAL', 'HIGH', 'NORMAL', 'LOW')),
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE', 'CANCELLED'
    )),
    due_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    workflow_step INTEGER NOT NULL,
    auto_assigned BOOLEAN DEFAULT false,
    reassignment_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due ON tasks(due_at);

-- ============================================================================
-- EXPORT MANAGEMENT
-- ============================================================================

CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    batch_id UUID, -- For batch exports
    format VARCHAR(50) NOT NULL CHECK (format IN (
        'MP4_H264', 'MP4_HEVC', 'MOV_PRORES', 'WEBM_VP9'
    )),
    preset VARCHAR(50) CHECK (preset IN ('MOBILE', 'WEB_STANDARD', 'HIGH_QUALITY', 'MASTER')),
    resolution VARCHAR(50),
    include_subtitles BOOLEAN DEFAULT true,
    subtitle_format VARCHAR(50) DEFAULT 'BURNED_IN',
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'PARTIAL'
    )),
    output_url VARCHAR(500),
    file_size_bytes BIGINT,
    progress DECIMAL(5,2) DEFAULT 0,
    error_message TEXT,
    requested_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_exports_project ON exports(project_id);
CREATE INDEX idx_exports_chapter ON exports(chapter_id);
CREATE INDEX idx_exports_batch ON exports(batch_id);
CREATE INDEX idx_exports_status ON exports(status);

-- ============================================================================
-- API QUOTA TRACKING
-- ============================================================================

CREATE TABLE api_quota_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    model_config_id UUID REFERENCES model_configs(id),
    provider VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    call_count INTEGER DEFAULT 1,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, model_config_id, date)
);

CREATE INDEX idx_api_quota_project ON api_quota_usage(project_id);
CREATE INDEX idx_api_quota_date ON api_quota_usage(date);

-- ============================================================================
-- WEBSOCKET CONNECTION TRACKING (Runtime, not persisted)
-- ============================================================================
-- Note: Connection tracking is handled in Redis, not PostgreSQL

```

### 2.2 Entity Relationship Summary

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    USERS    │       │   PROJECTS  │       │ MODEL_CONFIG│
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ email       │       │ name        │       │ project_id  │
│ role        │◄──────│ team_lead_id│───┐   │ category    │
└──────┬──────┘       └──────┬──────┘   │   │ provider    │
       │                     │          │   └─────────────┘
       │       ┌─────────────┴──────┐   │
       │       │  PROJECT_MEMBERS   │   │
       │       ├────────────────────┤   │
       └──────►│ user_id (FK)       │   │
               │ project_id (FK)    │   │
               │ role               │◄──┘
               └────────────────────┘

               ┌─────────────────────┐
               │      SCRIPTS        │
               ├─────────────────────┤
               │ id (PK)             │
               │ project_id (FK)     │
               │ content (JSONB)     │
               │ status              │
               └──────────┬──────────┘
                          │ 1:N
                          ▼
               ┌─────────────────────┐
               │      CHAPTERS       │
               ├─────────────────────┤
               │ id (PK)             │
               │ script_id (FK)      │
               │ status              │
               │ assigned_to (FK)    │
               └──────────┬──────────┘
                          │ 1:N
                          ▼
               ┌─────────────────────┐
               │  STORYBOARD_PANELS  │
               ├─────────────────────┤
               │ id (PK)             │
               │ chapter_id (FK)     │
               │ image_prompt        │
               │ selected_image_id   │
               │ selected_audio_id   │
               └──────────┬──────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│GENERATED_IMAGE│ │GENERATED_AUDIO│ │GENERATED_VIDEO│
└───────────────┘ └───────────────┘ └───────────────┘

               ┌─────────────────────┐
               │      AUDIT_LOGS     │
               ├─────────────────────┤
               │ chapter_id (FK)     │
               │ auditor_id (FK)     │
               │ decision            │
               └─────────────────────┘
```

---

## 3. API Endpoint Specifications

### 3.1 Authentication Endpoints

#### POST /api/v1/auth/login

**Purpose:** User authentication, returns JWT tokens.

**Request Schema:**
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int  # seconds
    token_type: str = "Bearer"
    user: UserSchema
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "Wang Fang",
      "role": "TEAM_MEMBER",
      "avatar_url": "https://cdn.example.com/avatars/..."
    }
  }
}
```

**Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_INVALID_CREDENTIALS | 401 | Email or password incorrect |
| AUTH_ACCOUNT_LOCKED | 403 | Account locked after failed attempts |
| AUTH_ACCOUNT_INACTIVE | 403 | Account deactivated by admin |

---

#### POST /api/v1/auth/refresh

**Purpose:** Refresh access token using refresh token.

**Request Schema:**
```python
class RefreshTokenRequest(BaseModel):
    refresh_token: str
```

---

#### POST /api/v1/auth/logout

**Purpose:** Invalidate token (add to blacklist).

---

### 3.2 Projects Endpoints

#### GET /api/v1/projects

**Purpose:** List projects accessible by current user.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | all | Filter by status (active/archived) |
| page | integer | 1 | Page number |
| page_size | integer | 20 | Items per page |

**Response Schema:**
```python
class ProjectListResponse(BaseModel):
    projects: List[ProjectSchema]
    total: int
    page: int
    page_size: int
    has_more: bool
```

---

#### POST /api/v1/projects

**Purpose:** Create new project.

**Request Schema:**
```python
class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    team_lead_id: UUID
    tier: str = "STARTER"
    model_config_ids: Optional[Dict[str, UUID]] = None  # {llm, image, video, tts}

class CreateProjectResponse(BaseModel):
    project: ProjectSchema
```

---

#### GET /api/v1/projects/{project_id}

**Purpose:** Get project details including storage usage.

**Response includes:**
- Project metadata
- Team members list
- Model configurations
- Storage usage statistics
- API quota usage

---

#### DELETE /api/v1/projects/{project_id}

**Purpose:** Archive project (soft delete).

**Behavior:**
- Sets status to ARCHIVED
- Makes all data read-only
- Preserves data for compliance

---

### 3.3 Scripts Endpoints

#### POST /api/v1/scripts

**Purpose:** Create script (upload or empty).

**Request Schema:**
```python
class CreateScriptRequest(BaseModel):
    project_id: UUID
    title: str
    content: Optional[Dict[str, Any]] = None  # Structured script
    source: str = "EMPTY"  # EMPTY, UPLOAD, GENERATE

class ScriptUploadRequest(BaseModel):
    file: UploadFile  # .txt, .docx
    title: str
```

---

#### POST /api/v1/scripts/{script_id}/generate

**Purpose:** Generate script using LLM.

**Request Schema:**
```python
class GenerateScriptRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=5000)
    tone: Optional[str] = None  # adventure, romance, comedy
    style: Optional[str] = None  # slice_of_life, fantasy
    target_length: str = "feature"  # short, feature
    estimated_duration_minutes: Optional[int] = None
    language: str = "zh-CN"
    llm_config_id: Optional[UUID] = None

class GenerateScriptResponse(BaseModel):
    script_id: UUID
    job_id: UUID
    status: str  # QUEUED, GENERATING, COMPLETED
    estimated_time_sec: int
```

**Async Behavior:**
- Returns immediately with job_id
- Progress tracked via WebSocket
- Polling endpoint: GET /api/v1/scripts/generate/{job_id}/status

---

#### POST /api/v1/scripts/{script_id}/lock

**Purpose:** Lock script, triggering Chapter Breakdown.

**Behavior:**
- Validates script content
- Sets status to LOCKED
- Creates initial chapter breakdown job
- Notifies assigned team members

**Request Schema:**
```python
class LockScriptRequest(BaseModel):
    confirm: bool = True  # Must be explicitly confirmed
```

**Response:**
```python
class LockScriptResponse(BaseModel):
    script_id: UUID
    status: str  # LOCKED
    chapters_created: int
    chapter_breakdown_job_id: UUID
```

---

### 3.4 Chapters Endpoints

#### GET /api/v1/scripts/{script_id}/chapters

**Purpose:** List chapters for a script.

**Response includes:**
- Chapter list with metadata
- Status per chapter
- Progress indicators

---

#### POST /api/v1/chapters/{chapter_id}/split

**Purpose:** Split chapter at specified scene.

**Request Schema:**
```python
class SplitChapterRequest(BaseModel):
    split_at_scene_index: int
    new_chapter_title: Optional[str] = None
```

---

#### POST /api/v1/chapters/merge

**Purpose:** Merge two adjacent chapters.

**Request Schema:**
```python
class MergeChaptersRequest(BaseModel):
    chapter_ids: List[UUID] = Field(..., min_items=2, max_items=2)
    merged_title: Optional[str] = None
```

---

#### POST /api/v1/chapters/reorder

**Purpose:** Reorder chapters.

**Request Schema:**
```python
class ReorderChaptersRequest(BaseModel):
    chapter_order: List[UUID]  # Ordered list of chapter IDs
```

---

### 3.5 Storyboard Endpoints

#### GET /api/v1/chapters/{chapter_id}/storyboard

**Purpose:** Get storyboard panels for chapter.

**Response Schema:**
```python
class StoryboardResponse(BaseModel):
    chapter_id: UUID
    panels: List[StoryboardPanelSchema]
    is_locked: bool
    locked_at: Optional[datetime]
```

---

#### POST /api/v1/chapters/{chapter_id}/storyboard/generate

**Purpose:** Auto-generate storyboard from chapter content.

**Response:**
```python
class GenerateStoryboardResponse(BaseModel):
    chapter_id: UUID
    job_id: UUID
    panels_generated: int
    estimated_time_sec: int
```

---

#### PUT /api/v1/storyboard/panels/{panel_id}

**Purpose:** Update panel content.

**Request Schema:**
```python
class UpdatePanelRequest(BaseModel):
    image_prompt: Optional[str] = None
    camera_direction: Optional[str] = None
    character_pose: Optional[str] = None
    dialogue: Optional[str] = None
    subtitle_text: Optional[str] = None
```

---

#### POST /api/v1/chapters/{chapter_id}/storyboard/lock

**Purpose:** Lock storyboard, triggering Material Generation.

**Behavior:**
- Validates all panels have required content
- Triggers Step 5 (Material Generation)
- Updates chapter workflow step

---

### 3.6 Material Generation Endpoints

#### POST /api/v1/generation/images

**Purpose:** Generate images for storyboard panels.

**Request Schema:**
```python
class GenerateImagesRequest(BaseModel):
    panel_ids: List[UUID] = Field(..., min_items=1)
    batch_size: int = Field(default=4, ge=2, le=8)
    image_config_id: Optional[UUID] = None
    style_preset: Optional[str] = None
    aspect_ratio: str = "16:9"
    resolution: str = "1920x1080"
    negative_prompt: Optional[str] = None

class GenerateImagesResponse(BaseModel):
    job_id: UUID
    status: str
    panels_queued: int
    estimated_time_sec: int
```

**Async Behavior:**
- Job queued in ARQ
- Progress pushed via WebSocket
- Retry logic with fallback provider

---

#### POST /api/v1/generation/audio

**Purpose:** Generate TTS audio for panel dialogue.

**Request Schema:**
```python
class GenerateAudioRequest(BaseModel):
    requests: List[AudioGenerationRequest]

class AudioGenerationRequest(BaseModel):
    panel_id: UUID
    text: str
    voice_id: str
    language: str = "zh-CN"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: int = Field(default=0, ge=-12, le=12)
    emotion: Optional[str] = None
    tts_config_id: Optional[UUID] = None
```

---

#### POST /api/v1/generation/video

**Purpose:** Generate lip-sync video from image + audio.

**Request Schema:**
```python
class GenerateVideoRequest(BaseModel):
    panel_id: UUID
    image_id: UUID
    audio_id: UUID
    video_config_id: Optional[UUID] = None
    model_provider: Optional[str] = None
    fps: int = 30
    resolution: str = "1920x1080"
    lip_sync_accuracy: str = "high"
    background_motion: str = "subtle"

class GenerateVideoResponse(BaseModel):
    job_id: UUID
    status: str
    estimated_time_sec: int
```

---

#### GET /api/v1/generation/jobs/{job_id}

**Purpose:** Poll generation job status.

**Response Schema:**
```python
class GenerationJobStatus(BaseModel):
    job_id: UUID
    job_type: str  # IMAGE, AUDIO, VIDEO
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED
    progress: float  # 0.0 - 1.0
    current_step: Optional[str]
    total_steps: int
    completed_steps: int
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    retry_count: int
    provider_used: Optional[str]
```

---

#### POST /api/v1/generation/jobs/{job_id}/cancel

**Purpose:** Cancel running generation job.

---

#### POST /api/v1/generation/jobs/{job_id}/retry

**Purpose:** Retry failed job (optionally with different provider).

**Request Schema:**
```python
class RetryJobRequest(BaseModel):
    use_alternative_provider: bool = False
    alternative_config_id: Optional[UUID] = None
```

---

### 3.7 Audit Endpoints

#### GET /api/v1/audits/pending

**Purpose:** Get pending audits for current user.

**Response Schema:**
```python
class PendingAuditsResponse(BaseModel):
    first_audits: List[AuditItemSchema]
    second_audits: List[AuditItemSchema]
    total_count: int
```

---

#### POST /api/v1/audits/first

**Purpose:** Submit first audit (Team Member).

**Request Schema:**
```python
class FirstAuditRequest(BaseModel):
    chapter_id: UUID
    status: str  # APPROVED, NEEDS_REPLACEMENT, NEEDS_REGENERATION
    approved_panels: List[int]  # Panel sequence numbers
    rejected_panels: List[int]
    selections: Dict[str, SelectionSchema]  # panel_id -> {image_id, audio_id}
    comments: Optional[str] = None
    time_spent_minutes: int

class SelectionSchema(BaseModel):
    image_id: UUID
    audio_id: UUID
```

**Behavior:**
- If APPROVED: Chapter moves to SECOND_AUDIT
- If NEEDS_REPLACEMENT: Stay in FIRST_AUDIT
- If NEEDS_REGENERATION: Trigger regeneration jobs

---

#### POST /api/v1/audits/second

**Purpose:** Submit second audit (Team Lead).

**Request Schema:**
```python
class SecondAuditRequest(BaseModel):
    chapter_id: UUID
    decision: str  # APPROVED, REJECTED, MINOR_EDIT
    rating: int = Field(default=5, ge=1, le=5)
    feedback: Optional[str] = None
    rejection_category: Optional[str] = None
    return_to_step: Optional[int] = None
    requires_re_audit: bool = True
    timestamped_comments: Optional[List[TimestampedComment]] = None
    time_spent_minutes: int

class TimestampedComment(BaseModel):
    timestamp_sec: float
    comment: str
```

**Rejection Categories:**
```python
REJECTION_CATEGORIES = [
    "VISUAL_QUALITY",
    "AUDIO_QUALITY",
    "LIP_SYNC_ISSUES",
    "STORYBOARD_ISSUES",
    "BGM_ISSUES",
    "SUBTITLE_ISSUES",
    "PACING_ISSUES"
]
```

**Return to Step Mapping:**
| Category | Return To Step | Re-audit Required |
|----------|----------------|-------------------|
| VISUAL_QUALITY | 5 | Yes |
| AUDIO_QUALITY | 5 | Yes |
| LIP_SYNC_ISSUES | 6 | Yes |
| STORYBOARD_ISSUES | 4 | Yes |
| BGM_ISSUES | 7 | Yes |
| SUBTITLE_ISSUES | 7 | No (Minor Edit) |

---

#### GET /api/v1/audits/history/{chapter_id}

**Purpose:** Get complete audit history for chapter.

**Response Schema:**
```python
class AuditHistoryResponse(BaseModel):
    chapter_id: UUID
    audits: List[AuditLogSchema]
    current_status: str
```

---

### 3.8 Model Configuration Endpoints

#### GET /api/v1/model-configs

**Purpose:** List model configurations for project.

---

#### POST /api/v1/model-configs

**Purpose:** Create new model configuration.

**Request Schema:**
```python
class CreateModelConfigRequest(BaseModel):
    project_id: UUID
    category: str  # LLM, IMAGE, VIDEO, TTS, BGM
    provider: str
    credentials: Dict[str, str]  # Will be encrypted
    default_model: str
    parameters: Dict[str, Any]
    priority: int = 1
```

---

#### POST /api/v1/model-configs/{config_id}/test

**Purpose:** Test connection to provider.

**Response:**
```python
class TestConnectionResponse(BaseModel):
    success: bool
    provider: str
    latency_ms: int
    models_available: List[str]
    quota_remaining: Optional[int]
    message: str
```

---

#### GET /api/v1/model-configs/providers

**Purpose:** List supported providers per category.

**Response:**
```python
class SupportedProvidersResponse(BaseModel):
    LLM: List[ProviderInfo]
    IMAGE: List[ProviderInfo]
    VIDEO: List[ProviderInfo]
    TTS: List[ProviderInfo]
    BGM: List[ProviderInfo]

class ProviderInfo(BaseModel):
    id: str
    name: str
    supported_features: List[str]
    config_parameters: List[ParameterSchema]
```

---

### 3.9 Dashboard Endpoints

#### GET /api/v1/dashboard/summary

**Purpose:** Get role-specific dashboard summary.

**Response (Team Member):**
```python
class TeamMemberDashboardResponse(BaseModel):
    current_task: Optional[TaskSchema]
    upcoming_tasks: List[TaskSchema]
    completed_this_week: List[TaskSchema]
    progress_stats: ProgressStatsSchema
    notifications: List[NotificationSchema]
```

**Response (Team Lead):**
```python
class TeamLeadDashboardResponse(BaseModel):
    pending_reviews: List[AuditItemSchema]
    team_workload: List[WorkloadSchema]
    project_timeline: List[ProjectTimelineSchema]
    quality_metrics: QualityMetricsSchema
```

**Response (Admin):**
```python
class AdminDashboardResponse(BaseModel):
    system_health: SystemHealthSchema
    project_overview: List[ProjectSummarySchema]
    api_usage: APIUsageSchema
    recent_audit_logs: List[SystemAuditLogSchema]
    alerts: List[AlertSchema]
```

---

#### GET /api/v1/dashboard/tasks

**Purpose:** Get tasks for current user.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | all | pending/in_progress/completed |
| priority | string | all | critical/high/normal/low |
| project_id | UUID | null | Filter by project |

---

### 3.10 Export Endpoints

#### POST /api/v1/exports/chapter

**Purpose:** Export single chapter.

**Request Schema:**
```python
class ExportChapterRequest(BaseModel):
    chapter_id: UUID
    format: str  # MP4_H264, MP4_HEVC, MOV_PRORES, WEBM_VP9
    preset: str  # MOBILE, WEB_STANDARD, HIGH_QUALITY, MASTER
    resolution: Optional[str] = "1920x1080"
    include_subtitles: bool = True
    subtitle_format: str = "BURNED_IN"  # or SRT_FILE, VTT_FILE
    include_chapter_markers: bool = True
    notify_on_complete: bool = True
```

---

#### POST /api/v1/exports/batch

**Purpose:** Batch export multiple chapters/formats.

**Request Schema:**
```python
class BatchExportRequest(BaseModel):
    project_id: UUID
    exports: List[ExportItemRequest]
    create_archive: bool = True
    archive_format: str = "ZIP"
    notify_on_complete: bool = True

class ExportItemRequest(BaseModel):
    chapter_id: UUID
    format: str
    preset: str
```

---

#### GET /api/v1/exports/batch/{batch_id}

**Purpose:** Get batch export status.

---

### 3.11 WebSocket Endpoints

#### WebSocket /ws/v1/notifications

**Purpose:** Real-time notifications and progress updates.

**Connection Handshake:**
```json
// Client -> Server
{
  "type": "CONNECTION_INIT",
  "payload": {
    "authorization": "Bearer <JWT_ACCESS_TOKEN>"
  }
}

// Server -> Server (Success)
{
  "type": "CONNECTION_ACK",
  "payload": {
    "connectionId": "uuid",
    "expiresIn": 3600
  }
}

// Server -> Client (Error)
{
  "type": "CONNECTION_ERROR",
  "payload": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

**Message Types:**

| Type | Direction | Purpose |
|------|-----------|---------|
| CONNECTION_INIT | Client -> Server | Initialize connection |
| CONNECTION_ACK | Server -> Client | Connection acknowledged |
| PROGRESS_UPDATE | Server -> Client | Job progress notification |
| TASK_COMPLETE | Server -> Client | Job completion |
| ERROR | Server -> Client | Error notification |
| PING | Client -> Server | Heartbeat |
| PONG | Server -> Client | Heartbeat response |

---

## 4. Service Layer Architecture

### 4.1 Service Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐ │
│  │  AuthService      │     │  UserService      │     │  ProjectService   │ │
│  ├───────────────────┤     ├───────────────────┤     ├───────────────────┤ │
│  │ + login()         │     │ + get_by_id()     │     │ + create()        │ │
│  │ + refresh_token() │     │ + update_role()   │     │ + archive()       │ │
│  │ + logout()        │     │ + get_projects()  │     │ + add_member()    │ │
│  │ + validate_jwt()  │     │ + get_team()      │     │ + remove_member() │ │
│  └───────────────────┘     └───────────────────┘     │ + get_storage()   │ │
│                                                     └───────────────────┘ │
│  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐ │
│  │  ScriptService    │     │  ChapterService   │     │  StoryboardService│ │
│  ├───────────────────┤     ├───────────────────┤     ├───────────────────┤ │
│  │ + create()        │     │ + generate_from_  │     │ + generate()      │ │
│  │ + generate_llm()  │     │   script()        │     │ + update_panel()  │ │
│  │ + lock()          │     │ + split()         │     │ + lock()          │ │
│  │ + unlock()        │     │ + merge()         │     │ + add_panel()     │ │
│  │ + rollback()      │     │ + reorder()       │     │ + delete_panel()  │ │
│  └───────────────────┘     │ + update_status() │     └───────────────────┘ │
│                            └───────────────────┘                            │
│  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐ │
│  │GenerationService  │     │  AuditService     │     │  ExportService    │ │
│  ├───────────────────┤     ├───────────────────┤     ├───────────────────┤ │
│  │ + generate_images()│    │ + submit_first()  │     │ + export_chapter()│ │
│  │ + generate_audio() │    │ + submit_second() │     │ + batch_export()  │ │
│  │ + generate_video() │    │ + get_history()   │     │ + get_status()    │ │
│  │ + get_job_status() │    │ + get_pending()   │     └───────────────────┘ │
│  │ + cancel_job()    │     └───────────────────┘                            │
│  │ + retry_job()     │                                                      │
│  └───────────────────┘                                                      │
│  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐ │
│  │ModelConfigService │     │  TaskService      │     │ DashboardService  │ │
│  ├───────────────────┤     ├───────────────────┤     ├───────────────────┤ │
│  │ + create()        │     │ + assign()        │     │ + get_summary()   │ │
│  │ + test_connection()│    │ + reassign()      │     │ + get_tasks()     │ │
│  │ + get_providers() │     │ + update_status() │     │ + get_notifications││
│  │ + health_check()  │     │ + get_workload()  │     └───────────────────┘ │
│  └───────────────────┘     │ + auto_assign()   │                              │
│                            └───────────────────┘                              │
│  ┌───────────────────┐                                                         │
│  │ WebSocketService  │                                                         │
│  ├───────────────────┤                                                         │
│  │ + handle_connect()│                                                         │
│  │ + handle_message()│                                                         │
│  │ + broadcast()     │                                                         │
│  │ + send_progress() │                                                         │
│  └───────────────────┘                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Core Service Implementations

#### AuthService

```python
class AuthService:
    """Handles authentication, JWT token management."""

    def __init__(
        self,
        db: AsyncSession,
        redis: Redis,
        config: AuthConfig
    ):
        self.db = db
        self.redis = redis
        self.config = config
        self.password_hasher = bcrypt.Bcrypt()

    async def login(
        self,
        email: str,
        password: str
    ) -> TokenPair:
        """Authenticate user and return JWT tokens."""
        user = await self._get_user_by_email(email)
        if not user or not user.is_active:
            raise AuthenticationError("AUTH_INVALID_CREDENTIALS")

        if not self.password_hasher.verify(password, user.password_hash):
            raise AuthenticationError("AUTH_INVALID_CREDENTIALS")

        await self._update_last_login(user.id)

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        await self._store_refresh_token(
            user.id,
            refresh_token,
            expires_in=self.config.refresh_token_expires_in
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_expires_in,
            user=UserSchema.from_orm(user)
        )

    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token."""
        payload = self._decode_refresh_token(refresh_token)
        user_id = payload.get("sub")

        # Verify refresh token is not blacklisted
        is_valid = await self._verify_refresh_token(user_id, refresh_token)
        if not is_valid:
            raise AuthenticationError("AUTH_TOKEN_INVALID")

        user = await self._get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("AUTH_ACCOUNT_INACTIVE")

        # Issue new token pair
        new_access_token = self._create_access_token(user)
        new_refresh_token = self._create_refresh_token(user)

        await self._store_refresh_token(
            user_id,
            new_refresh_token,
            expires_in=self.config.refresh_token_expires_in
        )

        return TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=self.config.access_token_expires_in,
            user=UserSchema.from_orm(user)
        )

    async def logout(self, user_id: UUID, token: str) -> None:
        """Logout user and blacklist token."""
        await self._blacklist_token(token)
        await self._delete_refresh_token(user_id)

    def _create_access_token(self, user: User) -> str:
        """Create short-lived access token."""
        now = datetime.utcnow()
        expires = now + timedelta(
            seconds=self.config.access_token_expires_in
        )

        claims = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expires,
            "iat": now,
            "type": "access"
        }

        return jwt.encode(
            claims,
            self.config.jwt_secret_key,
            algorithm=self.config.jwt_algorithm
        )

    def _create_refresh_token(self, user: User) -> str:
        """Create long-lived refresh token."""
        now = datetime.utcnow()
        expires = now + timedelta(
            seconds=self.config.refresh_token_expires_in
        )

        claims = {
            "sub": str(user.id),
            "exp": expires,
            "iat": now,
            "type": "refresh",
            "jti": str(uuid4())
        }

        return jwt.encode(
            claims,
            self.config.jwt_refresh_secret_key,
            algorithm=self.config.jwt_algorithm
        )
```

---

#### GenerationService

```python
class GenerationService:
    """Orchestrates AI generation with retry and failover logic."""

    def __init__(
        self,
        db: AsyncSession,
        redis: Redis,
        arq_pool: Pool,
        provider_registry: ProviderRegistry,
        config: GenerationConfig
    ):
        self.db = db
        self.redis = redis
        self.arq_pool = arq_pool
        self.provider_registry = provider_registry
        self.config = config

    async def generate_images(
        self,
        request: GenerateImagesRequest,
        project_id: UUID
    ) -> GenerationJob:
        """Queue image generation job with retry support."""
        job_id = uuid4()

        # Get available providers (healthy + active)
        providers = await self._get_available_providers(
            project_id,
            category="IMAGE",
            config_id=request.image_config_id
        )

        if not providers:
            raise GenerationError("No available image providers")

        # Create job record
        job = GenerationJob(
            id=job_id,
            job_type="IMAGE",
            status="QUEUED",
            project_id=project_id,
            panel_ids=request.panel_ids,
            provider_priority=[p.id for p in providers],
            retry_config=self.config.image_retry_config,
            created_at=datetime.utcnow()
        )

        await self.db.add(job)
        await self.db.commit()

        # Queue ARQ job
        await self.arq_pool.enqueue_job(
            "generate_images",
            job_id=str(job_id),
            panel_ids=[str(p) for p in request.panel_ids],
            batch_size=request.batch_size,
            provider_ids=[str(p) for p in providers],
            params=request.dict()
        )

        # Notify via WebSocket
        await self.websocket_service.broadcast(
            project_id=project_id,
            message=ProgressUpdate(
                job_id=job_id,
                job_type="IMAGE_GENERATION",
                status="QUEUED",
                progress=0.0,
                queue_position=await self._get_queue_position(job_id)
            )
        )

        return job

    async def _execute_with_retry(
        self,
        job: GenerationJob,
        operation: Callable,
        providers: List[ModelConfig]
    ) -> GenerationResult:
        """Execute generation with automatic retry and failover."""
        last_error = None

        for provider in providers:
            for attempt in range(job.retry_config.max_retries + 1):
                try:
                    # Apply exponential backoff
                    if attempt > 0:
                        delay = self._calculate_backoff(
                            attempt,
                            job.retry_config.initial_delay_ms,
                            job.retry_config.max_delay_ms,
                            job.retry_config.multiplier,
                            job.retry_config.jitter
                        )
                        await asyncio.sleep(delay / 1000)

                    # Update progress
                    await self._update_job_status(
                        job.id,
                        "PROCESSING",
                        provider=provider.provider,
                        attempt=attempt + 1
                    )

                    # Execute generation
                    result = await operation(provider)

                    return result

                except RateLimitError as e:
                    last_error = e
                    # Respect Retry-After header
                    retry_after = e.retry_after or self._calculate_backoff(
                        attempt + 1, 1000, 8000, 2, 0.1
                    )
                    await self._update_job_status(
                        job.id,
                        "RETRYING",
                        reason=f"Rate limited. Retrying in {retry_after/1000:.0f}s",
                        retry_after=retry_after
                    )
                    await asyncio.sleep(retry_after / 1000)

                except (NetworkError, ServerError) as e:
                    last_error = e
                    # Continue to next retry
                    continue

                except InvalidRequestError as e:
                    # Don't retry invalid requests
                    await self._update_job_status(
                        job.id,
                        "FAILED",
                        error=str(e),
                        retryable=False
                    )
                    raise GenerationError(
                        f"Invalid request: {str(e)}",
                        retryable=False
                    )

            # Provider exhausted, try next provider
            await self._mark_provider_degraded(provider.id)

        # All providers exhausted
        await self._update_job_status(
            job.id,
            "FAILED",
            error=f"All providers failed. Last error: {str(last_error)}",
            retryable=True,
            manual_intervention_required=True
        )

        raise GenerationError(
            "All generation attempts failed",
            last_error=last_error,
            retryable=True
        )

    def _calculate_backoff(
        self,
        attempt: int,
        initial_delay_ms: int,
        max_delay_ms: int,
        multiplier: float,
        jitter: float
    ) -> int:
        """Calculate exponential backoff with jitter."""
        delay = min(
            initial_delay_ms * (multiplier ** (attempt - 1)),
            max_delay_ms
        )

        # Add jitter
        jitter_range = delay * jitter
        delay += random.uniform(-jitter_range, jitter_range)

        return int(max(delay, 0))

    async def _mark_provider_degraded(self, provider_id: UUID) -> None:
        """Mark provider as degraded after consecutive failures."""
        # Increment failure count in Redis
        failure_key = f"provider:{provider_id}:failures"
        failures = await self.redis.incr(failure_key)
        await self.redis.expire(failure_key, 300)  # 5 minute window

        if failures >= 3:
            # Mark as degraded in database
            await self.db.execute(
                update(ModelConfig)
                .where(ModelConfig.id == provider_id)
                .values(
                    health_status="DEGRADED",
                    last_health_check_at=datetime.utcnow()
                )
            )
            await self.db.commit()
```

---

#### AuditService

```python
class AuditService:
    """Handles dual-audit workflow."""

    def __init__(
        self,
        db: AsyncSession,
        chapter_service: ChapterService,
        notification_service: NotificationService
    ):
        self.db = db
        self.chapter_service = chapter_service
        self.notification_service = notification_service

    async def submit_first_audit(
        self,
        request: FirstAuditRequest,
        user: User
    ) -> AuditResult:
        """Submit first audit (Team Member)."""
        # Verify user permissions
        chapter = await self._get_chapter(request.chapter_id)
        await self._verify_first_audit_permission(chapter, user)

        # Validate all panels have selections
        await self._validate_panel_selections(
            chapter.id,
            request.selections
        )

        # Create audit log
        audit_log = AuditLog(
            chapter_id=chapter.id,
            auditor_id=user.id,
            audit_type="FIRST",
            decision=self._map_status_to_decision(request.status),
            approved_panels=request.approved_panels,
            rejected_panels=request.rejected_panels,
            selection_snapshot=request.selections,
            feedback=request.comments,
            time_spent_minutes=request.time_spent_minutes
        )

        self.db.add(audit_log)

        # Update chapter status based on decision
        if request.status == "APPROVED":
            await self.chapter_service.advance_to_second_audit(chapter.id)
        elif request.status == "NEEDS_REGENERATION":
            await self.chapter_service.trigger_regeneration(chapter.id)
        else:
            await self.chapter_service.stay_in_first_audit(chapter.id)

        await self.db.commit()

        # Notify Team Lead if approved
        if request.status == "APPROVED":
            team_lead = await self._get_project_team_lead(chapter.project_id)
            await self.notification_service.send_audit_notification(
                recipient=team_lead,
                audit_type="SECOND",
                chapter=chapter
            )

        return AuditResult(
            audit_id=audit_log.id,
            chapter_id=chapter.id,
            new_status=chapter.status,
            next_action=self._get_next_action(chapter.status)
        )

    async def submit_second_audit(
        self,
        request: SecondAuditRequest,
        user: User
    ) -> AuditResult:
        """Submit second audit (Team Lead)."""
        # Verify user is Team Lead
        chapter = await self._get_chapter(request.chapter_id)
        await self._verify_second_audit_permission(chapter, user)

        # Validate rejection has category and return step
        if request.decision == "REJECTED":
            if not request.rejection_category:
                raise ValidationError("Rejection requires category")
            if not request.return_to_step:
                raise ValidationError("Rejection requires return_to_step")

        # Create audit log
        audit_log = AuditLog(
            chapter_id=chapter.id,
            auditor_id=user.id,
            audit_type="SECOND",
            decision=request.decision,
            rating=request.rating,
            feedback=request.feedback,
            rejection_category=request.rejection_category,
            return_to_step=request.return_to_step,
            requires_re_audit=request.requires_re_audit,
            time_spent_minutes=request.time_spent_minutes
        )

        self.db.add(audit_log)

        # Process decision
        if request.decision == "APPROVED":
            await self.chapter_service.publish(chapter.id)
        elif request.decision == "REJECTED":
            await self.chapter_service.return_to_step(
                chapter.id,
                step=request.return_to_step,
                requires_re_audit=request.requires_re_audit
            )
        elif request.decision == "MINOR_EDIT":
            await self.chapter_service.mark_for_minor_edit(chapter.id)

        await self.db.commit()

        # Notify assignee
        if chapter.assigned_to:
            assignee = await self._get_user(chapter.assigned_to)
            await self.notification_service.send_audit_result_notification(
                recipient=assignee,
                decision=request.decision,
                feedback=request.feedback,
                chapter=chapter
            )

        return AuditResult(
            audit_id=audit_log.id,
            chapter_id=chapter.id,
            new_status=chapter.status,
            next_action=self._get_next_action(chapter.status)
        )

    async def get_pending_audits(
        self,
        user: User,
        project_id: Optional[UUID] = None
    ) -> PendingAudits:
        """Get pending audits for user."""
        query = select(Chapter).where(
            Chapter.status.in_(["FIRST_AUDIT", "SECOND_AUDIT"])
        )

        if user.role == "TEAM_MEMBER":
            # Team members see their assigned chapters for first audit
            query = query.where(
                Chapter.assigned_to == user.id,
                Chapter.status == "FIRST_AUDIT"
            )
        elif user.role == "TEAM_LEAD":
            # Team leads see all pending second audits
            query = query.where(
                Chapter.project_id.in_(
                    select(ProjectMember.project_id).where(
                        ProjectMember.user_id == user.id
                    )
                )
            )

        if project_id:
            query = query.where(Chapter.project_id == project_id)

        result = await self.db.execute(query)
        chapters = result.scalars().all()

        first_audits = [c for c in chapters if c.status == "FIRST_AUDIT"]
        second_audits = [c for c in chapters if c.status == "SECOND_AUDIT"]

        return PendingAudits(
            first_audits=[ChapterSchema.from_orm(c) for c in first_audits],
            second_audits=[ChapterSchema.from_orm(c) for c in second_audits],
            total_count=len(first_audits) + len(second_audits)
        )
```

---

#### TaskService

```python
class TaskService:
    """Handles task assignment and workload balancing."""

    def __init__(
        self,
        db: AsyncSession,
        notification_service: NotificationService,
        config: TaskConfig
    ):
        self.db = db
        self.notification_service = notification_service
        self.config = config

    async def auto_assign_task(
        self,
        chapter: Chapter,
        task_type: str
    ) -> Task:
        """Auto-assign task using round-robin with workload balancing."""
        # Get eligible team members
        members = await self._get_eligible_members(
            project_id=chapter.project_id,
            exclude_user_id=chapter.assigned_to
        )

        if not members:
            raise TaskError("No eligible team members available")

        # Calculate workload scores
        workload_scores = await self._calculate_workload_scores(members)

        # Sort by score (lower is better)
        sorted_members = sorted(
            members,
            key=lambda m: workload_scores[m.id]
        )

        # Assign to member with lowest workload
        assignee = sorted_members[0]

        # Create task
        task = Task(
            project_id=chapter.project_id,
            chapter_id=chapter.id,
            task_type=task_type,
            assignee_id=assignee.id,
            assigned_by=chapter.project.team_lead_id,
            priority=self._calculate_priority(chapter),
            due_at=self._calculate_due_date(chapter),
            estimated_hours=self._estimate_hours(task_type),
            auto_assigned=True,
            workflow_step=chapter.workflow_step
        )

        self.db.add(task)
        await self.db.commit()

        # Notify assignee
        await self.notification_service.send_task_assignment(
            recipient=assignee,
            task=task,
            chapter=chapter
        )

        return task

    async def _calculate_workload_scores(
        self,
        members: List[User]
    ) -> Dict[UUID, float]:
        """Calculate workload score for each member."""
        scores = {}

        for member in members:
            # Count pending and in-progress tasks
            pending_count = await self._count_pending_tasks(member.id)
            in_progress_count = await self._count_in_progress_tasks(member.id)

            # Get completion rate
            completion_rate = await self._get_completion_rate(member.id)

            # Calculate score (lower is better)
            # Formula: pending * 2 + in_progress * 1 - completion_rate * 0.5
            score = (
                pending_count * 2.0 +
                in_progress_count * 1.0 -
                completion_rate * 0.5
            )

            scores[member.id] = score

        return scores

    async def reassign_task(
        self,
        task_id: UUID,
        new_assignee_id: UUID,
        user: User
    ) -> Task:
        """Reassign task to different team member."""
        task = await self._get_task(task_id)

        # Verify permission
        await self._verify_reassign_permission(task, user)

        # Update task
        old_assignee_id = task.assignee_id
        task.assignee_id = new_assignee_id
        task.reassignment_count += 1
        task.status = "ASSIGNED"
        task.started_at = None

        self.db.add(task)

        # Create audit log for reassignment
        await self._log_reassignment(
            task,
            old_assignee_id,
            new_assignee_id,
            user
        )

        await self.db.commit()

        # Notify old assignee (task removed)
        if old_assignee_id:
            old_assignee = await self._get_user(old_assignee_id)
            await self.notification_service.send_task_removed(
                recipient=old_assignee,
                task=task
            )

        # Notify new assignee
        new_assignee = await self._get_user(new_assignee_id)
        await self.notification_service.send_task_assignment(
            recipient=new_assignee,
            task=task,
            reason=f"Reassigned by {user.name}"
        )

        return task
```

---

### 4.3 Repository Pattern

```python
# Base repository with common CRUD operations
class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: UUID) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        query = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, data: Dict[str, Any]) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        instance = await self.get(id)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.flush()
        return instance

    async def delete(self, id: UUID) -> bool:
        instance = await self.get(id)
        if instance:
            await self.session.delete(instance)
            return True
        return False


# Specific repository implementations
class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get_with_storage_usage(self, id: UUID) -> Optional[Project]:
        """Get project with current storage usage."""
        query = (
            select(Project)
            .options(
                joinedload(Project.storage_usage),
                joinedload(Project.members),
                joinedload(Project.model_configs)
            )
            .where(Project.id == id)
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_user_projects(self, user_id: UUID) -> List[Project]:
        """Get all projects accessible by user."""
        query = (
            select(Project)
            .join(
                ProjectMember,
                Project.id == ProjectMember.project_id
            )
            .where(
                or_(
                    Project.team_lead_id == user_id,
                    ProjectMember.user_id == user_id
                )
            )
            .options(
                joinedload(Project.members),
                joinedload(Project.scripts)
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class ChapterRepository(BaseRepository[Chapter]):
    def __init__(self, session: AsyncSession):
        super().__init__(Chapter, session)

    async def get_with_panels(self, id: UUID) -> Optional[Chapter]:
        """Get chapter with storyboard panels."""
        query = (
            select(Chapter)
            .options(
                joinedload(Chapter.panels).joinedload(
                    StoryboardPanel.selected_image
                ),
                joinedload(Chapter.panels).joinedload(
                    StoryboardPanel.selected_audio
                )
            )
            .where(Chapter.id == id)
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_workflow_status(
        self,
        project_id: UUID,
        workflow_step: int
    ) -> List[Chapter]:
        """Get chapters at specific workflow step."""
        query = (
            select(Chapter)
            .where(
                Chapter.project_id == project_id,
                Chapter.workflow_step == workflow_step
            )
            .order_by(Chapter.chapter_number)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
```

---

## 5. WebSocket Handler Design

### 5.1 Connection Management

```python
class WebSocketConnectionManager:
    """Manages WebSocket connections with authentication and lifecycle."""

    def __init__(self, redis: Redis):
        self.redis = redis
        self.connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[UUID, Set[str]] = defaultdict(set)

    async def connect(
        self,
        websocket: WebSocket,
        token: str
    ) -> ConnectionContext:
        """Authenticate and establish WebSocket connection."""
        # Validate JWT token
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            user_id = UUID(payload["sub"])
        except jwt.InvalidTokenError as e:
            await websocket.close(code=4001, reason="Invalid token")
            raise WebSocketError("AUTH_INVALID_TOKEN")

        # Generate connection ID
        connection_id = str(uuid4())

        # Store connection
        self.connections[connection_id] = websocket
        self.user_connections[user_id].add(connection_id)

        # Store in Redis for cross-instance support
        await self.redis.hset(
            f"ws:connections:{connection_id}",
            mapping={
                "user_id": str(user_id),
                "established_at": datetime.utcnow().isoformat(),
                "last_ping": datetime.utcnow().isoformat()
            }
        )
        await self.redis.expire(
            f"ws:connections:{connection_id}",
            settings.websocket_connection_ttl
        )

        # Subscribe to user's channels
        await self.redis.psubscribe(
            f"ws:user:{user_id}:*",
            f"ws:project:*"  # Will be filtered by project membership
        )

        return ConnectionContext(
            connection_id=connection_id,
            user_id=user_id
        )

    async def disconnect(self, connection_id: UUID) -> None:
        """Clean up disconnected client."""
        connection_id = str(connection_id)

        if connection_id in self.connections:
            websocket = self.connections.pop(connection_id)
            await websocket.close()

        # Remove from Redis
        conn_data = await self.redis.hgetall(
            f"ws:connections:{connection_id}"
        )
        if conn_data:
            user_id = UUID(conn_data[b"user_id"].decode())
            self.user_connections[user_id].discard(connection_id)
            await self.redis.delete(f"ws:connections:{connection_id}")

    async def send_to_user(
        self,
        user_id: UUID,
        message: WebSocketMessage
    ) -> int:
        """Send message to all connections of a user."""
        sent_count = 0

        for connection_id in self.user_connections.get(user_id, set()):
            if connection_id in self.connections:
                try:
                    await self.connections[connection_id].send_json(
                        message.dict()
                    )
                    sent_count += 1
                except WebSocketDisconnect:
                    await self.disconnect(connection_id)

        return sent_count

    async def broadcast_to_project(
        self,
        project_id: UUID,
        message: WebSocketMessage
    ) -> None:
        """Broadcast message to all users in project."""
        await self.redis.publish(
            f"ws:project:{project_id}:notifications",
            json.dumps(message.dict())
        )

    async def handle_ping(self, connection_id: UUID) -> None:
        """Update last ping time."""
        await self.redis.hset(
            f"ws:connections:{connection_id}",
            "last_ping",
            datetime.utcnow().isoformat()
        )
```

### 5.2 Message Handlers

```python
class WebSocketMessageHandler:
    """Handles WebSocket message routing and processing."""

    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        generation_service: GenerationService,
        task_service: TaskService
    ):
        self.connection_manager = connection_manager
        self.generation_service = generation_service
        self.task_service = task_service

    async def handle_message(
        self,
        connection_id: UUID,
        message: dict
    ) -> None:
        """Route message to appropriate handler."""
        message_type = message.get("type")

        handlers = {
            "PING": self._handle_ping,
            "SUBSCRIBE_PROJECT": self._handle_subscribe_project,
            "UNSUBSCRIBE_PROJECT": self._handle_unsubscribe_project,
        }

        handler = handlers.get(message_type)
        if handler:
            await handler(connection_id, message)
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def _handle_ping(
        self,
        connection_id: UUID,
        message: dict
    ) -> None:
        """Respond to heartbeat ping."""
        await self.connection_manager.send_to_connection(
            connection_id,
            PongMessage(timestamp=datetime.utcnow())
        )

    async def _handle_subscribe_project(
        self,
        connection_id: UUID,
        message: dict
    ) -> None:
        """Subscribe to project notifications."""
        project_id = UUID(message["payload"]["project_id"])

        # Verify user has access to project
        user_id = await self._get_user_for_connection(connection_id)
        has_access = await self._verify_project_access(user_id, project_id)

        if not has_access:
            await self._send_error(
                connection_id,
                code="ACCESS_DENIED",
                message="No access to this project"
            )
            return

        # Subscribe to project channel
        await self.connection_manager.redis.sadd(
            f"ws:subscriptions:{connection_id}:projects",
            str(project_id)
        )

        await self._send_ack(
            connection_id,
            action="SUBSCRIBE_PROJECT",
            data={"project_id": str(project_id)}
        )

    async def send_progress_update(
        self,
        project_id: UUID,
        job_id: UUID,
        progress: ProgressData
    ) -> None:
        """Send progress update to all subscribed users in project."""
        message = ProgressUpdateMessage(
            job_id=job_id,
            job_type=progress.job_type,
            status=progress.status,
            progress=progress.progress,
            current_step=progress.current_step,
            total_steps=progress.total_steps,
            completed_steps=progress.completed_steps,
            estimated_time_remaining=progress.estimated_time_remaining,
            data=progress.data
        )

        # Get all connections subscribed to this project
        subscribed_connections = await self.connection_manager.redis.smembers(
            f"ws:subscriptions:projects:{project_id}"
        )

        for connection_id in subscribed_connections:
            try:
                await self.connection_manager.send_to_connection(
                    UUID(connection_id),
                    message
                )
            except WebSocketDisconnect:
                await self.connection_manager.disconnect(
                    UUID(connection_id)
                )
```

### 5.3 Message Schemas

```python
class WebSocketMessage(BaseModel):
    type: str
    payload: Dict[str, Any]


class ConnectionInitMessage(WebSocketMessage):
    type: str = "CONNECTION_INIT"

    class Payload(BaseModel):
        authorization: str


class ConnectionAckMessage(WebSocketMessage):
    type: str = "CONNECTION_ACK"

    class Payload(BaseModel):
        connectionId: str
        expiresIn: int


class ProgressUpdateMessage(WebSocketMessage):
    type: str = "PROGRESS_UPDATE"

    class Payload(BaseModel):
        jobId: UUID
        jobType: str
        status: str
        progress: float
        currentStep: Optional[str]
        totalSteps: int
        completedSteps: int
        estimatedTimeRemaining: Optional[int]
        data: Optional[Dict[str, Any]]


class TaskCompleteMessage(WebSocketMessage):
    type: str = "TASK_COMPLETE"

    class Payload(BaseModel):
        jobId: UUID
        jobType: str
        status: str = "COMPLETED"
        result: Dict[str, Any]


class ErrorMessage(WebSocketMessage):
    type: str = "ERROR"

    class Payload(BaseModel):
        code: str
        message: str
        jobId: Optional[UUID]
        retryable: bool
        retryAfter: Optional[int]
        suggestedAction: Optional[str]


class PingMessage(WebSocketMessage):
    type: str = "PING"
    timestamp: datetime


class PongMessage(WebSocketMessage):
    type: str = "PONG"
    timestamp: datetime
```

---

## 6. Async Task Queue Architecture (ARQ + Redis)

### 6.1 ARQ Configuration

```python
# arq_settings.py
from arq import func
from arq.worker import create_worker
from arq.connections import RedisSettings
from arq.functions import Function

# Redis settings
redis_settings = RedisSettings(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    db=settings.redis_db
)

# Worker settings
class WorkerSettings:
    functions = [
        generate_images,
        generate_audio,
        generate_video,
        compose_chapter,
        export_video,
        llm_generate_script,
        ai_generate_storyboard,
        ai_recommend_bgm
    ]

    redis_settings = redis_settings

    # Concurrency
    max_jobs = 10  # Max concurrent jobs per worker

    # Job timeouts
    job_timeout = 1800  # 30 minutes default

    # Retry settings
    retry_delay = 1.0  # Initial retry delay
    max_tries = 3  # Default max retries

    # Health check
    health_check_interval = 1  # seconds

    # Burst mode (for development)
    burst = False
```

### 6.2 Job Definitions

```python
# jobs/generation.py
from arq import Retry
from arq.worker import JobExecutionFailed

@func(retry=Retry(deadline=3600, max_attempts=3))
async def generate_images(
    ctx: Dict,
    job_id: str,
    panel_ids: List[str],
    batch_size: int,
    provider_ids: List[str],
    params: Dict
) -> Dict:
    """Generate images for storyboard panels."""
    from services.generation import GenerationService
    from db.session import get_db_session

    async with get_db_session() as db:
        service = GenerationService(db, ctx["redis"], ctx["arq_pool"])

        try:
            # Update job status
            await service.update_job_status(
                job_id=job_id,
                status="PROCESSING",
                current_step="Initializing generation..."
            )

            # Process each panel
            results = []
            total_panels = len(panel_ids)

            for idx, panel_id in enumerate(panel_ids):
                # Update progress
                progress = (idx + 1) / total_panels
                await service.update_job_status(
                    job_id=job_id,
                    progress=progress,
                    current_step=f"Generating panel {idx + 1}/{total_panels}"
                )

                # Generate images for panel with retry/failover
                panel_result = await service.generate_panel_images(
                    panel_id=UUID(panel_id),
                    batch_size=batch_size,
                    provider_ids=[UUID(pid) for pid in provider_ids],
                    params=params
                )

                results.append(panel_result)

                # Send progress via WebSocket
                await service.send_progress_update(
                    job_id=job_id,
                    project_id=panel_result.project_id,
                    progress=progress,
                    data={"generated_count": len(results)}
                )

            # Mark job complete
            await service.complete_job(job_id, results)

            return {
                "status": "COMPLETED",
                "results": results,
                "total_generated": len(results)
            }

        except Exception as e:
            await service.fail_job(job_id, str(e))
            raise JobExecutionFailed(f"Image generation failed: {str(e)}")


@func(retry=Retry(deadline=1800, max_attempts=3))
async def generate_audio(
    ctx: Dict,
    job_id: str,
    requests: List[Dict],
    config_id: Optional[str]
) -> Dict:
    """Generate TTS audio for panel dialogue."""
    from services.generation import GenerationService
    from db.session import get_db_session

    async with get_db_session() as db:
        service = GenerationService(db, ctx["redis"], ctx["arq_pool"])

        try:
            await service.update_job_status(
                job_id=job_id,
                status="PROCESSING"
            )

            results = []
            total_requests = len(requests)

            for idx, req in enumerate(requests):
                progress = (idx + 1) / total_requests
                await service.update_job_status(
                    job_id=job_id,
                    progress=progress,
                    current_step=f"Generating audio {idx + 1}/{total_requests}"
                )

                result = await service.generate_panel_audio(
                    panel_id=UUID(req["panel_id"]),
                    text=req["text"],
                    voice_id=req["voice_id"],
                    params=req
                )

                results.append(result)

                await service.send_progress_update(
                    job_id=job_id,
                    project_id=result.project_id,
                    progress=progress
                )

            await service.complete_job(job_id, results)

            return {"status": "COMPLETED", "results": results}

        except Exception as e:
            await service.fail_job(job_id, str(e))
            raise JobExecutionFailed(f"Audio generation failed: {str(e)}")


@func(retry=Retry(deadline=3600, max_attempts=3))
async def generate_video(
    ctx: Dict,
    job_id: str,
    panel_id: str,
    image_id: str,
    audio_id: str,
    params: Dict
) -> Dict:
    """Generate lip-sync video from image and audio."""
    from services.generation import GenerationService

    async with get_db_session() as db:
        service = GenerationService(db, ctx["redis"], ctx["arq_pool"])

        try:
            await service.update_job_status(
                job_id=job_id,
                status="PROCESSING",
                current_step="Analyzing audio phonemes..."
            )

            result = await service.generate_panel_video(
                panel_id=UUID(panel_id),
                image_id=UUID(image_id),
                audio_id=UUID(audio_id),
                params=params
            )

            await service.complete_job(job_id, result)

            return {"status": "COMPLETED", "result": result}

        except Exception as e:
            await service.fail_job(job_id, str(e))
            raise JobExecutionFailed(f"Video generation failed: {str(e)}")


@func(retry=Retry(deadline=7200, max_attempts=3))
async def compose_chapter(
    ctx: Dict,
    job_id: str,
    chapter_id: str,
    params: Dict
) -> Dict:
    """Compose final chapter video with BGM and subtitles."""
    from services.composition import CompositionService

    async with get_db_session() as db:
        service = CompositionService(db, ctx["redis"])

        try:
            await service.update_job_status(job_id, "PROCESSING")

            result = await service.assemble_chapter(
                chapter_id=UUID(chapter_id),
                params=params
            )

            await service.complete_job(job_id, result)

            return {"status": "COMPLETED", "result": result}

        except Exception as e:
            await service.fail_job(job_id, str(e))
            raise JobExecutionFailed(f"Chapter composition failed: {str(e)}")


@func(retry=Retry(deadline=3600, max_attempts=3))
async def export_video(
    ctx: Dict,
    job_id: str,
    chapter_id: str,
    format: str,
    preset: str,
    params: Dict
) -> Dict:
    """Export chapter video in specified format."""
    from services.export import ExportService

    async with get_db_session() as db:
        service = ExportService(db, ctx["redis"])

        try:
            await service.update_job_status(job_id, "PROCESSING")

            result = await service.render_export(
                chapter_id=UUID(chapter_id),
                format=format,
                preset=preset,
                params=params
            )

            await service.complete_job(job_id, result)

            return {"status": "COMPLETED", "result": result}

        except Exception as e:
            await service.fail_job(job_id, str(e))
            raise JobExecutionFailed(f"Export failed: {str(e)}")
```

### 6.3 Job Queue Dashboard

```python
# API endpoint for monitoring job queue
@router.get("/admin/jobs/queue")
async def get_queue_status(
    current_user: User = Depends(get_current_admin_user),
    redis: Redis = Depends(get_redis)
) -> QueueStatus:
    """Get ARQ job queue status."""
    from arq import create_pool
    from arq.connections import RedisSettings

    pool = await create_pool(RedisSettings())

    # Get queue info
    queued = await redis.zcard("arq:queue")
    in_progress = await redis.zcard("arq:in_progress")
    failed = await redis.zcard("arq:failed")

    # Get worker info
    workers = await redis.smembers("arq:workers")

    return QueueStatus(
        queued=queued,
        in_progress=in_progress,
        failed=failed,
        active_workers=len(workers),
        average_wait_time=await _calculate_avg_wait_time(redis)
    )
```

---

## 7. AI Provider Abstraction Layer

### 7.1 Provider Registry

```python
class ProviderRegistry:
    """Registry for AI model providers with factory pattern."""

    def __init__(self):
        self._providers: Dict[str, Type[BaseProvider]] = {}
        self._instances: Dict[str, BaseProvider] = {}

    def register(
        self,
        category: str,
        provider_id: str,
        provider_class: Type[BaseProvider]
    ) -> None:
        """Register a provider implementation."""
        key = f"{category}:{provider_id}"
        self._providers[key] = provider_class
        logger.info(f"Registered provider: {key}")

    def get_provider(
        self,
        category: str,
        provider_id: str,
        config: ModelConfig
    ) -> BaseProvider:
        """Get provider instance for given configuration."""
        key = f"{category}:{provider_id}"

        if key not in self._providers:
            raise ProviderNotFoundError(
                f"Provider not found: {key}. "
                f"Available: {list(self._providers.keys())}"
            )

        # Cache instance per config (credentials may differ)
        instance_key = f"{key}:{config.id}"
        if instance_key not in self._instances:
            self._instances[instance_key] = self._providers[key](config)

        return self._instances[instance_key]

    def get_all_providers(self, category: str) -> List[Dict[str, Any]]:
        """Get all registered providers for category."""
        providers = []

        for key, provider_class in self._providers.items():
            if key.startswith(f"{category}:"):
                providers.append({
                    "id": key.split(":")[1],
                    "name": provider_class.display_name,
                    "supported_features": provider_class.supported_features,
                    "config_schema": provider_class.config_schema
                })

        return providers


# Global registry instance
provider_registry = ProviderRegistry()
```

### 7.2 Base Provider Interface

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type


class ProviderCategory(str, Enum):
    LLM = "LLM"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    TTS = "TTS"
    BGM = "BGM"


class GenerationResult(BaseModel):
    """Standard result from any generation operation."""
    success: bool
    data: Any
    provider: str
    model: str
    latency_ms: int
    cost_credits: Optional[float]
    metadata: Dict[str, Any]


class BaseProvider(ABC):
    """Abstract base class for all AI providers."""

    category: ProviderCategory
    provider_id: str
    display_name: str

    # Features supported by this provider
    supported_features: List[str] = []

    # Configuration schema for UI
    config_schema: Dict[str, Any] = {}

    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_key = self._decrypt_credentials(config.credentials)
        self.base_url = config.credentials.get("base_url")
        self.model = config.default_model
        self.parameters = config.parameters or {}

    @abstractmethod
    async def validate_connection(self) -> ConnectionResult:
        """Test provider connectivity."""
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models from provider."""
        pass

    @abstractmethod
    async def get_quota_usage(self) -> QuotaInfo:
        """Get API quota/usage information."""
        pass

    def _decrypt_credentials(self, credentials: Dict) -> str:
        """Decrypt API key from stored credentials."""
        # Use application-level encryption
        from utils.crypto import decrypt_api_key
        return decrypt_api_key(credentials.get("api_key"))


# ============================================================================
# LLM PROVIDERS
# ============================================================================

class LLMProvider(BaseProvider, ABC):
    """Base class for LLM providers."""

    category = ProviderCategory.LLM

    @abstractmethod
    async def generate_script(
        self,
        prompt: str,
        tone: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs
    ) -> ScriptGenerationResult:
        """Generate script from prompt."""
        pass

    @abstractmethod
    async def generate_chapter_titles(
        self,
        script_content: str
    ) -> List[ChapterTitle]:
        """Generate chapter titles from script."""
        pass

    @abstractmethod
    async def generate_storyboard_prompts(
        self,
        scene: Scene
    ) -> List[PanelPrompt]:
        """Generate image prompts for storyboard panels."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""

    provider_id = "openai"
    display_name = "OpenAI (GPT-4)"
    supported_features = [
        "script_generation",
        "chapter_breakdown",
        "prompt_enhancement",
        "translation"
    ]
    config_schema = {
        "api_key": {"type": "string", "secret": True},
        "base_url": {"type": "string", "default": "https://api.openai.com/v1"},
        "default_model": {
            "type": "string",
            "options": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "max_tokens": {"type": "integer", "default": 4096},
        "temperature": {"type": "float", "default": 0.7, "min": 0, "max": 2}
    }

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def validate_connection(self) -> ConnectionResult:
        try:
            models = await self.client.models.list()
            return ConnectionResult(
                success=True,
                latency_ms=await self._measure_latency(),
                models_available=[m.id for m in models.data[:5]],
                message="Connection successful"
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                error=str(e),
                message=f"Connection failed: {str(e)}"
            )

    async def generate_script(
        self,
        prompt: str,
        tone: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs
    ) -> ScriptGenerationResult:
        """Generate script using GPT-4."""
        system_prompt = self._build_system_prompt(tone, style)
        user_prompt = self._build_user_prompt(prompt)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=self.parameters.get("max_tokens", 4096),
            temperature=self.parameters.get("temperature", 0.7)
        )

        content = response.choices[0].message.content

        # Parse structured response
        script_data = self._parse_script_response(content)

        return ScriptGenerationResult(
            success=True,
            data=script_data,
            provider=self.provider_id,
            model=self.model,
            latency_ms=response.usage.total_tokens,
            metadata={
                "tokens_used": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
        )

    async def list_models(self) -> List[ModelInfo]:
        response = await self.client.models.list()
        return [
            ModelInfo(id=m.id, name=m.id, context_window=self._get_context_window(m.id))
            for m in response.data
            if "gpt" in m.id.lower()
        ]


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    provider_id = "anthropic"
    display_name = "Anthropic (Claude)"
    supported_features = [
        "script_generation",
        "chapter_breakdown",
        "long_context"
    ]

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = AsyncAnthropic(api_key=self.api_key)

    async def generate_script(
        self,
        prompt: str,
        tone: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs
    ) -> ScriptGenerationResult:
        # Implementation similar to OpenAI provider
        pass


# ============================================================================
# IMAGE PROVIDERS
# ============================================================================

class ImageProvider(BaseProvider, ABC):
    """Base class for image generation providers."""

    category = ProviderCategory.IMAGE

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style_preset: Optional[str] = None,
        **kwargs
    ) -> ImageGenerationResult:
        """Generate image from prompt."""
        pass

    @abstractmethod
    async def generate_batch(
        self,
        prompt: str,
        batch_size: int = 4,
        **kwargs
    ) -> List[ImageGenerationResult]:
        """Generate multiple image variations."""
        pass


class StabilityAIProvider(ImageProvider):
    """Stable Diffusion provider implementation."""

    provider_id = "stability_ai"
    display_name = "Stability AI (Stable Diffusion)"
    supported_features = [
        "text_to_image",
        "image_variations",
        "style_presets",
        "inpainting"
    ]
    config_schema = {
        "api_key": {"type": "string", "secret": True},
        "base_url": {
            "type": "string",
            "default": "https://api.stability.ai/v1"
        },
        "default_model": {
            "type": "string",
            "options": ["sdxl-v1.0", "stable-diffusion-v2-1"]
        },
        "cfg_scale": {"type": "float", "default": 7.5, "min": 0, "max": 20},
        "steps": {"type": "integer", "default": 30, "min": 10, "max": 150}
    }

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style_preset: Optional[str] = None,
        **kwargs
    ) -> ImageGenerationResult:
        import aiohttp

        url = f"{self.base_url}/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": negative_prompt or "", "weight": -0.5}
            ],
            "cfg_scale": kwargs.get("cfg_scale", self.parameters.get("cfg_scale", 7.5)),
            "steps": kwargs.get("steps", self.parameters.get("steps", 30)),
            "width": 1920,
            "height": 1080,
            "samples": 1
        }

        if style_preset:
            payload["style_preset"] = style_preset

        start_time = datetime.utcnow()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise ProviderError(
                        f"Stability AI API error: {response.status}",
                        status_code=response.status
                    )

                result = await response.json()

        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Process response
        images = []
        for artifact in result.get("artifacts", []):
            image_url = await self._upload_to_storage(
                artifact["base64"],
                prefix="generated_images"
            )
            images.append({
                "url": image_url,
                "seed": artifact.get("seed")
            })

        return ImageGenerationResult(
            success=True,
            data=images,
            provider=self.provider_id,
            model=self.model,
            latency_ms=latency_ms,
            metadata={"style_preset": style_preset}
        )


class MidjourneyProvider(ImageProvider):
    """Midjourney provider (via proxy API)."""

    provider_id = "midjourney"
    display_name = "Midjourney"
    # Implementation for Midjourney API proxy


# ============================================================================
# VIDEO PROVIDERS
# ============================================================================

class VideoProvider(BaseProvider, ABC):
    """Base class for video generation providers."""

    category = ProviderCategory.VIDEO

    @abstractmethod
    async def generate_lip_sync_video(
        self,
        image_url: str,
        audio_url: str,
        **kwargs
    ) -> VideoGenerationResult:
        """Generate lip-sync video from image and audio."""
        pass


class HeyGenProvider(VideoProvider):
    """HeyGen video generation provider."""

    provider_id = "heygen"
    display_name = "HeyGen"
    supported_features = [
        "lip_sync",
        "avatar_animation",
        "voice_cloning"
    ]

    async def generate_lip_sync_video(
        self,
        image_url: str,
        audio_url: str,
        **kwargs
    ) -> VideoGenerationResult:
        # Implementation for HeyGen API
        pass


# ============================================================================
# TTS PROVIDERS
# ============================================================================

class TTSProvider(BaseProvider, ABC):
    """Base class for text-to-speech providers."""

    category = ProviderCategory.TTS

    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        voice_id: str,
        language: str = "zh-CN",
        speed: float = 1.0,
        emotion: Optional[str] = None,
        **kwargs
    ) -> AudioGenerationResult:
        """Generate speech from text."""
        pass


class AzureTTSProvider(TTSProvider):
    """Azure Cognitive Services TTS provider."""

    provider_id = "azure_tts"
    display_name = "Azure TTS"
    supported_features = [
        "neural_voices",
        "emotion_control",
        "speed_pitch_control",
        "ssml"
    ]

    async def synthesize_speech(
        self,
        text: str,
        voice_id: str,
        language: str = "zh-CN",
        speed: float = 1.0,
        emotion: Optional[str] = None,
        **kwargs
    ) -> AudioGenerationResult:
        # Implementation for Azure TTS API
        pass


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs premium TTS provider."""

    provider_id = "elevenlabs"
    display_name = "ElevenLabs"
    supported_features = [
        "ultra_realistic",
        "voice_cloning",
        "emotion_control"
    ]


# ============================================================================
# BGM PROVIDERS
# ============================================================================

class BGMProvider(BaseProvider, ABC):
    """Base class for background music generation providers."""

    category = ProviderCategory.BGM

    @abstractmethod
    async def generate_bgm(
        self,
        mood_tags: List[str],
        duration_sec: int,
        tempo: str = "moderate",
        instruments: Optional[List[str]] = None,
        **kwargs
    ) -> BGMGenerationResult:
        """Generate background music from mood specification."""
        pass


class AIBGMProvider(BGMProvider):
    """AI BGM generation provider (e.g., AIVA, Soundraw)."""

    provider_id = "aiva"
    display_name = "AIVA"
    supported_features = [
        "mood_based_generation",
        "custom_duration",
        "loop_seamless",
        "stem_separation"
    ]


# ============================================================================
# PROVIDER REGISTRATION
# ============================================================================

# Register all providers at application startup
def register_all_providers(registry: ProviderRegistry) -> None:
    """Register all available providers."""

    # LLM Providers
    registry.register(ProviderCategory.LLM, "openai", OpenAIProvider)
    registry.register(ProviderCategory.LLM, "anthropic", AnthropicProvider)

    # Image Providers
    registry.register(ProviderCategory.IMAGE, "stability_ai", StabilityAIProvider)
    registry.register(ProviderCategory.IMAGE, "midjourney", MidjourneyProvider)

    # Video Providers
    registry.register(ProviderCategory.VIDEO, "heygen", HeyGenProvider)

    # TTS Providers
    registry.register(ProviderCategory.TTS, "azure_tts", AzureTTSProvider)
    registry.register(ProviderCategory.TTS, "elevenlabs", ElevenLabsProvider)

    # BGM Providers
    registry.register(ProviderCategory.BGM, "aiva", AIBGMProvider)
```

### 7.3 Provider Health Monitoring

```python
class ProviderHealthMonitor:
    """Monitors AI provider health and manages circuit breakers."""

    def __init__(self, redis: Redis, db: AsyncSession):
        self.redis = redis
        self.db = db
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    async def check_all_providers(self) -> None:
        """Run health checks on all active providers."""
        query = select(ModelConfig).where(
            ModelConfig.is_active == True
        )
        result = await self.db.execute(query)
        configs = result.scalars().all()

        for config in configs:
            await self.check_provider(config)

    async def check_provider(self, config: ModelConfig) -> None:
        """Check single provider health."""
        try:
            provider = self._get_provider(config)
            result = await asyncio.wait_for(
                provider.validate_connection(),
                timeout=10.0
            )

            if result.success:
                await self._mark_healthy(config.id, result.latency_ms)
            else:
                await self._mark_degraded(config.id, result.error)

        except asyncio.TimeoutError:
            await self._mark_degraded(config.id, "Connection timeout")
        except Exception as e:
            await self._mark_degraded(config.id, str(e))

    async def _mark_healthy(
        self,
        config_id: UUID,
        latency_ms: int
    ) -> None:
        """Mark provider as healthy."""
        # Reset failure count
        await self.redis.delete(f"provider:{config_id}:failures")

        # Update database
        await self.db.execute(
            update(ModelConfig)
            .where(ModelConfig.id == config_id)
            .values(
                health_status="HEALTHY",
                last_health_check_at=datetime.utcnow(),
                parameters=ModelConfig.parameters.set_(
                    ModelConfig.parameters["last_latency_ms"].astext.cast(Integer),
                    latency_ms
                )
            )
        )
        await self.db.commit()

    async def _mark_degraded(
        self,
        config_id: UUID,
        error: str
    ) -> None:
        """Mark provider as degraded after failures."""
        failures = await self.redis.incr(f"provider:{config_id}:failures")
        await self.redis.expire(f"provider:{config_id}:failures", 300)

        status = "DEGRADED" if failures < 5 else "UNAVAILABLE"

        await self.db.execute(
            update(ModelConfig)
            .where(ModelConfig.id == config_id)
            .values(
                health_status=status,
                last_health_check_at=datetime.utcnow()
            )
        )
        await self.db.commit()

        if status == "UNAVAILABLE":
            logger.warning(f"Provider {config_id} marked as UNAVAILABLE")

    def get_circuit_breaker(self, provider_id: str) -> CircuitBreaker:
        """Get circuit breaker for provider."""
        if provider_id not in self.circuit_breakers:
            self.circuit_breakers[provider_id] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=ProviderError
            )

        return self.circuit_breakers[provider_id]
```

---

## 8. Security & Compliance

### 8.1 Authentication & Authorization

```python
# Security dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="AUTH_INVALID_TOKEN"
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await db.get(User, UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require ADMIN role."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="AUTH_INSUFFICIENT_PERMISSIONS"
        )
    return current_user


async def get_current_team_lead(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require TEAM_LEAD or ADMIN role."""
    if current_user.role not in ["ADMIN", "TEAM_LEAD"]:
        raise HTTPException(
            status_code=403,
            detail="AUTH_INSUFFICIENT_PERMISSIONS"
        )
    return current_user


async def verify_project_access(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Project:
    """Verify user has access to project."""
    if current_user.role == "ADMIN":
        return await db.get(Project, project_id)

    # Check project membership
    membership = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )

    if membership.scalar_one_or_none() is None:
        # Check if user is team lead of project
        project = await db.get(Project, project_id)
        if project and project.team_lead_id == current_user.id:
            return project

        raise HTTPException(
            status_code=403,
            detail="PROJECT_ACCESS_DENIED"
        )

    return await db.get(Project, project_id)
```

### 8.2 Data Encryption

```python
# Crypto utilities for sensitive data
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoService:
    """Handles encryption/decryption of sensitive data."""

    def __init__(self, master_key: str):
        self.master_key = master_key.encode()

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage."""
        salt = os.urandom(16)
        key = self._derive_key(salt)
        f = Fernet(key)

        encrypted = f.encrypt(api_key.encode())
        return base64.b64encode(salt + encrypted).decode()

    def decrypt_api_key(self, encrypted_data: str) -> str:
        """Decrypt API key for use."""
        data = base64.b64decode(encrypted_data.encode())
        salt = data[:16]
        encrypted = data[16:]

        key = self._derive_key(salt)
        f = Fernet(key)

        return f.decrypt(encrypted).decode()


# Usage in service layer
crypto_service = CryptoService(settings.encryption_master_key)


def encrypt_credentials(credentials: Dict[str, str]) -> Dict[str, str]:
    """Encrypt sensitive credentials before storage."""
    encrypted = {}
    for key, value in credentials.items():
        if key in ["api_key", "secret", "password"]:
            encrypted[key] = crypto_service.encrypt_api_key(value)
        else:
            encrypted[key] = value
    return encrypted


def decrypt_credentials(credentials: Dict[str, str]) -> Dict[str, str]:
    """Decrypt credentials for API use."""
    decrypted = {}
    for key, value in credentials.items():
        if key in ["api_key", "secret", "password"]:
            decrypted[key] = crypto_service.decrypt_api_key(value)
        else:
            decrypted[key] = value
    return decrypted
```

### 8.3 Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


# Rate limit configurations
@limiter.limit("10/minute")  # Login attempts
@router.post("/auth/login")
async def login(request: Request, credentials: LoginRequest):
    pass


@limiter.limit("100/minute")  # Standard API calls
@router.get("/projects")
async def list_projects(request: Request, current_user: User = Depends(get_current_user)):
    pass


@limiter.limit("30/minute")  # Generation requests
@router.post("/generation/images")
async def generate_images(
    request: Request,
    gen_request: GenerateImagesRequest,
    current_user: User = Depends(get_current_user)
):
    pass


# Project-based rate limiting for AI calls
async def check_project_quota(
    project_id: UUID,
    category: str,
    current_user: User = Depends(get_current_user)
):
    """Check if project has remaining API quota."""
    redis = get_redis()

    key = f"quota:{project_id}:{category}:{datetime.utcnow().date()}"
    usage = await redis.get(key)

    if usage and int(usage) >= settings.project_quota_limits.get(category, 1000):
        raise HTTPException(
            status_code=429,
            detail="PROJECT_QUOTA_EXCEEDED"
        )

    # Increment usage
    await redis.incr(key)
    await redis.expire(key, 86400)  # Reset at midnight
```

---

## 9. Performance Optimization

### 9.1 Caching Strategy

```python
class CacheService:
    """Redis-based caching for performance optimization."""

    def __init__(self, redis: Redis):
        self.redis = redis
        self.default_ttl = 3600  # 1 hour

    async def cache_script(
        self,
        script_id: UUID,
        script: ScriptSchema
    ) -> None:
        """Cache script with 1 hour TTL."""
        key = f"script:{script_id}"
        await self.redis.setex(
            key,
            self.default_ttl,
            json.dumps(script.dict())
        )

    async def get_cached_script(
        self,
        script_id: UUID
    ) -> Optional[ScriptSchema]:
        """Get cached script if available."""
        key = f"script:{script_id}"
        data = await self.redis.get(key)
        if data:
            return ScriptSchema.parse_raw(data)
        return None

    async def invalidate_script_cache(
        self,
        script_id: UUID
    ) -> None:
        """Invalidate script cache on update."""
        key = f"script:{script_id}"
        await self.redis.delete(key)

    async def cache_user_projects(
        self,
        user_id: UUID,
        projects: List[ProjectSchema],
        ttl: int = 300  # 5 minutes
    ) -> None:
        """Cache user's project list."""
        key = f"user:{user_id}:projects"
        await self.redis.setex(
            key,
            ttl,
            json.dumps([p.dict() for p in projects])
        )

    async def get_cached_user_projects(
        self,
        user_id: UUID
    ) -> Optional[List[ProjectSchema]]:
        """Get cached projects."""
        key = f"user:{user_id}:projects"
        data = await self.redis.get(key)
        if data:
            return [ProjectSchema.parse_raw(p) for p in json.loads(data)]
        return None


# Cache decorator for frequently accessed data
def cached(key_prefix: str, ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract ID from args/kwargs for cache key
            entity_id = kwargs.get('id') or (args[1] if len(args) > 1 else None)
            if not entity_id:
                return await func(*args, **kwargs)

            cache_key = f"{key_prefix}:{entity_id}"
            redis = get_redis()

            # Try cache
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            await redis.setex(
                cache_key,
                ttl,
                json.dumps(result.dict() if hasattr(result, 'dict') else result)
            )

            return result
        return wrapper
    return decorator


# Usage example
@cached("chapter", ttl=600)
async def get_chapter_with_panels(id: UUID) -> ChapterSchema:
    # Expensive database query
    pass
```

### 9.2 Database Optimization

```python
# Index recommendations for common queries
CREATE INDEX IF NOT EXISTS idx_chapters_workflow_status
ON chapters(project_id, workflow_step, status);

CREATE INDEX IF NOT EXISTS idx_tasks_assignment
ON tasks(assignee_id, status, priority);

CREATE INDEX IF NOT EXISTS idx_generated_assets_panel
ON generated_images(panel_id, is_selected);

CREATE INDEX IF NOT EXISTS idx_audit_logs_chapter_type
ON audit_logs(chapter_id, audit_type);

# Partial index for active records
CREATE INDEX IF NOT EXISTS idx_projects_active
ON projects(id, name) WHERE status = 'ACTIVE';

# JSONB index for metadata queries
CREATE INDEX IF NOT EXISTS idx_scripts_metadata
ON scripts USING GIN ((content->'metadata'));
```

### 9.3 Query Optimization

```python
# Use eager loading to avoid N+1 queries
async def get_project_with_details(project_id: UUID) -> Project:
    query = (
        select(Project)
        .options(
            joinedload(Project.members).joinedload(ProjectMember.user),
            joinedload(Project.model_configs),
            joinedload(Project.storage_usage),
            selectinload(Project.scripts).load_only(
                Script.id, Script.title, Script.status
            )
        )
        .where(Project.id == project_id)
    )
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()


# Use batch operations for bulk updates
async def update_panel_selections(
    selections: Dict[UUID, Dict[str, UUID]]
) -> None:
    """Batch update panel selections."""
    for panel_id, selection in selections.items():
        await db.execute(
            update(StoryboardPanel)
            .where(StoryboardPanel.id == panel_id)
            .values(
                selected_image_id=selection.get("image_id"),
                selected_audio_id=selection.get("audio_id"),
                updated_at=datetime.utcnow()
            )
        )
    await db.commit()
```

---

## 10. Remaining Concerns and Risks

### 10.1 Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| AI Provider API Changes | MEDIUM | Abstract provider layer with version pinning; contract tests |
| Large File Storage Costs | MEDIUM | Implement automatic cleanup policies; cold storage tier |
| Video Generation Latency | MEDIUM | Set proper expectations; async processing with progress updates |
| WebSocket Connection Limits | LOW | Horizontal scaling with Redis pub/sub; connection pooling |
| Database Growth | MEDIUM | Partitioning strategy for audit_logs; archive old data |

### 10.2 Compliance Considerations

| Consideration | Status | Action Required |
|---------------|--------|-----------------|
| Data Privacy (user data) | PENDING | Implement data retention policy; GDPR compliance if needed |
| Content Moderation | PENDING | Add content review workflow for generated content |
| API Credential Rotation | CONFIRMED | Automated rotation reminders; audit logging |
| Age Verification | N/A | Not required for this B2B system |

### 10.3 Operational Considerations

| Consideration | Recommendation |
|---------------|----------------|
| Monitoring | Set up Prometheus + Grafana for metrics; ELK for logs |
| Alerting | PagerDuty integration for critical alerts |
| Backup Strategy | Daily database backups; weekly full system backup |
| Disaster Recovery | Multi-region deployment consideration for production |
| Scaling | Horizontal scaling for stateless services; read replicas for database |

---

## 11. Development Roadmap

### Phase 1: Core Infrastructure (Weeks 1-4)
- [ ] Database schema setup
- [ ] Authentication service (JWT)
- [ ] User and project management
- [ ] Model configuration CRUD
- [ ] Basic ARQ worker setup

### Phase 2: Pipeline Core (Weeks 5-8)
- [ ] Script management with LLM integration
- [ ] Chapter breakdown auto-generation
- [ ] Storyboard generation
- [ ] Provider abstraction layer (LLM, Image)

### Phase 3: Generation Pipeline (Weeks 9-12)
- [ ] Image generation with retry/failover
- [ ] TTS audio generation
- [ ] Video lip-sync generation
- [ ] WebSocket progress updates

### Phase 4: Audit System (Weeks 13-14)
- [ ] First audit workflow
- [ ] Second audit workflow
- [ ] Rejection routing logic

### Phase 5: Composition & Export (Weeks 15-16)
- [ ] Smart composition (BGM, subtitles)
- [ ] Chapter assembly
- [ ] Video export in multiple formats

### Phase 6: Dashboard & Polish (Weeks 17-18)
- [ ] Role-specific dashboards
- [ ] Task management UI integration
- [ ] Performance optimization
- [ ] Security audit

---

## 12. Conclusion

### Final Architecture Assessment

The backend architecture for the AI Manga/Video Production Pipeline System is **COMPLETE** and **READY FOR DEVELOPMENT**. All previously identified gaps have been addressed:

1. **GAP-001 (Storage Quotas)**: Resolved with tier-based quotas and automatic cleanup policies
2. **GAP-002 (WebSocket)**: Resolved with complete WebSocket protocol specification
3. **GAP-003 (AI Fallback)**: Resolved with retry logic, circuit breakers, and manual failover
4. **GAP-004 (Task Assignment)**: Resolved with auto-assignment algorithm and workload balancing

### Key Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| JWT Authentication | Stateless, scalable, industry standard |
| ARQ + Redis for Async | Python-native, Redis integration, simple ops |
| Provider Abstraction | Hot-swappable AI providers per PRD requirement |
| PostgreSQL + JSONB | Structured data with flexible metadata storage |
| Repository Pattern | Clean separation of concerns, testable |
| WebSocket for Real-time | Efficient bidirectional communication for progress |

---

## BACKEND ARCHITECTURE: APPROVED FOR DEVELOPMENT

The technical solution fully addresses all PRD requirements. Development can proceed with confidence.

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-01 | Backend Architect | Initial architecture specification |
