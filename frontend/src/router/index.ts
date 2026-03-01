import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 布局组件
import AuthLayout from '@/layouts/AuthLayout.vue'
import MainLayout from '@/layouts/MainLayout.vue'

// 页面组件
import Login from '@/views/auth/Login.vue'
import NotFound from '@/views/common/NotFound.vue'
import Dashboard from '@/views/Dashboard.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import ProjectManagement from '@/views/admin/ProjectManagement.vue'
import ModelConfig from '@/views/admin/ModelConfig.vue'
import LeadDashboard from '@/views/lead/Dashboard.vue'
import ScriptEditor from '@/views/lead/ScriptEditor.vue'
import FinalAudit from '@/views/lead/FinalAudit.vue'
import MemberDashboard from '@/views/member/Dashboard.vue'
import ChapterBreakdown from '@/views/member/ChapterBreakdown.vue'
import StoryboardEditor from '@/views/member/StoryboardEditor.vue'
import MaterialSelection from '@/views/member/MaterialSelection.vue'
import FirstAudit from '@/views/member/FirstAudit.vue'
import VideoComposition from '@/views/member/VideoComposition.vue'
import ProjectDetail from '@/views/projects/ProjectDetail.vue'

const routes: RouteRecordRaw[] = [
  // 重定向
  {
    path: '/',
    redirect: '/dashboard',
  },

  // 认证路由
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
      },
      {
        path: 'logout',
        name: 'Logout',
        beforeEnter: async (to, from, next) => {
          const authStore = useAuthStore()
          await authStore.logout()
          next({ name: 'Login' })
        },
      },
    ],
  },

  // 主应用路由
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      // 通用仪表盘
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
      },

      // 管理后台
      {
        path: 'admin',
        redirect: '/admin/users',
        meta: { requiresAdmin: true },
        children: [
          {
            path: 'users',
            name: 'AdminUsers',
            component: UserManagement,
          },
          {
            path: 'projects',
            name: 'AdminProjects',
            component: ProjectManagement,
          },
          {
            path: 'models',
            name: 'AdminModels',
            component: ModelConfig,
          },
        ],
      },

      // 组长工作台
      {
        path: 'lead',
        redirect: '/lead/dashboard',
        meta: { requiresTeamLead: true },
        children: [
          {
            path: 'dashboard',
            name: 'LeadDashboard',
            component: LeadDashboard,
          },
          {
            path: 'projects/:projectId/scripts',
            name: 'LeadScripts',
            component: ScriptEditor,
          },
          {
            path: 'audits/final',
            name: 'LeadFinalAudit',
            component: FinalAudit,
          },
        ],
      },

      // 组员工作台
      {
        path: 'member',
        redirect: '/member/dashboard',
        meta: { requiresTeamMember: true },
        children: [
          {
            path: 'dashboard',
            name: 'MemberDashboard',
            component: MemberDashboard,
          },
          {
            path: 'projects/:projectId/chapters',
            name: 'MemberChapters',
            component: ChapterBreakdown,
          },
          {
            path: 'projects/:projectId/storyboards',
            name: 'MemberStoryboards',
            component: StoryboardEditor,
          },
          {
            path: 'projects/:projectId/materials',
            name: 'MemberMaterials',
            component: MaterialSelection,
          },
          {
            path: 'audits/first',
            name: 'MemberFirstAudit',
            component: FirstAudit,
          },
          {
            path: 'projects/:projectId/composition',
            name: 'MemberComposition',
            component: VideoComposition,
          },
        ],
      },

      // 项目路由
      {
        path: 'projects/:projectId',
        name: 'ProjectDetail',
        component: ProjectDetail,
        props: true,
      },
    ],
  },

  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 直接到登录页，不检查权限
  if (to.path === '/auth/login' || to.path === '/auth/logout') {
    next()
    return
  }

  // 初始化认证状态（仅在登录页之外的页面）
  if (!authStore.user && authStore.accessToken) {
    try {
      await authStore.initAuth()
    } catch (error) {
      // 初始化失败，清除认证状态，重定向到登录页
      next({ name: 'Login' })
      return
    }
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 检查管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' })
    return
  }

  // 检查组长权限
  if (to.meta.requiresTeamLead && !authStore.isTeamLead) {
    next({ name: 'Dashboard' })
    return
  }

  // 检查组员权限
  if (to.meta.requiresTeamMember && !authStore.isTeamMember) {
    next({ name: 'Dashboard' })
    return
  }

  // 已登录用户访问登录页，重定向到仪表盘
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
