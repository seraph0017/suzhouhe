// 类型定义

// API 响应基础结构
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 用户角色
export type UserRole = 'admin' | 'team_lead' | 'team_member'

// 用户信息
export interface User {
  id: number
  email: string
  name: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at?: string
}

// 登录请求
export interface LoginRequest {
  email: string
  password: string
}

// Token 响应
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// 项目状态
export type ProjectStatus = 'planning' | 'in_progress' | 'on_hold' | 'completed' | 'archived'

// 项目
export interface Project {
  id: number
  name: string
  description?: string
  status: ProjectStatus
  team_lead_id: number
  team_lead?: User
  created_at: string
  updated_at?: string
}

// 剧本状态
export type ScriptStatus = 'draft' | 'in_review' | 'locked' | 'archived'

// 剧本
export interface Script {
  id: number
  project_id: number
  title: string
  content: string
  summary?: string
  version: number
  status: ScriptStatus
  is_locked: boolean
  locked_at?: string
  locked_by?: number
  created_at: string
  updated_at?: string
}

// 章节状态
export type ChapterStatus = 'draft' | 'in_progress' | 'in_review' | 'completed' | 'archived'

// 章节
export interface Chapter {
  id: number
  script_id: number
  order: number
  title: string
  content: string
  summary?: string
  status: ChapterStatus
  created_at: string
  updated_at?: string
}

// 分镜状态
export type StoryboardStatus = 'draft' | 'in_review' | 'locked' | 'materials_generated' | 'video_generated' | 'completed'

// 分镜
export interface Storyboard {
  id: number
  chapter_id: number
  order: number
  title?: string
  visual_description: string
  camera_direction?: string
  dialogue?: string
  duration_seconds: number
  emotion?: string
  status: StoryboardStatus
  is_locked: boolean
  selected_image_id?: number
  selected_audio_id?: number
  selected_video_id?: number
  created_at: string
  updated_at?: string
  locked_at?: string
}

// 资产类型
export type AssetType = 'image' | 'audio' | 'video' | 'document' | 'other'
export type AssetStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'archived'

// 资产
export interface Asset {
  id: number
  project_id: number
  storyboard_id?: number
  type: AssetType
  status: AssetStatus
  file_path: string
  file_name: string
  file_size?: number
  mime_type?: string
  url: string
  metadata?: Record<string, unknown>
  provider?: string
  model_name?: string
  duration_seconds?: number
  width?: number
  height?: number
  created_at: string
  updated_at?: string
}

// 审核类型
export type ReviewType = 'first_audit' | 'second_audit' | 'script_review' | 'storyboard_review'
export type ReviewStatus = 'pending' | 'approved' | 'rejected' | 'changes_requested'

// 审核
export interface Review {
  id: number
  review_type: ReviewType
  target_type: string
  target_id: number
  reviewer_id: number
  status: ReviewStatus
  feedback?: string
  rejection_reason?: string
  created_at: string
  reviewed_at?: string
}

// 模型配置
export interface ModelProvider {
  id: number
  provider_type: string
  name: string
  display_name?: string
  api_endpoint?: string
  is_active: boolean
  is_default: boolean
  health_status?: string
  last_health_check?: string
  created_at: string
  updated_at?: string
}

// 任务状态
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'blocked'
export type TaskPriority = 'low' | 'normal' | 'high' | 'urgent'
export type TaskType = 'storyboard' | 'material_gen' | 'first_audit' | 'second_audit' | 'video_compose'

// 任务
export interface Task {
  id: number
  project_id: number
  chapter_id?: number
  assigned_to?: number
  assigned_by?: number
  task_type: TaskType
  status: TaskStatus
  priority: TaskPriority
  due_date?: string
  started_at?: string
  completed_at?: string
  metadata?: Record<string, unknown>
  created_at: string
  updated_at?: string
}

// 生成任务状态
export type JobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
export type JobType = 'image' | 'audio' | 'video' | 'bgm'

// 生成任务
export interface GenerationJob {
  id: number
  project_id: number
  storyboard_id?: number
  job_type: JobType
  status: JobStatus
  model_config_id?: number
  request_params: Record<string, unknown>
  result_data?: Record<string, unknown>
  error_message?: string
  progress: number
  retry_count: number
  created_at: string
  started_at?: string
  completed_at?: string
}

// 仪表盘统计
export interface DashboardStats {
  total_projects: number
  active_projects: number
  my_tasks: number
  pending_audits: number
  completed_today: number
}
