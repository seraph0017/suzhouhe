# Frontend Architecture - Final Approval Document
# AI Manga/Video Production Pipeline System

**Document Version:** 1.0 (Final)
**Date:** 2026-03-01
**Author:** Senior Frontend Architect
**Status:** APPROVED FOR DEVELOPMENT

---

## Executive Summary

This document provides the **FINAL FRONTEND ARCHITECTURE APPROVAL** for the AI Manga/Video Production Pipeline System. All open questions from the initial review have been addressed in the updated PRD (v1.1).

### Approval Statement

After thorough review of the updated PRD (v1.1) dated 2026-03-01, the frontend architecture is **APPROVED FOR DEVELOPMENT**. All critical requirements have been specified with sufficient detail for implementation.

---

## 1. Confirmation of Previously Open Questions

All previously identified open questions have been addressed in the PRD update:

| # | Open Question | PRD Resolution | Status |
|---|---------------|----------------|--------|
| 1 | **Authentication mechanism** | JWT with refresh tokens specified (Section 7.5, Appendix B.1) | ✅ RESOLVED |
| 2 | **BGM source** | AI-generated + user upload supported (Section 4.9, 7.6) | ✅ RESOLVED |
| 3 | **Real-time update mechanism** | WebSocket with full spec including reconnection strategy (Section 7.7) | ✅ RESOLVED |
| 4 | **Storage quotas** | Defined per project tier with file size limits (Section 7.6) | ✅ RESOLVED |
| 5 | **AI provider fallback** | 3 retries + manual failover with health checks (Section 7.8) | ✅ RESOLVED |
| 6 | **Export formats** | MP4/MOV/WebM with quality presets defined (Section 7.11) | ✅ RESOLVED |
| 7 | **Task assignment** | Auto-assignment + manual assignment with priority handling (Section 7.9) | ✅ RESOLVED |
| 8 | **UI Wireframes** | Provided for all dashboard types and key workflows (Appendix C) | ✅ RESOLVED |

---

## 2. Final Component Hierarchy with File Structure

### 2.1 Project Structure

```
code/frontend/
├── src/
│   ├── main.ts                          # Application entry point
│   ├── App.vue                          # Root component
│   │
│   ├── assets/                          # Static assets
│   │   ├── styles/
│   │   │   ├── index.scss               # Global styles
│   │   │   ├── variables.scss           # SCSS variables
│   │   │   └── element-plus.scss        # Element Plus overrides
│   │   └── images/
│   │
│   ├── components/                      # Reusable components
│   │   ├── common/
│   │   │   ├── BmButton.vue             # Branded button
│   │   │   ├── BmCard.vue               # Branded card
│   │   │   ├── BmDialog.vue             # Branded dialog
│   │   │   ├── BmEmpty.vue              # Empty state
│   │   │   ├── BmLoading.vue            # Loading placeholder
│   │   │   ├── GenerationProgress.vue   # Generation job progress
│   │   │   ├── TaskProgress.vue         # Pipeline step progress
│   │   │   ├── ProjectSwitcher.vue      # Project selector
│   │   │   └── RoleBadge.vue            # Role indicator
│   │   │
│   │   ├── script/
│   │   │   ├── ScriptEditor.vue         # Script editing component
│   │   │   ├── ScriptPreview.vue        # Script read-only view
│   │   │   ├── SceneNavigator.vue       # Scene list sidebar
│   │   │   ├── CharacterPanel.vue       # Character management
│   │   │   └── VersionCompare.vue       # Version diff viewer
│   │   │
│   │   ├── chapter/
│   │   │   ├── ChapterCard.vue          # Chapter display card
│   │   │   ├── ChapterList.vue          # Chapter list view
│   │   │   ├── ChapterSplitDialog.vue   # Split chapter dialog
│   │   │   └── ChapterMergeDialog.vue   # Merge chapters dialog
│   │   │
│   │   ├── storyboard/
│   │   │   ├── PanelCard.vue            # Single panel card
│   │   │   ├── PanelGrid.vue            # Panel grid layout
│   │   │   ├── PanelEditor.vue          # Panel detail editor
│   │   │   ├── PanelSlideshow.vue       # Sequential preview
│   │   │   └── CameraDirectionSelect.vue# Camera direction picker
│   │   │
│   │   ├── material/
│   │   │   ├── ImageGrid.vue            # Generated images grid
│   │   │   ├── ImageCard.vue            # Single image card
│   │   │   ├── ImagePreviewDialog.vue   # Full-screen image preview
│   │   │   ├── AudioPlayer.vue          # Audio player with waveform
│   │   │   ├── AudioSelect.vue          # TTS voice selector
│   │   │   └── BatchGenerateStatus.vue  # Batch generation dashboard
│   │   │
│   │   ├── video/
│   │   │   ├── VideoPlayer.vue          # Video player component
│   │   │   ├── VideoPreview.vue         # Video preview with controls
│   │   │   ├── LipSyncIndicator.vue     # Lip-sync quality display
│   │   │   └── VideoCompare.vue         # Side-by-side comparison
│   │   │
│   │   ├── composition/
│   │   │   ├── TimelineView.vue         # Multi-track timeline
│   │   │   ├── TimelineTrack.vue        # Single track component
│   │   │   ├── BGMSelector.vue          # BGM browser
│   │   │   ├── SubtitleEditor.vue       # Subtitle timing editor
│   │   │   ├── VolumeMixer.vue          # Audio mixing controls
│   │   │   └── ExportDialog.vue         # Export configuration
│   │   │
│   │   ├── audit/
│   │   │   ├── AuditCard.vue            # Audit record display
│   │   │   ├── AuditForm.vue            # Audit submission form
│   │   │   ├── AuditHistory.vue         # Audit trail viewer
│   │   │   ├── FirstAuditView.vue       # First audit interface
│   │   │   ├── SecondAuditView.vue      # Second audit interface
│   │   │   └── TimestampComment.vue     # Timestamped feedback
│   │   │
│   │   ├── dashboard/
│   │   │   ├── TaskList.vue             # Task cards
│   │   │   ├── TaskCard.vue             # Single task card
│   │   │   ├── ProgressBoard.vue        # Gantt/Kanban view
│   │   │   ├── WorkloadChart.vue        # Team workload visualization
│   │   │   ├── TimelineWidget.vue       # Project timeline
│   │   │   └── MetricsWidget.vue        # Quality metrics display
│   │   │
│   │   └── admin/
│   │       ├── SystemHealthWidget.vue   # Health dashboard
│   │       ├── UserTable.vue            # User management table
│   │       ├── ProjectTable.vue         # Project list
│   │       ├── ModelConfigForm.vue      # Model config editor
│   │       ├── ProviderStatusWidget.vue # Provider health display
│   │       └── AuditLogTable.vue        # System audit logs
│   │
│   ├── views/                           # Page-level components
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   │
│   │   ├── admin/
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── UserManagement.vue
│   │   │   ├── ProjectManagement.vue
│   │   │   ├── ModelConfigManagement.vue
│   │   │   └── AuditLogsView.vue
│   │   │
│   │   ├── lead/
│   │   │   ├── TeamLeadDashboard.vue
│   │   │   ├── ScriptListView.vue
│   │   │   ├── ScriptEditorView.vue
│   │   │   ├── PipelineConfigView.vue
│   │   │   └── FinalAuditView.vue
│   │   │
│   │   ├── member/
│   │   │   ├── TeamMemberDashboard.vue
│   │   │   ├── TaskListView.vue
│   │   │   ├── PipelineWizardView.vue
│   │   │   ├── ChapterBreakdownView.vue
│   │   │   ├── StoryboardEditorView.vue
│   │   │   ├── MaterialSelectionView.vue
│   │   │   ├── FirstAuditView.vue
│   │   │   ├── VideoCompositionView.vue
│   │   │   └── ChapterAssemblyView.vue
│   │   │
│   │   ├── project/
│   │   │   ├── ProjectOverview.vue
│   │   │   ├── ChapterListView.vue
│   │   │   └── ProjectMembersView.vue
│   │   │
│   │   └── error/
│   │       ├── NotFound.vue
│   │       ├── Forbidden.vue
│   │       └── Error.vue
│   │
│   ├── composables/                     # Composable functions
│   │   ├── useAuth.ts                   # Auth logic
│   │   ├── useWebSocket.ts              # WebSocket connection
│   │   ├── useGenerationPoller.ts       # Generation polling fallback
│   │   ├── useProjectAccess.ts          # Project permission checks
│   │   ├── usePipelineNavigation.ts     # Pipeline step navigation
│   │   ├── useMediaPreview.ts           # Media preview logic
│   │   ├── useViewportSize.ts           # Responsive breakpoint detection
│   │   └── useDebounce.ts               # Debounce utility
│   │
│   ├── stores/                          # Pinia stores (see Section 3)
│   │
│   ├── services/                        # API client services (see Section 6)
│   │
│   ├── router/                          # Vue Router configuration (see Section 4)
│   │
│   ├── types/                           # TypeScript type definitions
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
│   │   └── api.ts
│   │
│   ├── utils/                           # Utility functions
│   │   ├── format.ts                    # Date/number formatters
│   │   ├── validators.ts                # Form validators
│   │   ├── storage.ts                   # localStorage wrappers
│   │   └── constants.ts                 # App constants
│   │
│   └── plugins/                         # Vue plugins
│       ├── element-plus.ts
│       ├── directives.ts
│       └── i18n.ts
│
├── public/
├── tests/
│   ├── unit/
│   ├── components/
│   └── e2e/
├── package.json
├── vite.config.ts
├── tsconfig.json
└── .env.example
```

