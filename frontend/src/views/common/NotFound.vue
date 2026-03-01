<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <p class="error-message">页面未找到</p>
      <p class="error-description">抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="$router.push('/dashboard')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.not-found-content {
  text-align: center;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: $primary-color;
  margin: 0;
  line-height: 1;
}

.error-message {
  font-size: 24px;
  color: #333;
  margin: 20px 0 10px;
}

.error-description {
  font-size: 16px;
  color: #666;
  margin: 0 0 30px;
}
</style>
