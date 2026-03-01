<template>
  <div class="storyboard-editor">
    <div class="toolbar">
      <div class="breadcrumb">
        <el-button link @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span>章节拆解</span>
        <el-icon><ArrowRight /></el-icon>
        <span>分镜创作</span>
      </div>

      <div class="actions">
        <el-button :loading="generating" @click="handleAutoGenerate">
          <el-icon><MagicStick /></el-icon>
          AI 自动生成
        </el-button>
        <el-button type="primary" @click="handleAddPanel">
          <el-icon><Plus /></el-icon>
          添加分镜
        </el-button>
        <el-button
          v-if="!isLocked"
          type="success"
          @click="handleLockStoryboards"
        >
          <el-icon><Lock /></el-icon>
          锁定分镜
        </el-button>
      </div>
    </div>

    <!-- 分镜列表 -->
    <el-card class="storyboard-list-card" v-if="!editingPanel">
      <template #header>
        <div class="card-header">
          <span>分镜列表</span>
          <span class="hint">共 {{ storyboards.length }} 个镜头</span>
        </div>
      </template>

      <div v-loading="loading" class="storyboard-list">
        <el-empty v-if="storyboards.length === 0" description="暂无分镜，请添加或自动生成" />

        <div v-else class="panel-items">
          <div
            v-for="(panel, index) in storyboards"
            :key="panel.id || index"
            class="panel-item"
            :class="{ locked: isLocked }"
            @click="selectPanel(panel)"
          >
            <div class="panel-order">
              <span class="order-label">镜头 {{ panel.order }}</span>
              <el-tag v-if="panel.emotion" size="small" type="info">
                {{ panel.emotion }}
              </el-tag>
            </div>

            <div class="panel-preview">
              <div class="visual" v-if="panel.visual_description">
                <strong>画面：</strong>
                <span class="text-truncate">{{ panel.visual_description }}</span>
              </div>
              <div class="dialogue" v-if="panel.dialogue">
                <el-icon><Mic /></el-icon>
                <span class="text-truncate">{{ panel.dialogue }}</span>
              </div>
            </div>

            <div class="panel-meta">
              <span>{{ panel.duration_seconds }}s</span>
              <el-tag :type="panelStatusType(panel)" size="small">
                {{ panelStatusLabel(panel) }}
              </el-tag>
            </div>

            <div class="panel-actions" v-if="!isLocked">
              <el-button link type="danger" size="small" @click.stop="handleDeletePanel(index)">
                删除
              </el-button>
              <el-button link type="primary" size="small" @click.stop="selectPanel(panel)">
                编辑
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 分镜详情编辑器 -->
    <el-card v-else class="editor-card">
      <template #header>
        <div class="editor-header">
          <el-button link @click="editingPanel = null">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
          <div class="title-row">
            <span>镜头 {{ currentPanel.order }}</span>
            <el-tag :type="panelStatusType(currentPanel)">
              {{ panelStatusLabel(currentPanel) }}
            </el-tag>
          </div>
          <el-button type="primary" @click="handleSavePanel">保存</el-button>
        </div>
      </template>

      <el-form :model="currentPanel" label-width="100px">
        <el-row :gutter="20">
          <!-- 左侧：表单 -->
          <el-col :span="14">
            <el-form-item label="画面描述">
              <el-input
                v-model="currentPanel.visual_description"
                type="textarea"
                :rows="4"
                placeholder="详细描述镜头画面内容"
                :disabled="isLocked"
              />
            </el-form-item>

            <el-form-item label="镜头语言">
              <el-input
                v-model="currentPanel.camera_direction"
                placeholder="例如：全景 → 中景 → 特写，推镜头，摇镜头等"
                :disabled="isLocked"
              />
            </el-form-item>

            <el-form-item label="角色台词">
              <el-input
                v-model="currentPanel.dialogue"
                type="textarea"
                :rows="3"
                placeholder="输入角色对白内容"
                :disabled="isLocked"
              />
            </el-form-item>

            <el-form-item label="情绪基调">
              <el-select v-model="currentPanel.emotion" placeholder="请选择情绪" style="width: 100%">
                <el-option label="开心" value="happy" />
                <el-option label="悲伤" value="sad" />
                <el-option label="愤怒" value="angry" />
                <el-option label="惊讶" value="surprised" />
                <el-option label="恐惧" value="scared" />
                <el-option label="平静" value="calm" />
                <el-option label="紧张" value="tense" />
                <el-option label="期待" value="excited" />
              </el-select>
            </el-form-item>

            <el-form-item label="镜头时长">
              <el-input-number
                v-model="currentPanel.duration_seconds"
                :min="1"
                :max="30"
                :step="0.5"
                :disabled="isLocked"
              />
              <span class="hint">秒</span>
            </el-form-item>
          </el-col>

          <!-- 右侧：预览 -->
          <el-col :span="10">
            <div class="preview-section">
              <h4>分镜预览</h4>
              <div class="preview-card">
                <div class="preview-visual">
                  <div class="placeholder-image" v-if="!currentPanel.generated_image">
                    <el-icon><Picture /></el-icon>
                    <p>等待图片生成</p>
                  </div>
                  <img
                    v-else
                    :src="currentPanel.generated_image.url"
                    alt="Generated"
                  />
                </div>
                <div class="preview-info">
                  <div class="preview-line">
                    <strong>画面：</strong>{{ currentPanel.visual_description }}
                  </div>
                  <div class="preview-line" v-if="currentPanel.dialogue">
                    <el-icon><Mic /></el-icon>
                    <strong>台词：</strong>{{ currentPanel.dialogue }}
                  </div>
                  <div class="preview-line" v-if="currentPanel.camera_direction">
                    <strong>镜头：</strong>{{ currentPanel.camera_direction }}
                  </div>
                  <div class="preview-line">
                    <strong>时长：</strong>{{ currentPanel.duration_seconds }}s
                  </div>
                </div>
              </div>

              <!-- AI 生成图片 -->
              <div class="ai-generate" v-if="!isLocked">
                <el-button
                  type="primary"
                  :loading="generatingImage"
                  @click="handleGenerateImage"
                  style="width: 100%"
                >
                  <el-icon><MagicStick /></el-icon>
                  AI 生成画面
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- AI 生成对话框 -->
    <el-dialog v-model="showGenerateDialog" title="AI 生成分镜" width="500px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="参考章节">
          <el-select v-model="generateForm.chapterId" placeholder="请选择章节" style="width: 100%">
            <el-option
              v-for="chapter in chapters"
              :key="chapter.id"
              :label="chapter.title"
              :value="chapter.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="生成数量">
          <el-input-number v-model="generateForm.count" :min="3" :max="10" :step="1" />
          <span class="hint">个分镜</span>
        </el-form-item>
        <el-form-item label="风格参考">
          <el-select v-model="generateForm.style" placeholder="请选择风格" style="width: 100%">
            <el-option label="日式动漫" value="anime_jp" />
            <el-option label="美式漫画" value="comic_us" />
            <el-option label="写实风格" value="realistic" />
            <el-option label="水彩风格" value="watercolor" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="confirmGenerate">
          开始生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  ArrowRight,
  MagicStick,
  Plus,
  Lock,
  Mic,
  Picture,
} from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { Storyboard, Chapter } from '@/types'

