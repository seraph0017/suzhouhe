<template>
  <div class="first-audit">
    <div class="toolbar">
      <div class="breadcrumb">
        <span>一审工作台</span>
      </div>

      <div class="stats">
        <el-tag type="info">待审核：{{ pendingCount }}</el-tag>
        <el-tag type="success">已通过：{{ approvedCount }}</el-tag>
        <el-tag type="danger">已拒绝：{{ rejectedCount }}</el-tag>
      </div>
    </div>

    <!-- 分镜卡片列表 -->
    <el-card class="storyboard-cards">
      <template #header>
        <div class="card-header">
          <span>分镜素材审核</span>
          <el-radio-group v-model="filterStatus" size="small">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="pending">待审核</el-radio-button>
            <el-radio-button label="approved">已通过</el-radio-button>
            <el-radio-button label="rejected">已拒绝</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <div v-loading="loading" class="storyboard-grid">
        <el-empty v-if="filteredStoryboards.length === 0" description="暂无待审核内容" />

        <div v-else class="storyboard-items">
          <div
            v-for="sb in filteredStoryboards"
            :key="sb.id"
            class="storyboard-card"
            :class="{ 'is-pending': !sb.selected_image_id }"
          >
            <!-- 分镜描述 -->
            <div class="panel-header">
              <div class="panel-title">
                <span class="order">Panel {{ sb.order }}</span>
                <span class="emotion" v-if="sb.emotion">{{ sb.emotion }}</span>
              </div>
              <el-tag :type="panelStatusType(sb)" size="small">
                {{ panelStatusLabel(sb) }}
              </el-tag>
            </div>

            <div class="panel-content">
              <div class="visual-desc">
                <strong>画面：</strong>{{ sb.visual_description }}
              </div>
              <div class="dialogue" v-if="sb.dialogue">
                <strong>台词：</strong>{{ sb.dialogue }}
              </div>
              <div class="camera" v-if="sb.camera_direction">
                <strong>镜头：</strong>{{ sb.camera_direction }}
              </div>
            </div>

            <!-- 抽卡图片选择 -->
            <div class="image-selection">
              <div class="selection-header">
                <span>图片选择（抽卡）</span>
                <el-button
                  size="small"
                  type="primary"
                  @click="handleGenerateImages(sb)"
                  :loading="sb.generating"
                >
                  <el-icon><Refresh /></el-icon>
                  重新生成
                </el-button>
              </div>

              <div class="image-grid">
                <div
                  v-for="img in sb.generated_images || []"
                  :key="img.id"
                  class="image-card"
                  :class="{ selected: sb.selected_image_id === img.id }"
                  @click="handleSelectImage(sb, img)"
                >
                  <img :src="img.url" :alt="img.file_name" />
                  <div class="image-overlay">
                    <el-icon v-if="sb.selected_image_id === img.id"><CircleCheck /></el-icon>
                  </div>
                </div>

                <!-- 空状态 -->
                <div v-if="!sb.generated_images || sb.generated_images.length === 0" class="empty-images">
                  <p>暂无生成图片</p>
                  <el-button size="small" @click="handleGenerateImages(sb)">
                    生成图片
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 音频选择 -->
            <div class="audio-selection">
              <div class="selection-header">
                <span>TTS 配音</span>
                <el-button size="small" @click="handleGenerateAudio(sb)">
                  生成配音
                </el-button>
              </div>
              <div class="audio-item" v-if="sb.selected_audio">
                <el-icon><Headset /></el-icon>
                <span>{{ sb.selected_audio.file_name }}</span>
                <audio :src="sb.selected_audio.url" controls style="height: 24px; flex: 1" />
              </div>
              <p v-else class="no-audio">暂无配音</p>
            </div>

            <!-- 审核操作 -->
            <div class="audit-actions">
              <el-button
                v-if="!sb.selected_image_id"
                type="warning"
                size="small"
                @click="handleReject(sb)"
              >
                标记为待处理
              </el-button>
              <el-button
                v-if="sb.selected_image_id && !sb.audited"
                type="success"
                size="small"
                @click="handleApprove(sb)"
              >
                通过
              </el-button>
              <el-tag v-if="sb.audited" type="success" size="small">已审核</el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, CircleCheck, Headset } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { Storyboard, Asset } from '@/types'

const route = useRoute()
const loading = ref(false)
const filterStatus = ref('all')

const storyboards = ref<Partial<Storyboard>[]>([])

// 从路由获取 chapter_id（可选）
const chapterId = computed(() => {
  const id = route.query.chapter_id
  return id ? Number(id) : null
})

const filteredStoryboards = computed(() => {
  if (filterStatus.value === 'all') return storyboards.value
  if (filterStatus.value === 'pending') {
    return storyboards.value.filter(sb => !sb.selected_image_id)
  }
  if (filterStatus.value === 'approved') {
    return storyboards.value.filter(sb => sb.audited)
  }
  if (filterStatus.value === 'rejected') {
    return storyboards.value.filter(sb => !sb.audited && sb.selected_image_id)
  }
  return storyboards.value
})

