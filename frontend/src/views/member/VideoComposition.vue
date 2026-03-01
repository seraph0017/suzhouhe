<template>
  <div class="video-composition">
    <div class="toolbar">
      <div class="breadcrumb">
        <el-button link @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span>视频合成</span>
      </div>

      <div class="actions">
        <el-button type="primary" :loading="composing" @click="handleCompose">
          <el-icon><VideoCamera /></el-icon>
          开始合成
        </el-button>
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出视频
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：时间线 -->
      <el-col :span="16">
        <el-card class="timeline-card">
          <template #header>
            <span>视频时间线</span>
          </template>

          <div class="timeline-container">
            <!-- 视频轨道 -->
            <div class="track video-track">
              <div class="track-header">
                <el-icon><Picture /></el-icon>
                <span>视频轨道</span>
              </div>
              <div class="track-content">
                <div
                  v-for="clip in videoClips"
                  :key="clip.id"
                  class="clip"
                  :style="{ width: clip.duration * 20 + 'px' }"
                  @click="selectClip(clip)"
                >
                  <img :src="clip.thumbnail" alt="" />
                  <span class="clip-order">{{ clip.order }}</span>
                </div>
              </div>
            </div>

            <!-- 音频轨道 -->
            <div class="track audio-track">
              <div class="track-header">
                <el-icon><Mic /></el-icon>
                <span>配音轨道</span>
              </div>
              <div class="track-content">
                <div
                  v-for="clip in audioClips"
                  :key="clip.id"
                  class="clip audio-clip"
                  :style="{ width: clip.duration * 20 + 'px', marginLeft: clip.offset * 20 + 'px' }"
                >
                  <el-icon><Headset /></el-icon>
                  <span class="clip-name">{{ clip.name }}</span>
                </div>
              </div>
            </div>

            <!-- BGM 轨道 -->
            <div class="track bgm-track">
              <div class="track-header">
                <el-icon><Star /></el-icon>
                <span>BGM 轨道</span>
              </div>
              <div class="track-content">
                <div v-if="bgm" class="clip bgm-clip">
                  <el-icon><Star /></el-icon>
                  <span>{{ bgm.name }}</span>
                  <el-button link type="danger" size="small" @click="removeBGM">
                    <el-icon><CloseBold /></el-icon>
                  </el-button>
                </div>
                <div v-else class="add-bgm" @click="showBGMSelector = true">
                  <el-icon><Plus /></el-icon>
                  <span>添加 BGM</span>
                </div>
              </div>
            </div>

            <!-- 字幕轨道 -->
            <div class="track subtitle-track">
              <div class="track-header">
                <el-icon><Document /></el-icon>
                <span>字幕轨道</span>
              </div>
              <div class="track-content">
                <div
                  v-for="sub in subtitles"
                  :key="sub.id"
                  class="clip subtitle-clip"
                  :style="{ width: sub.duration * 20 + 'px', marginLeft: sub.start * 20 + 'px' }"
                >
                  <span class="subtitle-text">{{ sub.text }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 播放控制 -->
          <div class="playback-controls">
            <el-button circle @click="seek(0)">
              <el-icon><VideoPause /></el-icon>
            </el-button>
            <el-button circle type="primary" @click="togglePlay">
              <el-icon v-if="isPlaying"><VideoPause /></el-icon>
              <el-icon v-else><VideoPlay /></el-icon>
            </el-button>
            <span class="timecode">{{ currentTime }} / {{ totalTime }}</span>
          </div>
        </el-card>

        <!-- 字幕编辑 -->
        <el-card class="subtitle-card" style="margin-top: 20px">
          <template #header>
            <span>字幕编辑</span>
          </template>

          <div class="subtitle-list">
            <div
              v-for="(sub, index) in subtitles"
              :key="sub.id"
              class="subtitle-item"
            >
              <span class="subtitle-time">{{ sub.start }}s - {{ sub.start + sub.duration }}s</span>
              <el-input
                v-model="sub.text"
                placeholder="输入字幕内容"
                size="small"
                @change="updateSubtitle(index)"
              />
              <el-button link type="danger" @click="removeSubtitle(index)">
                <el-icon><CloseBold /></el-icon>
              </el-button>
            </div>
            <el-button @click="addSubtitle" style="width: 100%">
              <el-icon><Plus /></el-icon>
              添加字幕
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：预览和设置 -->
      <el-col :span="8">
        <!-- 预览播放器 -->
        <el-card class="preview-card">
          <template #header>
            <span>预览</span>
          </template>

          <div class="preview-container">
            <div class="preview-screen">
              <img
                v-if="currentClip"
                :src="currentClip.thumbnail"
                alt="Preview"
              />
              <div v-else class="placeholder">
                <el-icon><Picture /></el-icon>
                <p>选择片段预览</p>
              </div>
            </div>
          </div>
        </el-card>

        <!-- BGM 选择 -->
        <el-card class="bgm-card" style="margin-top: 20px">
          <template #header>
            <span>背景音乐</span>
          </template>

          <div v-if="!bgm" class="bgm-empty">
            <p>暂无 BGM</p>
            <el-button type="primary" size="small" @click="showBGMSelector = true">
              选择 BGM
            </el-button>
          </div>
          <div v-else class="bgm-selected">
            <div class="bgm-info">
              <el-icon><Star /></el-icon>
              <span>{{ bgm.name }}</span>
            </div>
            <div class="bgm-volume">
              <span>音量</span>
              <el-slider v-model="bgmVolume" :max="100" />
            </div>
          </div>
        </el-card>

        <!-- 合成进度 -->
        <el-card v-if="composeProgress > 0" class="progress-card" style="margin-top: 20px">
          <template #header>
            <span>合成进度</span>
          </template>

          <el-progress
            :percentage="composeProgress"
            :status="composeProgress === 100 ? 'success' : undefined"
          />
          <p class="progress-status">{{ composeStatus }}</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- BGM 选择对话框 -->
    <el-dialog v-model="showBGMSelector" title="选择背景音乐" width="600px">
      <div class="bgm-list">
        <div
          v-for="track in bgmOptions"
          :key="track.id"
          class="bgm-item"
          @click="selectBGM(track)"
        >
          <div class="bgm-item-info">
            <strong>{{ track.name }}</strong>
            <p>{{ track.mood }} - {{ track.duration }}s</p>
          </div>
          <el-button size="small">
            <el-icon><VideoPlay /></el-icon>
            试听
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  VideoCamera,
  Download,
  Picture,
  Mic,
  Document,
  Headset,
  Plus,
  CloseBold,
  VideoPlay,
  VideoPause,
  Star,
} from '@element-plus/icons-vue'