### 2.2 Component Dependency Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VIEW COMPONENT DEPENDENCIES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ScriptEditorView                                                            │
│   ├── ScriptEditor (dumb)                                                   │
│   ├── ScriptPreview (dumb)                                                  │
│   ├── SceneNavigator (dumb)                                                 │
│   ├── CharacterPanel (smart)                                                │
│   ├── VersionCompare (dumb)                                                 │
│   └── BmDialog, BmButton, BmCard                                            │
│                                                                             │
│ ChapterBreakdownView                                                        │
│   ├── ChapterList (dumb)                                                    │
│   ├── ChapterCard (dumb)                                                    │
│   ├── ChapterSplitDialog (dumb)                                             │
│   ├── ChapterMergeDialog (dumb)                                             │
│   └── GenerationProgress (smart)                                            │
│                                                                             │
│ StoryboardEditorView                                                        │
│   ├── PanelGrid (dumb)                                                      │
│   ├── PanelCard (dumb)                                                      │
│   ├── PanelEditor (smart)                                                   │
│   ├── PanelSlideshow (dumb)                                                 │
│   └── GenerationProgress (smart)                                            │
│                                                                             │
│ MaterialSelectionView                                                       │
│   ├── ImageGrid (dumb)                                                      │
│   ├── ImageCard (dumb)                                                      │
│   ├── ImagePreviewDialog (dumb)                                             │
│   ├── AudioPlayer (smart)                                                   │
│   ├── AudioSelect (dumb)                                                    │
│   └── BatchGenerateStatus (smart)                                           │
│                                                                             │
│ FirstAuditView                                                              │
│   ├── AuditForm (smart)                                                     │
│   ├── ImageGrid (dumb)                                                      │
│   ├── AudioPlayer (smart)                                                   │
│   ├── AuditHistory (smart)                                                  │
│   └── GenerationProgress (smart)                                            │
│                                                                             │
│ VideoCompositionView                                                        │
│   ├── TimelineView (smart)                                                  │
│   ├── BGMSelector (smart)                                                   │
│   ├── SubtitleEditor (smart)                                                │
│   ├── VolumeMixer (dumb)                                                    │
│   └── ExportDialog (smart)                                                  │
│                                                                             │
│ SecondAuditView                                                             │
│   ├── VideoPlayer (smart)                                                   │
│   ├── AuditForm (smart)                                                     │
│   ├── TimestampComment (dumb)                                               │
│   ├── AuditHistory (smart)                                                  │
│   └── VideoCompare (dumb)                                                   │
│                                                                             │
│ AdminDashboard                                                              │
│   ├── SystemHealthWidget (smart)                                            │
│   ├── UserTable (smart)                                                     │
│   ├── ProjectTable (smart)                                                  │
│   ├── ModelConfigForm (smart)                                               │
│   ├── ProviderStatusWidget (smart)                                          │
│   └── AuditLogTable (smart)                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Pinia Store Schemas and Actions

### 3.1 Auth Store

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Role, AuthTokens } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ========== STATE ==========
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ========== GETTERS ==========
  const isAuthenticated = computed(() => !!accessToken.value)
  const currentUser = computed(() => user.value)
  const currentRole = computed(() => user.value?.role)

  const isAdmin = computed(() => currentRole.value === 'ADMIN')
  const isTeamLead = computed(() => currentRole.value === 'TEAM_LEAD')
  const isTeamMember = computed(() => currentRole.value === 'TEAM_MEMBER')

  const hasProjectAccess = computed(() => {
    return (projectId: string) => {
      return user.value?.projects?.some(p => p.id === projectId) ?? false
    }
  })

  // ========== ACTIONS ==========
  async function login(email: string, password: string): Promise<User> {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login({ email, password })
      accessToken.value = response.accessToken
      refreshToken.value = response.refreshToken
      user.value = response.user
      persistAuth(response)
      return response.user
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await authApi.logout(accessToken.value!)
    } finally {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      clearPersistedAuth()
    }
  }

  async function refreshAccessToken(): Promise<void> {
    if (!refreshToken.value) throw new Error('No refresh token available')
    const response = await authApi.refresh(refreshToken.value)
    accessToken.value = response.accessToken
    refreshToken.value = response.refreshToken
  }

  function hasPermission(permission: string): boolean {
    const permissions: Record<Role, string[]> = {
      ADMIN: ['*'],
      TEAM_LEAD: ['script:*', 'audit:second', 'pipeline:configure', 'project:manage'],
      TEAM_MEMBER: ['pipeline:execute', 'audit:first', 'material:select']
    }
    const userPerms = permissions[currentRole.value!]
    return userPerms?.includes('*') || userPerms?.includes(permission) || false
  }

  // ========== PERSISTENCE ==========
  function persistAuth(tokens: AuthTokens): void {
    localStorage.setItem('auth_token', tokens.accessToken)
    localStorage.setItem('auth_refresh', tokens.refreshToken)
    localStorage.setItem('auth_user', JSON.stringify(tokens.user))
  }

  function restoreAuth(): boolean {
    const token = localStorage.getItem('auth_token')
    const refresh = localStorage.getItem('auth_refresh')
    const userStr = localStorage.getItem('auth_user')

    if (token && refresh && userStr) {
      accessToken.value = token
      refreshToken.value = refresh
      user.value = JSON.parse(userStr)
      return true
    }
    return false
  }

  function clearPersistedAuth(): void {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_refresh')
    localStorage.removeItem('auth_user')
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    // Getters
    isAuthenticated,
    currentUser,
    currentRole,
    isAdmin,
    isTeamLead,
    isTeamMember,
    hasProjectAccess,
    // Actions
    login,
    logout,
    refreshAccessToken,
    hasPermission,
    restoreAuth,
    clearPersistedAuth
  }
}, {
  persist: {
    key: 'auth',
    paths: ['accessToken', 'refreshToken', 'user'],
    storage: localStorage,
    serializer: {
      serialize: (value) => JSON.stringify(value),
      deserialize: (value) => JSON.parse(value)
    }
  }
})
```

### 3.2 Pipeline Store

```typescript
// stores/pipeline.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  PipelineState,
  PipelineStep,
  ChapterStatus,
  AuditType
} from '@/types/pipeline'

export const PIPELINE_STEPS: PipelineStep[] = [
  { id: 1, name: '剧本基座', key: 'script_base', icon: 'Document', requiresLock: false },
  { id: 2, name: '剧本精调', key: 'script_refine', icon: 'Edit', requiresLock: false },
  { id: 3, name: '章节拆解', key: 'chapter_breakdown', icon: 'Grid', requiresLock: true },
  { id: 4, name: '分镜创作', key: 'storyboard', icon: 'Grid', requiresLock: true },
  { id: 5, name: '素材生成', key: 'material_gen', icon: 'Image', requiresLock: true, isAudit: true },
  { id: 6, name: '视频生成', key: 'video_gen', icon: 'Video', requiresLock: true },
  { id: 7, name: '智能合成', key: 'composition', icon: 'Film', requiresLock: true },
  { id: 8, name: '章节封装', key: 'chapter_assembly', icon: 'Files', requiresLock: true, isAudit: true, auditType: 'SECOND' }
]

