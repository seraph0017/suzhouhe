<template>
  <div class="script-editor">
    <div class="toolbar">
      <div class="breadcrumb">
        <el-button link @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span class="project-name">{{ projectName }}</span>
        <el-icon><ArrowRight /></el-icon>
        <span>剧本管理</span>
      </div>

      <div class="actions">
        <el-button @click="fetchScripts">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建剧本
        </el-button>
        <el-button
          v-if="currentScript && !currentScript.is_locked"
          type="success"
          @click="handleLockScript"
        >
          <el-icon><Lock /></el-icon>
          锁定剧本
        </el-button>
        <el-button
          v-if="currentScript && currentScript.is_locked"
          type="warning"
          @click="handleUnlockScript"
        >
          <el-icon><Unlock /></el-icon>
          解锁剧本
        </el-button>
      </div>
    </div>

    <!-- 剧本列表 -->
    <el-card class="script-list-card" v-if="!currentScript">
      <template #header>
        <span>剧本列表</span>
      </template>

      <el-table v-loading="loading" :data="scripts" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="scriptStatusType(row.status)" size="small">
              {{ scriptStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_locked" label="锁定" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_locked ? 'danger' : 'info'" size="small">
              {{ row.is_locked ? '已锁定' : '未锁定' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="selectScript(row)">
              {{ row.is_locked ? '查看' : '编辑' }}
            </el-button>
            <el-button
              v-if="!row.is_locked"
              link
              type="success"
              size="small"
              @click="handleLockScript(row)"
            >
              锁定
            </el-button>
            <el-button
              v-if="!row.is_locked"
              link
              type="danger"
              size="small"
              @click="handleDeleteScript(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 剧本编辑器 -->
    <el-card v-else class="editor-card">
      <template #header>
        <div class="editor-header">
          <div class="title-row">
            <el-input
              v-model="currentScript.title"
              placeholder="剧本标题"
              size="large"
              :disabled="currentScript.is_locked"
              style="width: 400px"
            />
            <el-tag :type="scriptStatusType(currentScript.status)">
              {{ scriptStatusLabel(currentScript.status) }}
            </el-tag>
            <el-tag v-if="currentScript.is_locked" type="danger">已锁定</el-tag>
          </div>
          <div class="version-info">
            版本：v{{ currentScript.version }}
            <el-button link type="primary" @click="showVersionHistory = true">
              历史记录
            </el-button>
          </div>
        </div>
      </template>

      <!-- LLM 生成按钮 -->
      <div v-if="!currentScript.is_locked" class="llm-tools">
        <el-button type="primary" @click="showLLMDialog = true">
          <el-icon><MagicStick /></el-icon>
          AI 生成剧本
        </el-button>
      </div>

      <!-- 内容编辑器 -->
      <el-input
        v-model="currentScript.content"
        type="textarea"
        :rows="20"
        placeholder="在此输入剧本内容..."
        :disabled="currentScript.is_locked"
        @change="onContentChange"
      />

      <!-- 摘要 -->
      <div class="summary-section">
        <label>剧本摘要</label>
        <el-input
          v-model="currentScript.summary"
          placeholder="简短描述剧本内容（可选）"
          :disabled="currentScript.is_locked"
          @change="onContentChange"
        />
      </div>

      <!-- 保存按钮 -->
      <div v-if="hasUnsavedChanges && !currentScript.is_locked" class="save-bar">
        <span class="unsaved-hint">内容已修改，请保存</span>
        <el-button type="primary" size="small" @click="saveScript">保存更改</el-button>
      </div>
    </el-card>

    <!-- LLM 生成对话框 -->
    <el-dialog v-model="showLLMDialog" title="AI 生成剧本" width="600px">
      <el-form :model="llmForm" label-width="100px">
        <el-form-item label="故事主题">
          <el-input v-model="llmForm.theme" placeholder="例如：校园爱情、科幻冒险..." />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="llmForm.genre" placeholder="请选择类型" style="width: 100%">
            <el-option label="爱情" value="romance" />
            <el-option label="冒险" value="adventure" />
            <el-option label="科幻" value="sci-fi" />
            <el-option label="悬疑" value="mystery" />
            <el-option label="喜剧" value="comedy" />
            <el-option label="奇幻" value="fantasy" />
          </el-select>
        </el-form-item>
        <el-form-item label="语调">
          <el-select v-model="llmForm.tone" placeholder="请选择语调" style="width: 100%">
            <el-option label="轻松幽默" value="humorous" />
            <el-option label="严肃紧张" value="serious" />
            <el-option label="温馨感人" value="heartwarming" />
            <el-option label="悬疑烧脑" value="suspenseful" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计长度">
          <el-select v-model="llmForm.length" placeholder="请选择长度" style="width: 100%">
            <el-option label="短篇 (1000 字)" :value="1000" />
            <el-option label="中篇 (3000 字)" :value="3000" />
            <el-option label="长篇 (5000 字)" :value="5000" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLLMDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleLLMGenerate">
          开始生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 版本历史对话框 -->
    <el-dialog v-model="showVersionHistory" title="版本历史" width="800px">
      <el-timeline>
        <el-timeline-item
          v-for="version in versions"
          :key="version.id"
          :timestamp="formatDate(version.created_at)"
          placement="top"
        >
          <el-card>
            <h4>版本 v{{ version.version }}</h4>
            <p>{{ version.summary || '无摘要' }}</p>
            <el-button link type="primary" @click="restoreVersion(version)">
              恢复此版本
            </el-button>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  ArrowRight,
  Refresh,
  Plus,
  Lock,
  Unlock,
  MagicStick,
} from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { Script, ScriptVersion } from '@/types'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId))

const projectName = ref('项目')
const loading = ref(false)
const generating = ref(false)
const scripts = ref<Script[]>([])
const currentScript = ref<Script | null>(null)
const hasUnsavedChanges = ref(false)
const showLLMDialog = ref(false)
const showVersionHistory = ref(false)
const versions = ref<ScriptVersion[]>([])

const llmForm = reactive({
  theme: '',
  genre: 'adventure',
  tone: 'humorous',
  length: 3000,
})

const scriptStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    in_review: '审核中',
    locked: '已锁定',
    archived: '已归档',
  }
  return labels[status] || status
}

const scriptStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: 'info',
    in_review: 'warning',
    locked: 'danger',
    archived: 'info',
  }
  return types[status] || ''
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const fetchScripts = async () => {
  loading.value = true
  try {
    const response = await api.scripts.list(projectId.value)
    scripts.value = response.data
  } catch (error) {
    ElMessage.error('获取剧本列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const selectScript = (script: Script) => {
  currentScript.value = { ...script }
  hasUnsavedChanges.value = false
}

const openCreateDialog = async () => {
  try {
    const newScript = await api.scripts.create({
      project_id: projectId.value,
      title: '新剧本',
      content: '',
      summary: '',
    })
    ElMessage.success('剧本已创建')
    fetchScripts()
    selectScript(newScript)
  } catch (error) {
    ElMessage.error('创建剧本失败')
    console.error(error)
  }
}

const onContentChange = () => {
  hasUnsavedChanges.value = true
}

const saveScript = async () => {
  if (!currentScript.value) return

  try {
    await api.scripts.update(currentScript.value.id, {
      title: currentScript.value.title,
      content: currentScript.value.content,
      summary: currentScript.value.summary,
    })
    ElMessage.success('保存成功')
    hasUnsavedChanges.value = false
    fetchScripts()
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

const handleLockScript = async (script?: Script) => {
  const target = script || currentScript.value
  if (!target) return

  try {
    await ElMessageBox.confirm('锁定后将无法编辑，是否继续？', '提示', {
      type: 'warning',
    })

    await api.scripts.lock(target.id)
    ElMessage.success('剧本已锁定')
    fetchScripts()
    if (currentScript.value?.id === target.id) {
      selectScript({ ...target, is_locked: true })
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('锁定失败')
    }
  }
}

const handleUnlockScript = async () => {
  if (!currentScript.value) return

  try {
    await api.scripts.unlock(currentScript.value.id)
    ElMessage.success('剧本已解锁')
    fetchScripts()
    selectScript({ ...currentScript.value, is_locked: false })
  } catch (error) {
    ElMessage.error('解锁失败')
    console.error(error)
  }
}

const handleDeleteScript = async (script: Script) => {
  try {
    await ElMessageBox.confirm(`确定要删除剧本 "${script.title}" 吗？`, '警告', {
      type: 'warning',
    })

    await api.scripts.delete(script.id)
    ElMessage.success('删除成功')
    fetchScripts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleLLMGenerate = async () => {
  generating.value = true
  try {
    // TODO: Call actual LLM generation API
    await new Promise((resolve) => setTimeout(resolve, 3000))

    const generatedContent = `【${llmForm.theme}】剧本

类型：${llmForm.genre}
语调：${llmForm.tone}

---

第一幕：开端
场景：学校操场
时间：下午

[主角小明在操场上跑步，突然遇到了...]

（此处为 AI 生成的剧本内容，实际使用请调用 LLM API）
`

    if (currentScript.value) {
      currentScript.value.content = generatedContent
      currentScript.value.summary = `${llmForm.theme} - ${llmForm.genre}故事`
      hasUnsavedChanges.value = true
    } else {
      const newScript = await api.scripts.create({
        project_id: projectId.value,
        title: llmForm.theme,
        content: generatedContent,
        summary: `${llmForm.theme} - ${llmForm.genre}故事`,
      })
      selectScript(newScript)
    }

    ElMessage.success('剧本生成成功')
    showLLMDialog.value = false
    fetchScripts()
  } catch (error) {
    ElMessage.error('生成失败')
    console.error(error)
  } finally {
    generating.value = false
  }
}

const showVersionHistoryDialog = async () => {
  showVersionHistory.value = true
  // TODO: Fetch versions from API
  versions.value = []
}

const restoreVersion = (version: ScriptVersion) => {
  // TODO: Implement version restore
  console.log('Restore version:', version)
}

watch(() => showVersionHistory.value, (val) => {
  if (val) {
    showVersionHistoryDialog()
  }
})

onMounted(() => {
  fetchScripts()
})
</script>

<style scoped lang="scss">
.script-editor {
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .breadcrumb {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #666;

    .project-name {
      font-weight: 500;
      color: #333;
    }
  }

  .actions {
    display: flex;
    gap: 8px;
  }

  .script-list-card {
    margin-bottom: 20px;
  }

  .editor-card {
    .editor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .title-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .version-info {
      font-size: 14px;
      color: #666;
    }

    .llm-tools {
      margin-bottom: 16px;
    }

    .summary-section {
      margin-top: 16px;

      label {
        display: block;
        margin-bottom: 8px;
        font-size: 14px;
        color: #666;
      }
    }

    .save-bar {
      margin-top: 16px;
      padding: 12px;
      background: #f0f9eb;
      border-radius: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .unsaved-hint {
        color: #67c23a;
        font-size: 14px;
      }
    }
  }
}
</style>
