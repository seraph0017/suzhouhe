<template>
  <div class="final-audit">
    <div class="toolbar">
      <div class="breadcrumb">
        <span>终审工作台</span>
      </div>

      <div class="stats">
        <el-tag type="info">待审核：{{ pendingCount }}</el-tag>
        <el-tag type="success">已通过：{{ approvedCount }}</el-tag>
        <el-tag type="danger">需修改：{{ rejectedCount }}</el-tag>
      </div>
    </div>

    <!-- 审核列表 -->
    <el-card class="audit-list-card" v-if="!currentAudit">
      <template #header>
        <div class="card-header">
          <span>待审核章节</span>
          <el-radio-group v-model="filterStatus" size="small">
            <el-radio-button label="pending">待审核</el-radio-button>
            <el-radio-button label="approved">已通过</el-radio-button>
            <el-radio-button label="rejected">需修改</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <div v-loading="loading" class="chapter-list">
        <el-empty v-if="filteredChapters.length === 0" description="暂无待审核内容" />

        <div v-else class="chapter-items">
          <div
            v-for="chapter in filteredChapters"
            :key="chapter.id"
            class="chapter-card"
            @click="selectChapter(chapter)"
          >
            <div class="chapter-header">
              <h3>{{ chapter.title }}</h3>
              <el-tag :type="auditStatusType(chapter)" size="small">
                {{ auditStatusLabel(chapter.status) }}
              </el-tag>
            </div>

            <div class="chapter-info">
              <div class="info-item">
                <el-icon><Film /></el-icon>
                <span>{{ chapter.storyboard_count }} 个镜头</span>
              </div>
              <div class="info-item">
                <el-icon><Timer /></el-icon>
                <span>{{ chapter.duration }}s</span>
              </div>
              <div class="info-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ formatDate(chapter.submitted_at) }}</span>
              </div>
            </div>

            <div class="chapter-preview" v-if="chapter.thumbnail">
              <img :src="chapter.thumbnail" alt="Preview" />
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 审核详情 -->
    <el-card v-else class="audit-detail-card">
      <template #header>
        <div class="detail-header">
          <el-button link @click="currentAudit = null">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
          <h2>{{ currentAudit.title }}</h2>
          <div class="actions">
            <el-button @click="handleReject">
              <el-icon><CircleClose /></el-icon>
              驳回
            </el-button>
            <el-button type="success" @click="handleApprove">
              <el-icon><CircleCheck /></el-icon>
              通过
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：视频播放器 -->
        <el-col :span="16">
          <div class="video-player">
            <div class="player-container">
              <video
                ref="videoRef"
                :src="currentAudit.video_url"
                controls
                style="width: 100%; border-radius: 8px"
              />
            </div>

            <!-- 分镜列表 -->
            <div class="storyboard-review">
              <h4>分镜检查</h4>
              <div class="storyboard-list">
                <div
                  v-for="(panel, index) in currentAudit.storyboards"
                  :key="panel.id"
                  class="storyboard-item"
                  :class="{ selected: selectedPanel === index }"
                  @click="selectedPanel = index"
                >
                  <div class="panel-order">{{ index + 1 }}</div>
                  <img :src="panel.image_url" alt="" />
                  <div class="panel-status">
                    <el-tag
                      :type="panel.status === 'approved' ? 'success' : panel.status === 'rejected' ? 'danger' : 'info'"
                      size="small"
                    >
                      {{ panel.status || 'pending' }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧：审核表单 -->
        <el-col :span="8">
          <!-- 审核意见 -->
          <el-card class="review-form-card">
            <template #header>
              <span>审核意见</span>
            </template>

            <el-form :model="reviewForm" label-width="80px">
              <el-form-item label="整体评分">
                <el-rate v-model="reviewForm.rating" :colors="['#99A9BF', '#F7BA2A', '#67C23A']" />
              </el-form-item>

              <el-form-item label="画面质量">
                <el-select v-model="reviewForm.video_quality" placeholder="请选择" style="width: 100%">
                  <el-option label="优秀" value="excellent" />
                  <el-option label="良好" value="good" />
                  <el-option label="一般" value="fair" />
                  <el-option label="需改进" value="poor" />
                </el-select>
              </el-form-item>

              <el-form-item label="配音质量">
                <el-select v-model="reviewForm.audio_quality" placeholder="请选择" style="width: 100%">
                  <el-option label="优秀" value="excellent" />
                  <el-option label="良好" value="good" />
                  <el-option label="一般" value="fair" />
                  <el-option label="需改进" value="poor" />
                </el-select>
              </el-form-item>

              <el-form-item label="审核意见">
                <el-input
                  v-model="reviewForm.feedback"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入详细的审核意见"
                />
              </el-form-item>

              <el-form-item label="驳回理由" v-if="showRejectReason">
                <el-select
                  v-model="reviewForm.rejection_reason"
                  placeholder="请选择驳回理由"
                  style="width: 100%"
                  multiple
                >
                  <el-option label="画面质量不佳" value="video_quality" />
                  <el-option label="口型不同步" value="lip_sync" />
                  <el-option label="配音有问题" value="audio_quality" />
                  <el-option label="字幕错误" value="subtitle" />
                  <el-option label="BGM 不合适" value="bgm" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 时间轴标记 -->
          <el-card class="timeline-markers-card" style="margin-top: 20px">
            <template #header>
              <div class="marker-header">
                <span>问题标记</span>
                <el-button size="small" type="primary" @click="addMarker">
                  <el-icon><Plus /></el-icon>
                  添加标记
                </el-button>
              </div>
            </template>

            <div class="marker-list">
              <div
                v-for="(marker, index) in markers"
                :key="index"
                class="marker-item"
              >
                <div class="marker-time">{{ marker.time }}s</div>
                <div class="marker-content">{{ marker.note }}</div>
                <el-button link type="danger" size="small" @click="removeMarker(index)">
                  <el-icon><CloseBold /></el-icon>
                </el-button>
              </div>
              <el-empty v-if="markers.length === 0" description="暂无标记" :image-size="60" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 审核结果对话框 -->
    <el-dialog
      v-model="showResultDialog"
      :title="isApproved ? '审核通过' : '驳回修改'"
      width="500px"
      :close-on-click-modal="false"
    >
      <p v-if="isApproved">
        确认通过此章节吗？通过后将进入下一章节或项目完成流程。
      </p>
      <p v-else>
        请填写驳回理由并通知修改。
      </p>

      <el-input
        v-if="!isApproved"
        v-model="reviewForm.feedback"
        type="textarea"
        :rows="4"
        placeholder="请详细说明需要修改的问题"
      />

      <template #footer>
        <el-button @click="showResultDialog = false">取消</el-button>
        <el-button
          v-if="isApproved"
          type="success"
          @click="confirmApprove"
        >
          确认通过
        </el-button>
        <el-button
          v-else
          type="danger"
          @click="confirmReject"
        >
          确认驳回
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
  Film,
  Timer,
  Calendar,
  CircleCheck,
  CircleClose,
  Plus,
  CloseBold,
} from '@element-plus/icons-vue'
import { api } from '@/services/api'

