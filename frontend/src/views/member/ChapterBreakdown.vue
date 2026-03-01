<template>
  <div class="chapter-breakdown">
    <div class="toolbar">
      <div class="breadcrumb">
        <el-button link @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span>剧本管理</span>
        <el-icon><ArrowRight /></el-icon>
        <span>章节拆解</span>
      </div>

      <div class="actions">
        <el-button :loading="generating" @click="handleAutoGenerate">
          <el-icon><MagicStick /></el-icon>
          AI 自动生成
        </el-button>
        <el-button type="primary" @click="handleAddChapter">
          <el-icon><Plus /></el-icon>
          添加章节
        </el-button>
        <el-button type="success" @click="handleSaveAll">
          保存全部
        </el-button>
      </div>
    </div>

    <!-- 章节列表 -->
    <el-card class="chapters-card">
      <template #header>
        <div class="card-header">
          <span>章节列表</span>
          <span class="hint">共 {{ chapters.length }} 章</span>
        </div>
      </template>

      <div v-loading="loading" class="chapters-list">
        <el-empty v-if="chapters.length === 0" description="暂无章节，请添加或自动生成" />

        <div v-else class="chapter-items">
          <div
            v-for="(chapter, index) in chapters"
            :key="chapter.id || index"
            class="chapter-item"
            :class="{ dragging: dragIndex === index }"
            draggable
            @dragstart="handleDragStart(index)"
            @dragover.prevent
            @drop="handleDrop(index)"
          >
            <div class="drag-handle">
              <el-icon><Rank /></el-icon>
            </div>

            <div class="chapter-number">第 {{ chapter.order }} 章</div>

            <el-input
              v-model="chapter.title"
              placeholder="章节标题"
              class="chapter-title-input"
            />

            <el-input
              v-model="chapter.content"
              type="textarea"
              :rows="2"
              placeholder="章节内容概要"
              class="chapter-content-input"
            />

            <div class="chapter-actions">
              <el-button link type="danger" size="small" @click="handleDeleteChapter(chapter.id, index)">
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 章节详情编辑 -->
    <el-dialog
      v-model="showDetailDialog"
      title="章节详情"
      width="700px"
      :before-close="handleCloseDetail"
    >
      <el-form :model="editingChapter" label-width="80px">
        <el-form-item label="章节序号">
          <el-input-number v-model="editingChapter.order" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="章节标题">
          <el-input v-model="editingChapter.title" placeholder="请输入章节标题" />
        </el-form-item>
        <el-form-item label="章节内容">
          <el-input
            v-model="editingChapter.content"
            type="textarea"
            :rows="8"
            placeholder="请输入章节内容概要"
          />
        </el-form-item>
        <el-form-item label="章节摘要">
          <el-input
            v-model="editingChapter.summary"
            type="textarea"
            :rows="3"
            placeholder="简短描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDetailDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveChapter">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight, MagicStick, Plus, Rank } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { Chapter } from '@/types'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const generating = ref(false)
const chapters = ref<Chapter[]>([])
const showDetailDialog = ref(false)
const dragIndex = ref(-1)

const editingChapter = reactive<Partial<Chapter>>({
  id: null,
  script_id: 0,
  order: 1,
  title: '',
  content: '',
  summary: '',
  status: 'draft',
})

// 从路由获取 script_id
const scriptId = ref<number | null>(null)