export const usePipelineStore = defineStore('pipeline', () => {
  // ========== STATE ==========
  const currentProjectId = ref<string | null>(null)
  const currentChapterId = ref<string | null>(null)
  const pipelineState = ref<PipelineState | null>(null)
  const stepStatuses = ref<Record<number, 'pending' | 'in-progress' | 'completed' | 'blocked'>>({})
  const isLocked = ref(false)
  const lockOwner = ref<string | null>(null)
  const lockExpiresAt = ref<string | null>(null)

  // ========== GETTERS ==========
  const currentStep = computed(() => {
    if (!pipelineState.value) return null
    return PIPELINE_STEPS.find(s => s.key === pipelineState.value!.currentStepKey) || null
  })

  const currentStepIndex = computed(() => {
    if (!currentStep.value) return 0
    return currentStep.value.id - 1
  })

  const completedSteps = computed(() => {
    return PIPELINE_STEPS.filter(s => stepStatuses.value[s.id] === 'completed')
  })

  const nextAvailableStep = computed(() => {
    const currentIndex = currentStep.value?.id || 0
    return PIPELINE_STEPS.find(s => s.id > currentIndex && stepStatuses.value[s.id] !== 'completed') || null
  })

  const canProceed = computed(() => {
    if (!currentStep.value) return false
    // Steps 1-4 require lock
    if (currentStep.value.id < 5) return isLocked.value
    // Steps 5+ require completion confirmation
    return stepStatuses.value[currentStep.value.id] === 'completed' ||
           stepStatuses.value[currentStep.value.id] === 'in-progress'
  })

  const progressPercentage = computed(() => {
    const completed = completedSteps.value.length
    const total = PIPELINE_STEPS.length
    return Math.round((completed / total) * 100)
  })

  // ========== ACTIONS ==========
  function initialize(projectId: string, chapterId: string): void {
    currentProjectId.value = projectId
    currentChapterId.value = chapterId
  }

  function loadPipelineState(state: PipelineState): void {
    pipelineState.value = state
    state.stepStatuses.forEach(status => {
      stepStatuses.value[status.stepId] = status.status
    })
    isLocked.value = state.isLocked
    lockOwner.value = state.lockOwner
    lockExpiresAt.value = state.lockExpiresAt
  }

  function updateStepStatus(
    stepId: number,
    status: 'pending' | 'in-progress' | 'completed' | 'blocked'
  ): void {
    stepStatuses.value[stepId] = status
  }

  function setLock(locked: boolean, owner?: string, expiresAt?: string): void {
    isLocked.value = locked
    lockOwner.value = owner || null
    lockExpiresAt.value = expiresAt || null
  }

  async function acquireLock(): Promise<void> {
    if (isLocked.value) throw new Error('Already locked')
    const response = await pipelineApi.acquireLock(currentChapterId.value!)
    setLock(true, response.owner, response.expiresAt)
  }

  async function releaseLock(): Promise<void> {
    if (!isLocked.value) return
    await pipelineApi.releaseLock(currentChapterId.value!)
    setLock(false)
  }

  async function advanceToNextStep(): Promise<void> {
    if (!nextAvailableStep.value) throw new Error('No next step')
    if (!canProceed.value) throw new Error('Current step not complete')

    // Mark current step as completed
    if (currentStep.value) {
      updateStepStatus(currentStep.value.id, 'completed')
    }

    // Mark next step as in-progress
    updateStepStatus(nextAvailableStep.value.id, 'in-progress')

    // API call
    await pipelineApi.advanceChapter(
      currentChapterId.value!,
      nextAvailableStep.value.key
    )

    pipelineState.value!.currentStepKey = nextAvailableStep.value.key
  }

  async function submitAudit(
    auditType: AuditType,
    decision: string,
    feedback: string,
    selections?: Record<string, string>
  ): Promise<void> {
    await pipelineApi.submitAudit(currentChapterId.value!, {
      auditType,
      decision,
      feedback,
      selections
    })
    // Advance to next step after successful audit
    if (decision === 'APPROVED') {
      await advanceToNextStep()
    }
  }

  function canAccessStep(stepId: number, userRole: string): boolean {
    const step = PIPELINE_STEPS.find(s => s.id === stepId)
    if (!step) return false

    // Steps 1-4: Team Lead only (script definition)
    if (stepId <= 4) {
      return userRole === 'TEAM_LEAD' || userRole === 'ADMIN'
    }

    // Steps 5-7: Team Member (material generation, first audit)
    if (stepId >= 5 && stepId <= 7) {
      return userRole !== 'VIEWER'
    }

    // Step 8 + Second Audit: Team Lead only
    if (stepId >= 8) {
      return userRole === 'TEAM_LEAD' || userRole === 'ADMIN'
    }

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
    lockExpiresAt,
    // Getters
    currentStep,
    currentStepIndex,
    completedSteps,
    nextAvailableStep,
    canProceed,
    progressPercentage,
    // Actions
    initialize,
    loadPipelineState,
    updateStepStatus,
    setLock,
    acquireLock,
    releaseLock,
    advanceToNextStep,
    submitAudit,
    canAccessStep
  }
})
```

### 3.3 Material Store

```typescript
// stores/material.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GeneratedImage, GeneratedAudio, SelectionState } from '@/types/material'

export const useMaterialStore = defineStore('material', () => {
  // ========== STATE ==========
  const images = ref<Map<string, GeneratedImage[]>>(new Map()) // panelId -> images[]
  const audio = ref<Map<string, GeneratedAudio>>(new Map()) // panelId -> audio
  const selections = ref<Map<string, SelectionState>>(new Map()) // panelId -> selection
  const generatingPanels = ref<Set<string>>(new Set())
  const loading = ref(false)
  const error = ref<Map<string, string>>(new Map())

  // ========== GETTERS ==========
  const allPanelsHaveSelections = computed(() => {
    const panelIds = Array.from(images.keys())
    return panelIds.every(id => selections.value.has(id) && selections.value.get(id)?.imageId)
  })

  const selectionProgress = computed(() => {
    const total = images.value.size
    const selected = Array.from(selections.value.values()).filter(s => s.imageId).length
    return {
      total,
      selected,
      percentage: total > 0 ? Math.round((selected / total) * 100) : 0
    }
  })

  const getImagesForPanel = (panelId: string) => {
    return images.value.get(panelId) || []
  }

  const getSelectedImage = (panelId: string) => {
    const selection = selections.value.get(panelId)
    if (!selection?.imageId) return null
    const panelImages = images.value.get(panelId) || []
    return panelImages.find(img => img.id === selection.imageId) || null
  }

  const getAudioForPanel = (panelId: string) => {
    return audio.value.get(panelId) || null
  }

  // ========== ACTIONS ==========
  function setImages(panelId: string, newImages: GeneratedImage[]): void {
    images.value.set(panelId, newImages)
    error.value.delete(panelId)
  }

  function setAudio(panelId: string, newAudio: GeneratedAudio): void {
    audio.value.set(panelId, newAudio)
    error.value.delete(panelId)
  }

  function selectImage(panelId: string, imageId: string): void {
    const current = selections.value.get(panelId) || { imageId: null, audioId: null, notes: '' }
    selections.value.set(panelId, { ...current, imageId })
  }

  function selectAudio(panelId: string, audioId: string): void {
    const current = selections.value.get(panelId) || { imageId: null, audioId: null, notes: '' }
    selections.value.set(panelId, { ...current, audioId })
  }

  function setSelectionNotes(panelId: string, notes: string): void {
    const current = selections.value.get(panelId) || { imageId: null, audioId: null, notes: '' }
    selections.value.set(panelId, { ...current, notes })
  }

  async function generateImages(
    panelId: string,
    batchSize: number = 4,
    config?: { stylePreset?: string; aspectRatio?: string }
  ): Promise<void> {
    if (generatingPanels.value.has(panelId)) return

    generatingPanels.value.add(panelId)
    error.value.set(panelId, '')

    try {
      const result = await materialApi.generateImages({
        panelIds: [panelId],
        batchSize,
        ...config
      })
      // Result will come via WebSocket
    } catch (e) {
      error.value.set(panelId, (e as Error).message)
    } finally {
      generatingPanels.value.delete(panelId)
    }
  }

  async function generateAudio(
    panelId: string,
    text: string,
    config?: { voiceId?: string; emotion?: string }
  ): Promise<void> {
    generatingPanels.value.add(panelId)

    try {
      await materialApi.generateAudio({
        requests: [{ panelId, text, ...config }]
      })
      // Result will come via WebSocket
    } catch (e) {
      error.value.set(panelId, (e as Error).message)
    } finally {
      generatingPanels.value.delete(panelPanelId)
    }
  }

  async function saveSelections(chapterId: string): Promise<void> {
    const selectionsToSave = Array.from(selections.value.entries()).map(([panelId, selection]) => ({
      panelId,
      ...selection
    }))
    await materialApi.saveSelections(chapterId, selectionsToSave)
  }

  async function regenerateForPanel(panelId: string): Promise<void> {
    await generateImages(panelId, 4)
  }

  function clearSelections(): void {
    selections.value.clear()
  }

  function clearAll(): void {
    images.value.clear()
    audio.value.clear()
    selections.value.clear()
    generatingPanels.value.clear()
    error.value.clear()
  }

  return {
    // State
    images,
    audio,
    selections,
    generatingPanels,
    loading,
    error,
    // Getters
    allPanelsHaveSelections,
    selectionProgress,
    getImagesForPanel,
    getSelectedImage,
    getAudioForPanel,
    // Actions
    setImages,
    setAudio,
    selectImage,
    selectAudio,
    setSelectionNotes,
    generateImages,
    generateAudio,
    saveSelections,
    regenerateForPanel,
    clearSelections,
    clearAll
  }
})
```

### 3.4 Generation Store

```typescript
// stores/generation.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GenerationJob, JobStatus, JobType } from '@/types/generation'

