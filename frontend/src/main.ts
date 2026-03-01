import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// 持久化插件
pinia.use(piniaPluginPersistedstate)

// Element Plus
app.use(ElementPlus, { locale: zhCn })

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 路由
app.use(router)
app.use(pinia)

app.mount('#app')
