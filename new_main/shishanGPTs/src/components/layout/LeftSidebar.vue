<template>
  <div class="left-area">
    <div class="logo-container">
      <a href="https://www.hzau.edu.cn/">
        <i class="logo"></i>
      </a>
    </div>
    
    <a-menu
      v-model:selectedKeys="selectedKeys"
      mode="inline"
      theme="light"
      class="side-menu"
    >
      <a-menu-item key="/" @click="navigateTo('/')">
        <template #icon>
          <book-outlined />
        </template>
        <span>教育大模型问答</span>
      </a-menu-item>
      
      <a-menu-item key="/examples" @click="navigateTo('/examples')">
        <template #icon>
          <file-text-outlined />
        </template>
        <span>用户问答示例</span>
      </a-menu-item>
      
      <a-menu-item key="/regulations" @click="navigateTo('/regulations')">
        <template #icon>
          <read-outlined />
        </template>
        <span>规章制度文件</span>
      </a-menu-item>
      
      <a-menu-item key="/other">
        <template #icon>
          <appstore-outlined />
        </template>
        <span>其他内容待补充...</span>
      </a-menu-item>
    </a-menu>
    
    <div class="user-info">
      <img class="profile" src="@/assets/images/profile_default.svg" alt="用户头像">
      <span class="username">系统默认用户</span>
      <a-button type="text" shape="circle" class="logout-btn">
        <template #icon><logout-outlined /></template>
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  BookOutlined, 
  FileTextOutlined, 
  ReadOutlined, 
  AppstoreOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();

// 当前路径
const currentPath = computed(() => route.path);
const selectedKeys = ref(['/']);

// 导航方法
const navigateTo = (path) => {
  router.push(path);
};

// 监视路由变化，更新选中的菜单项
watch(
  () => route.path,
  (newPath) => {
    selectedKeys.value = [newPath];
  }
);

// 组件挂载时初始化
onMounted(() => {
  console.log('LeftSidebar mounted, current path:', currentPath.value);
  selectedKeys.value = [currentPath.value];
});
</script>

<style scoped>
.left-area {
  display: flex;
  flex-direction: column;
  margin: 15px 0;
  width: 310px;
  min-width: 310px;
  flex-shrink: 0;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 6px 16px -8px rgba(0, 0, 0, 0.08), 
              0 9px 28px 0 rgba(0, 0, 0, 0.05), 
              0 12px 48px 16px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  height: calc(100vh - 30px);
  z-index: 10;
}

.logo-container {
  padding: 20px 0;
  text-align: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.logo {
  display: inline-block;
  width: 170px;
  height: 43px;
  background: url(@/assets/images/hzau_logo.png) no-repeat;
  background-size: 100% 100%;
}

.side-menu {
  border-right: none;
  padding: 12px 0;
  flex: 1;
}

:deep(.ant-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 8px 0;
  padding: 0 16px 0 24px !important;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
}

:deep(.ant-menu-item-selected) {
  background-color: #e6f7f0 !important;
  color: #017230 !important;
  font-weight: 600;
  border-right: 3px solid #017230;
}

:deep(.ant-menu-item:hover:not(.ant-menu-item-selected)) {
  color: #3a9660 !important;
}

:deep(.ant-menu-item .anticon) {
  font-size: 18px;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  margin: 10px 0 20px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.username {
  margin-left: 12px;
  flex: 1;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  color: rgba(0, 0, 0, 0.45);
}

.logout-btn:hover {
  color: #017230;
  background-color: rgba(1, 114, 48, 0.1);
}

.profile {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

</style> 