import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task, TaskStatus, TaskPriority } from '@/types'
import { api } from '@/services/api'

export const useTaskStore = defineStore('tasks', () => {
  // State
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const myTasks = computed(() => tasks.value.filter(t => t.status !== 'completed'))
  const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending'))
  const inProgressTasks = computed(() => tasks.value.filter(t => t.status === 'in_progress'))
  const blockedTasks = computed(() => tasks.value.filter(t => t.status === 'blocked'))

  const tasksByPriority = computed(() => {
    const priorityOrder: Record<TaskPriority, number> = {
      urgent: 0,
      high: 1,
      normal: 2,
      low: 3,
    }
    return [...tasks.value].sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
  })

  // Actions
  async function fetchTasks(params?: { status?: TaskStatus; project_id?: number }) {
    loading.value = true
    error.value = null

    try {
      const response = await api.dashboard.getTasks()
      tasks.value = response.data.items || response.data
    } catch (err) {
      error.value = 'Failed to fetch tasks'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function updateTaskStatus(taskId: number, status: TaskStatus) {
    const originalTask = tasks.value.find(t => t.id === taskId)
    if (originalTask) {
      originalTask.status = status
    }

    try {
      // TODO: Implement update task API when available
      await Promise.resolve()
    } catch (err) {
      error.value = 'Failed to update task'
      console.error(err)
      if (originalTask) {
        originalTask.status = status
      }
      throw err
    }
  }

  return {
    // State
    tasks,
    loading,
    error,
    // Getters
    myTasks,
    pendingTasks,
    inProgressTasks,
    blockedTasks,
    tasksByPriority,
    // Actions
    fetchTasks,
    updateTaskStatus,
  }
}, {
  persist: {
    key: 'tasks',
    storage: localStorage,
  },
})