export const useGenerationStore = defineStore('generation', () => {
  // ========== STATE ==========
  const jobs = ref<Map<string, GenerationJob>>(new Map())
  const queue = ref<string[]>([]) // Job IDs in queue order

  // ========== GETTERS ==========
  const activeJobs = computed(() => {
    return Array.from(jobs.value.values()).filter(
      j => j.status === 'QUEUED' || j.status === 'PROCESSING'
    )
  })

  const pendingJobs = computed(() => {
    return Array.from(jobs.value.values()).filter(j => j.status === 'QUEUED')
  })

  const processingJobs = computed(() => {
    return Array.from(jobs.value.values()).filter(j => j.status === 'PROCESSING')
  })

  const failedJobs = computed(() => {
    return Array.from(jobs.value.values()).filter(j => j.status === 'FAILED')
  })

  const getJobById = (jobId: string) => {
    return jobs.value.get(jobId) || null
  }

  // ========== ACTIONS ==========
  function registerJob(job: GenerationJob): void {
    jobs.value.set(job.id, job)
    if (job.status === 'QUEUED') {
      queue.value.push(job.id)
    }
  }

  function updateJobProgress(
    jobId: string,
    updates: Partial<GenerationJob>
  ): void {
    const job = jobs.value.get(jobId)
    if (job) {
      jobs.value.set(jobId, { ...job, ...updates })
    }
  }

  function markJobComplete(jobId: string, result: any): void {
    const job = jobs.value.get(jobId)
    if (job) {
      jobs.value.set(jobId, {
        ...job,
        status: 'COMPLETED',
        progress: 1.0,
        result,
        completedAt: new Date().toISOString()
      })
      // Remove from queue
      const index = queue.value.indexOf(jobId)
      if (index > -1) queue.value.splice(index, 1)
    }
  }

  function markJobFailed(jobId: string, error: string, retryable: boolean): void {
    const job = jobs.value.get(jobId)
    if (job) {
      jobs.value.set(jobId, {
        ...job,
        status: 'FAILED',
        error: { message: error, retryable },
        completedAt: new Date().toISOString()
      })
      // Remove from queue
      const index = queue.value.indexOf(jobId)
      if (index > -1) queue.value.splice(index, 1)
    }
  }

  function removeJob(jobId: string): void {
    jobs.value.delete(jobId)
    const index = queue.value.indexOf(jobId)
    if (index > -1) queue.value.splice(index, 1)
  }

  function clearCompletedJobs(): void {
    for (const [jobId, job] of jobs.value.entries()) {
      if (job.status === 'COMPLETED' || job.status === 'FAILED') {
        jobs.value.delete(jobId)
      }
    }
  }

  async function cancelJob(jobId: string): Promise<void> {
    await generationApi.cancelJob(jobId)
    removeJob(jobId)
  }

  async function retryJob(jobId: string): Promise<void> {
    const job = jobs.value.get(jobId)
    if (!job || !job.error?.retryable) return

    removeJob(jobId)
    // Re-submit the job
    await generationApi.retry(jobId)
  }

  return {
    // State
    jobs,
    queue,
    // Getters
    activeJobs,
    pendingJobs,
    processingJobs,
    failedJobs,
    getJobById,
    // Actions
    registerJob,
    updateJobProgress,
    markJobComplete,
    markJobFailed,
    removeJob,
    clearCompletedJobs,
    cancelJob,
    retryJob
  }
})
```

### 3.5 Store Summary Table

| Store | File | State Properties | Key Actions | Persistence |
|-------|------|-----------------|-------------|-------------|
| **auth** | `stores/auth.ts` | user, accessToken, refreshToken, loading | login, logout, refreshAccessToken, hasPermission | localStorage |
| **pipeline** | `stores/pipeline.ts` | pipelineState, stepStatuses, isLocked, lockOwner | acquireLock, releaseLock, advanceToNextStep, submitAudit | None |
| **material** | `stores/material.ts` | images, audio, selections, generatingPanels | generateImages, generateAudio, selectImage, saveSelections | None |
| **generation** | `stores/generation.ts` | jobs, queue | registerJob, updateJobProgress, markJobComplete, retryJob | None |
| **project** | `stores/project.ts` | projects, currentProject, members | fetchProjects, selectProject, addMember | localStorage (currentProject) |
| **script** | `stores/script.ts` | scripts, currentScript, versions | fetchScripts, generateScript, lockScript, compareVersions | None |
| **chapter** | `stores/chapter.ts` | chapters, currentChapter, status | fetchChapters, splitChapter, mergeChapters, reorderChapters | None |
| **storyboard** | `storyboard.ts` | panels, currentPanel, lockState | fetchPanels, updatePanel, lockStoryboard, addPanel | None |
| **audit** | `stores/audit.ts` | audits, pendingAudits, history | fetchPendingAudits, submitAudit, fetchHistory | None |
| **notification** | `stores/notification.ts` | notifications, toasts | showToast, addNotification, markAsRead | None |

---

## 4. Vue Router Configuration

### 4.1 Complete Route Table

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, RouteMeta } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

type Role = 'ADMIN' | 'TEAM_LEAD' | 'TEAM_MEMBER'

interface AuthMeta extends RouteMeta {
  requiresAuth: boolean
  role?: Role
  requiresProjectAccess?: boolean
  requiresLock?: boolean
  workflowStep?: number
}

const routes: RouteRecordRaw[] = [
  // ==================== AUTH ROUTES ====================
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },

  // ==================== MAIN APP SHELL ====================
  {
    path: '/',
    component: () => import('@/layouts/AppShell.vue'),
    meta: { requiresAuth: true },
    children: [
      // Root redirect based on role
      {
        path: '',
        redirect: to => {
          const authStore = useAuthStore()
          const role = authStore.currentRole
          if (role === 'ADMIN') return '/admin/dashboard'
          if (role === 'TEAM_LEAD') return '/lead/dashboard'
          return '/member/dashboard'
        }
      },

      // ==================== ADMIN ROUTES ====================
      {
        path: 'admin',
        meta: { requiresAuth: true, role: 'ADMIN' },
        children: [
          {
            path: 'dashboard',
            name: 'AdminDashboard',
            component: () => import('@/views/admin/AdminDashboard.vue')
          },
          {
            path: 'users',
            name: 'UserManagement',
            component: () => import('@/views/admin/UserManagement.vue')
          },
          {
            path: 'projects',
            name: 'ProjectManagement',
            component: () => import('@/views/admin/ProjectManagement.vue')
          },
          {
            path: 'model-configs',
            name: 'ModelConfigManagement',
            component: () => import('@/views/admin/ModelConfigManagement.vue')
          },
          {
            path: 'audit-logs',
            name: 'AuditLogs',
            component: () => import('@/views/admin/AuditLogs.vue')
          }
        ]
      },

      // ==================== TEAM LEAD ROUTES ====================
      {
        path: 'lead',
        meta: { requiresAuth: true, role: 'TEAM_LEAD' },
        children: [
          {
            path: 'dashboard',
            name: 'TeamLeadDashboard',
            component: () => import('@/views/lead/TeamLeadDashboard.vue')
          },
          {
            path: 'scripts',
            name: 'ScriptList',
            component: () => import('@/views/lead/ScriptListView.vue')
          },
          {
            path: 'scripts/:scriptId',
            name: 'ScriptEditor',
            component: () => import('@/views/lead/ScriptEditorView.vue'),
            meta: { requiresAuth: true, role: 'TEAM_LEAD', requiresLock: true }
          },
          {
            path: 'pipeline/:chapterId',
            name: 'PipelineConfig',
            component: () => import('@/views/lead/PipelineConfigView.vue')
          },
          {
            path: 'audit/:chapterId/final',
            name: 'FinalAudit',
            component: () => import('@/views/lead/FinalAuditView.vue'),
            meta: { auditType: 'SECOND' }
          }
        ]
      },

      // ==================== TEAM MEMBER ROUTES ====================
      {
        path: 'member',
        meta: { requiresAuth: true, role: 'TEAM_MEMBER' },
        children: [
          {
            path: 'dashboard',
            name: 'TeamMemberDashboard',
            component: () => import('@/views/member/TeamMemberDashboard.vue')
          },
          {
            path: 'tasks',
            name: 'TaskList',
            component: () => import('@/views/member/TaskListView.vue')
          },
          {
            path: 'pipeline/:chapterId',
            name: 'PipelineWizard',
            component: () => import('@/views/member/PipelineWizardView.vue'),
            children: [
              {
                path: 'chapter-breakdown',
                name: 'ChapterBreakdown',
                component: () => import('@/views/member/ChapterBreakdownView.vue'),
                meta: { workflowStep: 3 }
              },
              {
                path: 'storyboard',
                name: 'StoryboardEditor',
                component: () => import('@/views/member/StoryboardEditorView.vue'),
                meta: { workflowStep: 4 }
              },
              {
                path: 'materials',
                name: 'MaterialSelection',
                component: () => import('@/views/member/MaterialSelectionView.vue'),
                meta: { workflowStep: 5 }
              },
              {
                path: 'first-audit',
                name: 'FirstAudit',
                component: () => import('@/views/member/FirstAuditView.vue'),
                meta: { workflowStep: 5, auditType: 'FIRST' }
              },
              {
                path: 'composition',
                name: 'VideoComposition',
                component: () => import('@/views/member/VideoCompositionView.vue'),
                meta: { workflowStep: 7 }
              },
              {
                path: 'assembly',
                name: 'ChapterAssembly',
                component: () => import('@/views/member/ChapterAssemblyView.vue'),
                meta: { workflowStep: 8 }
              }
            ]
          }
        ]
      },

      // ==================== PROJECT ROUTES ====================
      {
        path: 'projects/:projectId',
        component: () => import('@/layouts/ProjectLayout.vue'),
        meta: { requiresAuth: true, requiresProjectAccess: true },
        children: [
          {
            path: 'overview',
            name: 'ProjectOverview',
            component: () => import('@/views/project/ProjectOverview.vue')
          },
          {
            path: 'chapters',
            name: 'ChapterList',
            component: () => import('@/views/project/ChapterListView.vue')
          },
          {
            path: 'members',
            name: 'ProjectMembers',
            component: () => import('@/views/project/ProjectMembersView.vue')
          }
        ]
      }
    ]
  },

  // ==================== ERROR ROUTES ====================
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/Forbidden.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Route guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Check authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ path: '/auth/login', query: { redirect: to.fullPath } })
    return
  }

  // Skip other checks if going to auth page
  if (to.path.startsWith('/auth')) {
    next()
    return
  }

  // Restore auth if needed
  if (!authStore.isAuthenticated) {
    const restored = authStore.restoreAuth()
    if (!restored) {
      next({ path: '/auth/login', query: { redirect: to.fullPath } })
      return
    }
  }

  // Check role-based access
  if (to.meta.role && authStore.currentRole !== to.meta.role) {
    next({ name: 'Forbidden' })
    return
  }

  // Check project access
  if (to.meta.requiresProjectAccess && to.params.projectId) {
    const hasAccess = authStore.hasProjectAccess(to.params.projectId as string)
    if (!hasAccess) {
      next({ name: 'Forbidden' })
      return
    }
  }

  // Check lock requirement
  if (to.meta.requiresLock) {
    // Check if script is locked (implement in pipeline store)
    // If not locked, redirect or show unlock dialog
  }

  next()
})
```

