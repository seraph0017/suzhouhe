<template>
  <div class="material-selection">
    <div class="toolbar">
      <div class="breadcrumb">
        <span>素材库</span>
      </div>
      <div class="tabs">
        <el-radio-group v-model="activeTab" size="large">
          <el-radio-button label="images">图片库</el-radio-button>
          <el-radio-button label="audio">音频库</el-radio-button>
          <el-radio-button label="voices">音色库</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 图片库 -->
    <el-card v-if="activeTab === 'images'" class="material-card">
      <template #header>
        <div class="card-header">
          <span>图片素材</span>
          <el-input
            v-model="imageSearch"
            placeholder="搜索图片..."
            style="width: 200px"
            clearable
          />
        </div>
      </template>

      <div class="image-grid">
        <el-empty v-if="filteredImages.length === 0" description="暂无图片" />

        <div v-else class="image-items">
          <div
            v-for="img in filteredImages"
            :key="img.id"
            class="image-card"
            :class="{ selected: selectedImageIds.includes(img.id) }"
            @click="toggleImageSelection(img)"
          >
            <img :src="img.url" :alt="img.file_name" />
            <div class="image-info">
              <span class="image-name">{{ img.file_name }}</span>
              <span class="image-size">{{ img.width }}x{{ img.height }}</span>
            </div>
            <div class="image-overlay">
              <el-icon v-if="selectedImageIds.includes(img.id)"><CircleCheck /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="batch-actions" v-if="selectedImageIds.length > 0">
        <span>已选择 {{ selectedImageIds.length }} 张图片</span>
        <el-button type="primary" size="small" @click="handleBatchUse">批量使用</el-button>
      </div>
    </el-card>

    <!-- 音频库 -->
    <el-card v-if="activeTab === 'audio'" class="material-card">
      <template #header>
        <div class="card-header">
          <span>音频素材</span>
          <el-input
            v-model="audioSearch"
            placeholder="搜索音频..."
            style="width: 200px"
            clearable
          />
        </div>
      </template>

      <div class="audio-list">
        <el-empty v-if="filteredAudios.length === 0" description="暂无音频" />

        <el-table v-else :data="filteredAudios" style="width: 100%">
          <el-table-column label="选择" width="60">
            <template #default="{ row }">
              <el-radio
                v-model="selectedAudioId"
                :label="row.id"
                @change="handleSelectAudio(row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="file_name" label="文件名" min-width="200" />
          <el-table-column prop="duration_seconds" label="时长" width="100">
            <template #default="{ row }">
              {{ row.duration_seconds?.toFixed(1) }}s
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="播放" width="100">
            <template #default="{ row }">
              <audio :src="row.url" controls style="height: 32px; width: 150px" />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 音色库 -->
    <el-card v-if="activeTab === 'voices'" class="material-card">
      <template #header>
        <div class="card-header">
          <span>TTS 音色库</span>
        </div>
      </template>

      <div class="voice-grid">
        <div
          v-for="voice in voices"
          :key="voice.id"
          class="voice-card"
          :class="{ selected: selectedVoiceId === voice.id }"
          @click="selectedVoiceId = voice.id"
        >
          <div class="voice-avatar">
            <el-icon><User /></el-icon>
          </div>
          <div class="voice-info">
            <h4>{{ voice.name }}</h4>
            <p>{{ voice.description }}</p>
            <div class="voice-tags">
              <el-tag size="small" type="info">{{ voice.gender }}</el-tag>
              <el-tag size="small">{{ voice.style }}</el-tag>
            </div>
          </div>
          <div class="voice-actions">
            <el-button size="small" @click.stop="handlePreviewVoice(voice)">
              <el-icon><VideoPlay /></el-icon>
              试听
            </el-button>
            <el-button
              v-if="selectedVoiceId === voice.id"
              type="primary"
              size="small"
            >
              已选择
            </el-button>
            <el-button
              v-else
              type="primary"
              size="small"
              @click.stop="selectedVoiceId = voice.id"
            >
              选择
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck, User, VideoPlay } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { Asset } from '@/types'