const loading = ref(false)
const generating = ref(false)
const generatingImage = ref(false)
const isLocked = ref(false)
const editingPanel = ref(false)
const showGenerateDialog = ref(false)

const storyboards = ref<Partial<Storyboard>[]>([])
const chapters = ref<Chapter[]>([])

const currentPanel = reactive<Partial<Storyboard>>({
  order: 1,
  visual_description: '',
  camera_direction: '',
  dialogue: '',
  duration_seconds: 5,
  emotion: '',
  status: 'draft',
})

const generateForm = reactive({
  chapterId: null,
  count: 5,
  style: 'anime_jp',
})

const panelStatusLabel = (panel: Storyboard) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    in_review: '审核中',
    locked: '已锁定',
    materials_generated: '素材已生成',
    video_generated: '视频已生成',
    completed: '已完成',
  }
  return labels[panel.status || 'draft']
}

const panelStatusType = (panel: Storyboard) => {
  const types: Record<string, any> = {
    draft: 'info',
    in_review: 'warning',
    locked: 'danger',
    materials_generated: 'success',
    video_generated: 'success',
    completed: '',
  }
  return types[panel.status || 'draft']
}

const fetchStoryboards = async () => {
  loading.value = true
  try {
    // TODO: Get chapter_id from route
    const response = await api.storyboards.list(1)
    storyboards.value = response.data
  } catch (error) {
    ElMessage.error('获取分镜列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchChapters = async () => {
  try {
    // TODO: Get script_id from route
    const response = await api.chapters.list(1)
    chapters.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const selectPanel = (panel: Storyboard) => {
  Object.assign(currentPanel, panel)
  editingPanel.value = true
}

const handleAddPanel = () => {
  const newOrder = storyboards.value.length > 0
    ? Math.max(...storyboards.value.map(p => p.order || 0)) + 1
    : 1

  const newPanel: Partial<Storyboard> = {
    order: newOrder,
    visual_description: '',
    camera_direction: '',
    dialogue: '',
    duration_seconds: 5,
    emotion: '',
    status: 'draft',
  }

  storyboards.value.push(newPanel)
  selectPanel(newPanel)
}

const handleSavePanel = () => {
  // TODO: Call API to save
  ElMessage.success('保存成功')
  editingPanel.value = false
  fetchStoryboards()
}

const handleDeletePanel = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个分镜吗？', '警告', {
      type: 'warning',
    })
    storyboards.value.splice(index, 1)
    // Reorder
    storyboards.value.forEach((p, i) => {
      p.order = i + 1
    })
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleLockStoryboards = async () => {
  try {
    await ElMessageBox.confirm('锁定后将进入素材生成阶段，是否继续？', '提示', {
      type: 'warning',
    })
    // TODO: Call API to lock
    isLocked.value = true
    ElMessage.success('分镜已锁定')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('锁定失败')
    }
  }
}

const handleAutoGenerate = () => {
  showGenerateDialog.value = true
}

const confirmGenerate = async () => {
  generating.value = true
  try {
    // TODO: Call actual API
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Mock generated storyboards
    storyboards.value = [
      {
        id: 1,
        order: 1,
        visual_description: '主角站在学校门口，阳光明媚，樱花飘落',
        camera_direction: '全景 → 中景，缓慢推镜头',
        dialogue: '今天是个好日子！',
        emotion: 'happy',
        duration_seconds: 5,
        status: 'draft',
      },
      {
        id: 2,
        order: 2,
        visual_description: '好友从远处跑来，挥手打招呼',
        camera_direction: '中景，摇镜头跟随',
        dialogue: '好久不见！',
        emotion: 'excited',
        duration_seconds: 4,
        status: 'draft',
      },
      {
        id: 3,
        order: 3,
        visual_description: '两人并肩走在校园小路上',
        camera_direction: '跟拍镜头，侧面视角',
        dialogue: '最近怎么样？',
        emotion: 'calm',
        duration_seconds: 6,
        status: 'draft',
      },
    ]

    ElMessage.success('分镜生成成功')
    showGenerateDialog.value = false
  } catch (error) {
    ElMessage.error('生成失败')
    console.error(error)
  } finally {
    generating.value = false
  }
}

const handleGenerateImage = async () => {
  generatingImage.value = true
  try {
    // TODO: Call image generation API
    await new Promise(resolve => setTimeout(resolve, 2000))

    currentPanel.generated_image = {
      url: 'https://via.placeholder.com/400x300?text=Generated+Image',
    }

    ElMessage.success('图片生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generatingImage.value = false
  }
}

onMounted(() => {
  fetchStoryboards()
  fetchChapters()
})
</script>

<style scoped lang="scss">
.storyboard-editor {
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

  .storyboard-list-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .hint {
        font-size: 13px;
        color: #999;
      }
    }

    .storyboard-list {
      min-height: 400px;
    }

    .panel-items {
      .panel-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        margin-bottom: 12px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
        }

        &.locked {
          cursor: not-allowed;
          opacity: 0.8;
        }

        .panel-order {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          min-width: 60px;

          .order-label {
            font-size: 12px;
            font-weight: 600;
            color: #333;
          }
        }

        .panel-preview {
          flex: 1;

          .visual {
            font-size: 13px;
            color: #666;
            margin-bottom: 4px;

            strong {
              color: #333;
            }
          }

          .dialogue {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 13px;
            color: #666;
          }

          .text-truncate {
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
        }

        .panel-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 8px;
          font-size: 12px;
          color: #999;
        }

        .panel-actions {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
      }
    }
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
      font-size: 16px;
      font-weight: 600;
    }

    .preview-section {
      h4 {
        margin-bottom: 12px;
        color: #333;
      }

      .preview-card {
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        overflow: hidden;

        .preview-visual {
          aspect-ratio: 16 / 9;
          background: #f5f7fa;
          display: flex;
          align-items: center;
          justify-content: center;

          .placeholder-image {
            text-align: center;
            color: #999;

            .el-icon {
              font-size: 48px;
              margin-bottom: 8px;
            }
          }

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }

        .preview-info {
          padding: 12px;
          background: #fafafa;

          .preview-line {
            font-size: 13px;
            color: #666;
            margin-bottom: 6px;
            display: flex;
            align-items: flex-start;
            gap: 4px;

            strong {
              color: #333;
              white-space: nowrap;
            }
          }
        }
      }

      .ai-generate {
        margin-top: 16px;
      }
    }
  }
}
</style>
