import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

// 导入全局样式
import './assets/styles/global.css'

const app = createApp(App)

app.use(store)
app.use(router)
app.use(Antd)

app.mount('#app') 