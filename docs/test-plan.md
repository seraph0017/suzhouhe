# Test Plan - AI Manga/Video Production Pipeline System

**Document Version:** 1.0
**Date:** 2026-03-01
**Author:** QA Engineering Team
**Status:** DRAFT

---

## Table of Contents

1. [Test Strategy Overview](#1-test-strategy-overview)
2. [Test Environment](#2-test-environment)
3. [Test Data Preparation](#3-test-data-preparation)
4. [Authentication & Authorization Tests](#4-authentication--authorization-tests)
5. [Project Management Tests](#5-project-management-tests)
6. [8-Step Pipeline Workflow Tests](#6-8-step-pipeline-workflow-tests)
7. [Dual-Audit System Tests](#7-dual-audit-system-tests)
8. [Dashboard & Reports Tests](#8-dashboard--reports-tests)
9. [Model Configuration Tests](#9-model-configuration-tests)
10. [API Endpoint Tests](#10-api-endpoint-tests)
11. [Edge Cases & Error Scenarios](#11-edge-cases--error-scenarios)
12. [Performance Tests](#12-performance-tests)
13. [Security Tests](#13-security-tests)

---

## 1. Test Strategy Overview

### 1.1 Test Scope

| Module | Test Types | Priority |
|--------|-----------|----------|
| Authentication & Authorization | Unit, Integration, E2E | P0 |
| Project Management | Unit, Integration, API | P0 |
| Pipeline Workflow (8 Steps) | Integration, E2E, API | P0 |
| Dual-Audit System | Integration, E2E, API | P0 |
| Dashboard & Reports | Unit, Integration, UI | P1 |
| Model Configuration | Integration, API | P1 |
| API Endpoints | Unit, Integration | P0 |
| Edge Cases & Errors | Integration, E2E | P1 |
| Performance | Load, Stress | P2 |
| Security | Penetration, Validation | P0 |

### 1.2 Test Types Definition

| Test Type | Description | Tools |
|-----------|-------------|-------|
| **Unit Tests** | Test individual functions/components in isolation | pytest, Vitest |
| **Integration Tests** | Test module interactions | pytest + TestClient |
| **API Tests** | Test RESTful endpoints | pytest + httpx |
| **E2E Tests** | Test complete user workflows | Playwright |
| **UI Tests** | Test frontend components | Vitest + Testing Library |
| **Performance Tests** | Test response times, load capacity | locust, pytest-benchmark |
| **Security Tests** | Test auth, validation, injections | OWASP ZAP, custom scripts |

### 1.3 Risk Contingency

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI Provider API unavailable | High | Mock services, recorded responses |
| Database connection issues | High | Testcontainers, in-memory DB |
| Test data pollution | Medium | Transaction rollback, isolated test DBs |
| Flaky async tests | Medium | Proper async fixtures, timeouts |
| Rate limiting | Medium | Mock external APIs, adjust test timing |

---

## 2. Test Environment

### 2.1 Required Services

| Service | Version | Purpose | Test Configuration |
|---------|---------|---------|-------------------|
| PostgreSQL | 16 | Primary database | Test DB: `manga_test` |
| Redis | 7 | Cache, task queue | DB: 1 (test isolation) |
| MinIO/S3 | Latest | File storage | Bucket: `test-assets` |
| Mock AI Services | N/A | External API simulation | Local mock server |

### 2.2 Environment Variables

```bash
# Test Environment Configuration
TESTING=true
DATABASE_URL=postgresql://test:test@localhost:5432/manga_test
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=test-secret-key-for-testing-only
ACCESS_TOKEN_EXPIRE_MINUTES=5
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=test-access-key
MINIO_SECRET_KEY=test-secret-key
MINIO_BUCKET=test-assets

# Mock AI Provider URLs
MOCK_LLM_URL=http://localhost:8081/llm
MOCK_IMAGE_URL=http://localhost:8082/image
MOCK_VIDEO_URL=http://localhost:8083/video
MOCK_TTS_URL=http://localhost:8084/tts
```

---

## 3. Test Data Preparation

### 3.1 Test Users

| User | Email | Password | Role | Purpose |
|------|-------|----------|------|---------|
| Admin User | admin@test.com | TestPass123! | Admin | Admin operations |
| Team Lead | lead@test.com | TestPass123! | Team Lead | Lead operations |
| Team Member | member@test.com | TestPass123! | Team Member | Member operations |
| Inactive User | inactive@test.com | TestPass123! | Team Member | Test inactive account |

### 3.2 Test Projects

| Project | Name | Status | Team Lead | Purpose |
|---------|------|--------|-----------|---------|
| Project 1 | Test Manga A | in_progress | Team Lead | General workflow tests |
| Project 2 | Test Manga B | planning | Team Lead | Project CRUD tests |
| Project 3 | Archived Project | archived | Team Lead | Archive tests |

### 3.3 Fixtures Structure

```python
# conftest.py fixtures
- test_db()         # Database session with rollback
- test_client()     # TestClient with auth override
- admin_user()      # Admin user fixture
- team_lead_user()  # Team lead fixture
- team_member()     # Team member fixture
- test_project()    # Sample project fixture
- mock_ai_services() # Mock AI provider responses
```

---

## 4. Authentication & Authorization Tests

### 4.1 Login/Logout Functionality

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AUTH-001 | P0 | User registered | 1. POST /auth/login with valid credentials<br>2. Verify response contains access_token, refresh_token | 200 OK, tokens present, token_type="bearer" |
| AUTH-002 | P0 | User registered | 1. POST /auth/login with invalid email<br>2. Verify error response | 401 Unauthorized, detail="Incorrect email or password" |
| AUTH-003 | P0 | User registered | 1. POST /auth/login with invalid password<br>2. Verify error response | 401 Unauthorized, detail="Incorrect email or password" |
| AUTH-004 | P0 | User exists but inactive | 1. POST /auth/login with inactive user<br>2. Verify error response | 400 Bad Request, detail="Inactive user" |
| AUTH-005 | P0 | Valid tokens | 1. Login to get tokens<br>2. POST /auth/logout with access_token<br>3. Verify response | 200 OK, message="Successfully logged out" |
| AUTH-006 | P1 | No token provided | 1. POST /auth/logout without token<br>2. Verify response | 401 Unauthorized |
| AUTH-007 | P1 | Expired token | 1. Wait for token expiry<br>2. POST /auth/logout with expired token<br>3. Verify response | 401 Unauthorized, detail="Token expired" |

### 4.2 JWT Token Refresh

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AUTH-010 | P0 | Valid refresh token | 1. Login to get tokens<br>2. POST /auth/refresh with refresh_token<br>3. Verify new tokens | 200 OK, new access_token and refresh_token returned |
| AUTH-011 | P0 | Invalid refresh token | 1. POST /auth/refresh with malformed token<br>2. Verify response | 401 Unauthorized |
| AUTH-012 | P0 | Expired refresh token | 1. Wait for refresh token expiry<br>2. POST /auth/refresh with expired token<br>3. Verify response | 401 Unauthorized |
| AUTH-013 | P1 | Used refresh token | 1. Use refresh token twice<br>2. Verify second attempt | 401 Unauthorized (token rotation) |

### 4.3 Role-Based Access Control (API)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AUTH-020 | P0 | Admin user | 1. Login as admin<br>2. GET /users/ (list all users)<br>3. Verify response | 200 OK, returns all users |
| AUTH-021 | P0 | Team Lead user | 1. Login as Team Lead<br>2. GET /users/ (list all users)<br>3. Verify response | 403 Forbidden (admin only endpoint) |
| AUTH-022 | P0 | Team Member | 1. Login as Team Member<br>2. GET /users/<br>3. Verify response | 403 Forbidden |
| AUTH-023 | P0 | Team Lead user | 1. Login as Team Lead<br>2. POST /projects/ (create project)<br>3. Verify response | 200 OK, project created |
| AUTH-024 | P0 | Team Member | 1. Login as Team Member<br>2. POST /projects/ (create project)<br>3. Verify response | 403 Forbidden |
| AUTH-025 | P0 | Unauthenticated | 1. GET /projects/ without token<br>2. Verify response | 401 Unauthorized |

### 4.4 Permission Guards

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AUTH-030 | P0 | Team Member in Project A | 1. Login as member<br>2. GET /projects/{project_b_id}<br>3. Verify access | 403 Forbidden (no access to other projects) |
| AUTH-031 | P0 | Team Lead of Project A | 1. Login as lead<br>2. GET /projects/{own_project_id}<br>3. Verify access | 200 OK, project data returned |
| AUTH-032 | P0 | Team Member | 1. Login as member<br>2. DELETE /projects/{id}<br>3. Verify response | 403 Forbidden (admin only) |
| AUTH-033 | P1 | Frontend route guard | 1. Login as Team Member<br>2. Navigate to /admin/dashboard<br>3. Verify redirect | Redirect to /member/dashboard or 403 |

---

## 5. Project Management Tests

### 5.1 Project CRUD Operations

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| PROJ-001 | P0 | Team Lead logged in | 1. POST /projects/ with valid data<br>2. Verify project created | 200 OK, project returned with id, status="planning" |
| PROJ-002 | P0 | Team Lead logged in | 1. POST /projects/ with missing name<br>2. Verify validation | 422 Unprocessable Entity, validation error |
| PROJ-003 | P0 | Team Lead logged in | 1. POST /projects/ with name > 200 chars<br>2. Verify validation | 422 Unprocessable Entity |
| PROJ-004 | P0 | Project exists | 1. GET /projects/{id}<br>2. Verify project data | 200 OK, correct project data |
| PROJ-005 | P0 | Project doesn't exist | 1. GET /projects/{invalid_id}<br>2. Verify response | 404 Not Found |
| PROJ-006 | P0 | Project Lead logged in | 1. PUT /projects/{id} with new data<br>2. Verify update | 200 OK, updated fields reflected |
| PROJ-007 | P0 | Not project lead | 1. PUT /projects/{id} (not owner)<br>2. Verify response | 403 Forbidden |
| PROJ-008 | P0 | Admin logged in | 1. DELETE /projects/{id}<br>2. Verify deletion | 200 OK, project deleted |
| PROJ-009 | P0 | Non-admin | 1. DELETE /projects/{id} as non-admin<br>2. Verify response | 403 Forbidden |

### 5.2 Team Member Assignment

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| PROJ-010 | P0 | Project Lead logged in | 1. POST /projects/{id}/members with user_id, role<br>2. Verify member added | 200 OK, membership created |
| PROJ-011 | P0 | User already member | 1. POST /projects/{id}/members (same user twice)<br>2. Verify response | 400 Bad Request, "User is already a member" |
| PROJ-012 | P0 | Team Member (not lead) | 1. POST /projects/{id}/members<br>2. Verify response | 403 Forbidden |
| PROJ-013 | P0 | Project exists | 1. GET /projects/{id}/members<br>2. Verify member list | 200 OK, list of members with roles |

### 5.3 Project Status Workflow

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| PROJ-020 | P0 | Project in planning | 1. PUT /projects/{id} with status="in_progress"<br>2. Verify transition | 200 OK, status updated |
| PROJ-021 | P0 | Project in progress | 1. PUT /projects/{id} with status="completed"<br>2. Verify transition | 200 OK, status updated |
| PROJ-022 | P0 | Project in progress | 1. PUT /projects/{id} with status="archived"<br>2. Verify transition | 200 OK, status updated, project read-only |
| PROJ-023 | P1 | Project archived | 1. Attempt to create chapter in archived project<br>2. Verify rejection | 400 Bad Request, cannot modify archived project |

---

## 6. 8-Step Pipeline Workflow Tests

### 6.1 Step 1: Script Base (剧本基座)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| SCRIPT-001 | P0 | Project exists, Team Lead | 1. POST /scripts/ with LLM prompt<br>2. Wait for generation<br>3. Verify script created | 200 OK, script with scenes generated |
| SCRIPT-002 | P0 | Script file ready | 1. POST /scripts/upload with .txt file<br>2. Verify parsing | 200 OK, script content parsed |
| SCRIPT-003 | P0 | .docx file ready | 1. POST /scripts/upload with .docx<br>2. Verify parsing | 200 OK, document parsed correctly |
| SCRIPT-004 | P0 | File > 10MB | 1. POST /scripts/upload with large file<br>2. Verify rejection | 400 Bad Request, file too large |
| SCRIPT-005 | P0 | No scenes in script | 1. POST /scripts/validate with empty script<br>2. Verify validation | 422 Unprocessable Entity, at least 1 scene required |
| SCRIPT-006 | P0 | Script exists | 1. GET /scripts/{id}<br>2. Verify script data | 200 OK, script with scenes |
| SCRIPT-007 | P1 | Unsupported format | 1. POST /scripts/upload with .pdf<br>2. Verify rejection | 400 Bad Request, unsupported format |

### 6.2 Step 2: Script Refinement (剧本精调)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| SCRIPT-010 | P0 | Script exists (unlocked) | 1. PUT /scripts/{id} with edited dialogue<br>2. Verify update | 200 OK, changes saved, version created |
| SCRIPT-011 | P0 | Script has versions | 1. GET /scripts/{id}/versions<br>2. Verify history | 200 OK, list of versions with timestamps |
| SCRIPT-012 | P0 | Script exists | 1. POST /scripts/{id}/lock<br>2. Verify lock | 200 OK, script locked, Chapter Breakdown triggered |
| SCRIPT-013 | P0 | Script locked | 1. PUT /scripts/{id} (edit locked)<br>2. Verify rejection | 400 Bad Request, script is locked |
| SCRIPT-014 | P0 | Script locked | 1. POST /scripts/{id}/unlock (Team Lead)<br>2. Verify unlock | 200 OK, script unlocked |
| SCRIPT-015 | P1 | Version compare | 1. GET /scripts/{id}/compare?v1=x&v2=y<br>2. Verify diff | 200 OK, differences highlighted |

### 6.3 Step 3: Chapter Breakdown (章节拆解)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| CHAP-001 | P0 | Script locked | 1. Wait for auto-generation<br>2. GET /chapters?script_id={id}<br>3. Verify chapters | 200 OK, chapters with titles, summaries |
| CHAP-002 | P0 | Chapters generated | 1. PUT /chapters/{id} (edit title)<br>2. Verify update | 200 OK, chapter updated |
| CHAP-003 | P0 | Multiple chapters | 1. POST /chapters/{id}/split<br>2. Verify split | 200 OK, two chapters created |
| CHAP-004 | P0 | Adjacent chapters | 1. POST /chapters/merge with ids<br>2. Verify merge | 200 OK, single chapter created |
| CHAP-005 | P0 | Chapters exist | 1. PATCH /chapters/reorder with new order<br>2. Verify reordering | 200 OK, chapter numbers updated |
| CHAP-006 | P0 | Chapter duration > 15min | 1. Verify warning returned<br>2. Check response | 200 OK, includes warning about duration |
| CHAP-007 | P1 | No scenes in chapter | 1. Attempt to create empty chapter<br>2. Verify validation | 422 Unprocessable Entity |

### 6.4 Step 4: Storyboard Creation (分镜创作)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| STORY-001 | P0 | Chapter exists | 1. GET /storyboards?chapter_id={id}<br>2. Verify panels generated | 200 OK, storyboard panels with prompts |
| STORY-002 | P0 | Panel exists | 1. PUT /storyboards/{id} (edit prompt)<br>2. Verify update | 200 OK, panel updated |
| STORY-003 | P0 | Chapter panels | 1. POST /storyboards/ (add panel)<br>2. Verify creation | 200 OK, new panel added |
| STORY-004 | P0 | Panel exists | 1. DELETE /storyboards/{id}<br>2. Verify deletion | 200 OK, panel deleted |
| STORY-005 | P0 | Panels exist | 1. POST /storyboards/reorder<br>2. Verify sequence | 200 OK, sequence_numbers updated |
| STORY-006 | P0 | Storyboard complete | 1. POST /storyboards/lock<br>2. Verify lock, trigger Step 5 | 200 OK, storyboard locked, material generation started |
| STORY-007 | P0 | Storyboard locked | 1. Attempt to edit locked panel<br>2. Verify rejection | 400 Bad Request |

### 6.5 Step 5: Material Generation (素材生成)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| MAT-001 | P0 | Storyboard locked | 1. Wait for image generation<br>2. GET /assets?panel_id={id}&type=image<br>3. Verify images | 200 OK, 3-5 images per panel |
| MAT-002 | P0 | Images generated | 1. PUT /assets/{id}/select<br>2. Verify selection | 200 OK, image marked as selected |
| MAT-003 | P0 | Panel has no selected | 1. POST /assets/regenerate?panel_id={id}<br>2. Verify regeneration | 200 OK, new images generating |
| MAT-004 | P0 | TTS complete | 1. GET /assets?panel_id={id}&type=audio<br>2. Verify audio files | 200 OK, audio with duration metadata |
| MAT-005 | P0 | Audio generated | 1. PUT /assets/{audio_id}/select<br>2. Verify selection | 200 OK, audio marked selected |
| MAT-006 | P0 | Generation failed | 1. Check error handling<br>2. Verify retry option | 200 OK, retry mechanism available |
| MAT-007 | P1 | Batch generation | 1. POST /assets/batch-generate<br>2. Verify job queue | 202 Accepted, job_id returned |
| MAT-008 | P1 | Generation progress | 1. GET /assets/jobs/{job_id}/progress<br>2. Verify status | 200 OK, progress percentage |

### 6.6 Step 6: Video Generation (动态视频生成)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| VID-001 | P0 | Image+Audio selected | 1. POST /videos/generate<br>2. Wait for completion<br>3. Verify video | 200 OK, video with lip-sync |
| VID-002 | P0 | Video generated | 1. GET /videos/{id}<br>2. Verify metadata | 200 OK, duration, resolution |
| VID-003 | P0 | Lip-sync check | 1. Verify audio-video sync<br>2. Check timing | Video duration matches audio (±0.5s) |
| VID-004 | P0 | Generation failed | 1. Verify error handling<br>2. Check retry | 200 OK, retry available |
| VID-005 | P1 | Batch video gen | 1. POST /videos/batch-generate<br>2. Verify queue | 202 Accepted, job tracking |

### 6.7 Step 7: Smart Composition (智能合成)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| COMP-001 | P0 | Videos complete | 1. GET /composition/recommendations<br>2. Verify BGM suggestions | 200 OK, BGM tracks matching mood |
| COMP-002 | P0 | BGM selected | 1. PUT /composition/{chapter_id}/bgm<br>2. Verify assignment | 200 OK, BGM applied |
| COMP-003 | P0 | BGM playing | 1. Verify volume mixing<br>2. Check balance | Voice clearly dominant over BGM |
| COMP-004 | P0 | Subtitles needed | 1. PUT /composition/{id}/subtitles<br>2. Verify timing | 200 OK, subtitles timed to dialogue |
| COMP-005 | P1 | AI BGM gen | 1. POST /composition/generate-bgm<br>2. Verify generation | 200 OK, custom BGM created |

### 6.8 Step 8: Chapter Assembly (章节封装)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| ASSEM-001 | P0 | Composition complete | 1. POST /chapters/{id}/assemble<br>2. Wait for render<br>3. Verify output | 200 OK, final chapter video |
| ASSEM-002 | P0 | Chapter assembled | 1. GET /chapters/{id}/video<br>2. Verify format | 200 OK, MP4 H.264, 1080p |
| ASSEM-003 | P0 | Assembly complete | 1. Verify transitions applied<br>2. Check crossfade | Transitions present (0.5s crossfade) |
| ASSEM-004 | P0 | Assembly complete | 1. Verify audio normalization<br>2. Check LUFS | -16 LUFS target met |
| ASSEM-005 | P0 | Ready for audit | 1. Verify chapter status<br>2. Check second audit queue | Status="pending_second_audit" |

---

## 7. Dual-Audit System Tests

### 7.1 First Audit (Team Member)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AUDIT1-001 | P0 | Materials complete | 1. GET /audits/first/{chapter_id}<br>2. Verify audit interface data | 200 OK, all panels with assets |
| AUDIT1-002 | P0 | Reviewing assets | 1. PUT /audits/first/{id}/approve (panel)<br>2. Verify approval | 200 OK, panel approved |
| AUDIT1-003 | P0 | Asset issue | 1. PUT /audits/first/{id}/reject<br>2. Add comments | 200 OK, rejection recorded with reason |
| AUDIT1-004 | P0 | All approved | 1. POST /audits/first/{id}/submit (approve all)<br>2. Verify submission | 200 OK, status="approved", proceed to Step 8 |
| AUDIT1-005 | P0 | Issues found | 1. POST /audits/first/{id}/submit (with rejects)<br>2. Verify regeneration | 200 OK, stay in Step 5-7 |
| AUDIT1-006 | P0 | Audit submitted | 1. GET /audits/first/history<br>2. Verify audit log | 200 OK, audit record with timestamp |
| AUDIT1-007 | P1 | Partial approval | 1. Approve some panels, reject others<br>2. Submit | 200 OK, mixed status handled |

### 7.2 Second Audit (Team Lead)

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AUDIT2-001 | P0 | First audit approved | 1. GET /audits/second/{chapter_id}<br>2. Verify audit data | 200 OK, chapter video, audit trail |
| AUDIT2-002 | P0 | Viewing video | 1. Play chapter video<br>2. Add timestamped comment | 200 OK, comment attached to timestamp |
| AUDIT2-003 | P0 | Quality approved | 1. POST /audits/second/{id}/approve<br>2. Verify approval | 200 OK, status="published", chapter complete |
| AUDIT2-004 | P0 | Quality rejected | 1. POST /audits/second/{id}/reject with reason<br>2. Specify category | 200 OK, returned to appropriate step |
| AUDIT2-005 | P0 | Minor edit needed | 1. POST /audits/second/{id}/minor-edit<br>2. Verify no re-audit | 200 OK, team member can fix directly |
| AUDIT2-006 | P0 | Rejection routing | 1. Reject with "Lip-Sync Issues"<br>2. Verify routing | Chapter returns to Step 6 |
| AUDIT2-007 | P0 | Rejection routing | 1. Reject with "Subtitle Issues"<br>2. Verify routing | Chapter returns to Step 7, no re-audit |
| AUDIT2-008 | P1 | Audit statistics | 1. GET /audits/second/stats<br>2. Verify metrics | 200 OK, approval rate, avg time |

### 7.3 Rejection and Revision Flow

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| REV-001 | P0 | Chapter rejected | 1. Team Member receives notification<br>2. Views feedback | 200 OK, rejection reason displayed |
| REV-002 | P0 | Revision needed | 1. Navigate to returned step<br>2. Make corrections | Step accessible, previous selections preserved |
| REV-003 | P0 | Revision complete | 1. Resubmit for audit<br>2. Verify status | Status updated, returned to audit queue |
| REV-004 | P0 | Re-audit required | 1. Verify audit type<br>2. Check routing | Correct audit node based on issue type |
| REV-005 | P1 | Multiple rejections | 1. Reject same chapter 3 times<br>2. Verify escalation | 200 OK, notification to admin |

---

## 8. Dashboard & Reports Tests

### 8.1 Role-Specific Dashboards

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| DASH-001 | P0 | Admin logged in | 1. GET /admin/dashboard<br>2. Verify widgets | 200 OK, system health, users, projects |
| DASH-002 | P0 | Team Lead logged in | 1. GET /lead/dashboard<br>2. Verify widgets | 200 OK, pending reviews, team workload |
| DASH-003 | P0 | Team Member logged in | 1. GET /member/dashboard<br>2. Verify widgets | 200 OK, my tasks, current step |
| DASH-004 | P0 | Any role | 1. GET /dashboard/stats<br>2. Verify stats accuracy | 200 OK, correct counts |
| DASH-005 | P1 | Dashboard refresh | 1. Complete task<br>2. Refresh dashboard | Stats updated immediately |

### 8.2 Task Management

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| TASK-001 | P0 | Team Member logged in | 1. GET /tasks/my<br>2. Verify task list | 200 OK, tasks filtered by status |
| TASK-002 | P0 | Task exists | 1. POST /tasks/{id}/start<br>2. Verify status change | 200 OK, status="in_progress" |
| TASK-003 | P0 | Task complete | 1. POST /tasks/{id}/complete<br>2. Verify status | 200 OK, status="completed" |
| TASK-004 | P0 | Due date approaching | 1. Check task card<br>2. Verify indicator | Visual urgency indicator shown |
| TASK-005 | P1 | Task reassignment | 1. Team Lead reassigns task<br>2. New assignee notified | Task transferred, notification sent |

### 8.3 Progress Tracking

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| PROG-001 | P0 | Project in progress | 1. GET /projects/{id}/progress<br>2. Verify progress data | 200 OK, chapter completion status |
| PROG-002 | P0 | Multiple chapters | 1. View Gantt chart data<br>2. Verify timeline | 200 OK, chapter timeline |
| PROG-003 | P0 | Milestone reached | 1. Complete chapter<br>2. Verify milestone | Milestone marked complete |
| PROG-004 | P1 | Export report | 1. POST /reports/export<br>2. Verify PDF generation | 200 OK, report downloaded |

---

## 9. Model Configuration Tests

### 9.1 Provider CRUD

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| MODEL-001 | P0 | Admin logged in | 1. POST /models/ with LLM config<br>2. Verify creation | 200 OK, provider created |
| MODEL-002 | P0 | Provider exists | 1. GET /models/{id}<br>2. Verify config | 200 OK, provider details (api_key masked) |
| MODEL-003 | P0 | Provider exists | 1. PUT /models/{id} with new config<br>2. Verify update | 200 OK, config updated |
| MODEL-004 | P0 | Provider unused | 1. DELETE /models/{id}<br>2. Verify deletion | 200 OK, provider deleted |
| MODEL-005 | P0 | Non-admin | 1. POST /models/ as Team Lead<br>2. Verify response | 403 Forbidden |

### 9.2 Health Checks

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| MODEL-010 | P0 | Provider configured | 1. POST /models/{id}/test<br>2. Verify connection test | 200 OK, connection successful |
| MODEL-011 | P0 | Invalid credentials | 1. POST /models/{id}/test with bad key<br>2. Verify failure | 400 Bad Request, connection failed |
| MODEL-012 | P1 | Health check API | 1. GET /models/health<br>2. Verify all providers | 200 OK, health status per provider |

### 9.3 Hot-Swap Functionality

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| MODEL-020 | P0 | Multiple providers | 1. PATCH /models/default?type=llm&id={new}<br>2. Verify swap | 200 OK, default provider changed |
| MODEL-021 | P0 | Generation running | 1. Swap provider during generation<br>2. Verify handling | Current job completes, new jobs use new provider |
| MODEL-022 | P1 | Provider failover | 1. Simulate provider failure<br>2. Verify auto-failover | Fallback to secondary provider |

---

## 10. API Endpoint Tests

### 10.1 RESTful API Coverage

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| API-001 | P0 | All endpoints | 1. Test HTTP methods (GET, POST, PUT, DELETE)<br>2. Verify status codes | Correct status codes per REST conventions |
| API-002 | P0 | All POST endpoints | 1. Send invalid JSON<br>2. Verify handling | 400 Bad Request or 422 Unprocessable Entity |
| API-003 | P0 | Pagination endpoints | 1. GET with skip/limit params<br>2. Verify pagination | Correct subset returned with total count |
| API-004 | P0 | Resource not found | 1. GET /{invalid_id}<br>2. Verify response | 404 Not Found |
| API-005 | P0 | Concurrent requests | 1. Send 100 parallel requests<br>2. Verify handling | All requests handled correctly |

### 10.2 Error Handling

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| ERR-001 | P0 | Any endpoint | 1. Send malformed request<br>2. Verify error format | Consistent error response format |
| ERR-002 | P0 | Database error | 1. Simulate DB connection loss<br>2. Verify handling | 500 Internal Server Error with log |
| ERR-003 | P0 | Validation error | 1. Send invalid data<br>2. Verify error details | 422 with field-level validation errors |

### 10.3 Input Validation

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| VAL-001 | P0 | String fields | 1. Send XSS payload in string<br>2. Verify sanitization | Payload escaped or rejected |
| VAL-002 | P0 | Email fields | 1. Send invalid email format<br>2. Verify validation | 422 Unprocessable Entity |
| VAL-003 | P0 | Enum fields | 1. Send invalid enum value<br>2. Verify validation | 422 Unprocessable Entity |
| VAL-004 | P0 | Required fields | 1. Omit required field<br>2. Verify validation | 422 with field required error |

---

## 11. Edge Cases & Error Scenarios

### 11.1 Network Failures

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| NET-001 | P0 | Generation in progress | 1. Simulate network disconnect<br>2. Verify recovery | Job status preserved, can resume |
| NET-002 | P0 | WebSocket dropped | 1. Disconnect WebSocket<br>2. Verify reconnection | Auto-reconnect with backoff |
| NET-003 | P1 | Partial upload | 1. Cancel file upload mid-way<br>2. Verify cleanup | Partial file removed |

### 11.2 AI Provider Failures

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| AI-001 | P0 | Provider returns 500 | 1. Simulate provider error<br>2. Verify retry | 3 retries with exponential backoff |
| AI-002 | P0 | Rate limit hit | 1. Exceed provider quota<br>2. Verify handling | 429 with retry-after, queue paused |
| AI-003 | P0 | Provider timeout | 1. Simulate timeout<br>2. Verify handling | Timeout after 30s, retry or fail |
| AI-004 | P1 | All providers down | 1. Mark all providers unavailable<br>2. Verify user message | User informed, manual intervention required |

### 11.3 Rate Limiting

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| RATE-001 | P0 | Exceed API limit | 1. Send 100 requests/minute<br>2. Verify limiting | 429 Too Many Requests after limit |
| RATE-002 | P0 | Project quota | 1. Exceed project API quota<br>2. Verify blocking | Generation blocked until quota reset |
| RATE-003 | P1 | Rate limit headers | 1. Check response headers<br>2. Verify info | X-RateLimit-Remaining, X-RateLimit-Reset |

### 11.4 Storage Quotas

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| STORE-001 | P0 | Near quota limit | 1. Upload file at 90% usage<br>2. Verify warning | 200 OK, warning returned |
| STORE-002 | P0 | Quota exceeded | 1. Upload file exceeding quota<br>2. Verify rejection | 400 Bad Request, quota exceeded |
| STORE-003 | P0 | Large file upload | 1. Upload 2GB video<br>2. Verify handling | Accepted with progress tracking |

---

## 12. Performance Tests

### 12.1 Response Time Targets

| Case ID | Priority | Endpoint | Target | Measurement |
|---------|----------|----------|--------|-------------|
| PERF-001 | P1 | GET /dashboard/stats | P95 < 200ms | Load test 100 users |
| PERF-002 | P1 | GET /projects/{id} | P95 < 100ms | Load test 100 users |
| PERF-003 | P1 | POST /scripts/ (LLM) | P95 < 60s | Single request (includes AI time) |
| PERF-004 | P1 | GET /assets (batch) | P95 < 500ms | Load test 50 users |
| PERF-005 | P1 | WebSocket message | P95 < 100ms | Real-time update latency |

### 12.2 Load Testing

| Case ID | Priority | Scenario | Target | Measurement |
|---------|----------|----------|--------|-------------|
| PERF-010 | P1 | 100 concurrent users | System stable | Error rate < 1% |
| PERF-011 | P1 | 500 API calls/min | System stable | Response times within target |
| PERF-012 | P1 | 1000 asset generations | Queue handles load | No data loss, fair scheduling |
| PERF-013 | P2 | 24-hour endurance | No memory leaks | Stable resource usage |

---

## 13. Security Tests

### 13.1 Authentication Security

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| SEC-001 | P0 | Login endpoint | 1. Brute force 100 passwords<br>2. Verify lockout | Account locked after 5 attempts |
| SEC-002 | P0 | JWT tokens | 1. Tamper with token payload<br>2. Verify validation | 401 Unauthorized, signature invalid |
| SEC-003 | P0 | Token storage | 1. Check token in logs<br>2. Verify masking | Tokens never logged in plain text |

### 13.2 Authorization Security

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| SEC-010 | P0 | IDOR test | 1. Access other user's data with ID manipulation<br>2. Verify check | 403 Forbidden |
| SEC-011 | P0 | Privilege escalation | 1. Attempt to change own role<br>2. Verify rejection | 403 Forbidden |
| SEC-012 | P0 | Horizontal access | 1. Access another project's data<br>2. Verify isolation | 403 Forbidden |

### 13.3 Input Security

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| SEC-020 | P0 | SQL injection | 1. Send SQL injection payload<br>2. Verify handling | Payload escaped, no SQL error |
| SEC-021 | P0 | XSS prevention | 1. Send script in user input<br>2. Verify sanitization | Script escaped in output |
| SEC-022 | P0 | Path traversal | 1. Send ../../ in file paths<br>2. Verify rejection | 400 Bad Request |

### 13.4 Data Protection

| Case ID | Priority | Precondition | Steps | Expected Result |
|---------|----------|--------------|-------|-----------------|
| SEC-030 | P0 | API keys | 1. Check database encryption<br>2. Verify encryption | API keys encrypted (AES-256) |
| SEC-031 | P0 | Password storage | 1. Check password hash<br>2. Verify algorithm | bcrypt/argon2 with salt |
| SEC-032 | P0 | HTTPS enforcement | 1. Attempt HTTP request<br>2. Verify redirect | Redirect to HTTPS or rejected |

---

## Appendix A: Test Execution Priority

| Priority | Description | Execution Timing |
|----------|-------------|-----------------|
| **P0** | Critical path, compliance, security | Every commit, CI pipeline |
| **P1** | Important features, edge cases | Nightly build |
| **P2** | Performance, nice-to-have | Weekly, before releases |

---

## Appendix B: Test Data Cleanup

After each test run:
1. Rollback all database transactions
2. Clear Redis test cache
3. Remove generated test assets from storage
4. Reset mock service states

---

## Appendix C: Related Documents

- PRD: `/Users/xunan/Projects/suzhou/PRD.md`
- Backend Architecture: `/Users/xunan/Projects/suzhou/docs/backend-architecture-final.md`
- Frontend Architecture: `/Users/xunan/Projects/suzhou/docs/frontend-architecture-final.md`
