<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon projects">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_projects }}</div>
              <div class="stat-label">总项目</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon active">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active_projects }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-card>
      </el-col>

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
            <div class="stat-icon audits">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_audits }}</div>
              <div class="stat-label">待审核</div>
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
              <el-button link type="primary" @click="refreshTasks">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <el-tabs v-model="taskTab">
            <el-tab-pane label="待处理" name="pending">
              <el-table :data="pendingTasks" style="width: 100%">
                <el-table-column prop="task_type" label="类型" width="120" />
                <el-table-column prop="project_name" label="项目" min-width="150" />
                <el-table-column prop="priority" label="优先级" width="80">
                  <template #default="{ row }">
                    <el-tag :type="priorityType(row.priority)" size="small">
                      {{ priorityLabel(row.priority) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="due_date" label="截止日期" width="120" />
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="handleTask(row)">
                      处理
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="进行中" name="in_progress">
              <el-table :data="inProgressTasks" style="width: 100%">
                <el-table-column prop="task_type" label="类型" width="120" />
                <el-table-column prop="project_name" label="项目" min-width="150" />
                <el-table-column prop="progress" label="进度" width="100">
                  <template #default="{ row }">
                    <el-progress :percentage="row.progress" :stroke-width="12" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button link type="success" size="small" @click="handleComplete(row)">
                      完成
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="已完成" name="completed">
              <el-table :data="completedTasks" style="width: 100%">
                <el-table-column prop="task_type" label="类型" width="120" />
                <el-table-column prop="project_name" label="项目" min-width="150" />
                <el-table-column prop="completed_at" label="完成时间" width="150" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>

        <!-- 项目进度 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>项目进度</span>
          </template>

          <div class="project-progress-list">
            <div
              v-for="project in recentProjects"
              :key="project.id"
              class="project-progress-item"
              @click="goToProject(project.id)"
            >
              <div class="project-info">
                <h4>{{ project.name }}</h4>
                <p>{{ project.status_label }}</p>
              </div>
              <div class="progress-info">
                <el-progress
                  :percentage="project.progress"
                  :status="project.progress === 100 ? 'success' : undefined"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：通知和活动 -->
      <el-col :span="8">
        <!-- 通知 -->
        <el-card>
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
              <div class="notif-icon" :class="notif.type">
                <el-icon :size="16">
                  <component :is="notif.icon" />
                </el-icon>
              </div>
              <div class="notif-content">
                <p class="notif-title">{{ notif.title }}</p>
                <p class="notif-time">{{ notif.time }}</p>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 快捷入口 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>快捷入口</span>
          </template>

          <div class="quick-actions">
            <el-button
              v-for="action in quickActions"
              :key="action.label"
              :icon="action.icon"
              @click="action.handler"
            >
              {{ action.label }}
            </el-button>
          </div>
        </el-card>

        <!-- 最近活动 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>最近活动</span>
          </template>

          <el-timeline class="activity-timeline">
            <el-timeline-item
              v-for="activity in activities"
              :key="activity.id"
              :timestamp="activity.time"
              placement="top"
            >
              <p>{{ activity.content }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  FolderOpened,
  VideoCamera,
  List,
  DocumentChecked,
  Refresh,
  Bell,
  Document,
  CircleCheck,
  Clock,
  Plus,
  Check,
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const taskTab = ref('pending')

const stats = ref({
  total_projects: 0,
  active_projects: 0,
  my_tasks: 0,
  pending_audits: 0,
})

const tasks = ref<any[]>([])
const recentProjects = ref<any[]>([])
const notifications = ref<any[]>([])
const activities = ref<any[]>([])

const quickActions = [
  { label: '新建项目', icon: Plus, handler: () => router.push('/admin/projects') },
  { label: '剧本创作', icon: Document, handler: () => router.push('/lead/scripts') },
  { label: '一审', icon: Check, handler: () => router.push('/member/audits/first') },
  { label: '二审', icon: DocumentChecked, handler: () => router.push('/lead/audits/final') },
]

const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending'))
const inProgressTasks = computed(() => tasks.value.filter(t => t.status === 'in_progress'))
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed'))

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

const refreshTasks = () => {
  // TODO: Fetch from API
}

const handleTask = (task: any) => {
  // Navigate to task page based on task type
  console.log('Handle task:', task)
}

const handleComplete = (task: any) => {
  task.status = 'completed'
}

const goToProject = (projectId: number) => {
  router.push(`/projects/${projectId}`)
}

onMounted(() => {
  // Mock data
  stats.value = {
    total_projects: 5,
    active_projects: 3,
    my_tasks: 8,
    pending_audits: 4,
  }

  tasks.value = [
    { id: 1, task_type: '分镜创作', project_name: '项目 A', priority: 'high', due_date: '2026-03-05', status: 'pending', progress: 0 },
    { id: 2, task_type: '一审', project_name: '项目 B', priority: 'urgent', due_date: '2026-03-03', status: 'in_progress', progress: 60 },
    { id: 3, task_type: '素材生成', project_name: '项目 A', priority: 'normal', due_date: '2026-03-06', status: 'pending', progress: 0 },
  ]

  recentProjects.value = [
    { id: 1, name: '项目 A', status_label: '进行中', progress: 65 },
    { id: 2, name: '项目 B', status_label: '进行中', progress: 40 },
    { id: 3, name: '项目 C', status_label: '剧本阶段', progress: 20 },
  ]

  notifications.value = [
    { id: 1, type: 'task', icon: Bell, title: '新任务已分配', time: '10 分钟前', read: false },
    { id: 2, type: 'audit', icon: DocumentChecked, title: '一审已通过', time: '1 小时前', read: false },
    { id: 3, type: 'system', icon: Bell, title: '系统维护通知', time: '2 小时前', read: true },
  ]

  activities.value = [
    { id: 1, content: '用户 A 完成了分镜创作', time: '10:30' },
    { id: 2, content: '用户 B 通过了项目 A 的一审', time: '09:45' },
    { id: 3, content: '项目 C 已创建', time: '09:00' },
  ]
})
</script>

<style scoped lang="scss">
.dashboard {
  .stats-row {
    .stat-card {
      :deep(.el-card__body) {
        padding: 20px;
      }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;
      }

      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        color: white;

        &.projects {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        &.active {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        &.tasks {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        &.audits {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #333;
        }

        .stat-label {
          font-size: 14px;
          color: #666;
          margin-top: 4px;
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .project-progress-list {
    .project-progress-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        .project-info h4 {
          color: #409eff;
        }
      }

      .project-info {
        h4 {
          margin: 0 0 4px;
          font-size: 14px;
          color: #333;
          transition: color 0.2s;
        }

        p {
          margin: 0;
          font-size: 12px;
          color: #999;
        }
      }

      .progress-info {
        width: 150px;
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
        border-radius: 4px;
      }

      .notif-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        &.task {
          background: #e6f7ff;
          color: #1890ff;
        }

        &.audit {
          background: #f6ffed;
          color: #52c41a;
        }

        &.system {
          background: #fff7e6;
          color: #fa8c16;
        }
      }

      .notif-content {
        flex: 1;

        .notif-title {
          margin: 0 0 4px;
          font-size: 14px;
          color: #333;
        }

        .notif-time {
          margin: 0;
          font-size: 12px;
          color: #999;
        }
      }
    }
  }

  .quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .el-button {
      flex: 1;
      min-width: calc(50% - 4px);
    }
  }

  .activity-timeline {
    :deep(.el-timeline-item__content) {
      font-size: 13px;
      color: #666;
    }
  }
}
</style>