### 4.2 Route Summary Table

| Route Path | Component | Role | Meta | Description |
|------------|-----------|------|------|-------------|
| `/auth/login` | LoginView | Public | - | User login |
| `/auth/register` | RegisterView | Public | - | User registration |
| `/admin/dashboard` | AdminDashboard | ADMIN | - | Admin overview |
| `/admin/users` | UserManagement | ADMIN | - | User management |
| `/admin/projects` | ProjectManagement | ADMIN | - | Project list |
| `/admin/model-configs` | ModelConfigManagement | ADMIN | - | AI model config |
| `/admin/audit-logs` | AuditLogs | ADMIN | - | System audit trail |
| `/lead/dashboard` | TeamLeadDashboard | TEAM_LEAD | - | Team Lead overview |
| `/lead/scripts` | ScriptListView | TEAM_LEAD | - | Script list |
| `/lead/scripts/:id` | ScriptEditorView | TEAM_LEAD | requiresLock | Script editor |
| `/lead/pipeline/:chapterId` | PipelineConfigView | TEAM_LEAD | - | Pipeline config |
| `/lead/audit/:chapterId/final` | FinalAuditView | TEAM_LEAD | SECOND audit | Final audit |
| `/member/dashboard` | TeamMemberDashboard | TEAM_MEMBER | - | Member overview |
| `/member/tasks` | TaskListView | TEAM_MEMBER | - | Task list |
| `/member/pipeline/:chapterId` | PipelineWizardView | TEAM_MEMBER | - | Pipeline wizard |
| `/projects/:projectId/overview` | ProjectOverview | Member+ | requiresProjectAccess | Project overview |
| `/projects/:projectId/chapters` | ChapterListView | Member+ | requiresProjectAccess | Chapter list |
| `/projects/:projectId/members` | ProjectMembersView | Member+ | requiresProjectAccess | Team members |

---

## 5. WebSocket Composable Interface

### 5.1 WebSocket Composable

