import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, TokenResponse } from '@/types'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string>('')
  const refreshToken = ref<string>('')
  const tokenExpiry = ref<number>(0)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeamLead = computed(() => user.value?.role === 'team_lead')
  const isTeamMember = computed(() => user.value?.role === 'team_member')
  const isTokenExpiring = computed(() => {
    const now = Date.now()
    return tokenExpiry.value - now < 5 * 60 * 1000 // 5 分钟内过期
  })

  // Actions
  function setTokens(tokens: TokenResponse) {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    tokenExpiry.value = Date.now() + tokens.expires_in * 1000
  }

  function setUser(userData: User) {
    user.value = userData
  }

  async function login(email: string, password: string) {
    try {
      const response = await api.auth.login(email, password)
      // 响应拦截器已经返回 response.data
      setTokens(response as TokenResponse)

      // 获取当前用户信息
      const userResponse = await api.auth.getCurrentUser()
      setUser(userResponse as User)

      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  async function refreshTokenAction() {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await api.auth.refreshToken()
      setTokens(response as TokenResponse)
      return { success: true }
    } catch (error) {
      // 刷新失败，清除所有数据但不调用 logout() 避免无限循环
      user.value = null
      accessToken.value = ''
      refreshToken.value = ''
      tokenExpiry.value = 0
      throw error
    }
  }

  async function logout() {
    // 先清除本地数据，防止无限循环
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    tokenExpiry.value = 0

    // 静默调用后端 logout，不处理错误
    api.auth.logout().catch(() => {
      // 忽略错误，不递归调用 logout
    })
  }

  async function initAuth() {
    // 从持久化恢复后验证 token
    if (accessToken.value && !user.value) {
      try {
        const userResponse = await api.auth.getCurrentUser()
        setUser(userResponse as User)
      } catch (error) {
        // Token 无效，尝试刷新
        if (refreshToken.value) {
          try {
            await refreshTokenAction()
            const userResponse = await api.auth.getCurrentUser()
            setUser(userResponse as User)
          } catch {
            // 刷新也失败，清除所有数据
            user.value = null
            accessToken.value = ''
            refreshToken.value = ''
            tokenExpiry.value = 0
          }
        } else {
          // 没有 refresh token，清除所有数据
          user.value = null
          accessToken.value = ''
          refreshToken.value = ''
          tokenExpiry.value = 0
        }
      }
    }
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    tokenExpiry,
    // Getters
    isAuthenticated,
    isTokenExpiring,
    isAdmin,
    isTeamLead,
    isTeamMember,
    // Actions
    setTokens,
    setUser,
    login,
    logout,
    refreshTokenAction,
    initAuth,
  }
}, {
  persist: {
    key: 'auth',
    storage: localStorage,
    paths: ['accessToken', 'refreshToken', 'tokenExpiry', 'user'],
  },
})
