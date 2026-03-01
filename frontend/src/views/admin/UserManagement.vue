<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="header">
          <span>用户管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建用户
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索姓名或邮箱"
          style="width: 240px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterRole" placeholder="角色筛选" clearable style="width: 150px" @change="handleFilter">
          <el-option label="管理员" value="admin" />
          <el-option label="组长" value="team_lead" />
          <el-option label="组员" value="team_member" />
        </el-select>

        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px" @change="handleFilter">
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
      </div>

      <!-- 用户表格 -->
      <el-table
        v-loading="loading"
        :data="filteredUsers"
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :active-value="true"
              :inactive-value="false"
              @change="handleToggleStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="500px"
      @close="resetDialog"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱"
            :disabled="!!editingUser"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码（编辑时留空表示不修改）"
            show-password
            :required="!editingUser"
          />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="组长" value="team_lead" />
            <el-option label="组员" value="team_member" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
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
import { Plus, Search } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import type { User, UserRole } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const filterRole = ref<string>('')
const filterStatus = ref<boolean | ''>('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const users = ref<User[]>([])
const dialogVisible = ref(false)
const editingUser = ref<User | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  name: '',
  email: '',
  password: '',
  role: 'team_member' as UserRole,
  is_active: true,
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2-20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' },
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' },
  ],
}

const filteredUsers = computed(() => {
  let result = users.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      (u) =>
        u.name.toLowerCase().includes(query) ||
        u.email.toLowerCase().includes(query)
    )
  }

  if (filterRole.value) {
    result = result.filter((u) => u.role === filterRole.value)
  }

  if (filterStatus !== '') {
    result = result.filter((u) => u.is_active === filterStatus.value)
  }

  return result
})

const roleLabel = (role: string) => {
  const labels: Record<string, string> = {
    admin: '管理员',
    team_lead: '组长',
    team_member: '组员',
  }
  return labels[role] || role
}

const roleType = (role: string) => {
  const types: Record<string, any> = {
    admin: 'danger',
    team_lead: 'warning',
    team_member: '',
  }
  return types[role] || ''
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.users.list({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
    })
    users.value = response.data.items || response.data
    pagination.total = response.data.total || users.value.length
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
}

const handleFilter = () => {
  pagination.page = 1
}

const openCreateDialog = () => {
  editingUser.value = null
  dialogVisible.value = true
}

const handleEdit = (user: User) => {
  editingUser.value = user
  formData.name = user.name
  formData.email = user.email
  formData.role = user.role
  formData.is_active = user.is_active
  formData.password = ''
  dialogVisible.value = true
}

const handleToggleStatus = async (user: User) => {
  try {
    await api.users.update(user.id, { is_active: user.is_active })
    ElMessage.success('状态已更新')
  } catch (error) {
    user.is_active = !user.is_active
    ElMessage.error('更新状态失败')
  }
}

const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${user.name}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await api.users.delete(user.id)
    ElMessage.success('删除成功')
    fetchUsers()
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
      const data: any = {
        name: formData.name,
        email: formData.email,
        role: formData.role,
        is_active: formData.is_active,
      }

      if (formData.password) {
        data.password = formData.password
      }

      if (editingUser.value) {
        await api.users.update(editingUser.value.id, data)
        ElMessage.success('更新成功')
      } else {
        await api.users.create(data)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      fetchUsers()
    } catch (error) {
      ElMessage.error(editingUser.value ? '更新失败' : '创建失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

const resetDialog = () => {
  editingUser.value = null
  formData.name = ''
  formData.email = ''
  formData.password = ''
  formData.role = 'team_member'
  formData.is_active = true
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped lang="scss">
.user-management {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .pagination {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
