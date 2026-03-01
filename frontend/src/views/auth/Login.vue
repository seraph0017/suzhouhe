<template>
  <div class="login-page">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      class="login-form"
      @keyup.enter="handleLogin"
    >
      <el-form-item prop="email">
        <el-input
          v-model="formData.email"
          placeholder="邮箱"
          size="large"
          :prefix-icon="Message"
          clearable
          @input="handleEmailInput"
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="formData.password"
          type="password"
          placeholder="密码"
          size="large"
          :prefix-icon="Lock"
          show-password
        />
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="formData.remember">记住我</el-checkbox>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          class="login-btn"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form-item>

      <div class="login-tips">
        <p>演示账号：</p>
        <p>管理员：admin@example.com / admin123</p>
        <p>组长：lead@example.com / lead123</p>
        <p>组员：member@example.com / member123</p>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = reactive({
  email: '',
  password: '',
  remember: false,
})

const formRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' },
  ],
}

// 自动去除邮箱前后空格
const handleEmailInput = (value: string) => {
  formData.email = value.trim()
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      const result = await authStore.login(formData.email, formData.password)

      if (result.success) {
        ElMessage.success('登录成功')

        // 重定向到原页面或仪表盘
        const redirect = route.query.redirect as string
        router.push(redirect || '/dashboard')
      } else {
        ElMessage.error('登录失败，请检查账号密码')
      }
    } catch (error) {
      ElMessage.error('登录失败，请检查网络连接')
      console.error(error)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  padding: 40px 20px;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
}

.login-tips {
  margin-top: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 13px;
  color: #606266;
}

.login-tips p {
  margin: 4px 0;
}
</style>