```typescript
// composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGenerationStore } from '@/stores/generation'
import type {
  WebSocketMessage,
  ProgressUpdate,
  TaskComplete,
  ErrorMessage
} from '@/types/websocket'

interface UseWebSocketOptions {
  url?: string
  reconnectAttempts?: number
  reconnectDelay?: number
  heartbeatInterval?: number
}

const DEFAULT_OPTIONS: Required<UseWebSocketOptions> = {
  url: import.meta.env.VITE_WS_URL || 'wss://api.domain.com/ws/v1/notifications',
  reconnectAttempts: 5,
  reconnectDelay: 1000, // 1s, doubles each attempt
  heartbeatInterval: 30000 // 30 seconds
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const opts = { ...DEFAULT_OPTIONS, ...options }

  const authStore = useAuthStore()
  const generationStore = useGenerationStore()

  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const error = ref<string | null>(null)
  const reconnectCount = ref(0)
  const heartbeatTimer = ref<number | null>(null)

  // Message type handlers
  const handlers = {
    CONNECTION_ACK: (payload: any) => {
      console.log('[WS] Connection acknowledged', payload)
      isConnected.value = true
      isConnecting.value = false
      reconnectCount.value = 0
      startHeartbeat()
    },

    CONNECTION_ERROR: (payload: any) => {
      console.error('[WS] Connection error', payload)
      error.value = payload.message
      isConnected.value = false
      isConnecting.value = false

      if (payload.code === 'UNAUTHORIZED') {
        // Token expired, refresh and reconnect
        handleTokenRefresh()
      }
    },

    PROGRESS_UPDATE: (payload: ProgressUpdate) => {
      console.log('[WS] Progress update', payload)
      generationStore.updateJobProgress(payload.jobId, {
        status: payload.status,
        progress: payload.progress,
        currentStep: payload.currentStep,
        completedSteps: payload.completedSteps,
        totalSteps: payload.totalSteps,
        estimatedTimeRemaining: payload.estimatedTimeRemaining
      })
    },

    TASK_COMPLETE: (payload: TaskComplete) => {
      console.log('[WS] Task complete', payload)
      generationStore.markJobComplete(payload.jobId, payload.result)

      // Trigger notification
      // Could emit event or call notification store
    },

    ERROR: (payload: ErrorMessage) => {
      console.error('[WS] Error', payload)
      generationStore.markJobFailed(payload.jobId, payload.message, payload.retryable)
    },

    PONG: (payload: any) => {
      // Heartbeat response - connection is healthy
      console.log('[WS] Heartbeat OK')
    }
  }

  function connect(): void {
    if (isConnected.value || isConnecting.value) return

    isConnecting.value = true
    error.value = null

    const token = authStore.accessToken
    if (!token) {
      error.value = 'No authentication token available'
      isConnecting.value = false
      return
    }

    try {
      ws.value = new WebSocket(opts.url)

      ws.value.onopen = () => {
        // Send connection init with auth
        ws.value?.send(JSON.stringify({
          type: 'CONNECTION_INIT',
          payload: {
            authorization: `Bearer ${token}`
          }
        }))
      }

      ws.value.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data)
        const handler = handlers[message.type as keyof typeof handlers]
        if (handler) {
          handler(message.payload)
        }
      }

      ws.value.onerror = () => {
        error.value = 'WebSocket connection error'
        isConnecting.value = false
      }

      ws.value.onclose = (event) => {
        console.log('[WS] Connection closed', event.code, event.reason)
        isConnected.value = false
        isConnecting.value = false
        stopHeartbeat()

        // Attempt reconnect if not closed normally
        if (event.code !== 1000 && reconnectCount.value < opts.reconnectAttempts) {
          scheduleReconnect()
        }
      }
    } catch (e) {
      error.value = (e as Error).message
      isConnecting.value = false
    }
  }

  function disconnect(): void {
    stopHeartbeat()
    if (ws.value) {
      ws.value.close(1000, 'Client disconnected')
      ws.value = null
    }
    isConnected.value = false
    isConnecting.value = false
  }

  function scheduleReconnect(): void {
    const delay = opts.reconnectDelay * Math.pow(2, reconnectCount.value)
    reconnectCount.value++

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectCount.value})`)

    setTimeout(() => {
      connect()
    }, delay)
  }

  async function handleTokenRefresh(): Promise<void> {
    try {
      await authStore.refreshAccessToken()
      // Reconnect with new token
      disconnect()
      setTimeout(connect, 500)
    } catch (e) {
      // Refresh failed, redirect to login
      authStore.logout()
      window.location.href = '/auth/login'
    }
  }

  function startHeartbeat(): void {
    stopHeartbeat()
    heartbeatTimer.value = window.setInterval(() => {
      if (ws.value && isConnected.value) {
        ws.value.send(JSON.stringify({
          type: 'PING',
          timestamp: new Date().toISOString()
        }))
      }
    }, opts.heartbeatInterval)
  }

  function stopHeartbeat(): void {
    if (heartbeatTimer.value) {
      clearInterval(heartbeatTimer.value)
      heartbeatTimer.value = null
    }
  }

  function sendMessage(type: string, payload: any): void {
    if (!ws.value || !isConnected.value) {
      console.warn('[WS] Cannot send message - not connected')
      return
    }
    ws.value.send(JSON.stringify({ type, payload }))
  }

  // Lifecycle
  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    isConnected,
    isConnecting,
    error,
    // Actions
    connect,
    disconnect,
    sendMessage
  }
}
```

### 5.2 WebSocket Message Types

```typescript
// types/websocket.ts
export type WebSocketMessageType =
  | 'CONNECTION_INIT'
  | 'CONNECTION_ACK'
  | 'CONNECTION_ERROR'
  | 'PROGRESS_UPDATE'
  | 'TASK_COMPLETE'
  | 'ERROR'
  | 'PING'
  | 'PONG'

export interface WebSocketMessage {
  type: WebSocketMessageType
  payload: any
}

export interface ConnectionAckPayload {
  connectionId: string
  expiresIn: number
}

export interface ConnectionErrorPayload {
  code: 'UNAUTHORIZED' | 'INVALID_REQUEST' | 'SERVER_ERROR'
  message: string
}

export type JobStatus = 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
export type JobType = 'IMAGE_GENERATION' | 'AUDIO_GENERATION' | 'VIDEO_GENERATION' | 'COMPOSITION'

export interface ProgressUpdate {
  jobId: string
  jobType: JobType
  status: JobStatus
  progress: number // 0-1
  currentStep: string
  totalSteps: number
  completedSteps: number
  estimatedTimeRemaining: number // seconds
  data?: {
    panelId?: string
    generatedCount?: number
    expectedCount?: number
  }
}

export interface TaskComplete {
  jobId: string
  jobType: JobType
  status: 'COMPLETED'
  result: {
    generatedItems: Array<{
      id: string
      url: string
      thumbnailUrl?: string
    }>
    metadata: {
      generationTime: number
      provider: string
    }
  }
}

export interface ErrorMessage {
  code: string
  message: string
  jobId?: string
  retryable: boolean
  retryAfter?: number
  suggestedAction?: string
}
```

---

## 6. API Client Service with Interceptors

### 6.1 API Client Configuration

```typescript
// services/api-client.ts
import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError
} from 'axios'
import { useAuthStore } from '@/stores/auth'
import { router } from '@/router'

// Types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  meta: {
    requestId: string
    timestamp: string
  }
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, any>
  }
  meta: {
    requestId: string
    timestamp: string
  }
}

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.domain.com/api/v1'
const API_TIMEOUT = 30000 // 30 seconds

// Create instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()

    // Add auth header
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = generateRequestId()

    // Add project ID if available
    const currentProject = localStorage.getItem('current_project')
    if (currentProject) {
      config.headers['X-Project-ID'] = currentProject
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response
  },
  async (error: AxiosError<ApiError>) => {
    const authStore = useAuthStore()
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // Check if it's a token expiration
      if (!originalRequest._retry) {
        originalRequest._retry = true

        try {
          // Try to refresh token
          await authStore.refreshAccessToken()

          // Retry original request with new token
          originalRequest.headers = {
            ...originalRequest.headers,
            Authorization: `Bearer ${authStore.accessToken}`
          }
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Refresh failed - logout and redirect
          authStore.logout()
          router.push({
            path: '/auth/login',
            query: { redirect: window.location.pathname }
          })
          return Promise.reject(refreshError)
        }
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      router.push({ name: 'Forbidden' })
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      router.push({ name: 'NotFound' })
    }

    // Handle 500+ Server errors
    if (error.response && error.response.status >= 500) {
      // Could trigger global error notification
      console.error('[API] Server error:', error.response.data)
    }

    return Promise.reject(formatApiError(error))
  }
)

// Helper functions
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

function formatApiError(error: AxiosError<ApiError>): Error {
  if (error.response?.data) {
    const apiError = error.response.data
    const formattedError = new Error(apiError.error.message)
    Object.assign(formattedError, {
      code: apiError.error.code,
      details: apiError.error.details,
      requestId: apiError.meta.requestId
    })
    return formattedError
  }

  if (error.code === 'ECONNABORTED') {
    const timeoutError = new Error('Request timeout')
    Object.assign(timeoutError, { code: 'TIMEOUT' })
    return timeoutError
  }

  if (error.code === 'ERR_NETWORK') {
    const networkError = new Error('Network error - please check your connection')
    Object.assign(networkError, { code: 'NETWORK_ERROR' })
    return networkError
  }

  return error as Error
}

