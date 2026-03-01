<template>
  <div class="member-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon tasks">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.my_tasks }}</div>
              <div class="stat-label">我的任务</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_tasks }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon progress">
              <el-icon><Finished /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.in_progress }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧：任务列表 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的任务</span>
              <el-radio-group v-model="taskFilter" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="pending">待处理</el-radio-button>
                <el-radio-button label="in_progress">进行中</el-radio-button>
                <el-radio-button label="completed">已完成</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <el-table v-loading="tasksLoading" :data="filteredTasks" style="width: 100%">
            <el-table-column prop="task_type" label="任务类型" width="120" />
            <el-table-column prop="project_name" label="项目" min-width="150" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="priorityType(row.priority)" size="small">
                  {{ priorityLabel(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="截止日期" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleTask(row)">
                  {{ row.status === 'completed' ? '查看' : '处理' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 参与项目 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>参与项目</span>
          </template>

          <div v-loading="projectsLoading" class="project-list">
            <el-empty v-if="projects.length === 0" description="暂无参与项目" />
            <div v-else class="project-items">
              <div
                v-for="project in projects"
                :key="project.id"
                class="project-item"
                @click="goToProject(project)"
              >
                <div class="project-info">
                  <h4>{{ project.name }}</h4>
                  <p>{{ project.description || '暂无描述' }}</p>
                </div>
                <div class="project-meta">
                  <el-tag :type="projectStatusType(project.status)" size="small">
                    {{ projectStatusLabel(project.status) }}
                  </el-tag>
                  <span class="progress">{{ project.progress }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快捷操作和通知 -->
      <el-col :span="8">
        <!-- 快捷操作 -->
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>

          <div class="quick-actions">
            <el-button @click="goToFirstAudit" style="width: 100%; margin-bottom: 8px">
              <el-icon><DocumentChecked /></el-icon>
              一审工作台
            </el-button>
            <el-button @click="goToChapters" style="width: 100%; margin-bottom: 8px">
              <el-icon><FolderOpened /></el-icon>
              章节拆解
            </el-button>
            <el-button @click="goToStoryboards" style="width: 100%; margin-bottom: 8px">
              <el-icon><Picture /></el-icon>
              分镜创作
            </el-button>
            <el-button @click="goToMaterials" style="width: 100%; margin-bottom: 8px">
              <el-icon><MagicStick /></el-icon>
              素材选择
            </el-button>
            <el-button @click="goToComposition" style="width: 100%">
              <el-icon><VideoCamera /></el-icon>
              视频合成
            </el-button>
          </div>
        </el-card>

        <!-- 待审核（一审） -->
        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>待一审</span>
              <el-tag type="warning" size="small">{{ pendingFirstAudits.length }}</el-tag>
            </div>
          </template>

          <div v-loading="auditsLoading" class="audit-list">
            <el-empty v-if="pendingFirstAudits.length === 0" description="暂无待审核" />
            <div v-else class="audit-items">
              <div
                v-for="audit in pendingFirstAudits"
                :key="audit.id"
                class="audit-item"
                @click="goToFirstAuditDetail(audit)"
              >
                <div class="audit-title">{{ audit.storyboard?.visual_description || '分镜审核' }}</div>
                <div class="audit-info">
                  <span>{{ audit.project_name }}</span>
                  <span>{{ formatDate(audit.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 通知 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>通知</span>
          </template>

          <div class="notification-list">
            <div
              v-for="notif in notifications"
              :key="notif.id"
              class="notification-item"
              :class="{ unread: !notif.read }"
            >
              <div class="notif-icon">
                <el-icon :size="16"><Bell /></el-icon>
              </div>
              <div class="notif-content">
                <p class="notif-title">{{ notif.title }}</p>
                <p class="notif-time">{{ notif.time }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  List,
  Clock,
  Finished,
  CircleCheck,
  DocumentChecked,
  FolderOpened,
  Picture,
  MagicStick,
  VideoCamera,
  Bell,
} from '@element-plus/icons-vue'
import { api } from '@/services/api'

const router = useRouter()

const stats = ref({
  my_tasks: 0,
  pending_tasks: 0,
  in_progress: 0,
  completed: 0,
})

const tasksLoading = ref(false)
const tasks = ref<any[]>([])
const taskFilter = ref('pending')

const projectsLoading = ref(false)
const projects = ref<any[]>([])

const auditsLoading = ref(false)
const pendingFirstAudits = ref<any[]>([])

const notifications = ref<any[]>([])

const filteredTasks = computed(() => {
  if (taskFilter.value === 'all') return tasks.value
  return tasks.value.filter(t => t.status === taskFilter.value)
})

const priorityLabel = (priority: string) => {
  const labels: Record<string, string> = {
    urgent: '紧急',
    high: '高',
    normal: '普通',
    low: '低',
  }
  return labels[priority] || priority
}

const priorityType = (priority: string) => {
  const types: Record<string, any> = {
    urgent: 'danger',
    high: 'warning',
    normal: '',
    low: 'info',
  }
  return types[priority] || ''
}

const statusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
  }
  return labels[status] || status
}

const statusType = (status: string) => {
  const types: Record<string, any> = {
    pending: 'warning',
    in_progress: 'success',
    completed: '',
  }
  return types[status] || ''
}

const projectStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    planning: '规划中',
    in_progress: '进行中',
    on_hold: '暂停',
    completed: '已完成',
    archived: '已归档',
  }
  return labels[status] || status
}

const projectStatusType = (status: string) => {
  const types: Record<string, any> = {
    planning: 'info',
    in_progress: 'success',
    on_hold: 'warning',
    completed: '',
    archived: 'info',
  }
  return types[status] || ''
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const fetchStats = async () => {
  try {
    const response = await api.dashboard.getStats()
    stats.value = response.data || { my_tasks: 0, pending_tasks: 0, in_progress: 0, completed: 0 }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchTasks = async () => {
  tasksLoading.value = true
  try {
    const response = await api.dashboard.getTasks()
    tasks.value = response.data?.items || response.data || []
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    tasksLoading.value = false
  }
}

const fetchProjects = async () => {
  projectsLoading.value = true
  try {
    const response = await api.projects.list()
    projects.value = (response.data?.items || response.data || []).slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  } finally {
    projectsLoading.value = false
  }
}

const fetchPendingAudits = async () => {
  auditsLoading.value = true
  try {
    const response = await api.audits.listPending('first')
    pendingFirstAudits.value = response.data || response
  } catch (error) {
    console.error('Failed to fetch audits:', error)
  } finally {
    auditsLoading.value = false
  }
}

const handleTask = (task: any) => {
  if (task.task_type === '分镜创作') {
    goToStoryboards()
  } else if (task.task_type === '一审') {
    goToFirstAudit()
  } else if (task.task_type === '章节拆解') {
    goToChapters()
  } else if (task.task_type === '素材选择') {
    goToMaterials()
  } else if (task.task_type === '视频合成') {
    goToComposition()
  } else {
    ElMessage.info(`处理任务：${task.task_type}`)
  }
}

const goToProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

const goToFirstAudit = () => {
  router.push('/member/audits/first')
}

const goToFirstAuditDetail = (audit: any) => {
  router.push({ path: '/member/audits/first', query: { storyboard_id: audit.storyboard_id } })
}

const goToChapters = () => {
  if (projects.value.length > 0) {
    router.push(`/member/projects/${projects.value[0].id}/chapters`)
  }
}

const goToStoryboards = () => {
  if (projects.value.length > 0) {
    router.push(`/member/projects/${projects.value[0].id}/storyboards`)
  }
}

const goToMaterials = () => {
  if (projects.value.length > 0) {
    router.push(`/member/projects/${projects.value[0].id}/materials`)
  }
}

const goToComposition = () => {
  if (projects.value.length > 0) {
    router.push(`/member/projects/${projects.value[0].id}/composition`)
  }
}

onMounted(() => {
  fetchStats()
  fetchTasks()
  fetchProjects()
  fetchPendingAudits()

  // Mock notifications
  notifications.value = [
    { id: 1, title: '新任务已分配：分镜创作', time: '10 分钟前', read: false },
    { id: 2, title: '《项目 A》第一章已提交审核', time: '30 分钟前', read: false },
    { id: 3, title: '系统通知：本周将进行系统维护', time: '2 小时前', read: true },
  ]
})
</script>

<style scoped lang="scss">
.member-dashboard {
  .stats-row {
    .stat-card {
      :deep(.el-card__body) {
        padding: 20px;
      }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          color: white;

          &.tasks {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.pending {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }

          &.progress {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }

          &.completed {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }
        }

        .stat-info {
          .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #333;
          }

          .stat-label {
            font-size: 13px;
            color: #999;
            margin-top: 4px;
          }
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .project-list {
    min-height: 200px;

    .project-items {
      .project-item {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #fafafa;
        }

        &:last-child {
          border-bottom: none;
        }

        .project-info {
          flex: 1;

          h4 {
            margin: 0 0 4px;
            font-size: 15px;
            color: #333;
          }

          p {
            margin: 0;
            font-size: 13px;
            color: #999;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
        }

        .project-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 4px;

          .progress {
            font-size: 12px;
            color: #409eff;
            font-weight: 600;
          }
        }
      }
    }
  }

  .quick-actions {
    display: flex;
    flex-direction: column;
  }

  .audit-list {
    min-height: 150px;

    .audit-items {
      .audit-item {
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #fafafa;
        }

        &:last-child {
          border-bottom: none;
        }

        .audit-title {
          font-size: 14px;
          color: #333;
          margin-bottom: 4px;
          display: -webkit-box;
          -webkit-line-clamp: 1;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .audit-info {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #999;
        }
      }
    }
  }

  .notification-list {
    .notification-item {
      display: flex;
      gap: 12px;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      &.unread {
        background: #f5f7fa;
        margin: 0 -12px;
        padding: 12px;
        border-radius: 8px;
      }

      .notif-icon {
        color: #409eff;
      }

      .notif-content {
        flex: 1;

        .notif-title {
          font-size: 14px;
          color: #333;
          margin: 0 0 4px;
        }

        .notif-time {
          font-size: 12px;
          color: #999;
          margin: 0;
        }
      }
    }
  }
}
</style>
