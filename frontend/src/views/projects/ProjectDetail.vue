<template>
  <div class="empty-page">
    <el-empty :description="description || '功能开发中...'" />
    <el-button type="primary" @click="$router.back()">返回</el-button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  description?: string
}>()
</script>

<style scoped lang="scss">
.empty-page {
  text-align: center;
  padding: 40px;
}
</style>
