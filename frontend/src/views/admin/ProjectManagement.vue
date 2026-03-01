<template>
  <div class="project-management">
    <el-card>
      <template #header>
        <div class="header">
          <span>项目管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目名称"
          style="width: 240px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterStatus" placeholder="项目状态" clearable style="width: 150px" @change="handleFilter">
          <el-option label="规划中" value="planning" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="暂停" value="on_hold" />
          <el-option label="已完成" value="completed" />
          <el-option label="已归档" value="archived" />
        </el-select>
      </div>

      <!-- 项目列表 -->
      <div v-loading="loading" class="project-list">
        <el-empty v-if="filteredProjects.length === 0" description="暂无项目" />

        <div v-else class="project-grid">
          <el-card
            v-for="project in filteredProjects"
            :key="project.id"
            class="project-card"
            @click="goToProject(project.id)"
          >
            <div class="project-header">
              <h3 class="project-name">{{ project.name }}</h3>
              <el-tag :type="projectStatusType(project.status)" size="small">
                {{ projectStatusLabel(project.status) }}
              </el-tag>
            </div>

            <p class="project-description">{{ project.description || '暂无描述' }}</p>

            <div class="project-footer">
              <div class="project-meta">
                <span class="meta-item">
                  <el-icon><User /></el-icon>
                  {{ project.team_lead?.name || '未设置' }}
                </span>
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(project.created_at) }}
                </span>
              </div>
            </div>

            <div class="project-actions">
              <el-button link type="primary" @click.stop="handleEdit(project)">编辑</el-button>
              <el-button link type="danger" @click.stop="handleArchive(project)">归档</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingProject ? '编辑项目' : '新建项目'"
      width="600px"
      @close="resetDialog"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>

        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述（可选）"
          />
        </el-form-item>

        <el-form-item label="项目状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="规划中" value="planning" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="暂停" value="on_hold" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, User, Calendar } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { Project, ProjectStatus } from '@/types'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const filterStatus = ref<string>('')

const projects = ref<Project[]>([])
const dialogVisible = ref(false)
const editingProject = ref<Project | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  name: '',
  description: '',
  status: 'planning' as ProjectStatus,
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在 2-50 个字符', trigger: 'blur' },
  ],
}

const filteredProjects = computed(() => {
  let result = projects.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((p) => p.name.toLowerCase().includes(query))
  }

  if (filterStatus.value) {
    result = result.filter((p) => p.status === filterStatus.value)
  }

  return result
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

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const response = await api.projects.list()
    projects.value = response.data.items || response.data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // Real-time search, no action needed
}

const handleFilter = () => {
  // Filter applied via computed property
}

const openCreateDialog = () => {
  editingProject.value = null
  dialogVisible.value = true
}

const handleEdit = (project: Project) => {
  editingProject.value = project
  formData.name = project.name
  formData.description = project.description || ''
  formData.status = project.status
  dialogVisible.value = true
}

const handleArchive = async (project: Project) => {
  try {
    await ElMessageBox.confirm(`确定要归档项目 "${project.name}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await api.projects.update(project.id, { status: 'archived' })
    ElMessage.success('归档成功')
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('归档失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const data = {
        name: formData.name,
        description: formData.description,
        status: formData.status,
      }

      if (editingProject.value) {
        await api.projects.update(editingProject.value.id, data)
        ElMessage.success('更新成功')
      } else {
        await api.projects.create(data)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      fetchProjects()
    } catch (error) {
      ElMessage.error(editingProject.value ? '更新失败' : '创建失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

const resetDialog = () => {
  editingProject.value = null
  formData.name = ''
  formData.description = ''
  formData.status = 'planning'
  formRef.value?.resetFields()
}

const goToProject = (projectId: number) => {
  router.push(`/projects/${projectId}`)
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped lang="scss">
.project-management {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .project-list {
    min-height: 400px;
  }

  .project-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }

  .project-card {
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .project-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }

    .project-name {
      font-size: 16px;
      font-weight: 600;
      margin: 0;
      color: #333;
    }

    .project-description {
      font-size: 14px;
      color: #666;
      margin-bottom: 16px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .project-footer {
      border-top: 1px solid #e8e8e8;
      padding-top: 12px;
    }

    .project-meta {
      display: flex;
      gap: 16px;
      font-size: 13px;
      color: #999;
    }

    .meta-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .project-actions {
      position: absolute;
      top: 12px;
      right: 12px;
      opacity: 0;
      transition: opacity 0.2s;
    }

    &:hover .project-actions {
      opacity: 1;
    }
  }
}
</style>
