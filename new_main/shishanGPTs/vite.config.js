import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'static': path.resolve(__dirname, 'src/assets')
    },
  },
  // 确保静态资源正确处理
  publicDir: 'public',
  server: {
    port: 5001,
    allowedHosts: ['shizi.hzau.edu.cn','218.199.69.86'],
    open: true
  },
  base: './'
})
