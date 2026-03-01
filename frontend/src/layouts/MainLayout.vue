<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 class="sidebar-logo" v-if="!sidebarCollapsed">AI Manga</h2>
        <h2 class="sidebar-logo-short" v-else>AI</h2>
      </div>

      <!-- 项目选择器 -->
      <div class="sidebar-project" v-if="!sidebarCollapsed">
        <el-select v-model="currentProjectId" placeholder="选择项目" size="small">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </div>

      <!-- 导航菜单 -->
      <el-menu
        class="sidebar-nav"
        :default-active="route.path"
        :collapse="sidebarCollapsed"
        background-color="#001529"
        text-color="rgba(255, 255, 255, 0.65)"
        active-text-color="#fff"
        :unique-opened="false"
      >
        <template v-for="menu in menuItems" :key="menu.path">
          <el-menu-item
            v-if="!menu.children && canAccess(menu)"
            :index="menu.path"
            @click="$router.push(menu.path)"
          >
            <el-icon><component :is="menu.icon" /></el-icon>
            <span v-if="!sidebarCollapsed">{{ menu.title }}</span>
          </el-menu-item>

          <el-sub-menu v-else-if="menu.children && canAccess(menu)" :index="menu.path">
            <template #title>
              <el-icon><component :is="menu.icon" /></el-icon>
              <span v-if="!sidebarCollapsed">{{ menu.title }}</span>
            </template>
            <el-menu-item
              v-for="child in menu.children"
              :key="child.path"
              :index="child.path"
              @click="$router.push(child.path)"
            >
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>

      <!-- 底部用户信息 -->
      <div class="sidebar-footer">
        <el-dropdown trigger="click">
          <div class="user-info">
            <el-avatar :size="32" :icon="UserFilled" />
            <div class="user-details" v-if="!sidebarCollapsed">
              <div class="user-name">{{ user?.name }}</div>
              <div class="user-role">{{ roleLabel }}</div>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/dashboard')">
                <el-icon><HomeFilled /></el-icon>
                仪表盘
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="header-left">
          <el-button link @click="sidebarCollapsed = !sidebarCollapsed">
            <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="notifications" :hidden="notifications === 0">
            <el-button link :icon="Bell" />
          </el-badge>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'
import {
  UserFilled,
  HomeFilled,
  SwitchButton,
  Bell,
  Fold,
  Expand,
  Grid,
  User,
  FolderOpened,
  Setting,
  Document,
  VideoCamera,
  Picture,
  Mic,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const sidebarCollapsed = ref(false)
const currentProjectId = ref<number | undefined>()

const user = computed(() => authStore.user)
const projects = computed(() => projectStore.projects)
const notifications = ref(3)

const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    team_lead: '组长',
    team_member: '组员',
  }
  return roleMap[user.value?.role || ''] || ''
})

// 菜单配置
const menuItems = computed(() => {
  const commonMenus = [
    {
      path: '/dashboard',
      title: '仪表盘',
      icon: Grid,
    },
  ]

  if (authStore.isAdmin) {
    return [
      ...commonMenus,
      {
        path: '/admin',
        title: '系统管理',
        icon: Setting,
        children: [
          { path: '/admin/users', title: '用户管理' },
          { path: '/admin/projects', title: '项目管理' },
          { path: '/admin/models', title: '模型配置' },
        ],
      },
    ]
  }

  if (authStore.isTeamLead) {
    return [
      ...commonMenus,
      {
        path: '/lead',
        title: '我的工作',
        icon: Document,
        children: [
          { path: '/lead/dashboard', title: '工作台' },
          { path: '/lead/audits/final', title: '终审' },
        ],
      },
      {
        path: '/projects',
        title: '项目',
        icon: FolderOpened,
      },
    ]
  }

  if (authStore.isTeamMember) {
    return [
      ...commonMenus,
      {
        path: '/member',
        title: '生产流程',
        icon: VideoCamera,
        children: [
          { path: '/member/dashboard', title: '我的任务' },
          { path: '/member/audits/first', title: '一审' },
          { path: '/member/projects', title: '项目' },
        ],
      },
    ]
  }

  return commonMenus
})

const breadcrumbs = computed(() => {
  const matched = route.matched.filter((r) => r.meta?.title)
  return matched.map((r) => ({
    path: r.path,
    title: r.meta.title as string,
  }))
})

// 权限检查
function canAccess(menu: { path?: string; roles?: string[] }) {
  if (!menu.roles) return true
  return menu.roles.includes(user.value?.role || '')
}

// 监听认证状态，认证成功后获取项目列表
watch(
  () => authStore.isAuthenticated,
  (isAuth) => {
    if (isAuth) {
      projectStore.fetchProjects()
    }
  }
)

// 切换项目
watch(currentProjectId, (newId) => {
  if (newId) {
    projectStore.fetchProject(newId)
  }
})

// 初始化 - 在组件挂载时检查认证状态并获取项目列表
onMounted(() => {
  if (authStore.isAuthenticated) {
    projectStore.fetchProjects()
  }
})

// 退出登录
async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: $sidebar-width;
  background: #001529;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;

  &.collapsed {
    width: 64px;
  }
}

.sidebar-header {
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.sidebar-logo-short {
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.sidebar-project {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  border-right: none !important;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    &:hover {
      background-color: rgba(255, 255, 255, 0.08) !important;
      color: white !important;
    }

    &.is-active {
      background-color: $primary-color !important;
      color: white !important;
    }
  }
}

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.user-role {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: $header-height;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.content {
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
