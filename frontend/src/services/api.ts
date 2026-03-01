import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios'
import type { ApiResponse, TokenResponse } from '@/types'
import { useAuthStore } from '@/stores/auth'

// API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.accessToken

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError<ApiResponse>) => {
    const authStore = useAuthStore()
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    // 如果是 refresh 请求，失败后直接退出，不重试
    if (originalRequest.headers?.['X-Skip-Refresh']) {
      authStore.logout()
      return Promise.reject(error)
    }

    // 如果是 logout 请求，失败后不重试
    if (originalRequest.url?.includes('/auth/logout')) {
      return Promise.reject(error)
    }

    // 401 错误且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // 尝试刷新 token
        await authStore.refreshTokenAction()

        // 重试原请求
        const token = authStore.accessToken
        if (token && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        // 刷新失败，退出登录
        authStore.logout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API 服务方法
export const api = {
  // 认证
  auth: {
    login: (email: string, password: string) => {
      // OAuth2 使用 application/x-www-form-urlencoded 格式
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)
      return apiClient.post<TokenResponse>('/auth/login', form.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
    },
    refreshToken: () => {
      const authStore = useAuthStore()
      // 发送 refresh token，使用 custom header 避免触发 401 重试
      return apiClient.post<TokenResponse>('/auth/refresh', null, {
        headers: {
          Authorization: `Bearer ${authStore.refreshToken}`,
          'X-Skip-Refresh': 'true',
        },
      })
    },
    logout: () => {
      return apiClient.post('/auth/logout')
    },
    getCurrentUser: () => {
      return apiClient.get('/auth/me')
    },
  },

  // 用户
  users: {
    list: (params?: Record<string, unknown>) => {
      return apiClient.get('/users', { params })
    },
    get: (id: number) => {
      return apiClient.get(`/users/${id}`)
    },
    create: (data: Record<string, unknown>) => {
      return apiClient.post('/users', data)
    },
    update: (id: number, data: Record<string, unknown>) => {
      return apiClient.put(`/users/${id}`, data)
    },
    delete: (id: number) => {
      return apiClient.delete(`/users/${id}`)
    },
  },

  // 项目
  projects: {
    list: (params?: Record<string, unknown>) => {
      return apiClient.get('/projects', { params })
    },
    get: (id: number) => {
      return apiClient.get(`/projects/${id}`)
    },
    create: (data: Record<string, unknown>) => {
      return apiClient.post('/projects', data)
    },
    update: (id: number, data: Record<string, unknown>) => {
      return apiClient.put(`/projects/${id}`, data)
    },
    delete: (id: number) => {
      return apiClient.delete(`/projects/${id}`)
    },
    getMembers: (id: number) => {
      return apiClient.get(`/projects/${id}/members`)
    },
    addMember: (id: number, userId: number, role: string) => {
      return apiClient.post(`/projects/${id}/members`, { user_id: userId, role })
    },
    removeMember: (projectId: number, userId: number) => {
      return apiClient.delete(`/projects/${projectId}/members/${userId}`)
    },
  },

  // 剧本
  scripts: {
    list: (projectId: number) => {
      return apiClient.get(`/scripts?project_id=${projectId}`)
    },
    get: (id: number) => {
      return apiClient.get(`/scripts/${id}`)
    },
    create: (data: Record<string, unknown>) => {
      return apiClient.post('/scripts', data)
    },
    update: (id: number, data: Record<string, unknown>) => {
      return apiClient.put(`/scripts/${id}`, data)
    },
    delete: (id: number) => {
      return apiClient.delete(`/scripts/${id}`)
    },
    generate: (data: Record<string, unknown>) => {
      return apiClient.post('/scripts/generate', data)
    },
    lock: (id: number) => {
      return apiClient.post(`/scripts/${id}/lock`)
    },
    unlock: (id: number) => {
      return apiClient.post(`/scripts/${id}/unlock`)
    },
  },

  // 章节
  chapters: {
    list: (scriptId: number) => {
      return apiClient.get(`/chapters?script_id=${scriptId}`)
    },
    get: (id: number) => {
      return apiClient.get(`/chapters/${id}`)
    },
    create: (data: Record<string, unknown>) => {
      return apiClient.post('/chapters', data)
    },
    update: (id: number, data: Record<string, unknown>) => {
      return apiClient.put(`/chapters/${id}`, data)
    },
    delete: (id: number) => {
      return apiClient.delete(`/chapters/${id}`)
    },
    reorder: (ids: number[]) => {
      return apiClient.post('/chapters/reorder', { ids })
    },
    generate: (scriptId: number) => {
      return apiClient.post('/chapters/generate', { script_id: scriptId })
    },
  },

  // 分镜
  storyboards: {
    list: (chapterId: number) => {
      return apiClient.get(`/storyboards?chapter_id=${chapterId}`)
    },
    get: (id: number) => {
      return apiClient.get(`/storyboards/${id}`)
    },
    create: (data: Record<string, unknown>) => {
      return apiClient.post('/storyboards', data)
    },
    update: (id: number, data: Record<string, unknown>) => {
      return apiClient.put(`/storyboards/${id}`, data)
    },
    delete: (id: number) => {
      return apiClient.delete(`/storyboards/${id}`)
    },
    generate: (chapterId: number) => {
      return apiClient.post('/storyboards/generate', { chapter_id: chapterId })
    },
    generateImage: (storyboardId: number) => {
      return apiClient.post(`/storyboards/${storyboardId}/generate-image`)
    },
    lock: (id: number) => {
      return apiClient.post(`/storyboards/${id}/lock`)
    },
  },

  // 素材生成
  generation: {
    generateImages: (storyboardId: number, count?: number) => {
      return apiClient.post('/generation/images', { storyboard_id: storyboardId, count })
    },
    generateAudio: (storyboardId: number, voiceId?: string) => {
      return apiClient.post('/generation/audio', { storyboard_id: storyboardId, voice_id: voiceId })
    },
    generateVideo: (storyboardId: number) => {
      return apiClient.post('/generation/video', { storyboard_id: storyboardId })
    },
    getJobStatus: (jobId: number) => {
      return apiClient.get(`/generation/jobs/${jobId}`)
    },
    listJobs: (projectId?: number) => {
      return apiClient.get('/generation/jobs', { params: { project_id: projectId } })
    },
  },

  // 素材选择
  materials: {
    listImages: (storyboardId: number) => {
      return apiClient.get(`/materials/images?storyboard_id=${storyboardId}`)
    },
    selectImage: (storyboardId: number, imageId: number) => {
      return apiClient.post(`/materials/${storyboardId}/select-image`, { image_id: imageId })
    },
    listVoices: () => {
      return apiClient.get('/materials/voices')
    },
    selectVoice: (storyboardId: number, voiceId: string) => {
      return apiClient.post(`/materials/${storyboardId}/select-voice`, { voice_id: voiceId })
    },
  },

  // 审核
  audits: {
    submitFirst: (targetType: string, targetId: number, feedback?: string) => {
      return apiClient.post('/audits/first', { target_type: targetType, target_id: targetId, feedback })
    },
    submitSecond: (targetType: string, targetId: number, feedback?: string) => {
      return apiClient.post('/audits/second', { target_type: targetType, target_id: targetId, feedback })
    },
    approve: (reviewId: number, feedback?: string) => {
      return apiClient.post(`/audits/${reviewId}/approve`, { feedback })
    },
    reject: (reviewId: number, reason: string) => {
      return apiClient.post(`/audits/${reviewId}/reject`, { reason })
    },
    listPending: (type?: 'first' | 'second') => {
      return apiClient.get('/audits/pending', { params: { type } })
    },
  },

  // 模型配置
  models: {
    list: (type?: string) => {
      return apiClient.get('/models', { params: { type } })
    },
    get: (id: number) => {
      return apiClient.get(`/models/${id}`)
    },
    create: (data: Record<string, unknown>) => {
      return apiClient.post('/models', data)
    },
    update: (id: number, data: Record<string, unknown>) => {
      return apiClient.put(`/models/${id}`, data)
    },
    delete: (id: number) => {
      return apiClient.delete(`/models/${id}`)
    },
    setDefault: (id: number) => {
      return apiClient.post(`/models/${id}/set-default`)
    },
    healthCheck: (id: number) => {
      return apiClient.post(`/models/${id}/health-check`)
    },
  },

  // 仪表盘
  dashboard: {
    getStats: () => {
      return apiClient.get('/dashboard/stats')
    },
    getTasks: () => {
      return apiClient.get('/dashboard/tasks')
    },
    getProjects: () => {
      return apiClient.get('/dashboard/projects')
    },
  },
}

export default apiClient