const composing = ref(false)
const composeProgress = ref(0)
const composeStatus = ref('')
const isPlaying = ref(false)
const currentTime = ref('00:00')
const totalTime = ref('00:30')
const showBGMSelector = ref(false)
const bgmVolume = ref(80)

const currentClip = ref<any>(null)

// Mock data
const videoClips = ref([
  { id: 1, order: 1, duration: 5, thumbnail: 'https://via.placeholder.com/160x90?text=Clip+1' },
  { id: 2, order: 2, duration: 4, thumbnail: 'https://via.placeholder.com/160x90?text=Clip+2' },
  { id: 3, order: 3, duration: 6, thumbnail: 'https://via.placeholder.com/160x90?text=Clip+3' },
])

const audioClips = ref([
  { id: 1, name: 'voice_001.mp3', duration: 5, offset: 0 },
  { id: 2, name: 'voice_002.mp3', duration: 4, offset: 5 },
])

const subtitles = ref([
  { id: 1, text: '今天是个好日子！', start: 0, duration: 3 },
  { id: 2, text: '好久不见！', start: 5, duration: 2 },
])

const bgm = ref<any>(null)

const bgmOptions = ref([
  { id: 1, name: 'Happy Background', mood: '欢快', duration: 120 },
  { id: 2, name: 'Sad Piano', mood: '悲伤', duration: 180 },
  { id: 3, name: 'Tense Strings', mood: '紧张', duration: 150 },
])

