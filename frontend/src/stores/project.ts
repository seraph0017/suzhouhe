import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, ProjectStatus } from '@/types'
import { api } from '@/services/api'

export const useProjectStore = defineStore('projects', () => {
  // State
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeProjects = computed(() =>
    projects.value.filter(p => p.status === 'in_progress' || p.status === 'planning')
  )

  const archivedProjects = computed(() =>
    projects.value.filter(p => p.status === 'archived' || p.status === 'completed')
  )

  const projectById = computed(() => (id: number) =>
    projects.value.find(p => p.id === id)
  )

  // Actions
  async function fetchProjects(params?: { status?: ProjectStatus }) {
    loading.value = true
    error.value = null

    try {
      const response = await api.projects.list(params)
      projects.value = response.data.items || response.data
    } catch (err: any) {
      // 401 错误不显示提示，因为会被重定向到登录页
      if (err?.response?.status !== 401) {
        error.value = 'Failed to fetch projects'
        console.error(err)
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: number) {
    loading.value = true
    error.value = null

    try {
      const response = await api.projects.get(id)
      currentProject.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Failed to fetch project'
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: { name: string; description?: string }) {
    try {
      const response = await api.projects.create(data)
      const newProject = response.data
      projects.value.unshift(newProject)
      return newProject
    } catch (err) {
      error.value = 'Failed to create project'
      console.error(err)
      throw err
    }
  }

  async function updateProject(id: number, data: Partial<Project>) {
    try {
      const response = await api.projects.update(id, data)
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = response.data
      }
      if (currentProject.value?.id === id) {
        currentProject.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = 'Failed to update project'
      console.error(err)
      throw err
    }
  }

  async function deleteProject(id: number) {
    try {
      await api.projects.delete(id)
      projects.value = projects.value.filter(p => p.id !== id)
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } catch (err) {
      error.value = 'Failed to delete project'
      console.error(err)
      throw err
    }
  }

  async function addMember(projectId: number, userId: number, role: string) {
    try {
      await api.projects.addMember(projectId, userId, role)
      // 刷新项目详情
      if (currentProject.value?.id === projectId) {
        await fetchProject(projectId)
      }
    } catch (err) {
      error.value = 'Failed to add member'
      console.error(err)
      throw err
    }
  }

  async function removeMember(projectId: number, userId: number) {
    try {
      await api.projects.removeMember(projectId, userId)
      if (currentProject.value?.id === projectId) {
        await fetchProject(projectId)
      }
    } catch (err) {
      error.value = 'Failed to remove member'
      console.error(err)
      throw err
    }
  }

  function setCurrentProject(project: Project | null) {
    currentProject.value = project
  }

  return {
    // State
    projects,
    currentProject,
    loading,
    error,
    // Getters
    activeProjects,
    archivedProjects,
    projectById,
    // Actions
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    addMember,
    removeMember,
    setCurrentProject,
  }
}, {
  persist: {
    key: 'projects',
    storage: localStorage,
    paths: ['currentProject'],
  },
})
