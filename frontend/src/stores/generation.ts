import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GenerationJob, JobStatus } from '@/types'
import { api } from '@/services/api'

export const useGenerationStore = defineStore('generation', () => {
  // State
  const jobs = ref<GenerationJob[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const runningJobs = computed(() => jobs.value.filter(j => j.status === 'running'))
  const pendingJobs = computed(() => jobs.value.filter(j => j.status === 'queued'))
  const failedJobs = computed(() => jobs.value.filter(j => j.status === 'failed'))
  const completedJobs = computed(() => jobs.value.filter(j => j.status === 'completed'))

  const getJobById = computed(() => (id: number) => jobs.value.find(j => j.id === id))

  // Actions
  async function fetchJobs(projectId?: number) {
    loading.value = true
    error.value = null

    try {
      const response = await api.generation.listJobs(projectId)
      jobs.value = response.data.items || response.data
    } catch (err) {
      error.value = 'Failed to fetch generation jobs'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchJobStatus(jobId: number) {
    try {
      const response = await api.generation.getJobStatus(jobId)
      const job = response.data
      const index = jobs.value.findIndex(j => j.id === jobId)
      if (index !== -1) {
        jobs.value[index] = job
      }
      return job
    } catch (err) {
      error.value = 'Failed to fetch job status'
      console.error(err)
      throw err
    }
  }

  function updateJob(jobId: number, updates: Partial<GenerationJob>) {
    const job = jobs.value.find(j => j.id === jobId)
    if (job) {
      Object.assign(job, updates)
    } else {
      jobs.value.push({ ...updates, id: jobId } as GenerationJob)
    }
  }

  function removeJob(jobId: number) {
    const index = jobs.value.findIndex(j => j.id === jobId)
    if (index !== -1) {
      jobs.value.splice(index, 1)
    }
  }

  return {
    // State
    jobs,
    loading,
    error,
    // Getters
    runningJobs,
    pendingJobs,
    failedJobs,
    completedJobs,
    getJobById,
    // Actions
    fetchJobs,
    fetchJobStatus,
    updateJob,
    removeJob,
  }
}, {
  persist: {
    key: 'generation',
    storage: localStorage,
    paths: ['jobs'],
  },
})
