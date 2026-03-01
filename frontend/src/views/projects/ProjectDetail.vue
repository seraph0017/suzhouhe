<template>
  <div class="project-detail">
    <!-- 项目头部 -->
    <el-card class="project-header-card">
      <div class="project-header">
        <div class="project-info">
          <h1>{{ project.name }}</h1>
          <p class="description">{{ project.description || '暂无描述' }}</p>
          <div class="meta-info">
            <span>
              <el-icon><User /></el-icon>
              负责人：{{ project.team_lead?.name || '未设置' }}
            </span>
            <span>
              <el-icon><Calendar /></el-icon>
              创建时间：{{ formatDate(project.created_at) }}
            </span>
            <el-tag :type="projectStatusType(project.status)">
              {{ projectStatusLabel(project.status) }}
            </el-tag>
          </div>
        </div>
        <div class="project-actions">
          <el-button type="primary" @click="handleEditProject">编辑项目</el-button>
          <el-button @click="handleMembers">团队成员</el-button>
        </div>
      </div>
    </el-card>

    <!-- 项目进度 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>项目进度</span>
          </template>

          <div class="progress-steps">
            <div
              v-for="(step, index) in pipelineSteps"
              :key="step.id"
              class="step-item"
              :class="{ active: currentStep >= index, completed: currentStep > index }"
            >
              <div class="step-circle">
                <el-icon v-if="currentStep > index"><Check /></el-icon>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="step-info">
                <div class="step-name">{{ step.name }}</div>
                <div class="step-desc">{{ step.description }}</div>
              </div>
            </div>
          </div>

          <el-progress :percentage="projectProgress" :stroke-width="20" />
        </el-card>

        <!-- 剧本列表 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>剧本列表</span>
              <el-button type="primary" size="small" @click="goToScriptEditor">
                <el-icon><Plus /></el-icon>
                新建剧本
              </el-button>
            </div>
          </template>

          <el-table v-loading="scriptsLoading" :data="scripts" style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="version" label="版本" width="80" />
            <el-table-column prop="is_locked" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_locked ? 'success' : 'info'" size="small">
                  {{ row.is_locked ? '已锁定' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="goToScript(row.id)">
                  {{ row.is_locked ? '查看' : '编辑' }}
                </el-button>
                <el-button link type="success" size="small" v-if="row.is_locked" @click="goToChapters(row.id)">
                  章节
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 章节列表 -->
        <el-card style="margin-top: 20px" v-if="selectedScript">
          <template #header>
            <span>章节列表 - {{ selectedScript.title }}</span>
          </template>

          <el-table v-loading="chaptersLoading" :data="chapters" style="width: 100%">
            <el-table-column prop="order" label="序号" width="80" />
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="chapterStatusType(row.status)" size="small">
                  {{ chapterStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="goToStoryboards(row.id)">
                  分镜
                </el-button>
                <el-button link type="success" size="small" @click="viewChapter(row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：团队成员和活动 -->
      <el-col :span="8">
        <!-- 团队成员 -->
        <el-card>
          <template #header>
            <div class="card-header">
              <span>团队成员</span>
              <el-button link type="primary" @click="handleMembers">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>

          <div class="member-list">
            <div
              v-for="member in members"
              :key="member.id"
              class="member-item"
            >
              <div class="member-avatar">
                <el-icon :size="24"><User /></el-icon>
              </div>
              <div class="member-info">
                <div class="member-name">{{ member.name }}</div>
                <div class="member-role">{{ memberRoleLabel(member.role) }}</div>
              </div>
              <el-tag v-if="member.id === project.team_lead_id" type="success" size="small">组长</el-tag>
            </div>
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

    <!-- 编辑项目对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑项目" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="editForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item label="项目状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="规划中" value="planning" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="暂停" value="on_hold" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Calendar, Plus, Check } from '@element-plus/icons-vue'
import { api } from '@/services/api'

const route = useRoute()
const router = useRouter()

const projectId = computed(() => Number(route.params.projectId))

const project = ref<any>({
  id: 0,
  name: '',
  description: '',
  status: 'planning',
  team_lead_id: null,
  team_lead: null,
  created_at: '',
})

const editDialogVisible = ref(false)
const editForm = reactive({
  name: '',
  description: '',
  status: '',
})

const scriptsLoading = ref(false)
const scripts = ref<any[]>([])
const selectedScript = ref<any>(null)

const chaptersLoading = ref(false)
const chapters = ref<any[]>([])

const members = ref<any[]>([])
const activities = ref<any[]>([])

const pipelineSteps = [
  { id: 1, name: '剧本基座', description: 'LLM 生成或上传剧本' },
  { id: 2, name: '剧本精调', description: '交互式调整剧本' },
  { id: 3, name: '章节拆解', description: '自动生成章节结构' },
  { id: 4, name: '分镜创作', description: '生成镜头脚本' },
  { id: 5, name: '素材生成', description: '图片 +TTS 生成' },
  { id: 6, name: '视频生成', description: '口型同步视频' },
  { id: 7, name: '智能合成', description: '添加字幕+BGM' },
  { id: 8, name: '章节封装', description: '合成章节视频' },
]

const currentStep = ref(2)

const projectProgress = computed(() => {
  return (currentStep.value / pipelineSteps.length) * 100
})

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

const chapterStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成',
    approved: '已通过',
  }
  return labels[status] || status
}

const chapterStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: 'info',
    in_progress: 'warning',
    completed: 'success',
    approved: '',
  }
  return types[status] || ''
}

const memberRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    admin: '管理员',
    team_lead: '组长',
    team_member: '组员',
  }
  return labels[role] || role
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const fetchProject = async () => {
  try {
    const response = await api.projects.get(projectId.value)
    project.value = response.data
    editForm.name = response.data.name
    editForm.description = response.data.description || ''
    editForm.status = response.data.status
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    console.error(error)
  }
}

const fetchScripts = async () => {
  scriptsLoading.value = true
  try {
    const response = await api.scripts.list(projectId.value)
    scripts.value = response.data || response
  } catch (error) {
    console.error('Failed to fetch scripts:', error)
  } finally {
    scriptsLoading.value = false
  }
}

const fetchChapters = async (scriptId: number) => {
  chaptersLoading.value = true
  try {
    const response = await api.chapters.list(scriptId)
    chapters.value = response.data || response
  } catch (error) {
    console.error('Failed to fetch chapters:', error)
  } finally {
    chaptersLoading.value = false
  }
}

const fetchMembers = async () => {
  try {
    const response = await api.projects.getMembers(projectId.value)
    members.value = response.data || response
  } catch (error) {
    console.error('Failed to fetch members:', error)
  }
}

const handleEditProject = () => {
  editDialogVisible.value = true
}

const saveProject = async () => {
  try {
    await api.projects.update(projectId.value, editForm)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    fetchProject()
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

const handleMembers = () => {
  ElMessage.info('团队成员功能开发中')
}

const goToScriptEditor = () => {
  router.push(`/lead/projects/${projectId.value}/scripts`)
}

const goToScript = (scriptId: number) => {
  router.push(`/lead/projects/${projectId.value}/scripts?script_id=${scriptId}`)
}

const goToChapters = (scriptId: number) => {
  selectedScript.value = scripts.value.find(s => s.id === scriptId)
  fetchChapters(scriptId)
}

const goToStoryboards = (chapterId: number) => {
  router.push(`/member/projects/${projectId.value}/storyboards?chapter_id=${chapterId}`)
}

const viewChapter = (chapter: any) => {
  ElMessage.info(`查看章节：${chapter.title}`)
}

onMounted(() => {
  fetchProject()
  fetchScripts()
  fetchMembers()

  // Mock activities
  activities.value = [
    { id: 1, content: '项目已创建', time: '2026-03-01 09:00' },
    { id: 2, content: '剧本已创建', time: '2026-03-01 10:00' },
    { id: 3, content: '章节已生成', time: '2026-03-01 11:00' },
  ]
})
</script>

<style scoped lang="scss">
.project-detail {
  .project-header-card {
    .project-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .project-info {
        h1 {
          margin: 0 0 8px;
          font-size: 24px;
          color: #333;
        }

        .description {
          margin: 0 0 12px;
          font-size: 14px;
          color: #666;
        }

        .meta-info {
          display: flex;
          gap: 16px;
          font-size: 13px;
          color: #999;
          align-items: center;
        }
      }

      .project-actions {
        display: flex;
        gap: 8px;
      }
    }
  }

  .progress-steps {
    display: flex;
    margin-bottom: 20px;
    overflow-x: auto;

    .step-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      opacity: 0.5;
      transition: all 0.2s;

      &.active {
        opacity: 1;
      }

      &.completed {
        opacity: 0.8;
      }

      .step-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #e8e8e8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;

        .el-icon {
          color: white;
        }
      }

      &.completed .step-circle {
        background: #67c23a;
      }

      &.active .step-circle {
        background: #409eff;
        color: white;
      }

      .step-info {
        .step-name {
          font-size: 13px;
          font-weight: 600;
          color: #333;
        }

        .step-desc {
          font-size: 11px;
          color: #999;
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .member-list {
    .member-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .member-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
      }

      .member-info {
        flex: 1;

        .member-name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        .member-role {
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