const activeTab = ref('images')
const imageSearch = ref('')
const audioSearch = ref('')

const images = ref<Partial<Asset>[]>([])
const audios = ref<Partial<Asset>[]>([])
const voices = ref<any[]>([])

const selectedImageIds = ref<number[]>([])
const selectedAudioId = ref<number | null>(null)
const selectedVoiceId = ref<string>('')

const filteredImages = computed(() => {
  if (!imageSearch.value) return images.value
  return images.value.filter(img =>
    img.file_name?.toLowerCase().includes(imageSearch.value.toLowerCase())
  )
})

const filteredAudios = computed(() => {
  if (!audioSearch.value) return audios.value
  return audios.value.filter(audio =>
    audio.file_name?.toLowerCase().includes(audioSearch.value.toLowerCase())
  )
})

const fetchImages = async () => {
  try {
    // 获取所有图片素材（可能需要新的 API）
    // const response = await api.materials.listImages()
    // images.value = response.data || response
    ElMessage.info('图片库功能开发中')
  } catch (error) {
    console.error('Failed to fetch images:', error)
  }
}

const fetchAudios = async () => {
  try {
    // 获取所有音频素材
    // const response = await api.materials.listAudios()
    // audios.value = response.data || response
    ElMessage.info('音频库功能开发中')
  } catch (error) {
    console.error('Failed to fetch audios:', error)
  }
}

const fetchVoices = async () => {
  try {
    const response = await api.materials.listVoices()
    voices.value = response.data || response
  } catch (error) {
    console.error('Failed to fetch voices:', error)
  }
}

const toggleImageSelection = (img: Asset) => {
  const index = selectedImageIds.value.indexOf(img.id)
  if (index > -1) {
    selectedImageIds.value.splice(index, 1)
  } else {
    selectedImageIds.value.push(img.id)
  }
}

const handleSelectAudio = async (audio: Asset) => {
  try {
    // 调用 API 选择音频
    ElMessage.success(`已选择：${audio.file_name}`)
  } catch (error) {
    ElMessage.error('选择失败')
    console.error(error)
  }
}

const handlePreviewVoice = async (voice: any) => {
  try {
    // 播放试听音频
    ElMessage.info(`试听：${voice.name}`)
  } catch (error) {
    console.error('Failed to preview voice:', error)
  }
}

const handleBatchUse = () => {
  ElMessage.success(`已选择 ${selectedImageIds.value.length} 张图片`)
  // 批量使用功能开发中
}

onMounted(() => {
  fetchVoices()
})
</script>

<style scoped lang="scss">
.material-selection {
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

  .tabs {
    :deep(.el-radio-button) {
      margin-right: 8px;
    }
  }

  .material-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .image-grid {
      min-height: 400px;

      .image-items {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
      }

      .image-card {
        position: relative;
        border-radius: 8px;
        overflow: hidden;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.2s;

        &.selected {
          border-color: #67c23a;
        }

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        img {
          width: 100%;
          aspect-ratio: 1;
          object-fit: cover;
        }

        .image-info {
          padding: 8px;
          background: white;

          .image-name {
            display: block;
            font-size: 13px;
            color: #333;
            margin-bottom: 2px;
          }

          .image-size {
            font-size: 12px;
            color: #999;
          }
        }

        .image-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 50%;
          background: rgba(0, 0, 0, 0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 32px;
        }
      }
    }

    .batch-actions {
      margin-top: 16px;
      padding: 12px;
      background: #f0f9eb;
      border-radius: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .voice-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;

    .voice-card {
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.2s;

      &.selected {
        border-color: #67c23a;
        background: #f0f9eb;
      }

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      .voice-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        margin-bottom: 12px;
      }

      .voice-info {
        h4 {
          margin: 0 0 4px;
          font-size: 16px;
          color: #333;
        }

        p {
          margin: 0 0 8px;
          font-size: 13px;
          color: #666;
        }

        .voice-tags {
          display: flex;
          gap: 4px;
        }
      }

      .voice-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }
    }
  }
}
</style>
