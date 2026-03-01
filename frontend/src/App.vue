<template>
  <router-view />
</template>

<script setup lang="ts">
// 根组件，仅作为路由容器
</script>

<style>
#app {
  width: 100%;
  height: 100%;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