const fetchChapters = async () => {
  if (!scriptId.value) {
    ElMessage.warning('请先选择剧本')
    return
  }

  loading.value = true
  try {
    const response = await api.chapters.list(scriptId.value)
    chapters.value = response.data || response
  } catch (error: any) {
    if (error?.response?.status !== 401) {
      ElMessage.error('获取章节列表失败')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const handleAutoGenerate = async () => {
  if (!scriptId.value) {
    ElMessage.warning('请先选择剧本')
    return
  }

  generating.value = true
  try {
    // 调用 API 生成章节
    const response = await api.chapters.generate(scriptId.value)

    chapters.value = response.data || response

    ElMessage.success('章节生成成功')
    fetchChapters()
  } catch (error: any) {
    ElMessage.error('生成失败')
    console.error(error)
  } finally {
    generating.value = false
  }
}

const handleAddChapter = async () => {
  if (!scriptId.value) {
    ElMessage.warning('请先选择剧本')
    return
  }

  const newOrder = chapters.value.length > 0
    ? Math.max(...chapters.value.map(c => c.order)) + 1
    : 1

  try {
    const response = await api.chapters.create({
      script_id: scriptId.value,
      order: newOrder,
      title: `第${newOrder}章`,
      content: '',
      summary: '',
    })

    const newChapter = response.data
    chapters.value.push(newChapter)
    ElMessage.success('添加成功')
  } catch (error: any) {
    ElMessage.error('添加章节失败')
    console.error(error)
  }
}

const handleDeleteChapter = async (id: number | null, index: number) => {
  if (!id) {
    // 未保存的章节，直接从本地删除
    chapters.value.splice(index, 1)
    chapters.value.forEach((c, i) => {
      c.order = i + 1
    })
    return
  }

  try {
    await ElMessageBox.confirm('确定要删除这个章节吗？', '警告', {
      type: 'warning',
    })

    await api.chapters.delete(id)
    chapters.value.splice(index, 1)

    // 重新排序
    chapters.value.forEach((c, i) => {
      c.order = i + 1
    })

    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSaveChapter = async () => {
  if (!editingChapter.id) {
    ElMessage.error('章节 ID 缺失')
    return
  }

  try {
    await api.chapters.update(editingChapter.id, {
      title: editingChapter.title,
      content: editingChapter.content,
      summary: editingChapter.summary,
      order: editingChapter.order,
    })

    ElMessage.success('保存成功')
    showDetailDialog.value = false
    fetchChapters()
  } catch (error: any) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

const handleSaveAll = async () => {
  try {
    // 批量保存所有章节
    const updatePromises = chapters.value
      .filter(c => c.id)
      .map(chapter => api.chapters.update(chapter.id!, {
        title: chapter.title,
        content: chapter.content,
        summary: chapter.summary,
        order: chapter.order,
      }))

    await Promise.all(updatePromises)

    ElMessage.success('全部保存成功')
  } catch (error: any) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

const handleDragStart = (index: number) => {
  dragIndex.value = index
}

const handleDrop = async (index: number) => {
  if (dragIndex.value === -1 || dragIndex.value === index) return

  const draggedItem = chapters.value[dragIndex.value]
  chapters.value.splice(dragIndex.value, 1)
  chapters.value.splice(index, 0, draggedItem)

  // 重新排序
  chapters.value.forEach((c, i) => {
    c.order = i + 1
  })

  dragIndex.value = -1

  // 保存到后端
  if (draggedItem.id) {
    try {
      await api.chapters.reorder(chapters.value.map(c => c.id!))
    } catch (error) {
      console.error('Failed to reorder chapters:', error)
    }
  }
}

const handleCloseDetail = () => {
  showDetailDialog.value = false
}

onMounted(() => {
  // 从路由参数获取 script_id
  scriptId.value = Number(route.query.script_id || route.params.scriptId) || null
  if (scriptId.value) {
    fetchChapters()
  } else {
    ElMessage.warning('缺少剧本 ID 参数')
  }
})
</script>

<style scoped lang="scss">
.chapter-breakdown {
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
  }

  .actions {
    display: flex;
    gap: 8px;
  }

  .chapters-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .hint {
        font-size: 13px;
        color: #999;
      }
    }

    .chapters-list {
      min-height: 400px;
    }

    .chapter-items {
      .chapter-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        margin-bottom: 12px;
        cursor: move;
        transition: box-shadow 0.2s;

        &:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        &.dragging {
          opacity: 0.5;
        }

        .drag-handle {
          color: #999;
          cursor: grab;
          padding: 4px;
        }

        .chapter-number {
          font-size: 14px;
          font-weight: 600;
          color: #333;
          min-width: 80px;
        }

        .chapter-title-input {
          flex: 1;
        }

        .chapter-content-input {
          width: 100%;
          margin-top: 8px;
        }

        .chapter-actions {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
      }
    }
  }
}
</style>