const pendingCount = computed(() =>
  storyboards.value.filter(sb => !sb.selected_image_id).length
)
const approvedCount = computed(() =>
  storyboards.value.filter(sb => sb.audited).length
)
const rejectedCount = computed(() =>
  storyboards.value.filter(sb => !sb.audited && sb.selected_image_id).length
)

const panelStatusLabel = (sb: Storyboard) => {
  if (sb.audited) return '已审核'
  if (!sb.selected_image_id) return '待选图'
  return '待审核'
}

const panelStatusType = (sb: Storyboard) => {
  if (sb.audited) return 'success'
  if (!sb.selected_image_id) return 'warning'
  return 'info'
}

const fetchStoryboards = async () => {
  loading.value = true
  try {
    // 如果有 chapter_id，只获取该章节的分镜
    if (chapterId.value) {
      const response = await api.storyboards.list(chapterId.value)
      storyboards.value = response.data || response
    } else {
      // 否则获取所有分镜（可能需要新的 API）
      ElMessage.info('请先选择章节')
    }
  } catch (error: any) {
    if (error?.response?.status !== 401) {
      ElMessage.error('获取分镜列表失败')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const handleGenerateImages = async (sb: any) => {
  sb.generating = true
  try {
    // 调用图片生成 API
    const response = await api.storyboards.generateImage(sb.id)

    // 添加生成的图片到列表
    if (!sb.generated_images) {
      sb.generated_images = []
    }
    sb.generated_images.push({
      id: response.data.id,
      url: response.data.url,
      file_name: `generated_${sb.id}_${Date.now()}.png`,
    })

    ElMessage.success('图片生成成功')
  } catch (error: any) {
    ElMessage.error('生成失败')
    console.error(error)
  } finally {
    sb.generating = false
  }
}

const handleSelectImage = async (sb: any, img: Asset) => {
  try {
    // 调用 API 选择图片
    await api.materials.selectImage(sb.id, img.id)

    sb.selected_image_id = img.id
    ElMessage.success('图片已选择')
  } catch (error: any) {
    ElMessage.error('选择失败')
    console.error(error)
  }
}

const handleGenerateAudio = async (sb: any) => {
  try {
    // 调用 TTS 生成 API
    const response = await api.generation.generateAudio(sb.id)

    sb.selected_audio = response.data
    ElMessage.success('配音生成成功')
  } catch (error: any) {
    ElMessage.error('生成失败')
    console.error(error)
  }
}

const handleApprove = async (sb: any) => {
  try {
    await ElMessageBox.confirm('确认通过这个分镜的审核？', '提示', {
      type: 'success',
    })

    // 调用 API 提交审核
    await api.audits.submitFirst('storyboard', sb.id)

    sb.audited = true
    ElMessage.success('审核通过')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('审核失败')
      console.error(error)
    }
  }
}

const handleReject = (sb: any) => {
  sb.audited = false
  sb.selected_image_id = null
  ElMessage.warning('已标记为待处理')
}

onMounted(() => {
  fetchStoryboards()
})
</script>

<style scoped lang="scss">
.first-audit {
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
    font-size: 16px;
    font-weight: 500;
  }

  .stats {
    display: flex;
    gap: 12px;
  }

  .storyboard-cards {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .storyboard-grid {
      min-height: 400px;
    }

    .storyboard-items {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
    }

    .storyboard-card {
      border: 1px solid #e8e8e8;
      border-radius: 12px;
      padding: 16px;
      background: white;

      &.is-pending {
        border-color: #e6a23c;
        background: #fffbeb;
      }

      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
      }

      .panel-title {
        display: flex;
        align-items: center;
        gap: 8px;

        .order {
          font-size: 14px;
          font-weight: 600;
        }

        .emotion {
          font-size: 12px;
          color: #666;
          background: #f0f0f0;
          padding: 2px 8px;
          border-radius: 4px;
        }
      }

      .panel-content {
        margin-bottom: 16px;
        font-size: 13px;

        .visual-desc, .dialogue, .camera {
          margin-bottom: 4px;
          color: #666;

          strong {
            color: #333;
          }
        }
      }

      .image-selection {
        margin-bottom: 16px;

        .selection-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .image-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;

          .image-card {
            position: relative;
            aspect-ratio: 1;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            border: 2px solid transparent;

            &.selected {
              border-color: #67c23a;
            }

            img {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }

            .image-overlay {
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background: rgba(0, 0, 0, 0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 24px;
            }
          }

          .empty-images {
            grid-column: 1 / -1;
            text-align: center;
            padding: 20px;
            color: #999;
          }
        }
      }

      .audio-selection {
        margin-bottom: 16px;

        .selection-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .audio-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px;
          background: #f5f7fa;
          border-radius: 4px;
        }

        .no-audio {
          color: #999;
          font-size: 13px;
        }
      }

      .audit-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
      }
    }
  }
}
</style>