const loading = ref(false)
const filterStatus = ref('pending')
const currentAudit = ref<any>(null)
const selectedPanel = ref(0)
const showResultDialog = ref(false)
const isApproved = ref(false)
const videoRef = ref<HTMLVideoElement>()

const markers = ref<any[]>([])

const reviewForm = reactive({
  rating: 0,
  video_quality: '',
  audio_quality: '',
  feedback: '',
  rejection_reason: [],
})

const chapters = ref<any[]>([])

const fetchPendingAudits = async () => {
  loading.value = true
  try {
    const response = await api.audits.listPending('second')
    chapters.value = response.data || response
  } catch (error) {
    ElMessage.error('获取审核列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const filteredChapters = computed(() => {
  if (filterStatus.value === 'all') return chapters.value
  return chapters.value.filter(c => c.status === filterStatus.value)
})

const pendingCount = computed(() =>
  chapters.value.filter(c => c.status === 'pending').length
)
const approvedCount = computed(() =>
  chapters.value.filter(c => c.status === 'approved').length
)
const rejectedCount = computed(() =>
  chapters.value.filter(c => c.status === 'rejected').length
)

const auditStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '需修改',
  }
  return labels[status] || status
}

const auditStatusType = (chapter: any) => {
  const types: Record<string, any> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return types[chapter.status || 'pending']
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const selectChapter = (chapter: any) => {
  currentAudit.value = chapter
  selectedPanel.value = 0
  // Reset form
  reviewForm.rating = 0
  reviewForm.video_quality = ''
  reviewForm.audio_quality = ''
  reviewForm.feedback = ''
  reviewForm.rejection_reason = []
  markers.value = []
}

const showRejectReason = computed(() => {
  return reviewForm.rating <= 2 || reviewForm.feedback.includes('不')
})

const handleApprove = () => {
  isApproved.value = true
  showResultDialog.value = true
}

const handleReject = () => {
  isApproved.value = false
  showResultDialog.value = true
}

const confirmApprove = async () => {
  if (currentAudit.value) {
    try {
      await api.audits.approve(currentAudit.value.review_id, reviewForm.feedback)
      currentAudit.value.status = 'approved'
      showResultDialog.value = false
      ElMessage.success('审核通过')
      fetchPendingAudits()
    } catch (error) {
      ElMessage.error('审核失败')
      console.error(error)
    }
  }
}

const confirmReject = async () => {
  if (currentAudit.value) {
    try {
      const reason = reviewForm.rejection_reason.join(', ')
      await api.audits.reject(currentAudit.value.review_id, reason || reviewForm.feedback)
      currentAudit.value.status = 'rejected'
      showResultDialog.value = false
      ElMessage.warning('已驳回，等待修改')
      fetchPendingAudits()
    } catch (error) {
      ElMessage.error('驳回失败')
      console.error(error)
    }
  }
}

const addMarker = () => {
  const time = videoRef.value?.currentTime?.toFixed(1) || '0.0'
  markers.value.push({
    time,
    note: '问题描述...',
  })
}

const removeMarker = (index: number) => {
  markers.value.splice(index, 1)
}

onMounted(() => {
  fetchPendingAudits()
})
</script>

<style scoped lang="scss">
.final-audit {
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

  .audit-list-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chapter-list {
      min-height: 400px;

      .chapter-items {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
      }

      .chapter-card {
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
        }

        .chapter-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          h3 {
            margin: 0;
            font-size: 16px;
            color: #333;
          }
        }

        .chapter-info {
          display: flex;
          gap: 16px;
          margin-bottom: 12px;
          font-size: 13px;
          color: #666;

          .info-item {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }

        .chapter-preview {
          img {
            width: 100%;
            border-radius: 4px;
          }
        }
      }
    }
  }

  .audit-detail-card {
    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        margin: 0;
        font-size: 18px;
      }

      .actions {
        display: flex;
        gap: 8px;
      }
    }

    .video-player {
      .player-container {
        margin-bottom: 20px;
      }

      .storyboard-review {
        h4 {
          margin: 0 0 12px;
          color: #333;
        }

        .storyboard-list {
          display: flex;
          gap: 12px;
          overflow-x: auto;
          padding-bottom: 8px;

          .storyboard-item {
            flex-shrink: 0;
            border: 2px solid transparent;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s;

            &.selected {
              border-color: #409eff;
            }

            &:hover {
              transform: scale(1.05);
            }

            .panel-order {
              position: absolute;
              top: 4px;
              left: 4px;
              background: rgba(0, 0, 0, 0.6);
              color: white;
              font-size: 12px;
              padding: 2px 6px;
              border-radius: 4px;
            }

            img {
              width: 100px;
              height: 100px;
              object-fit: cover;
            }

            .panel-status {
              padding: 4px;
              text-align: center;
            }
          }
        }
      }
    }

    .review-form-card {
      :deep(.el-form-item) {
        margin-bottom: 16px;
      }
    }

    .timeline-markers-card {
      .marker-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .marker-list {
        .marker-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px;
          background: #f5f7fa;
          border-radius: 4px;
          margin-bottom: 8px;

          .marker-time {
            font-family: monospace;
            font-size: 12px;
            color: #409eff;
            min-width: 50px;
          }

          .marker-content {
            flex: 1;
            font-size: 13px;
            color: #666;
          }
        }
      }
    }
  }
}
</style>
