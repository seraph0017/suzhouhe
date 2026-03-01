<template>
  <div class="lead-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon projects">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.project_count }}</div>
              <div class="stat-label">负责项目</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon scripts">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.script_count }}</div>
              <div class="stat-label">剧本总数</div>
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
              <div class="stat-label">待终审</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon members">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.team_members }}</div>
              <div class="stat-label">团队成员</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧：项目进度 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>项目进度</span>
              <el-button link type="primary" @click="goToProjects">
                <el-icon><Plus /></el-icon>
                新建项目
              </el-button>
            </div>
          </template>

          <el-table v-loading="projectsLoading" :data="projects" style="width: 100%">
            <el-table-column prop="name" label="项目名称" min-width="180" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="projectStatusType(row.status)" size="small">
                  {{ projectStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :stroke-width="12" />
              </template>
            </el-table-column>
            <el-table-column prop="team_members" label="团队成员" width="120" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="goToProject(r)">
                  详情
                </el-button>
                <el-button link type="success" size="small" @click="goToScripts(r)">
                  剧本
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 剧本快速入口 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>最近剧本</span>
              <el-button link type="primary" @click="goToScripts">
                查看全部
              </el-button>
            </div>
          </template>

          <div v-loading="scriptsLoading" class="script-list">
            <el-empty v-if="recentScripts.length === 0" description="暂无剧本" />
            <div v-else class="script-items">
              <div
                v-for="script in recentScripts"
                :key="script.id"
                class="script-item"
                @click="goToScriptDetail(script)"
              >
                <div class="script-info">
                  <h4>{{ script.title }}</h4>
                  <p>{{ script.summary || '无摘要' }}</p>
                </div>
                <div class="script-meta">
                  <el-tag :type="script.is_locked ? 'success' : 'info'" size="small">
                    {{ script.is_locked ? '已锁定' : '草稿' }}
                  </el-tag>
                  <span class="time">{{ formatDate(script.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：待办和通知 -->
      <el-col :span="8">
        <!-- 待审核 -->
        <el-card>
          <template #header>
            <span>待终审</span>
          </template>

          <div v-loading="auditsLoading" class="audit-list">
            <el-empty v-if="pendingAudits.length === 0" description="暂无待审核" />
            <div v-else class="audit-items">
              <div
                v-for="audit in pendingAudits"
                :key="audit.id"
                class="audit-item"
                @click="goToFinalAudit(audit)"
              >
                <div class="audit-header">
                  <span class="audit-title">{{ audit.chapter_title }}</span>
                  <el-tag type="warning" size="small">待审核</el-tag>
                </div>
                <div class="audit-info">
                  <span>项目：{{ audit.project_name }}</span>
                  <span>提交：{{ formatDate(audit.submitted_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 团队动态 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>团队动态</span>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  FolderOpened,
  Document,
  DocumentChecked,
  User,
  Plus,
} from '@element-plus/icons-vue'
import { api } from '@/services/api'

const router = useRouter()

const stats = ref({
  project_count: 0,
  script_count: 0,
  pending_audits: 0,
  team_members: 0,
})

const projectsLoading = ref(false)
const projects = ref<any[]>([])

const scriptsLoading = ref(false)
const recentScripts = ref<any[]>([])

const auditsLoading = ref(false)
const pendingAudits = ref<any[]>([])

const activities = ref<any[]>([])

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
    stats.value = response.data || { project_count: 0, script_count: 0, pending_audits: 0, team_members: 0 }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchProjects = async () => {
  projectsLoading.value = true
  try {
    const response = await api.dashboard.getProjects()
    projects.value = response.data?.items || response.data || []
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  } finally {
    projectsLoading.value = false
  }
}

const fetchRecentScripts = async () => {
  scriptsLoading.value = true
  try {
    // 获取所有项目的剧本
    const response = await api.scripts.list(1) // TODO: Get from all projects
    recentScripts.value = (response.data || response).slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch scripts:', error)
  } finally {
    scriptsLoading.value = false
  }
}

const fetchPendingAudits = async () => {
  auditsLoading.value = true
  try {
    const response = await api.audits.listPending('second')
    pendingAudits.value = response.data || response
  } catch (error) {
    console.error('Failed to fetch audits:', error)
  } finally {
    auditsLoading.value = false
  }
}

const goToProjects = () => {
  router.push('/admin/projects')
}

const goToProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

const goToScripts = () => {
  if (projects.value.length > 0) {
    router.push(`/lead/projects/${projects.value[0].id}/scripts`)
  }
}

const goToScriptDetail = (script: any) => {
  // Find project for this script
  router.push(`/lead/projects/${script.project_id}/scripts?script_id=${script.id}`)
}

const goToFinalAudit = (audit: any) => {
  router.push(`/lead/audits/final?chapter_id=${audit.chapter_id}`)
}

onMounted(() => {
  fetchStats()
  fetchProjects()
  fetchRecentScripts()
  fetchPendingAudits()

  // Mock activities
  activities.value = [
    { id: 1, content: '张三 完成了《项目 A》的剧本创作', time: '10 分钟前' },
    { id: 2, content: '李四 提交了《项目 B》第一章审核', time: '30 分钟前' },
    { id: 3, content: '王五 通过了《项目 C》的终审', time: '1 小时前' },
  ]
})
</script>

<style scoped lang="scss">
.lead-dashboard {
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

          &.projects {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.scripts {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }

          &.audits {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }

          &.members {
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

  .script-list {
    min-height: 200px;

    .script-items {
      .script-item {
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

        .script-info {
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

        .script-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 4px;

          .time {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }
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

        .audit-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .audit-title {
            font-size: 14px;
            font-weight: 500;
            color: #333;
          }
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

  .activity-timeline {
    :deep(.el-timeline-item__content) {
      font-size: 13px;
      color: #666;
    }
  }
}
</style>
