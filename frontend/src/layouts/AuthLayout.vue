<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1 class="auth-title">AI Manga Pipeline</h1>
          <p class="auth-subtitle">漫剧生成流水线系统</p>
        </div>
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.auth-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  text-align: center;
}

.auth-title {
  color: white;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 1px;
}

.auth-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin: 8px 0 0;
}
</style>
