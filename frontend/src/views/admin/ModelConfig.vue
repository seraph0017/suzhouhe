<template>
  <div class="model-config">
    <el-card>
      <template #header>
        <div class="header">
          <span>AI 模型配置</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            添加模型
          </el-button>
        </div>
      </template>

      <!-- 模型列表 -->
      <div v-loading="loading" class="model-list">
        <el-empty v-if="models.length === 0" description="暂无模型配置" />

        <div v-else class="model-items">
          <el-card
            v-for="model in models"
            :key="model.id"
            class="model-card"
            :class="{ default: model.is_default, active: model.is_active }"
          >
            <div class="model-header">
              <div class="model-info">
                <h3>{{ model.provider_name }}</h3>
                <el-tag :type="model.provider_type === 'llm' ? 'primary' : model.provider_type === 'image' ? 'success' : 'warning'" size="small">
                  {{ modelTypeLabel(model.provider_type) }}
                </el-tag>
              </div>
              <div class="model-actions">
                <el-switch
                  v-model="model.is_active"
                  @change="handleToggleStatus(model)"
                />
              </div>
            </div>

            <div class="model-content">
              <div class="model-row">
                <span class="label">API 端点:</span>
                <span class="value">{{ maskApiEndpoint(model.api_endpoint) }}</span>
              </div>
              <div class="model-row">
                <span class="label">状态:</span>
                <el-tag :type="model.is_active ? 'success' : 'info'" size="small">
                  {{ model.is_active ? '已启用' : '已禁用' }}
                </el-tag>
              </div>
              <div class="model-row">
                <span class="label">默认:</span>
                <el-tag v-if="model.is_default" type="success" size="small">是</el-tag>
                <span v-else class="value">否</span>
              </div>
            </div>

            <div class="model-footer">
              <el-button link type="primary" @click="handleEdit(model)">编辑</el-button>
              <el-button link type="success" v-if="!model.is_default" @click="handleSetDefault(model)">设为默认</el-button>
              <el-button link type="warning" @click="handleHealthCheck(model)">检测</el-button>
              <el-button link type="danger" @click="handleDelete(model)">删除</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 创建/编辑模型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingModel ? '编辑模型' : '添加模型'"
      width="600px"
      @close="resetDialog"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="模型类型" prop="provider_type">
          <el-select v-model="formData.provider_type" placeholder="请选择模型类型" style="width: 100%">
            <el-option label="LLM (文本生成)" value="llm" />
            <el-option label="Image (图片生成)" value="image" />
            <el-option label="Video (视频生成)" value="video" />
            <el-option label="TTS (语音合成)" value="tts" />
            <el-option label="BGM (背景音乐)" value="bgm" />
          </el-select>
        </el-form-item>

        <el-form-item label="提供商名称" prop="provider_name">
          <el-input v-model="formData.provider_name" placeholder="例如：OpenAI, Anthropic, Runway" />
        </el-form-item>

        <el-form-item label="API 端点" prop="api_endpoint">
          <el-input v-model="formData.api_endpoint" placeholder="例如：https://api.openai.com/v1" />
        </el-form-item>

        <el-form-item label="API Key" prop="api_key">
          <el-input
            v-model="formData.api_key"
            type="password"
            placeholder="请输入 API Key"
            show-password
            :required="!editingModel"
          />
        </el-form-item>

        <el-form-item label="启用" prop="is_active">
          <el-switch v-model="formData.is_active" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api } from '@/services/api'

const loading = ref(false)
const submitting = ref(false)
const models = ref<any[]>([])
const dialogVisible = ref(false)
const editingModel = ref<any>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  provider_type: 'llm',
  provider_name: '',
  api_endpoint: '',
  api_key: '',
  is_active: true,
  config: {},
})

const formRules: FormRules = {
  provider_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' },
  ],
  provider_name: [
    { required: true, message: '请输入提供商名称', trigger: 'blur' },
  ],
  api_endpoint: [
    { required: true, message: '请输入 API 端点', trigger: 'blur' },
    { type: 'url', message: '请输入有效的 URL', trigger: 'blur' },
  ],
  api_key: [
    { required: true, message: '请输入 API Key', trigger: 'blur' },
  ],
}

const modelTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    llm: 'LLM (文本生成)',
    image: 'Image (图片生成)',
    video: 'Video (视频生成)',
    tts: 'TTS (语音合成)',
    bgm: 'BGM (背景音乐)',
  }
  return labels[type] || type
}

const maskApiEndpoint = (endpoint: string) => {
  if (!endpoint) return ''
  try {
    const url = new URL(endpoint)
    return `${url.protocol}//${url.hostname}***`
  } catch {
    return endpoint.substring(0, 20) + '...'
  }
}

const fetchModels = async () => {
  loading.value = true
  try {
    const response = await api.models.list()
    models.value = response.data || response
  } catch (error) {
    ElMessage.error('获取模型列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = async (model: any) => {
  try {
    await api.models.update(model.id, { is_active: model.is_active })
    ElMessage.success('状态已更新')
  } catch (error) {
    model.is_active = !model.is_active
    ElMessage.error('更新失败')
  }
}

const handleEdit = (model: any) => {
  editingModel.value = model
  formData.provider_type = model.provider_type
  formData.provider_name = model.provider_name
  formData.api_endpoint = model.api_endpoint || ''
  formData.api_key = ''
  formData.is_active = model.is_active
  dialogVisible.value = true
}

const handleSetDefault = async (model: any) => {
  try {
    await api.models.setDefault(model.id)
    ElMessage.success('默认模型已设置')
    fetchModels()
  } catch (error) {
    ElMessage.error('设置失败')
    console.error(error)
  }
}

const handleHealthCheck = async (model: any) => {
  try {
    const response = await api.models.healthCheck(model.id)
    if (response.data?.success) {
      ElMessage.success('模型连接正常')
    } else {
      ElMessage.warning('模型连接异常')
    }
  } catch (error) {
    ElMessage.error('模型连接失败')
    console.error(error)
  }
}

const handleDelete = async (model: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除模型 "${model.provider_name}" 吗？`, '警告', {
      type: 'warning',
    })

    await api.models.delete(model.id)
    ElMessage.success('删除成功')
    fetchModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
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
        provider_type: formData.provider_type,
        provider_name: formData.provider_name,
        api_endpoint: formData.api_endpoint,
        api_key: formData.api_key,
        is_active: formData.is_active,
        config: {},
      }

      if (editingModel.value) {
        await api.models.update(editingModel.value.id, data)
        ElMessage.success('更新成功')
      } else {
        await api.models.create(data)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      fetchModels()
    } catch (error) {
      ElMessage.error(editingModel.value ? '更新失败' : '创建失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

const resetDialog = () => {
  editingModel.value = null
  formData.provider_type = 'llm'
  formData.provider_name = ''
  formData.api_endpoint = ''
  formData.api_key = ''
  formData.is_active = true
  formRef.value?.resetFields()
}

const openCreateDialog = () => {
  editingModel.value = null
  dialogVisible.value = true
}

onMounted(() => {
  fetchModels()
})
</script>

<style scoped lang="scss">
.model-config {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .model-list {
    min-height: 400px;
  }

  .model-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }

  .model-card {
    border: 2px solid #e8e8e8;
    border-radius: 12px;
    transition: all 0.2s;

    &.default {
      border-color: #67c23a;
      background: linear-gradient(135deg, #f0f9eb 0%, white 100%);
    }

    &.active {
      box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
    }

    .model-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;

      .model-info {
        h3 {
          margin: 0 0 8px;
          font-size: 16px;
          color: #333;
        }
      }
    }

    .model-content {
      margin-bottom: 16px;

      .model-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 13px;

        .label {
          color: #666;
        }

        .value {
          color: #333;
        }
      }
    }

    .model-footer {
      display: flex;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #e8e8e8;
    }
  }
}
</style>
