<template>
  <div class="container">
    <!-- 左侧边栏 -->
    <left-sidebar />
    
    <!-- 右侧内容区域 - 使用路由视图 -->
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import LeftSidebar from './components/layout/LeftSidebar.vue';
import { configureMarked } from './utils/chatUtils';

const router = useRouter();
const route = useRoute();

// 初始化
onMounted(() => {
  configureMarked();
  console.log("App mounted, Vue 3 Composition API initialized");
  
  // 检查是否有预选的问题需要显示
  const selectedQuestion = localStorage.getItem('selectedQuestion');
  if (selectedQuestion && route.path !== '/') {
    console.log('Redirecting to home with selected question');
    router.push('/');
  }
  
  // 监听自定义事件，用于处理需要从示例页面跳转到首页的情况
  window.addEventListener('customNavigation', (event) => {
    if (event.detail && event.detail.path) {
      router.push(event.detail.path);
    }
  });
  
  // 监听直接问题事件，如果当前不在主页则先导航到主页
  window.addEventListener('directQuestion', (event) => {
    if (event.detail && event.detail.question && route.path !== '/') {
      console.log('App received direct question, navigating to home');
      router.push('/').then(() => {
        // 导航完成后，重新触发事件以便Home组件接收
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('directQuestion', {
            detail: event.detail
          }));
        }, 300);
      });
    }
  });
});

// 卸载前清理
onBeforeUnmount(() => {
  window.removeEventListener('customNavigation', null);
  window.removeEventListener('directQuestion', null);
});
</script>

<style>
/* Reset CSS */
body, p, h1, h2, h3, ul, ol, li, dl, dt, dd {
  margin: 0; 
  padding: 0;
}

a {
  text-decoration: none;
  color: #000;
  outline: none;
}

ul, li {
  list-style: none;
}

input {
  outline: none;
  border: none;
  background: none;
  box-shadow: none;
}

button {
  outline: none;
  border: none;
  background: none;
  box-shadow: none;
  cursor: pointer;
}

img {
  vertical-align: top;
}

i {
  font-style: normal;
}

/* Common CSS */
body, button, input, select, textarea {
  font: 12px "Microsoft Yahe";
}

body {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* Main CSS */
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: url(@/assets/images/bg.png);
  background-size: 100% 100%;
  overflow: hidden; /* 确保不出现滚动条 */
}

.right-area {
  display: flex;
  justify-content: space-around;
  flex-direction: column;
  flex: 1;
}

.right-area .top {
  display: flex;
  justify-content: space-between;
}

.right-area .top .title {
  margin-top: 40px;
  margin-left: 30px;
  height: 45px;
  line-height: 45px;
  font-size: 28px;
  font-weight: 400;
  color: rgba(27, 37, 89, 1);
  vertical-align: top;
}

.right-area .top .tool-bar {
  padding: 0 10px;
  margin-top: 40px;
  margin-right: 35px;
  width: 300px;
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 30px;
  box-shadow: 14px 17px 20px 4px rgba(112, 144, 176, 0.08);
}

.right-area .top .tool-bar .enter-icon {
  margin-right: 20px;
  display: block;
  width: 8px;
  height: 12px;
  background: url(@/assets/images/enter_icon.png) no-repeat;
}

.right-area .top .tool-bar .profile {
  width: 45px;
  height: 45px;
}
</style>