// Request wrappers
export const api = {
  // Generic methods
  get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return apiClient.get<T>(url, config)
  },

  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return apiClient.post<T>(url, data, config)
  },

  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return apiClient.put<T>(url, data, config)
  },

  patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return apiClient.patch<T>(url, data, config)
  },

  delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return apiClient.delete<T>(url, config)
  }
}

export default apiClient
```

### 6.2 API Service Modules

```typescript
// services/auth.ts
import { api } from './api-client'
import type { User, AuthTokens } from '@/types/auth'

export const authService = {
  login(email: string, password: string) {
    return api.post<AuthTokens>('/auth/login', { email, password })
      .then(res => res.data.data)
  },

  refreshToken(refreshToken: string) {
    return api.post<AuthTokens>('/auth/refresh', { refresh_token: refreshToken })
      .then(res => res.data.data)
  },

  logout(accessToken: string) {
    return api.post('/auth/logout', {}, {
      headers: { Authorization: `Bearer ${accessToken}` }
    })
  }
}

// services/project.ts
import { api } from './api-client'
import type { Project, ProjectMember } from '@/types/project'

export const projectApi = {
  list() {
    return api.get<Project[]>('/projects')
      .then(res => res.data.data)
  },

  get(projectId: string) {
    return api.get<Project>(`/projects/${projectId}`)
      .then(res => res.data.data)
  },

  create(data: Partial<Project>) {
    return api.post<Project>('/projects', data)
      .then(res => res.data.data)
  },

  update(projectId: string, data: Partial<Project>) {
    return api.put<Project>(`/projects/${projectId}`, data)
      .then(res => res.data.data)
  },

  archive(projectId: string) {
    return api.delete(`/projects/${projectId}`)
      .then(res => res.data.data)
  },

  getMembers(projectId: string) {
    return api.get<ProjectMember[]>(`/projects/${projectId}/members`)
      .then(res => res.data.data)
  },

  addMember(projectId: string, userId: string, role: string) {
    return api.post<ProjectMember>(`/projects/${projectId}/members`, {
      user_id: userId,
      role
    })
      .then(res => res.data.data)
  }
}

// services/pipeline.ts
import { api } from './api-client'
import type { PipelineState, AuditSubmission } from '@/types/pipeline'

export const pipelineApi = {
  getState(chapterId: string) {
    return api.get<PipelineState>(`/chapters/${chapterId}/pipeline`)
      .then(res => res.data.data)
  },

  acquireLock(chapterId: string) {
    return api.post(`/chapters/${chapterId}/lock`)
      .then(res => res.data.data)
  },

  releaseLock(chapterId: string) {
    return api.post(`/chapters/${chapterId}/unlock`)
      .then(res => res.data.data)
  },

  advanceChapter(chapterId: string, nextStepKey: string) {
    return api.post(`/chapters/${chapterId}/advance`, { next_step: nextStepKey })
      .then(res => res.data.data)
  },

  submitAudit(chapterId: string, submission: AuditSubmission) {
    const endpoint = submission.auditType === 'FIRST'
      ? '/audits/first'
      : '/audits/second'
    return api.post(endpoint, { chapter_id: chapterId, ...submission })
      .then(res => res.data.data)
  }
}

// services/material.ts
import { api } from './api-client'
import type { GeneratedImage, GeneratedAudio, SelectionInput } from '@/types/material'

export const materialApi = {
  generateImages(params: {
    panelIds: string[]
    batchSize: number
    stylePreset?: string
    aspectRatio?: string
  }) {
    return api.post('/generation/images', params)
      .then(res => res.data.data)
  },

  generateAudio(params: {
    requests: Array<{
      panelId: string
      text: string
      voiceId?: string
      emotion?: string
    }>
  }) {
    return api.post('/generation/audio', params)
      .then(res => res.data.data)
  },

  saveSelections(chapterId: string, selections: SelectionInput[]) {
    return api.post(`/chapters/${chapterId}/selections`, { selections })
      .then(res => res.data.data)
  }
}

// services/generation.ts
import { api } from './api-client'
import type { GenerationJob } from '@/types/generation'

export const generationApi = {
  getJob(jobId: string) {
    return api.get<GenerationJob>(`/generation/jobs/${jobId}`)
      .then(res => res.data.data)
  },

  cancelJob(jobId: string) {
    return api.post(`/generation/jobs/${jobId}/cancel`)
      .then(res => res.data.data)
  },

  retry(jobId: string) {
    return api.post(`/generation/jobs/${jobId}/retry`)
      .then(res => res.data.data)
  }
}
```

---

## 7. Element Plus Theme Customization

### 7.1 Design Tokens

```scss
// styles/variables.scss

// Color Palette - Bingo Market Design System
$colors: (
  'primary': (
    'base': #3b82f6,
    'light': #60a5fa,
    'dark': #2563eb,
    'lighter': #93c5fd,
    'lightest': #dbeafe
  ),
  'success': (
    'base': #22c55e,
    'light': #4ade80,
    'dark': #16a34a
  ),
  'warning': (
    'base': #f59e0b,
    'light': #fbbf24,
    'dark': #d97706
  ),
  'error': (
    'base': #ef4444,
    'light': #f87171,
    'dark': #dc2626
  ),
  'info': (
    'base': #3b82f6,
    'light': #60a5fa,
    'dark': #2563eb
  )
);

// Neutral Colors
$neutral-colors: (
  50: #fafafa,
  100: #f4f4f5,
  200: #e4e4e7,
  300: #d4d4d8,
  400: #a1a1aa,
  500: #71717a,
  600: #52525b,
  700: #3f3f46,
  800: #27272a,
  900: #18181b
);

// Typography
$font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
$font-size-base: 16px; // Vietnamese +30% text expansion consideration
$font-size-scale: (
  'xs': 0.75rem,    // 12px
  'sm': 0.875rem,   // 14px
  'md': 1rem,       // 16px
  'lg': 1.125rem,   // 18px
  'xl': 1.25rem,    // 20px
  '2xl': 1.5rem     // 24px
);

// Spacing
$spacing-scale: (
  'xs': 0.25rem,    // 4px
  'sm': 0.5rem,     // 8px
  'md': 1rem,       // 16px
  'lg': 1.5rem,     // 24px
  'xl': 2rem,       // 32px
  '2xl': 3rem       // 48px
);

// Border Radius
$border-radius: (
  'none': 0,
  'sm': 0.25rem,    // 4px
  'md': 0.375rem,   // 6px
  'lg': 0.5rem,     // 8px
  'xl': 0.75rem,    // 12px
  'full': 9999px
);

// Shadows
$shadows: (
  'sm': 0 1px 2px 0 rgba(0, 0, 0, 0.05),
  'md': 0 4px 6px -1px rgba(0, 0, 0, 0.1),
  'lg': 0 10px 15px -3px rgba(0, 0, 0, 0.1),
  'xl': 0 20px 25px -5px rgba(0, 0, 0, 0.1)
);

// Layout
$sidebar-width: 240px;
$sidebar-collapsed-width: 64px;
$header-height: 56px;
$content-max-width: 1400px;
$content-padding: 24px;

// Transitions
$transition-duration: (
  'fast': 150ms,
  'normal': 250ms,
  'slow': 350ms
);
$transition-timing: ease-in-out;
```

### 7.2 Element Plus Override Styles

```scss
// styles/element-plus.scss

// Import Element Plus styles
@use 'element-plus/theme-chalk/src/index.scss' as *;

