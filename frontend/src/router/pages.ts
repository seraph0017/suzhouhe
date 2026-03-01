import { defineAsyncComponent } from 'vue'

// 页面组件映射
export const pages = {
  // 公共
  Login: defineAsyncComponent(() => import('@/views/auth/Login.vue')),
  NotFound: defineAsyncComponent(() => import('@/views/common/NotFound.vue')),

  // 管理后台
  AdminDashboard: defineAsyncComponent(() => import('@/views/admin/Dashboard.vue')),
  UserManagement: defineAsyncComponent(() => import('@/views/admin/UserManagement.vue')),
  ProjectManagement: defineAsyncComponent(() => import('@/views/admin/ProjectManagement.vue')),
  ModelConfig: defineAsyncComponent(() => import('@/views/admin/ModelConfig.vue')),

  // 组长工作台
  LeadDashboard: defineAsyncComponent(() => import('@/views/lead/Dashboard.vue')),
  ScriptEditor: defineAsyncComponent(() => import('@/views/lead/ScriptEditor.vue')),
  FinalAudit: defineAsyncComponent(() => import('@/views/lead/FinalAudit.vue')),

  // 组员工作台
  MemberDashboard: defineAsyncComponent(() => import('@/views/member/Dashboard.vue')),
  ChapterBreakdown: defineAsyncComponent(() => import('@/views/member/ChapterBreakdown.vue')),
  StoryboardEditor: defineAsyncComponent(() => import('@/views/member/StoryboardEditor.vue')),
  MaterialSelection: defineAsyncComponent(() => import('@/views/member/MaterialSelection.vue')),
  FirstAudit: defineAsyncComponent(() => import('@/views/member/FirstAudit.vue')),
  VideoComposition: defineAsyncComponent(() => import('@/views/member/VideoComposition.vue')),
}
