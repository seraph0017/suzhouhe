# Frontend Architecture Review
# AI Manga/Video Production Pipeline System

**Document Version:** 1.0
**Date:** 2026-03-01
**Reviewer:** Senior Frontend Architect
**Framework:** Vue 3 + TypeScript + Pinia + Element Plus

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Component Architecture](#2-component-architecture)
3. [State Management](#3-state-management)
4. [Routing Design](#4-routing-design)
5. [UI/UX Architecture](#5-uiux-architecture)
6. [Dashboard Implementation](#6-dashboard-implementation)
7. [Pipeline Workflow UI](#7-pipeline-workflow-ui)
8. [Audit Workflow UI](#8-audit-workflow-ui)
9. [Real-time Updates](#9-real-time-updates)
10. [Performance Optimization](#10-performance-optimization)
11. [Technical Risk Assessment](#11-technical-risk-assessment)
12. [Open Questions & Clarifications Needed](#12-open-questions--clarifications-needed)

---

## 1. Executive Summary

### 1.1 Architecture Overview

This document provides a comprehensive frontend architecture review for the AI Manga/Video Production Pipeline System. The system is a complex enterprise application with:

- **3 User Roles:** Admin, Team Lead, Team Member
- **8-Step Production Pipeline** with dual-audit gates
- **Multi-project support** with complete data isolation
- **Real-time task progress** tracking for long-running AI generation jobs
- **Rich media handling** (images, audio, video) with preview and comparison capabilities

### 1.2 Recommended Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Framework** | Vue 3.4+ (Composition API) | Reactive system, `<script setup>` syntax |
| **Language** | TypeScript 5.x | Type safety, better DX, auto-completion |
| **State Management** | Pinia 2.x | Vue 3 native, better TypeScript support than Vuex |
| **Routing** | Vue Router 4.x | Route guards, lazy loading, meta fields |
| **UI Framework** | Element Plus | Rich component library, enterprise-ready |
| **HTTP Client** | Axios | Interceptors, request cancellation, error handling |
| **Build Tool** | Vite 5.x | Fast HMR, optimized builds, code splitting |
| **Real-time** | WebSocket + EventSource | Dual strategy for different update patterns |
| **Media Handling** | Video.js + WaveSurfer.js | Professional media playback |
| **Testing** | Vitest + Vue Test Utils | Fast unit testing, Vue 3 compatible |

### 1.3 Key Architectural Decisions

1. **Feature-based folder structure** over type-based for better scalability
2. **Pinia stores per domain** (projects, pipeline, audits, users) for separation of concerns
3. **Route-based code splitting** with component lazy loading
4. **WebSocket for real-time** generation progress, polling as fallback
5. **Composable-based logic reuse** following Vue 3 best practices

---

## 2. Component Architecture

### 2.1 High-Level Component Hierarchy

```
App.vue
├── AppShell (layout container)
│   ├── AppHeader (global navigation, user menu, notifications)
│   ├── AppSidebar (project switcher, navigation menu)
│   └── AppMain (route view with transition)
│       └── [Role-Specific Dashboard / Pipeline Views]
│
├── Admin Views
│   ├── AdminDashboard
│   ├── UserManagement
│   ├── ProjectManagement
│   └── ModelConfigManagement
│
├── Team Lead Views
│   ├── TeamLeadDashboard
│   ├── ScriptEditor
│   ├── PipelineConfig
│   └── FinalAuditView
│
└── Team Member Views
    ├── TeamMemberDashboard
    ├── ChapterBreakdownView
    ├── StoryboardEditorView
    ├── MaterialSelectionView
    ├── FirstAuditView
    └── VideoCompositionView
```

### 2.2 Component Classification

#### Smart Components (Container/View Components)

These components connect to Pinia stores and handle business logic:

| Component | File Path | Responsibilities |
|-----------|-----------|------------------|
| `ScriptEditorView` | `views/script/ScriptEditorView.vue` | LLM generation, script editing, version compare, lock action |
| `ChapterBreakdownView` | `views/chapter/ChapterBreakdownView.vue` | Chapter list, merge/split, reordering, duration display |
| `StoryboardEditorView` | `views/storyboard/StoryboardEditorView.vue` | Panel grid, panel editor, preview mode, lock trigger |
| `MaterialSelectionView` | `views/material/MaterialSelectionView.vue` | Image gallery, TTS player, selection state, regenerate |
| `FirstAuditView` | `views/audit/FirstAuditView.vue` | Audit checklist, batch approve, rejection flow |
| `FinalAuditView` | `views/audit/FinalAuditView.vue` | Full video player, timestamp comments, rating, decision |
| `VideoCompositionView` | `views/composition/VideoCompositionView.vue` | Timeline view, BGM selector, subtitle editor, mix controls |

#### Dumb Components (Presentational Components)

Pure UI components receiving data via props and emitting events:

| Component | File Path | Props | Events | Slots |
|-----------|-----------|-------|--------|-------|
| `ScriptEditor` | `components/script/ScriptEditor.vue` | `content`, `readonly`, `changes` | `update:content`, `save`, `compare` | `toolbar`, `footer` |
| `ChapterCard` | `components/chapter/ChapterCard.vue` | `chapter`, `expanded`, `selectable` | `click`, `expand`, `select`, `action` | `header`, `actions` |
| `PanelCard` | `components/storyboard/PanelCard.vue` | `panel`, `selectedImage`, `status` | `select-image`, `regenerate`, `edit` | `thumbnail`, `metadata` |
| `ImageGrid` | `components/material/ImageGrid.vue` | `images`, `selectedId`, `loading` | `select`, `preview`, `regenerate` | `empty`, `loading` |
| `AudioPlayer` | `components/material/AudioPlayer.vue` | `audioUrl`, `waveform`, `duration` | `play`, `pause`, `seek` | - |
| `VideoPlayer` | `components/video/VideoPlayer.vue` | `videoUrl`, `thumbnail`, `subtitles` | `play`, `pause`, `timeupdate`, `comment` | `overlay`, `controls` |
| `AuditCard` | `components/audit/AuditCard.vue` | `audit`, `expandable` | `view`, `approve`, `reject` | `feedback`, `actions` |
| `TimelineView` | `components/composition/TimelineView.vue` | `tracks`, `zoom`, `playhead` | `seek`, `zoom`, `track-update` | `track-header`, `track-content` |
| `TaskProgress` | `components/common/TaskProgress.vue` | `steps`, `currentStep`, `status` | `navigate`, `help` | `step-icon`, `step-content` |
| `GenerationProgress` | `components/common/GenerationProgress.vue` | `jobId`, `status`, `progress`, `eta` | `cancel`, `retry` | - |

### 2.3 Reusable Base Components

Extend Element Plus components with project-specific styling:

| Component | Extends | Purpose |
|-----------|---------|---------|
| `BmButton` | `ElButton` | Consistent button styles, loading states |
| `BmCard` | `ElCard` | Standard card container with shadow variants |
| `BmDialog` | `ElDialog` | Full-screen and modal variants with standard actions |
| `BmForm` | `ElForm` | Form layout with validation feedback |
| `BmTable` | `ElTable` | Table with sorting, pagination, row actions |
| `BmEmpty` | `ElEmpty` | Custom empty states with illustrations |
| `BmLoading` | `ElSkeleton` | Content loading placeholders |

### 2.4 Smart/Dumb Component Pattern Example

```vue
<!-- Smart Component: MaterialSelectionView.vue -->
<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useMaterialStore } from '@/stores/material'
import { usePipelineStore } from '@/stores/pipeline'
import ImageGrid from '@/components/material/ImageGrid.vue'
import AudioPlayer from '@/components/material/AudioPlayer.vue'
import GenerationProgress from '@/components/common/GenerationProgress.vue'

const props = defineProps<{
  chapterId: string
}>()

const materialStore = useMaterialStore()
const pipelineStore = usePipelineStore()

const { images, audio, generationJobs, selectedImages } = storeToRefs(materialStore)

// Business logic: trigger generation
const handleRegenerate = async (panelId: string) => {
  await materialStore.generateImages({ panelId, batchSize: 4 })
}

const handleSelectImage = async (panelId: string, imageId: string) => {
  await materialStore.selectImage({ panelId, imageId })
  // Auto-advance if all panels have selections
  if (materialStore.allPanelsHaveSelections) {
    pipelineStore.enableNextStep()
  }
}
</script>

<template>
  <div class="material-selection-view">
    <GenerationProgress v-if="generationJobs.length" :jobs="generationJobs" />

    <ImageGrid
      v-for="panel in materialStore.panels"
      :key="panel.id"
      :images="images.get(panel.id)"
      :selected-id="selectedImages.get(panel.id)"
      @select="handleSelectImage(panel.id, $event)"
      @regenerate="handleRegenerate"
    />

    <AudioPlayer
      v-for="panel in materialStore.panels"
      :key="panel.id"
      :audio-url="audio.get(panel.id)?.url"
      @regenerate="handleRegenerateAudio"
    />
  </div>
</template>
```

```vue
<!-- Dumb Component: ImageGrid.vue -->
<script setup lang="ts">
import type { GeneratedImage } from '@/types/material'

defineProps<{
  images: GeneratedImage[]
  selectedId: string | null
  loading: boolean
  error: string | null
}>()

const emit = defineEmits<{
  select: [imageId: string]
  regenerate: []
  preview: [image: GeneratedImage]
}>()
</script>

<template>
  <div class="image-grid">
    <template v-if="loading">
      <ElSkeleton :rows="2" animated />
    </template>

    <template v-else-if="error">
      <BmEmpty :description="error">
        <ElButton type="primary" @click="$emit('regenerate')">
          Regenerate
        </ElButton>
      </BmEmpty>
    </template>

    <template v-else-if="images?.length">
      <div
        v-for="image in images"
        :key="image.id"
        class="image-card"
        :class="{ selected: image.id === selectedId }"
        @click="$emit('select', image.id)"
      >
        <ElImage :src="image.thumbnailUrl" fit="cover" lazy />
        <div class="image-actions">
          <ElButton size="small" @click.stop="$emit('preview', image)">
            Preview
          </ElButton>
        </div>
      </div>
    </template>
  </div>
</template>
```

---

## 3. State Management

### 3.1 Pinia Store Architecture

```
src/stores/
├── index.ts                 # Store registration
├── auth.ts                  # Authentication, user session
├── user.ts                  # User profile, preferences
├── project.ts               # Projects, members, permissions
├── script.ts                # Scripts, versions, lock state
├── chapter.ts               # Chapters, structure, ordering
├── storyboard.ts            # Storyboard panels, editing
├── material.ts              # Generated images, audio, selections
├── video.ts                 # Generated videos, lip-sync status
├── audit.ts                 # Audit records, decisions, feedback
├── pipeline.ts              # Pipeline state, step progression
├── generation.ts            # Generation jobs, progress, queue
├── notification.ts          # Toast notifications, alerts
└── dashboard.ts             # Dashboard widgets, metrics
```

### 3.2 Core Store Designs

#### Auth Store

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Role } from '@/types/user'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const role = computed(() => user.value?.role)
  const isAdmin = computed(() => role.value === 'ADMIN')
  const isTeamLead = computed(() => role.value === 'TEAM_LEAD')
  const isTeamMember = computed(() => role.value === 'TEAM_MEMBER')

  const hasProjectAccess = computed(() => (projectId: string) => {
    return user.value?.projects?.includes(projectId) ?? false
  })

  // Actions
  async function login(email: string, password: string) {
    loading.value = true
    try {
      const response = await authService.login(email, password)
      token.value = response.accessToken
      refreshToken.value = response.refreshToken
      user.value = response.user
      persistAuth(response)
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    await authService.logout(token.value!)
    token.value = null
    refreshToken.value = null
    user.value = null
    clearPersistedAuth()
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const response = await authService.refresh(refreshToken.value)
    token.value = response.accessToken
    refreshToken.value = response.refreshToken
  }

  function hasPermission(permission: string): boolean {
    // Role-based permission check
    const permissions: Record<Role, string[]> = {
      ADMIN: ['*'],
      TEAM_LEAD: ['script:*', 'audit:second', 'pipeline:configure'],
      TEAM_MEMBER: ['pipeline:execute', 'audit:first', 'material:select']
    }
    const userPerms = permissions[role.value!]
    return userPerms?.includes('*') || userPerms?.includes(permission) || false
  }

  return {
    // State
    user,
    token,
    refreshToken,
    loading,
    // Getters
    isAuthenticated,
    role,
    isAdmin,
    isTeamLead,
    isTeamMember,
    hasProjectAccess,
    // Actions
    login,
    logout,
    refreshAccessToken,
    hasPermission
  }
}, {
  persist: {
    key: 'auth',
    paths: ['token', 'refreshToken', 'user'],
    storage: localStorage
  }
})
```

#### Pipeline Store (Complex State Machine)

```typescript
// stores/pipeline.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PipelineState, PipelineStep, ChapterStatus } from '@/types/pipeline'

export const PIPELINE_STEPS: PipelineStep[] = [
  { id: 1, name: 'Script Base', key: 'script_base', icon: 'document' },
  { id: 2, name: 'Script Refine', key: 'script_refine', icon: 'edit' },
  { id: 3, name: 'Chapter Breakdown', key: 'chapter_breakdown', icon: 'grid' },
  { id: 4, name: 'Storyboard', key: 'storyboard', icon: 'grid' },
  { id: 5, name: 'Material Gen', key: 'material_gen', icon: 'image' },
  { id: 6, name: 'Video Gen', key: 'video_gen', icon: 'video' },
  { id: 7, name: 'Composition', key: 'composition', icon: 'film' },
  { id: 8, name: 'Chapter Assembly', key: 'chapter_assembly', icon: 'files' }
]

export const usePipelineStore = defineStore('pipeline', () => {
  // State
  const currentProjectId = ref<string | null>(null)
  const currentChapterId = ref<string | null>(null)
  const pipelineState = ref<PipelineState | null>(null)
  const stepStatuses = ref<Record<number, 'pending' | 'in-progress' | 'completed' | 'blocked'>>({})
  const isLocked = ref(false)
  const lockOwner = ref<string | null>(null)

  // Getters
  const currentStep = computed(() => {
    if (!pipelineState.value) return null
    return PIPELINE_STEPS.find(s => s.key === pipelineState.value!.currentStepKey)
  })

  const completedSteps = computed(() => {
    return PIPELINE_STEPS.filter(s => stepStatuses.value[s.id] === 'completed')
  })

  const nextAvailableStep = computed(() => {
    return PIPELINE_STEPS.find(s => stepStatuses.value[s.id] !== 'completed' && s.id > (currentStep.value?.id || 0))
  })

  const canProceed = computed(() => {
    // Check if current step requirements are met
    if (!currentStep.value) return false
    if (currentStep.value.id < 5) return isLocked.value // Steps 1-4 require lock
    return stepStatuses.value[currentStep.value.id] === 'completed'
  })

  const isAuditStep = computed(() => {
    if (!currentStep.value) return false
    return currentStep.value.id === 5 || currentStep.value.id === 8 // First audit after step 5, second after step 8
  })

  // Actions
  function initialize(projectId: string, chapterId: string) {
    currentProjectId.value = projectId
    currentChapterId.value = chapterId
    // Load pipeline state from API
  }

  function updateStepStatus(stepId: number, status: 'pending' | 'in-progress' | 'completed' | 'blocked') {
    stepStatuses.value[stepId] = status
  }

  function setLock(locked: boolean, owner?: string) {
    isLocked.value = locked
    lockOwner.value = owner || null
  }

  async function proceedToNextStep() {
    if (!canProceed.value || !nextAvailableStep.value) return

    updateStepStatus(currentStep.value!.id, 'completed')
    updateStepStatus(nextAvailableStep.value.id, 'in-progress')

    // API call to advance pipeline
    await pipelineService.advanceChapter(currentChapterId.value!, nextAvailableStep.value.key)
  }

  function canAccessStep(stepId: number, userRole: Role): boolean {
    const step = PIPELINE_STEPS.find(s => s.id === stepId)
    if (!step) return false

    // Steps 1-4: Team Lead only (script definition)
    if (stepId <= 4) return userRole === 'TEAM_LEAD' || userRole === 'ADMIN'

    // Steps 5-7: Team Member (material generation, first audit)
    if (stepId >= 5 && stepId <= 7) return userRole !== 'VIEWER'

    // Step 8 + Second Audit: Team Lead only
    if (stepId >= 8) return userRole === 'TEAM_LEAD' || userRole === 'ADMIN'

    return true
  }

  return {
    // State
    currentProjectId,
    currentChapterId,
    pipelineState,
    stepStatuses,
    isLocked,
    lockOwner,
    // Getters
    currentStep,
    completedSteps,
    nextAvailableStep,
    canProceed,
    isAuditStep,
    // Actions
    initialize,
    updateStepStatus,
    setLock,
    proceedToNextStep,
    canAccessStep
  }
})
```

#### Material Store (抽卡制 - Card Draw System)

```typescript
// stores/material.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GeneratedImage, GeneratedAudio, SelectionState } from '@/types/material'

export const useMaterialStore = defineStore('material', () => {
  // State
  const images = ref<Map<string, GeneratedImage[]>>(new Map()) // panelId -> images[]
  const audio = ref<Map<string, GeneratedAudio>>(new Map()) // panelId -> audio
  const selections = ref<Map<string, string>>(new Map()) // panelId -> selectedImageId
  const selectionNotes = ref<Map<string, string>>(new Map()) // panelId -> notes
  const generatingPanels = ref<Set<string>>(new Set())

  // Getters
  const allPanelsHaveSelections = computed(() => {
    const panelIds = Array.from(images.keys())
    return panelIds.every(id => selections.value.has(id))
  })

  const selectionProgress = computed(() => {
    const total = images.value.size
    const selected = Array.from(selections.value.values()).filter(Boolean).length
    return { total, selected, percentage: total > 0 ? (selected / total) * 100 : 0 }
  })

  const getImagesForPanel = (panelId: string) => images.value.get(panelId) || []
  const getSelectedImage = (panelId: string) => {
    const selectedId = selections.value.get(panelId)
    return images.value.get(panelId)?.find(img => img.id === selectedId)
  }

  // Actions
  function setImages(panelId: string, newImages: GeneratedImage[]) {
    images.value.set(panelId, newImages)
  }

  function selectImage({ panelId, imageId }: { panelId: string; imageId: string }) {
    selections.value.set(panelId, imageId)
    // Auto-save selection to backend
    materialService.saveSelection(panelId, imageId)
  }

  async function generateImages({ panelId, batchSize = 4 }: { panelId: string; batchSize?: number }) {
    if (generatingPanels.value.has(panelId)) return

    generatingPanels.value.add(panelId)
    try {
      const result = await materialService.generateImages(panelId, batchSize)
      setImages(panelId, result.images)
    } finally {
      generatingPanels.value.delete(panelId)
    }
  }

  function clearSelections(chapterId: string) {
    selections.value.clear()
    selectionNotes.value.clear()
  }

  return {
    // State
    images,
    audio,
    selections,
    selectionNotes,
    generatingPanels,
    // Getters
    allPanelsHaveSelections,
    selectionProgress,
    getImagesForPanel,
    getSelectedImage,
    // Actions
    setImages,
    selectImage,
    generateImages,
    clearSelections
  }
})
```

### 3.3 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW DIAGRAM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│   │   Component  │────>│   Pinia      │────>│   API        │              │
│   │   (View)     │     │   Store      │     │   Service    │              │
│   └──────────────┘     └──────────────┘     └──────────────┘              │
│         │                    │                    │                         │
│         │ props              │ state              │ request                 │
│         ▼                    ▼                    ▼                         │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│   │   Component  │<────│   Pinia      │<────│   API        │              │
│   │   (Present.) │ emit│   Store      │     │   Response   │              │
│   └──────────────┘     └──────────────┘     └──────────────┘              │
│                                                                             │
│   Events: update:xxx, click:xxx, submit                                    │
│   WebSocket: generation_progress, notification                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Caching Strategy

| Data Type | Cache Strategy | Invalidation |
|-----------|----------------|--------------|
| **User Profile** | Store in Pinia + localStorage | On logout, profile update |
| **Project List** | Pinia store, TTL 5 min | On project create/delete |
| **Script Content** | Pinia + optimistic updates | On version change |
| **Generated Images** | IndexedDB for thumbnails | On regeneration |
| **Generation Jobs** | Pinia, real-time sync | On job completion |
| **Audit History** | Pinia, refetch on action | On new audit submission |

---

## 4. Routing Design

### 4.1 Route Structure

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      { path: 'login', component: () => import('@/views/auth/LoginView.vue') },
      { path: 'register', component: () => import('@/views/auth/RegisterView.vue') },
    ]
  },
  {
    path: '/',
    component: () => import('@/layouts/AppShell.vue'),
    meta: { requiresAuth: true },
    children: [
      // Dashboard - redirects based on role
      {
        path: '',
        redirect: to => {
          const role = to.meta.role
          if (role === 'ADMIN') return '/admin/dashboard'
          if (role === 'TEAM_LEAD') return '/lead/dashboard'
          return '/member/dashboard'
        }
      },

      // Admin Routes
      {
        path: 'admin',
        meta: { requiresAuth: true, role: 'ADMIN' },
        children: [
          { path: 'dashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
          { path: 'users', component: () => import('@/views/admin/UserManagement.vue') },
          { path: 'projects', component: () => import('@/views/admin/ProjectManagement.vue') },
          { path: 'model-configs', component: () => import('@/views/admin/ModelConfigManagement.vue') },
          { path: 'audit-logs', component: () => import('@/views/admin/AuditLogs.vue') },
        ]
      },

      // Team Lead Routes
      {
        path: 'lead',
        meta: { requiresAuth: true, role: 'TEAM_LEAD' },
        children: [
          { path: 'dashboard', component: () => import('@/views/lead/TeamLeadDashboard.vue') },
          { path: 'scripts', component: () => import('@/views/lead/ScriptList.vue') },
          {
            path: 'scripts/:scriptId',
            component: () => import('@/views/lead/ScriptEditorView.vue'),
            meta: { requiresLock: true }
          },
          {
            path: 'pipeline/:chapterId',
            component: () => import('@/views/lead/PipelineConfigView.vue')
          },
          {
            path: 'audit/:chapterId/final',
            component: () => import('@/views/lead/FinalAuditView.vue'),
            meta: { auditType: 'SECOND' }
          }
        ]
      },

      // Team Member Routes
      {
        path: 'member',
        meta: { requiresAuth: true, role: 'TEAM_MEMBER' },
        children: [
          { path: 'dashboard', component: () => import('@/views/member/TeamMemberDashboard.vue') },
          { path: 'tasks', component: () => import('@/views/member/TaskList.vue') },
          {
            path: 'pipeline/:chapterId',
            component: () => import('@/views/member/PipelineWizard.vue'),
            children: [
              { path: 'chapter-breakdown', component: () => import('@/views/member/ChapterBreakdownView.vue') },
              { path: 'storyboard', component: () => import('@/views/member/StoryboardEditorView.vue') },
              { path: 'materials', component: () => import('@/views/member/MaterialSelectionView.vue') },
              { path: 'first-audit', component: () => import('@/views/member/FirstAuditView.vue') },
              { path: 'composition', component: () => import('@/views/member/VideoCompositionView.vue') },
            ]
          }
        ]
      },

      // Project Context Routes
      {
        path: 'projects/:projectId',
        component: () => import('@/layouts/ProjectLayout.vue'),
        meta: { requiresAuth: true, requiresProjectAccess: true },
        children: [
          { path: 'overview', component: () => import('@/views/project/ProjectOverview.vue') },
          { path: 'chapters', component: () => import('@/views/project/ChapterList.vue') },
          { path: 'members', component: () => import('@/views/project/ProjectMembers.vue') },
        ]
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/error/NotFound.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
```

### 4.2 Route Guards

```typescript
// router/guards.ts
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export async function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ path: '/auth/login', query: { redirect: to.fullPath } })
    return
  }

  // Check role-based access
  if (to.meta.role && authStore.role !== to.meta.role) {
    next({ path: '/403' })
    return
  }

  // Check project access
  if (to.meta.requiresProjectAccess && to.params.projectId) {
    const hasAccess = authStore.hasProjectAccess(to.params.projectId as string)
    if (!hasAccess) {
      next({ path: '/403' })
      return
    }
  }

  next()
}

export async function lockGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  if (to.meta.requiresLock) {
    const pipelineStore = usePipelineStore()
    if (!pipelineStore.isLocked) {
      // Show unlock dialog or redirect
      next({ name: 'ScriptList' })
      return
    }
  }
  next()
}
```

### 4.3 Lazy Loading Strategy

| Route Group | Chunk Name | Load Strategy |
|-------------|------------|---------------|
| Auth views | `auth` | Eager (small, critical) |
| Admin views | `admin` | Lazy (admin users only) |
| Team Lead views | `lead` | Lazy (role-based) |
| Team Member views | `member` | Lazy (role-based) |
| Pipeline wizard | `pipeline` | Prefetch on dashboard |
| Audit views | `audit` | Prefetch when task available |

---

## 5. UI/UX Architecture

### 5.1 Layout System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APP SHELL LAYOUT                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        APP HEADER                                    │   │
│  │  [Logo] [Project Switcher]              [Notifications] [User Menu] │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────┐  ┌──────────────────────────────────────────────────┐   │
│  │              │  │                                                  │   │
│  │   SIDEBAR    │  │                  MAIN CONTENT                    │   │
│  │              │  │                                                  │   │
│  │  - Nav Menu  │  │            Route View Component                  │   │
│  │  - Quick     │  │                                                  │   │
│  │    Actions   │  │                                                  │   │
│  │              │  │                                                  │   │
│  │  [Collapse]  │  │                                                  │   │
│  │              │  │                                                  │   │
│  └──────────────┘  └──────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Responsive Breakpoints

```typescript
// styles/breakpoints.ts
export const BREAKPOINTS = {
  MOBILE: 0,        // H5 mobile first
  TABLET: 768,      // Tablet portrait
  DESKTOP: 1024,    // Desktop small
  DESKTOP_LG: 1440, // Desktop large
  DESKTOP_XL: 1920  // Desktop extra large
}

// CSS custom properties
:root {
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --header-height: 56px;
  --content-max-width: 1400px;
}
```

### 5.3 Accessibility Considerations

| Requirement | Implementation | Priority |
|-------------|----------------|----------|
| **Keyboard Navigation** | Tab order, focus traps in dialogs, skip links | P0 |
| **ARIA Labels** | All interactive elements, icons without text | P0 |
| **Focus Indicators** | Custom focus styles matching design system | P0 |
| **Screen Reader** | Semantic HTML, proper heading hierarchy | P1 |
| **Color Contrast** | WCAG AA minimum (4.5:1 for text) | P1 |
| **Reduced Motion** | Respect `prefers-reduced-motion` | P2 |
| **Font Scaling** | Support browser font size up to 200% | P2 |

### 5.4 Design Tokens

```typescript
// styles/tokens.ts
export const tokens = {
  colors: {
    primary: {
      base: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb'
    },
    semantic: {
      success: '#22c55e',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6'
    },
    neutral: {
      50: '#fafafa',
      100: '#f4f4f5',
      900: '#18181b'
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem'
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem'
    }
  }
}
```

---

## 6. Dashboard Implementation

### 6.1 Role-Specific Dashboard Architecture

#### Dashboard Widget System

```typescript
// components/dashboard/types.ts
export interface DashboardWidget {
  id: string
  type: 'stat' | 'chart' | 'table' | 'list' | 'timeline'
  title: string
  data: () => Promise<any>
  refreshInterval?: number // ms, optional polling
  component: Component
  size: 'small' | 'medium' | 'large' | 'full'
  permissions?: string[]
}
```

#### Admin Dashboard Widgets

```vue
<!-- views/admin/AdminDashboard.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import SystemHealthWidget from '@/components/dashboard/SystemHealthWidget.vue'
import UserStatsWidget from '@/components/dashboard/UserStatsWidget.vue'
import ProjectOverviewTable from '@/components/dashboard/ProjectOverviewTable.vue'
import ApiQuotaWidget from '@/components/dashboard/ApiQuotaWidget.vue'
import RecentAuditLogs from '@/components/dashboard/RecentAuditLogs.vue'

const widgets = [
  { component: SystemHealthWidget, size: 'small', title: 'System Health' },
  { component: ApiQuotaWidget, size: 'small', title: 'API Quota' },
  { component: UserStatsWidget, size: 'small', title: 'Active Users' },
  { component: ProjectOverviewTable, size: 'full', title: 'Projects' },
  { component: RecentAuditLogs, size: 'full', title: 'Recent Activity' }
]
</script>

<template>
  <div class="admin-dashboard">
    <ElPageHeader title="Admin Dashboard" />

    <div class="widget-grid">
      <template v-for="widget in widgets" :key="widget.component.name">
        <ElCard
          :class="['widget', `widget-${widget.size}`]"
          :header="widget.title"
        >
          <component :is="widget.component" />
        </ElCard>
      </template>
    </div>
  </div>
</template>

<style scoped>
.widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}
.widget-full {
  grid-column: 1 / -1;
}
</style>
```

#### Team Lead Dashboard

```vue
<!-- views/lead/TeamLeadDashboard.vue -->
<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useDashboardStore } from '@/stores/dashboard'
import PendingReviewsWidget from '@/components/dashboard/PendingReviewsWidget.vue'
import TeamWorkloadWidget from '@/components/dashboard/TeamWorkloadWidget.vue'
import ProjectTimelineWidget from '@/components/dashboard/ProjectTimelineWidget.vue'
import QualityMetricsWidget from '@/components/dashboard/QualityMetricsWidget.vue'
import ScriptLibraryWidget from '@/components/dashboard/ScriptLibraryWidget.vue'

const dashboardStore = useDashboardStore()
const { pendingReviews, teamWorkload, projectTimeline, qualityMetrics } = storeToRefs(dashboardStore)
</script>

<template>
  <div class="lead-dashboard">
    <ElPageHeader title="Team Lead Dashboard">
      <template #extra>
        <ElButton type="primary" @click="$router.push('/lead/scripts/new')">
          New Script
        </ElButton>
      </template>
    </ElPageHeader>

    <div class="dashboard-grid">
      <!-- Top Row: Key Metrics -->
      <div class="grid-col-2">
        <PendingReviewsWidget :items="pendingReviews" />
        <TeamWorkloadWidget :workload="teamWorkload" />
      </div>

      <!-- Middle: Timeline -->
      <div class="grid-full">
        <ProjectTimelineWidget :timeline="projectTimeline" />
      </div>

      <!-- Bottom: Quality Metrics -->
      <div class="grid-full">
        <QualityMetricsWidget :metrics="qualityMetrics" />
      </div>
    </div>
  </div>
</template>
```

#### Team Member Dashboard

```vue
<!-- views/member/TeamMemberDashboard.vue -->
<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useDashboardStore } from '@/stores/dashboard'
import CurrentTaskWidget from '@/components/dashboard/CurrentTaskWidget.vue'
import UpcomingTasksWidget from '@/components/dashboard/UpcomingTasksWidget.vue'
import TaskPipelineWidget from '@/components/dashboard/TaskPipelineWidget.vue'
import MyProgressWidget from '@/components/dashboard/MyProgressWidget.vue'

const dashboardStore = useDashboardStore()
const { currentTask, upcomingTasks, myProgress } = storeToRefs(dashboardStore)

const startTask = (task: any) => {
  // Navigate to pipeline wizard at appropriate step
}
</script>

<template>
  <div class="member-dashboard">
    <ElPageHeader title="My Tasks" />

    <div class="dashboard-grid">
      <!-- Current Task (Prominent) -->
      <div class="grid-full">
        <CurrentTaskWidget
          v-if="currentTask"
          :task="currentTask"
          @start="startTask"
        />
        <ElEmpty v-else description="No active task. Pick one from upcoming!" />
      </div>

      <!-- Task Pipeline Visualization -->
      <div class="grid-full">
        <TaskPipelineWidget :steps="currentTask?.pipelineSteps" />
      </div>

      <!-- Side by Side: Upcoming + Progress -->
      <div class="grid-col-2">
        <UpcomingTasksWidget :tasks="upcomingTasks" />
        <MyProgressWidget :progress="myProgress" />
      </div>
    </div>
  </div>
</template>
```

### 6.2 Widget Architecture

```typescript
// composables/useWidget.ts
import { ref, onMounted, onUnmounted } from 'vue'
import type { DashboardWidget } from '@/components/dashboard/types'

export function useWidget(widget: DashboardWidget) {
  const data = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  let refreshTimer: number | null = null

  async function fetchData() {
    loading.value = true
    error.value = null
    try {
      data.value = await widget.data()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load data'
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    fetchData()
    if (widget.refreshInterval) {
      refreshTimer = window.setInterval(fetchData, widget.refreshInterval)
    }
  })

  onUnmounted(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
  })

  return {
    data,
    loading,
    error,
    refresh: fetchData
  }
}
```

---

## 7. Pipeline Workflow UI

### 7.1 Step-by-Step Wizard Design

```vue
<!-- components/pipeline/PipelineWizard.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { PIPELINE_STEPS } from '@/stores/pipeline'
import { usePipelineStore } from '@/stores/pipeline'
import StepIndicator from './StepIndicator.vue'
import StepContent from './StepContent.vue'

const props = defineProps<{
  chapterId: string
  initialStep?: number
}>()

const pipelineStore = usePipelineStore()
const currentStep = computed(() => pipelineStore.currentStep)
const completedSteps = computed(() => pipelineStore.completedSteps)

const canNavigateTo = (stepId: number) => {
  // Can navigate to completed steps or current step
  return stepId <= currentStep.value!.id + 1
}
</script>

<template>
  <div class="pipeline-wizard">
    <!-- Step Indicator (Top) -->
    <StepIndicator
      :steps="PIPELINE_STEPS"
      :current-step="currentStep?.id || 0"
      :completed-steps="completedSteps.map(s => s.id)"
      @navigate="id => canNavigateTo(id) && pipelineStore.navigateTo(id)"
    />

    <!-- Step Content Area -->
    <div class="step-content">
      <StepContent :step="currentStep" :chapter-id="chapterId" />
    </div>

    <!-- Navigation Footer -->
    <div class="wizard-footer">
      <ElButton
        :disabled="!currentStep || currentStep.id <= 1"
        @click="pipelineStore.previousStep()"
      >
        Previous
      </ElButton>

      <ElButton
        type="primary"
        :disabled="!pipelineStore.canProceed"
        @click="pipelineStore.nextStep()"
      >
        {{ currentStep?.id === 8 ? 'Complete' : 'Next Step' }}
      </ElButton>
    </div>
  </div>
</template>
```

### 7.2 Progress Tracking Component

```vue
<!-- components/pipeline/StepIndicator.vue -->
<script setup lang="ts">
import type { PipelineStep } from '@/types/pipeline'

defineProps<{
  steps: PipelineStep[]
  currentStep: number
  completedSteps: number[]
}>()

const emit = defineEmits<{
  navigate: [stepId: number]
}>()

const getStepStatus = (stepId: number) => {
  if (completedSteps.includes(stepId)) return 'completed'
  if (stepId === currentStep) return 'active'
  if (stepId < currentStep) return 'completed'
  return 'pending'
}
</script>

<template>
  <div class="step-indicator">
    <div
      v-for="step in steps"
      :key="step.id"
      class="step-item"
      :class="getStepStatus(step.id)"
      @click="emit('navigate', step.id)"
    >
      <div class="step-connector" />

      <div class="step-circle">
        <ElIcon v-if="getStepStatus(step.id) === 'completed'">
          <Check />
        </ElIcon>
        <span v-else>{{ step.id }}</span>
      </div>

      <div class="step-label">{{ step.name }}</div>

      <!-- Audit Badge -->
      <span v-if="[5, 8].includes(step.id)" class="audit-badge">
        {{ step.id === 5 ? '1st Audit' : '2nd Audit' }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.step-indicator {
  display: flex;
  align-items: flex-start;
  padding: 2rem 1rem;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.step-item:hover:not(.pending) {
  opacity: 0.8;
}

.step-item.active {
  opacity: 1;
}

.step-item.completed {
  opacity: 1;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.step-item.completed .step-circle {
  background: var(--el-color-success);
}

.step-label {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  text-align: center;
}

.audit-badge {
  font-size: 0.75rem;
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  margin-top: 0.25rem;
}
</style>
```

### 7.3 State Synchronization

```typescript
// composables/usePipelineSync.ts
import { onMounted, onUnmounted } from 'vue'
import { usePipelineStore } from '@/stores/pipeline'
import { useWebSocket } from './useWebSocket'

export function usePipelineSync(chapterId: string) {
  const pipelineStore = usePipelineStore()

  const { connect, disconnect, lastMessage } = useWebSocket(
    `/ws/pipeline/${chapterId}`
  )

  onMounted(() => {
    connect()
    // Initialize from API
    pipelineStore.initialize(chapterId)
  })

  onUnmounted(() => {
    disconnect()
  })

  // Handle WebSocket updates
  watch(lastMessage, (message) => {
    if (!message) return

    const { type, payload } = JSON.parse(message.data)

    switch (type) {
      case 'STEP_UPDATE':
        pipelineStore.updateStepStatus(payload.stepId, payload.status)
        break
      case 'LOCK_CHANGED':
        pipelineStore.setLock(payload.locked, payload.owner)
        break
      case 'GENERATION_PROGRESS':
        // Update generation job state
        break
    }
  })

  return {
    syncStatus: pipelineStore.syncStatus
  }
}
```

---

## 8. Audit Workflow UI

### 8.1 Card-Based Selection Interface (抽卡制)

```vue
<!-- components/audit/CardDrawSelection.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { StoryboardPanel, GeneratedImage } from '@/types'
import ImageCompare from '@/components/material/ImageCompare.vue'

const props = defineProps<{
  panels: StoryboardPanel[]
  images: Map<string, GeneratedImage[]>
  selections: Map<string, string>
}>()

const emit = defineEmits<{
  select: [panelId: string, imageId: string]
  regenerate: [panelId: string]
  approve: [panelId: string]
}>()

const previewMode = ref<'single' | 'slideshow'>('single')
const currentPreviewIndex = ref(0)

const allApproved = computed(() => {
  return props.panels.every(p => emit('approve', p.id))
})
</script>

<template>
  <div class="card-draw-selection">
    <!-- Toolbar -->
    <div class="selection-toolbar">
      <ElButtonGroup>
        <ElButton :type="previewMode === 'single' ? 'primary' : 'default'">
          Grid View
        </ElButton>
        <ElButton :type="previewMode === 'slideshow' ? 'primary' : 'default'">
          Slideshow
        </ElButton>
      </ElButtonGroup>

      <ElButton type="success" :disabled="!allApproved">
        Approve All & Proceed
      </ElButton>
    </div>

    <!-- Panel Cards -->
    <div v-for="panel in panels" :key="panel.id" class="panel-card">
      <div class="panel-header">
        <span class="panel-number">Panel {{ panel.sequenceNumber }}</span>
        <span class="panel-dialogue">{{ panel.dialogue }}</span>
      </div>

      <!-- Image Options (抽卡 options) -->
      <div class="image-options">
        <div
          v-for="image in images.get(panel.id)"
          :key="image.id"
          class="image-option"
          :class="{ selected: selections.get(panel.id) === image.id }"
          @click="emit('select', panel.id, image.id)"
        >
          <ElImage :src="image.url" fit="cover" lazy />
          <div class="image-overlay">
            <ElTag v-if="selections.get(panel.id) === image.id" type="success">
              Selected
            </ElTag>
          </div>
        </div>

        <!-- Regenerate Option -->
        <div class="image-option regenerate" @click="emit('regenerate', panel.id)">
          <ElIcon :size="32"><Refresh /></ElIcon>
          <span>Regenerate</span>
        </div>
      </div>
    </div>
  </div>
</template>
```

### 8.2 First Audit Interface

```vue
<!-- views/audit/FirstAuditView.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuditStore } from '@/stores/audit'
import { useMaterialStore } from '@/stores/material'
import AuditChecklist from '@/components/audit/AuditChecklist.vue'
import SideBySideCompare from '@/components/audit/SideBySideCompare.vue'

const auditStore = useAuditStore()
const materialStore = useMaterialStore()

const { panels } = storeToRefs(materialStore)

// Checklist state
const checklist = ref([
  { key: 'images_selected', label: 'All panels have selected images', checked: false },
  { key: 'style_consistent', label: 'Image style is consistent', checked: false },
  { key: 'character_consistent', label: 'Character appearance consistent', checked: false },
  { key: 'audio_matches', label: 'Audio matches dialogue timing', checked: false },
  { key: 'voice_tone', label: 'Voice tone matches scene emotion', checked: false },
  { key: 'no_artifacts', label: 'No audio artifacts or clipping', checked: false }
])

const canSubmit = computed(() => {
  return checklist.value.every(item => item.checked)
})

const handleSubmit = (decision: 'APPROVE' | 'REJECT') => {
  auditStore.submitFirstAudit({
    decision,
    checklist: checklist.value,
    comments: decision === 'REJECT' ? '' : undefined
  })
}
</script>

<template>
  <div class="first-audit-view">
    <ElPageHeader title="First Audit">
      <template #description>
        Review all generated materials before proceeding to video generation
      </template>
    </ElPageHeader>

    <div class="audit-layout">
      <!-- Left: Materials Review -->
      <div class="materials-section">
        <SideBySideCompare
          v-for="panel in panels"
          :key="panel.id"
          :panel="panel"
          :selected-image="materialStore.getSelectedImage(panel.id)"
          :audio="materialStore.audio.get(panel.id)"
        />
      </div>

      <!-- Right: Audit Form -->
      <div class="audit-form-section">
        <ElCard header="Audit Checklist">
          <AuditChecklist v-model="checklist" />

          <ElDivider />

          <ElButton
            type="success"
            :disabled="!canSubmit"
            @click="handleSubmit('APPROVE')"
          >
            Approve & Proceed
          </ElButton>

          <ElButton
            type="warning"
            @click="handleSubmit('REJECT')"
          >
            Request Changes
          </ElButton>
        </ElCard>
      </div>
    </div>
  </div>
</template>
```

### 8.3 Second Audit (Final Review) Interface

```vue
<!-- views/lead/FinalAuditView.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import TimestampComment from '@/components/audit/TimestampComment.vue'

const props = defineProps<{
  chapterId: string
}>()

const videoUrl = ref('')
const isPlaying = ref(false)
const currentTime = ref(0)
const rating = ref(5)
const feedback = ref('')
const comments = ref<Array<{ time: number; text: string }>>([])

const decision = ref<'APPROVE' | 'REJECT' | 'MINOR_EDIT'>('APPROVE')

const addTimestampComment = () => {
  comments.value.push({
    time: currentTime.value,
    text: ''
  })
}

const submitAudit = async () => {
  await auditStore.submitSecondAudit({
    chapterId: props.chapterId,
    decision: decision.value,
    rating: rating.value,
    feedback: feedback.value,
    comments: comments.value
  })
}
</script>

<template>
  <div class="final-audit-view">
    <ElPageHeader title="Final Audit">
      <template #description>
        Review and approve the final chapter video
      </template>
    </ElPageHeader>

    <div class="audit-layout">
      <!-- Video Player -->
      <div class="video-section">
        <VideoPlayer
          :src="videoUrl"
          :allow-comments="true"
          @timeupdate="currentTime = $event"
          @add-comment="addTimestampComment"
        />

        <!-- Comment Timeline -->
        <div class="comment-timeline">
          <TimestampComment
            v-for="(comment, idx) in comments"
            :key="idx"
            :time="comment.time"
            v-model="comment.text"
            @seek="currentTime = $event"
          />
        </div>
      </div>

      <!-- Audit Form -->
      <div class="audit-form-section">
        <ElCard header="Evaluation">
          <ElForm label-width="100px">
            <ElFormItem label="Rating">
              <ElRate v-model="rating" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
            </ElFormItem>

            <ElFormItem label="Decision">
              <ElRadioGroup v-model="decision">
                <ElRadioButton label="APPROVE">Approve</ElRadioButton>
                <ElRadioButton label="MINOR_EDIT">Minor Edit</ElRadioButton>
                <ElRadioButton label="REJECT">Reject</ElRadioButton>
              </ElRadioGroup>
            </ElFormItem>

            <ElFormItem label="Feedback" v-if="decision !== 'APPROVE'">
              <ElInput
                v-model="feedback"
                type="textarea"
                :rows="4"
                placeholder="Provide detailed feedback for revisions..."
              />
            </ElFormItem>

            <ElFormItem label="Issue Category" v-if="decision === 'REJECT'">
              <ElSelect v-model="rejectionCategory" placeholder="Select category">
                <ElOption label="Visual Quality" value="visual" />
                <ElOption label="Audio Quality" value="audio" />
                <ElOption label="Lip-Sync Issues" value="lipsync" />
                <ElOption label="Story/Pacing" value="story" />
                <ElOption label="Subtitle Issues" value="subtitle" />
              </ElSelect>
            </ElFormItem>
          </ElForm>

          <ElDivider />

          <ElButton type="primary" @click="submitAudit">
            Submit Audit
          </ElButton>
        </ElCard>
      </div>
    </div>
  </div>
</template>
```

### 8.4 Feedback Form Component

```vue
<!-- components/audit/FeedbackForm.vue -->
<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  type: 'FIRST' | 'SECOND'
}>()

const emit = defineEmits<{
  submit: [feedback: AuditFeedback]
}>()

const feedbackForm = ref({
  rating: 5,
  overallComment: '',
  panelComments: [] as Array<{ panelId: string; comment: string }>,
  issueCategory: null as string | null
})

const rejectionCategories = [
  { value: 'visual', label: 'Visual Quality', returnStep: 5 },
  { value: 'audio', label: 'Audio/TTS', returnStep: 5 },
  { value: 'lipsync', label: 'Lip-Sync', returnStep: 6 },
  { value: 'story', label: 'Storyboard/Story', returnStep: 4 },
  { value: 'bgm', label: 'BGM', returnStep: 7 },
  { value: 'subtitle', label: 'Subtitle', returnStep: 7, minorEdit: true }
]
</script>

<template>
  <ElForm :model="feedbackForm" label-width="120px">
    <ElFormItem label="Overall Rating">
      <ElRate v-model="feedbackForm.rating" />
    </ElFormItem>

    <ElFormItem label="Overall Comment">
      <ElInput
        v-model="feedbackForm.overallComment"
        type="textarea"
        :rows="3"
        placeholder="Share your overall impression..."
      />
    </ElFormItem>

    <ElFormItem label="Issue Category" v-if="type === 'SECOND'">
      <ElSelect
        v-model="feedbackForm.issueCategory"
        placeholder="Select if rejecting"
        clearable
      >
        <ElOption
          v-for="cat in rejectionCategories"
          :key="cat.value"
          :label="cat.label"
          :value="cat.value"
        >
          {{ cat.label }}
          <ElTag size="small" v-if="cat.minorEdit">Minor Edit</ElTag>
        </ElOption>
      </ElSelect>
    </ElFormItem>

    <ElButton type="primary" @click="emit('submit', feedbackForm)">
      Submit Feedback
    </ElButton>
  </ElForm>
</template>
```

---

## 9. Real-time Updates

### 9.1 WebSocket Strategy

```typescript
// composables/useWebSocket.ts
import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useWebSocket(endpoint: string) {
  const authStore = useAuthStore()
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const lastMessage = ref<MessageEvent | null>(null)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  function connect() {
    const token = authStore.token
    ws.value = new WebSocket(
      `wss://api.example.com${endpoint}?token=${token}`
    )

    ws.value.onopen = () => {
      isConnected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onclose = () => {
      isConnected.value = false
      // Auto-reconnect with exponential backoff
      if (reconnectAttempts.value < maxReconnectAttempts) {
        setTimeout(connect, Math.pow(2, reconnectAttempts.value) * 1000)
        reconnectAttempts.value++
      }
    }

    ws.value.onmessage = (event) => {
      lastMessage.value = event
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  function send(data: any) {
    if (ws.value && isConnected.value) {
      ws.value.send(JSON.stringify(data))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    lastMessage,
    connect,
    disconnect,
    send
  }
}
```

### 9.2 Generation Progress Updates

```typescript
// composables/useGenerationProgress.ts
import { ref, watch } from 'vue'
import { useWebSocket } from './useWebSocket'

export interface GenerationJob {
  id: string
  type: 'IMAGE' | 'AUDIO' | 'VIDEO'
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  progress: number
  eta?: number
  error?: string
}

export function useGenerationProgress() {
  const jobs = ref<Map<string, GenerationJob>>(new Map())

  const { lastMessage } = useWebSocket('/ws/generation')

  watch(lastMessage, (message) => {
    if (!message) return

    const data = JSON.parse(message.data)

    switch (data.type) {
      case 'JOB_CREATED':
        jobs.value.set(data.jobId, {
          id: data.jobId,
          type: data.jobType,
          status: 'QUEUED',
          progress: 0
        })
        break

      case 'JOB_PROGRESS':
        const job = jobs.value.get(data.jobId)
        if (job) {
          job.status = 'PROCESSING'
          job.progress = data.progress
          job.eta = data.eta
        }
        break

      case 'JOB_COMPLETED':
        const completedJob = jobs.value.get(data.jobId)
        if (completedJob) {
          completedJob.status = 'COMPLETED'
          completedJob.progress = 100
        }
        break

      case 'JOB_FAILED':
        const failedJob = jobs.value.get(data.jobId)
        if (failedJob) {
          failedJob.status = 'FAILED'
          failedJob.error = data.error
        }
        break
    }
  })

  return {
    jobs,
    getJob: (id: string) => jobs.value.get(id),
    getAllJobs: () => Array.from(jobs.value.values())
  }
}
```

### 9.3 Polling Fallback Strategy

```typescript
// composables/usePolling.ts
import { ref, onUnmounted } from 'vue'

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  intervalMs: number = 5000,
  immediate: boolean = true
) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  let timer: number | null = null

  async function fetch() {
    loading.value = true
    error.value = null
    try {
      data.value = await fetchFn()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch'
    } finally {
      loading.value = false
    }
  }

  function start() {
    if (immediate) {
      fetch()
    }
    timer = window.setInterval(fetch, intervalMs)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onUnmounted(() => {
    stop()
  })

  return {
    data,
    loading,
    error,
    start,
    stop,
    refresh: fetch
  }
}
```

### 9.4 Notification System

```typescript
// stores/notification.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElNotification } from 'element-plus'

export interface Notification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  timestamp: number
  read: boolean
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)

  function show(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) {
    const id = Date.now().toString()
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
      read: false
    }

    notifications.value.unshift(newNotification)
    unreadCount.value++

    ElNotification({
      title: notification.title,
      message: notification.message,
      type: notification.type,
      duration: 5000
    })
  }

  function markAsRead(id: string) {
    const notification = notifications.value.find(n => n.id === id)
    if (notification && !notification.read) {
      notification.read = true
      unreadCount.value--
    }
  }

  function markAllAsRead() {
    notifications.value.forEach(n => n.read = true)
    unreadCount.value = 0
  }

  function clear() {
    notifications.value = []
    unreadCount.value = 0
  }

  return {
    notifications,
    unreadCount,
    show,
    markAsRead,
    markAllAsRead,
    clear
  }
})
```

---

## 10. Performance Optimization

### 10.1 Code Splitting Strategy

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-element': ['element-plus'],
          'vendor-media': ['video.js', 'wavesurfer.js'],

          // Feature chunks
          'admin': ['./src/views/admin'],
          'lead': ['./src/views/lead'],
          'member': ['./src/views/member'],
          'pipeline': ['./src/views/pipeline'],
          'audit': ['./src/views/audit']
        }
      }
    },
    chunkSizeWarningLimit: 500
  }
})
```

### 10.2 Image Lazy Loading

```vue
<!-- components/common/LazyImage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  src: string
  thumbnail?: string
  alt: string
  width?: number
  height?: number
}>()

const imageSrc = ref(props.thumbnail || props.src)
const isLoaded = ref(false)
const isIntersecting = ref(false)

let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      isIntersecting.value = true
      // Load full image
      const img = new Image()
      img.src = props.src
      img.onload = () => {
        imageSrc.value = props.src
        isLoaded.value = true
      }
      observer?.disconnect()
    }
  }, { rootMargin: '100px' })

  observer.observe(document.getElementById(`lazy-img-${props.src}`)!)
})
</script>

<template>
  <ElImage
    :id="`lazy-img-${src}`"
    :src="imageSrc"
    :alt="alt"
    :width="width"
    :height="height"
    fit="cover"
    lazy
    :class="{ loaded: isLoaded }"
  >
    <template #placeholder>
      <div class="image-placeholder">
        <ElSkeletonItem variant="image" />
      </div>
    </template>
  </ElImage>
</template>
```

### 10.3 Virtual Scrolling for Asset Galleries

```vue
<!-- components/material/VirtualImageGrid.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { useVirtualList } from '@vueuse/core'

const props = defineProps<{
  images: Array<{ id: string; url: string }>
  columnCount?: number
}>()

const containerRef = ref<HTMLElement | null>(null)

// Use virtual list for large galleries
const { list, containerProps, wrapperProps } = useVirtualList(
  props.images,
  {
    itemHeight: 200, // Approximate height of image card
    overscan: 10
  }
)

const gridStyle = computed(() => ({
  display: 'grid',
  gridTemplateColumns: `repeat(${props.columnCount || 4}, 1fr)`,
  gap: '1rem'
}))
</script>

<template>
  <div ref="containerRef" v-bind="containerProps" style="height: 400px; overflow: auto">
    <div v-bind="wrapperProps" :style="gridStyle">
      <div
        v-for="item in list"
        :key="item.data.id"
        class="image-card"
        :style="{ height: '200px' }"
      >
        <ElImage :src="item.data.url" fit="cover" lazy />
      </div>
    </div>
  </div>
</template>
```

### 10.4 Component Lazy Loading

```typescript
// utils/lazyLoadComponent.ts
import { defineAsyncComponent } from 'vue'
import type { Component } from 'vue'

export function lazyLoadComponent(
  loader: () => Promise<Component>,
  loadingComponent?: Component,
  errorComponent?: Component,
  delay: number = 200,
  timeout: number = 3000
) {
  return defineAsyncComponent({
    loader,
    loadingComponent,
    errorComponent,
    delay,
    timeout,
    suspensible: true,
    onError(error, retry, fail, attempts) {
      if (attempts <= 3) {
        retry()
      } else {
        fail()
      }
    }
  })
}

// Usage
const HeavyComponent = lazyLoadComponent(
  () => import('@/components/heavy/HeavyComponent.vue')
)
```

### 10.5 Bundle Size Budget

```json
{
  "performance": {
    "budgets": [
      {
        "path": "**/*.js",
        "maxSize": "250 KB"
      },
      {
        "path": "**/*.css",
        "maxSize": "50 KB"
      },
      {
        "path": "**/vendor*.js",
        "maxSize": "500 KB"
      }
    ]
  }
}
```

---

## 11. Technical Risk Assessment

### 11.1 Identified Risks

| Risk ID | Risk Description | Impact | Probability | Mitigation Strategy |
|---------|------------------|--------|-------------|---------------------|
| **R01** | Long-running AI generation jobs (>5 min) causing UI timeout | High | High | Implement optimistic UI, background job polling, user feedback |
| **R02** | Large media files (4K video) causing slow page loads | High | Medium | CDN delivery, progressive loading, thumbnail lazy loading |
| **R03** | WebSocket connection drops during generation updates | Medium | Medium | Auto-reconnect with exponential backoff, polling fallback |
| **R04** | State synchronization issues in multi-user scenarios | High | Medium | Optimistic locking, last-write-wins with conflict detection |
| **R05** | Memory leaks from large image galleries | Medium | Medium | Virtual scrolling, image cleanup on unmount, weak refs |
| **R06** | Cross-browser video playback compatibility | Medium | Low | Use Video.js abstraction, test matrix for all browsers |
| **R07** | Accessibility compliance gaps | Medium | Medium | Early a11y testing, automated axe-core checks |
| **R08** | Vietnamese text expansion breaking layouts | Low | High | CSS `word-break`, flex layouts, +30% space allocation |
| **R09** | Element Plus theme customization complexity | Low | Medium | Design token system early, scoped CSS overrides |
| **R10** | Pinia store complexity for pipeline state machine | Medium | Medium | State machine library (XState) for complex workflows |

### 11.2 High-Priority Mitigation Plans

#### R01: Long-Running Jobs

```typescript
// composables/useLongRunningJob.ts
import { ref, watch } from 'vue'
import { useGenerationProgress } from './useGenerationProgress'

export function useLongRunningJob(jobId: string) {
  const { getJob } = useGenerationProgress()
  const job = ref(getJob(jobId))
  const userNotified = ref(false)

  // Show initial "started" notification
  onMounted(() => {
    notificationStore.show({
      type: 'info',
      title: 'Generation Started',
      message: 'This may take several minutes...'
    })
  })

  // Watch for completion
  watch(job, (newJob) => {
    if (newJob?.status === 'COMPLETED' && !userNotified.value) {
      notificationStore.show({
        type: 'success',
        title: 'Generation Complete',
        message: 'Your assets are ready for review'
      })
      userNotified.value = true
    }
  })

  return { job }
}
```

#### R04: State Synchronization

```typescript
// stores/pipeline.ts (excerpt with optimistic locking)
async function updateChapter(data: ChapterUpdate) {
  const currentVersion = chapter.value?.version

  try {
    // Optimistic update
    Object.assign(chapter.value, data)

    const response = await api.put(`/chapters/${data.id}`, {
      ...data,
      expectedVersion: currentVersion
    })

    // Server returns new version
    chapter.value = response.data
  } catch (error) {
    if (error.status === 409) {
      // Conflict - someone else updated
      showConflictModal(error.data)
      // Refresh from server
      await fetchChapter(data.id)
    }
    throw error
  }
}
```

#### R08: Vietnamese Localization

```scss
// styles/i18n.scss
:root {
  --text-expansion-factor: 1.3; // 30% for Vietnamese
}

.btn-text,
.label-text {
  // Allow text wrapping
  white-space: normal;
  word-break: break-word;

  // Vietnamese-specific
  &:lang(vi) {
    min-width: calc(100% * var(--text-expansion-factor));
  }
}

// Flexible layouts for text expansion
.flexible-container {
  display: flex;
  min-width: 0; // Allow flex items to shrink
}
```

---

## 12. Open Questions & Clarifications Needed

### 12.1 Requirements Gaps

| Question | Section | Impact | Recommended Action |
|----------|---------|--------|-------------------|
| What are the exact WCAG accessibility requirements? | 7.4 | Medium | Request WCAG AA or AAA target level |
| What browsers must be supported? | 7.4 | Medium | Define browser support matrix |
| What is the expected concurrent user load? | 7.4 | High | Clarify for performance planning |
| Are there offline capabilities required? | 7.6 | Medium | Confirm PWA requirements |
| What is the mobile H5 viewport target? | 7.4 | Medium | Define minimum viewport dimensions |

### 12.2 API Contract Clarifications

| Question | Impact | Recommended Action |
|----------|--------|-------------------|
| What is the exact WebSocket message format? | High | Define WebSocket protocol schema |
| How are generation job cancellations handled? | Medium | Add cancel endpoint specification |
| What pagination format is used for lists? | Medium | Confirm cursor vs offset pagination |
| How are file uploads handled (multipart vs presigned URLs)? | High | Define upload flow |

### 12.3 Design System Gaps

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No component specification document | High | Create `prd/ui_ux_component_spec.md` |
| No Vietnamese translation strings | Medium | Begin i18n key extraction |
| No loading state designs | Medium | Define skeleton patterns |
| No error state illustrations | Low | Create or source error state SVGs |

### 12.4 Technical Decisions Needed

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Video player library | Video.js, Plyr, custom | **Video.js** - enterprise ready |
| Audio waveform | WaveSurfer.js, peaks.js | **WaveSurfer.js** - mature, feature-rich |
| Image comparison | custom, img-compare-slider | Start custom, evaluate libraries |
| State machine for pipeline | Custom, XState | **XState** for complex workflow |
| Form validation | Vuelidate, VeeValidate | **VeeValidate** - Vue 3 compatible |

---

## Appendix A: File Structure

```
code/frontend/
├── src/
│   ├── assets/                  # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── illustrations/
│   │
│   ├── components/              # Reusable components
│   │   ├── common/              # Shared UI components
│   │   │   ├── BmButton.vue
│   │   │   ├── BmCard.vue
│   │   │   ├── BmDialog.vue
│   │   │   ├── LazyImage.vue
│   │   │   └── TaskProgress.vue
│   │   │
│   │   ├── dashboard/           # Dashboard widgets
│   │   │   ├── SystemHealthWidget.vue
│   │   │   ├── PendingReviewsWidget.vue
│   │   │   └── TeamWorkloadWidget.vue
│   │   │
│   │   ├── script/              # Script-related components
│   │   │   ├── ScriptEditor.vue
│   │   │   └── ScriptCompare.vue
│   │   │
│   │   ├── chapter/             # Chapter components
│   │   │   ├── ChapterCard.vue
│   │   │   └── ChapterTimeline.vue
│   │   │
│   │   ├── storyboard/          # Storyboard components
│   │   │   ├── PanelCard.vue
│   │   │   └── StoryboardGrid.vue
│   │   │
│   │   ├── material/            # Material generation components
│   │   │   ├── ImageGrid.vue
│   │   │   ├── AudioPlayer.vue
│   │   │   └── VirtualImageGrid.vue
│   │   │
│   │   ├── video/               # Video components
│   │   │   ├── VideoPlayer.vue
│   │   │   └── LipSyncPreview.vue
│   │   │
│   │   ├── audit/               # Audit components
│   │   │   ├── AuditCard.vue
│   │   │   ├── AuditChecklist.vue
│   │   │   ├── CardDrawSelection.vue
│   │   │   └── TimestampComment.vue
│   │   │
│   │   ├── composition/         # Composition components
│   │   │   ├── TimelineView.vue
│   │   │   └── BgmSelector.vue
│   │   │
│   │   └── pipeline/            # Pipeline wizard components
│   │       ├── PipelineWizard.vue
│   │       ├── StepIndicator.vue
│   │       └── GenerationProgress.vue
│   │
│   ├── composables/             # Composable functions
│   │   ├── useWebSocket.ts
│   │   ├── usePolling.ts
│   │   ├── usePipelineSync.ts
│   │   ├── useGenerationProgress.ts
│   │   └── useWidget.ts
│   │
│   ├── layouts/                 # Layout components
│   │   ├── AppShell.vue
│   │   ├── AuthLayout.vue
│   │   └── ProjectLayout.vue
│   │
│   ├── router/                  # Routing configuration
│   │   ├── index.ts
│   │   └── guards.ts
│   │
│   ├── services/                # API services
│   │   ├── api.ts               # Axios instance
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   ├── script.ts
│   │   ├── chapter.ts
│   │   ├── material.ts
│   │   ├── audit.ts
│   │   └── generation.ts
│   │
│   ├── stores/                  # Pinia stores
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   ├── user.ts
│   │   ├── project.ts
│   │   ├── script.ts
│   │   ├── chapter.ts
│   │   ├── storyboard.ts
│   │   ├── material.ts
│   │   ├── video.ts
│   │   ├── audit.ts
│   │   ├── pipeline.ts
│   │   ├── generation.ts
│   │   ├── notification.ts
│   │   └── dashboard.ts
│   │
│   ├── styles/                  # Global styles
│   │   ├── variables.scss
│   │   ├── tokens.ts
│   │   ├── breakpoints.ts
│   │   ├── i18n.scss
│   │   └── element-overrides.scss
│   │
│   ├── types/                   # TypeScript types
│   │   ├── user.ts
│   │   ├── project.ts
│   │   ├── script.ts
│   │   ├── chapter.ts
│   │   ├── storyboard.ts
│   │   ├── material.ts
│   │   ├── video.ts
│   │   ├── audit.ts
│   │   ├── pipeline.ts
│   │   └── api.ts
│   │
│   ├── utils/                   # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── lazyLoadComponent.ts
│   │   └── storage.ts
│   │
│   ├── views/                   # Page-level components
│   │   ├── auth/
│   │   │   └── LoginView.vue
│   │   ├── admin/
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── UserManagement.vue
│   │   │   └── ProjectManagement.vue
│   │   ├── lead/
│   │   │   ├── TeamLeadDashboard.vue
│   │   │   ├── ScriptEditorView.vue
│   │   │   └── FinalAuditView.vue
│   │   ├── member/
│   │   │   ├── TeamMemberDashboard.vue
│   │   │   ├── PipelineWizard.vue
│   │   │   └── FirstAuditView.vue
│   │   ├── project/
│   │   │   └── ProjectOverview.vue
│   │   └── error/
│   │       └── NotFound.vue
│   │
│   ├── App.vue
│   └── main.ts
│
├── public/
│   └── locales/
│       ├── en.json
│       └── vi.json
│
├── tests/
│   ├── unit/
│   ├── component/
│   └── e2e/
│
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── vitest.config.ts
```

---

## Appendix B: Development Task Breakdown

### Phase 1: Foundation (Weeks 1-2)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| F01 | Project Setup | Vite, TypeScript, ESLint, Prettier | 4 |
| F02 | Pinia Stores | Auth, User, Notification stores | 8 |
| F03 | Router Setup | Routes, guards, lazy loading | 6 |
| F04 | Element Plus | Theme customization, design tokens | 8 |
| F05 | Base Components | BmButton, BmCard, BmDialog | 6 |
| F06 | API Layer | Axios instance, interceptors, error handling | 6 |
| **Phase 1 Total** | | | **38 hours** |

### Phase 2: Auth & Dashboard (Weeks 2-4)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| D01 | Login View | Auth form, JWT handling | 8 |
| D02 | App Shell | Header, sidebar, navigation | 12 |
| D03 | Admin Dashboard | Widgets, tables, charts | 16 |
| D04 | Team Lead Dashboard | Pending reviews, workload | 16 |
| D05 | Team Member Dashboard | Task list, progress | 16 |
| D06 | WebSocket Integration | Real-time updates | 12 |
| **Phase 2 Total** | | | **80 hours** |

### Phase 3: Script & Chapter (Weeks 4-6)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| S01 | Script Editor | Rich text, LLM generation UI | 20 |
| S02 | Version Compare | Side-by-side diff view | 12 |
| S03 | Chapter Breakdown | Chapter cards, merge/split | 16 |
| S04 | Storyboard Grid | Panel layout, editor modal | 20 |
| S05 | Lock Mechanism | Lock UI, confirmation flows | 8 |
| **Phase 3 Total** | | | **76 hours** |

### Phase 4: Material Generation (Weeks 6-8)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| M01 | Image Grid | Gallery, selection, regenerate | 16 |
| M02 | Audio Player | Waveform, TTS controls | 12 |
| M03 | Generation Progress | Job tracking, ETA display | 12 |
| M04 | Virtual Scrolling | Performance for large galleries | 8 |
| M05 | Card Draw UI | 抽卡制 selection interface | 16 |
| **Phase 4 Total** | | | **64 hours** |

### Phase 5: Audit Workflow (Weeks 8-10)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| A01 | First Audit View | Checklist, approve/reject | 16 |
| A02 | Final Audit View | Video player, rating, feedback | 20 |
| A03 | Timestamp Comments | Video annotation | 16 |
| A04 | Audit History | Timeline, rollback UI | 12 |
| A05 | Side-by-Side Compare | Before/after comparison | 12 |
| **Phase 5 Total** | | | **76 hours** |

### Phase 6: Video & Composition (Weeks 10-12)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| V01 | Video Player | Video.js integration, subtitles | 20 |
| V02 | Timeline View | Multi-track composition | 24 |
| V03 | BGM Selector | Mood-based, AI generate UI | 16 |
| V04 | Subtitle Editor | Timing, text, styling | 20 |
| V05 | Lip-Sync Preview | Comparison view | 12 |
| **Phase 6 Total** | | | **92 hours** |

### Phase 7: Testing & Polish (Weeks 12-14)

| Task ID | Component | Description | Est. Hours |
|---------|-----------|-------------|------------|
| T01 | Unit Tests | Vitest, store tests | 20 |
| T02 | Component Tests | Vue Test Utils | 20 |
| T03 | E2E Tests | Playwright/Cypress | 24 |
| T04 | Performance Audit | Bundle analysis, optimization | 12 |
| T05 | Accessibility Audit | axe-core, manual testing | 12 |
| T06 | i18n Vietnamese | Translation integration | 16 |
| **Phase 7 Total** | | | **104 hours** |

**Total Estimated Development Time: ~530 hours (~13 weeks for 1 developer)**

---

## Appendix C: References

- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router 4](https://router.vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [Vite Documentation](https://vitejs.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [VueUse Composables](https://vueuse.org/)

---

**END OF FRONTEND ARCHITECTURE REVIEW**