// Override CSS custom properties
:root {
  // Primary Color
  --el-color-primary: #{$colors-primary-base};
  --el-color-primary-light-3: #{$colors-primary-lighter};
  --el-color-primary-light-5: #{$colors-primary-lightest};
  --el-color-primary-light-7: #{$colors-primary-lightest};
  --el-color-primary-light-8: #{$colors-primary-lightest};
  --el-color-primary-light-9: #{$colors-primary-lightest};
  --el-color-primary-dark-2: #{$colors-primary-dark};

  // Success Color
  --el-color-success: #{$colors-success-base};

  // Warning Color
  --el-color-warning: #{$colors-warning-base};

  // Error Color
  --el-color-error: #{$colors-error-base};

  // Border & Background
  --el-border-color: #{$neutral-colors-300};
  --el-border-color-light: #{$neutral-colors-200};
  --el-border-color-lighter: #{$neutral-colors-100};
  --el-fill-color: #{$neutral-colors-50};
  --el-fill-color-light: #fff;
  --el-bg-color: #fff;

  // Text Color
  --el-text-color-primary: #{$neutral-colors-900};
  --el-text-color-regular: #{$neutral-colors-700};
  --el-text-color-secondary: #{$neutral-colors-500};
  --el-text-color-placeholder: #{$neutral-colors-400};

  // Font
  --el-font-family: #{$font-family};
  --el-font-size-base: #{$font-size-base};

  // Border Radius
  --el-border-radius-base: #{map-get($border-radius, 'lg')};
  --el-border-radius-round: #{map-get($border-radius, 'xl')};
  --el-border-radius-circle: #{map-get($border-radius, 'full')};

  // Shadow
  --el-box-shadow: #{map-get($shadows, 'md')};
  --el-box-shadow-light: #{map-get($shadows, 'sm')};
  --el-box-shadow-lighter: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
}

// Component-specific overrides

// Button
.el-button {
  font-weight: 500;
  transition: all #{map-get($transition-duration, 'normal')} $transition-timing;

  &--primary {
    --el-button-bg-color: #{$colors-primary-base};
    --el-button-border-color: #{$colors-primary-base};

    &:hover {
      --el-button-bg-color: #{$colors-primary-light};
      --el-button-border-color: #{$colors-primary-light};
    }

    &:active {
      --el-button-bg-color: #{$colors-primary-dark};
      --el-button-border-color: #{$colors-primary-dark};
    }
  }

  &--round {
    border-radius: #{map-get($border-radius, 'full')};
  }
}

// Card
.el-card {
  border-radius: #{map-get($border-radius, 'xl')};
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: var(--el-box-shadow-light);

  &__header {
    border-bottom-color: var(--el-border-color-lighter);
    padding: 16px 20px;
  }

  &__body {
    padding: 20px;
  }
}

// Dialog
.el-dialog {
  border-radius: #{map-get($border-radius, 'xl')};
  overflow: hidden;

  &__header {
    background-color: var(--el-fill-color);
    padding: 16px 20px;
  }

  &__title {
    font-weight: 600;
    font-size: #{map-get($font-size-scale, 'lg')};
  }

  &__body {
    padding: 24px;
  }

  &__footer {
    border-top-color: var(--el-border-color-lighter);
    padding: 16px 24px;
  }
}

// Table
.el-table {
  --el-table-header-bg-color: var(--el-fill-color);
  --el-table-header-text-color: var(--el-text-color-regular);
  --el-table-row-hover-bg-color: var(--el-fill-color-light);

  border-radius: #{map-get($border-radius, 'lg')};
  overflow: hidden;

  &__header th {
    font-weight: 600;
    padding: 12px 16px;
  }

  &__body td {
    padding: 14px 16px;
  }
}

// Form
.el-form-item {
  &__label {
    font-weight: 500;
    color: var(--el-text-color-regular);
  }

  &__error {
    font-size: #{map-get($font-size-scale, 'sm')};
  }
}

// Input
.el-input__inner,
.el-textarea__inner {
  border-radius: #{map-get($border-radius, 'md')};
  transition: all #{map-get($transition-duration, 'fast')} $transition-timing;
}

// Progress
.el-progress-bar__inner {
  border-radius: #{map-get($border-radius, 'full')};
}

// Tag
.el-tag {
  border-radius: #{map-get($border-radius, 'sm')};
  font-weight: 500;
}

// Timeline
.el-timeline-item__node {
  border-width: 3px;
}

// Steps
.el-step__head {
  &.is-finish {
    color: var(--el-color-primary);
  }
}
```

### 7.3 Custom Branded Components

```vue
<!-- components/common/BmButton.vue -->
<script setup lang="ts">
import { ElButton } from 'element-plus'
import type { ButtonHTMLAttributes } from 'vue'

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
  loading?: boolean
  round?: boolean
  circle?: boolean
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'default',
  round: false
})

defineOptions({
  inheritAttrs: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <ElButton
    v-bind="$attrs"
    :type="type"
    :size="size"
    :disabled="disabled"
    :loading="loading"
    :round="round"
    :circle="circle"
    :icon="icon"
    @click="emit('click', $event)"
  >
    <slot />
  </ElButton>
</template>
```

---

## 8. Remaining Concerns and Risks

### 8.1 Technical Risks (Mitigated)

| Risk | Severity | Mitigation Strategy | Status |
|------|----------|---------------------|--------|
| **WebSocket reconnection** | Medium | Exponential backoff with max 30s, token refresh handling | ✅ Mitigated |
| **Large file upload (video)** | Medium | Chunked upload with progress, retry logic | To implement |
| **State synchronization** | Medium | Optimistic updates with rollback on error | ✅ Mitigated |
| **Memory with media previews** | Low | Lazy loading, virtual scrolling for large lists | ✅ Mitigated |

### 8.2 Implementation Considerations

1. **Vietnamese Text Expansion**: Base font size is 16px to accommodate +30% text expansion. All layouts should be tested with Vietnamese content.

2. **Mobile-First (H5)**: While primary use is desktop, responsive breakpoints are defined. Mobile-specific optimizations may be needed based on actual usage.

3. **Accessibility**: WCAG AA compliance targeted. Keyboard navigation and ARIA labels are mandatory. Full accessibility audit recommended before launch.

4. **Performance Budget**:
   - Initial bundle: < 500KB gzipped
   - First Contentful Paint: < 2 seconds
   - Time to Interactive: < 3 seconds

### 8.3 Open for Future Phases

| Feature | Priority | Notes |
|---------|----------|-------|
| **PWA Support** | P2 | Offline capability for script editing |
| **Real-time Collaboration** | P2 | Multiple users editing same script |
| **Advanced Analytics** | P3 | Detailed production metrics dashboard |
| **Mobile App** | P3 | React Native or Vue Native |
| **Platform Auto-Upload** | P2 | Direct YouTube/Bilibili upload |

---

## 9. Development Task Summary

### Phase 1: Foundation (Week 1-2)
- [ ] Project initialization with Vite + Vue 3 + TypeScript
- [ ] Element Plus integration with custom theme
- [ ] Pinia store setup with persistence
- [ ] Vue Router configuration with guards
- [ ] API client with interceptors
- [ ] WebSocket composable
- [ ] Base component library (BmButton, BmCard, etc.)

### Phase 2: Authentication & Admin (Week 3-4)
- [ ] Login/Register views
- [ ] Auth store with JWT handling
- [ ] Admin dashboard
- [ ] User management
- [ ] Project management
- [ ] Model configuration UI

### Phase 3: Core Pipeline (Week 5-8)
- [ ] Script editor with version control
- [ ] Chapter breakdown UI
- [ ] Storyboard editor
- [ ] Material selection (card draw system)
- [ ] First audit interface
- [ ] Video composition timeline
- [ ] Second audit interface

### Phase 4: Dashboard & Polish (Week 9-10)
- [ ] Role-specific dashboards
- [ ] Generation progress tracking
- [ ] WebSocket real-time updates
- [ ] Error handling and edge cases
- [ ] Performance optimization
- [ ] Accessibility audit

---

## Conclusion

This frontend architecture document provides a complete blueprint for implementing the AI Manga/Video Production Pipeline System. All requirements from the PRD (v1.1) have been addressed with:

1. **Component hierarchy** with clear smart/dumb separation
2. **Pinia store schemas** with typed state, getters, and actions
3. **Vue Router configuration** with role-based guards
4. **WebSocket composable** with reconnection strategy
5. **API client** with interceptors for auth and error handling
6. **Element Plus theme** customization matching Bingo Market design system

The architecture follows Vue 3 best practices with Composition API, TypeScript for type safety, and a clear separation of concerns between views, components, stores, and services.

---

## Approval Statement

**FRONTEND ARCHITECTURE: APPROVED FOR DEVELOPMENT**

All open questions have been resolved, component hierarchies are defined, state management schemas are complete, routing is configured, and real-time communication patterns are established. The development team can proceed with implementation following this architecture document.

**Approved by:** Senior Frontend Architect
**Date:** 2026-03-01
**Next Step:** Begin Phase 1 development (Foundation setup)