const selectClip = (clip: any) => {
  currentClip.value = clip
}

const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  // TODO: Implement actual playback
}

const seek = (time: number) => {
  currentTime.value = '00:00'
  isPlaying.value = false
}

const handleCompose = async () => {
  composing.value = true
  composeProgress.value = 0

  const stages = [
    '正在合成视频...',
    '正在添加配音...',
    '正在添加 BGM...',
    '正在添加字幕...',
    '正在渲染输出...',
  ]

  for (let i = 0; i < stages.length; i++) {
    composeStatus.value = stages[i]
    composeProgress.value = (i + 1) * 20
    await new Promise(resolve => setTimeout(resolve, 1000))
  }

  composing.value = false
  ElMessage.success('合成成功')
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

const selectBGM = (track: any) => {
  bgm.value = track
  showBGMSelector.value = false
  ElMessage.success(`已选择：${track.name}`)
}

const removeBGM = () => {
  bgm.value = null
}

const addSubtitle = () => {
  subtitles.value.push({
    id: Date.now(),
    text: '',
    start: 0,
    duration: 3,
  })
}

const updateSubtitle = (index: number) => {
  ElMessage.success('字幕已更新')
}

const removeSubtitle = (index: number) => {
  subtitles.value.splice(index, 1)
  ElMessage.success('字幕已删除')
}
</script>

<style scoped lang="scss">
.video-composition {
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
  }

  .actions {
    display: flex;
    gap: 8px;
  }

  .timeline-container {
    .track {
      display: flex;
      margin-bottom: 12px;

      .track-header {
        width: 100px;
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: #666;
      }

      .track-content {
        flex: 1;
        display: flex;
        align-items: center;
        background: #f5f7fa;
        border-radius: 4px;
        padding: 8px;
        min-height: 60px;
      }

      .clip {
        height: 50px;
        border-radius: 4px;
        overflow: hidden;
        margin-right: 4px;
        cursor: pointer;
        position: relative;
        transition: transform 0.2s;

        &:hover {
          transform: scale(1.05);
        }

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .clip-order {
          position: absolute;
          bottom: 2px;
          right: 4px;
          background: rgba(0, 0, 0, 0.6);
          color: white;
          font-size: 11px;
          padding: 1px 4px;
          border-radius: 2px;
        }

        &.audio-clip, &.bgm-clip {
          background: #e6f7ff;
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 0 8px;

          .clip-name {
            font-size: 12px;
            color: #333;
          }
        }

        &.bgm-clip {
          background: #f9f0ff;
        }

        &.subtitle-clip {
          background: #fff7e6;
          display: flex;
          align-items: center;
          justify-content: center;

          .subtitle-text {
            font-size: 12px;
            color: #333;
          }
        }
      }

      .add-bgm {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #999;
        cursor: pointer;
        padding: 0 16px;

        &:hover {
          color: #409eff;
        }
      }
    }
  }

  .playback-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-top: 16px;

    .timecode {
      font-family: monospace;
      font-size: 14px;
      color: #666;
    }
  }

  .preview-container {
    .preview-screen {
      aspect-ratio: 16 / 9;
      background: #000;
      border-radius: 4px;
      overflow: hidden;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .placeholder {
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #666;

        .el-icon {
          font-size: 48px;
          margin-bottom: 8px;
        }
      }
    }
  }

  .subtitle-list {
    .subtitle-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;

      .subtitle-time {
        font-size: 12px;
        color: #999;
        min-width: 100px;
      }
    }
  }

  .bgm-empty {
    text-align: center;
    padding: 20px;
    color: #999;
  }

  .bgm-selected {
    .bgm-info {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
    }

    .bgm-volume {
      display: flex;
      align-items: center;
      gap: 12px;

      span {
        min-width: 40px;
        font-size: 13px;
        color: #666;
      }

      .el-slider {
        flex: 1;
      }
    }
  }

  .progress-card {
    .progress-status {
      margin-top: 8px;
      font-size: 13px;
      color: #666;
      text-align: center;
    }
  }
}
</style>
