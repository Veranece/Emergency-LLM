<template>
  <div class="examples-container">
    <h2 class="page-title">用户问答示例</h2>
    <p class="page-desc">以下是一些您可以向教育大模型提问的示例问题</p>
    
    <div class="examples-grid">
      <!-- 学术研究相关问题 -->
      <a-card 
        class="example-card academic" 
        :bodyStyle="{ padding: 0 }"
        @click="selectExample(examples[0])"
      >
        <template #title>
          <div class="card-header">
            <experiment-outlined />
            <span>学术研究</span>
          </div>
        </template>
        <div class="card-content">
          <p>{{ examples[0].question }}</p>
        </div>
      </a-card>
      
      <!-- 学校规章相关问题 -->
      <a-card 
        class="example-card regulations" 
        :bodyStyle="{ padding: 0 }"
        @click="selectExample(examples[1])"
      >
        <template #title>
          <div class="card-header">
            <book-outlined />
            <span>规章制度</span>
          </div>
        </template>
        <div class="card-content">
          <p>{{ examples[1].question }}</p>
        </div>
      </a-card>
      
      <!-- 学生事务相关问题 -->
      <a-card 
        class="example-card student" 
        :bodyStyle="{ padding: 0 }"
        @click="selectExample(examples[2])"
      >
        <template #title>
          <div class="card-header">
            <user-outlined />
            <span>学生事务</span>
          </div>
        </template>
        <div class="card-content">
          <p>{{ examples[2].question }}</p>
        </div>
      </a-card>
      
      <!-- 教学资源相关问题 -->
      <a-card 
        class="example-card teaching" 
        :bodyStyle="{ padding: 0 }"
        @click="selectExample(examples[3])"
      >
        <template #title>
          <div class="card-header">
            <read-outlined />
            <span>教学资源</span>
          </div>
        </template>
        <div class="card-content">
          <p>{{ examples[3].question }}</p>
        </div>
      </a-card>
      
      <!-- 校园生活相关问题 -->
      <a-card 
        class="example-card campus" 
        :bodyStyle="{ padding: 0 }"
        @click="selectExample(examples[4])"
      >
        <template #title>
          <div class="card-header">
            <home-outlined />
            <span>校园生活</span>
          </div>
        </template>
        <div class="card-content">
          <p>{{ examples[4].question }}</p>
        </div>
      </a-card>
      
      <!-- 职业规划相关问题 -->
      <a-card 
        class="example-card career" 
        :bodyStyle="{ padding: 0 }"
        @click="selectExample(examples[5])"
      >
        <template #title>
          <div class="card-header">
            <solution-outlined />
            <span>职业规划</span>
          </div>
        </template>
        <div class="card-content">
          <p>{{ examples[5].question }}</p>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  BookOutlined, 
  UserOutlined, 
  ReadOutlined, 
  HomeOutlined,
  SolutionOutlined,
  ExperimentOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { configureMarked, sendMessageToServer, renderMarkdown } from '../utils/chatUtils';

const router = useRouter();

// 全局状态，用于在组件间共享数据
const globalState = ref({
  messages: [],
  sending: false,
  controller: null,
  loadingElement: null,
  characterCount: 0
});

// 示例问题列表
const examples = ref([
  {
    category: 'academic',
    question: '华农有哪些重点学科和研究方向？'
  },
  {
    category: 'regulations',
    question: '本科生申请出国交流项目需要满足哪些条件？'
  },
  {
    category: 'student',
    question: '华农奖学金评定标准是什么？'
  },
  {
    category: 'teaching',
    question: '如何申请华农的在线课程资源？'
  },
  {
    category: 'campus',
    question: '华农校园内有哪些餐厅和特色美食？'
  },
  {
    category: 'career',
    question: '华农毕业生就业率如何？主要就业方向有哪些？'
  }
]);

// 避免重复发送标记
let isProcessing = false;

// 选择示例问题并发送
const selectExample = async (example) => {
  // 防止重复点击
  if (isProcessing) return;
  isProcessing = true;

  try {
    // 显示加载提示
    message.loading({ content: '准备发送问题...', key: 'sendQuestion', duration: 0 });
    
    // 存储问题到localStorage以便页面切换时能够保留
    localStorage.setItem('selectedQuestion', example.question);
    localStorage.setItem('questionTimestamp', Date.now().toString());
    
    // 如果不在主页，先导航到主页
    if (router.currentRoute.value.path !== '/') {
      message.loading({ content: '正在切换到问答页面...', key: 'sendQuestion', duration: 0 });
      await router.push('/');
      
      // 等待路由跳转完成
      await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    // 发送一个自定义事件，通知主页直接开始提问
    window.dispatchEvent(new CustomEvent('directQuestion', {
      detail: { 
        question: example.question,
        timestamp: Date.now()
      }
    }));
    
    // 更新提示
    message.success({ content: '问题已发送！', key: 'sendQuestion', duration: 2 });
    
  } catch (error) {
    console.error('Error sending question:', error);
    message.error({ content: '发送问题失败，请重试', key: 'sendQuestion' });
  } finally {
    isProcessing = false;
  }
};

// 在组件挂载时配置marked
onMounted(() => {
  // 确保工具库初始化
  configureMarked();
});
</script>

<style scoped>
.examples-container {
  padding: 30px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 28px;
  font-weight: 400;
  color: rgba(27, 37, 89, 1);
  margin-bottom: 15px;
}

.page-desc {
  font-size: 16px;
  color: rgba(113, 128, 150, 1);
  margin-bottom: 30px;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  flex-grow: 1;
  margin-bottom: 20px;
}

.example-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 180px;
}

.example-card:hover {
  transform: translateY(-5px);
  box-shadow: 0px 12px 25px rgba(112, 144, 176, 0.15);
}

.example-card :deep(.ant-card-head) {
  padding: 0;
  border-bottom: none;
  min-height: auto;
}

.card-header {
  padding: 16px;
  color: #fff;
  display: flex;
  align-items: center;
}

.card-header span {
  margin-left: 10px;
  font-size: 18px;
  font-weight: 500;
}

.card-header .anticon {
  font-size: 20px;
}

.card-content {
  padding: 16px;
  height: calc(100% - 56px);
  display: flex;
  align-items: center;
}

.card-content p {
  font-size: 16px;
  color: rgba(27, 37, 89, 0.8);
  line-height: 1.5;
  margin-bottom: 0;
}

/* 卡片标题栏的不同颜色 */
.academic :deep(.ant-card-head) {
  background: linear-gradient(to right, #017230, #07a649);
}

.regulations :deep(.ant-card-head) {
  background: linear-gradient(to right, #2a52be, #4169e1);
}

.student :deep(.ant-card-head) {
  background: linear-gradient(to right, #e6873c, #f2994a);
}

.teaching :deep(.ant-card-head) {
  background: linear-gradient(to right, #8e44ad, #9b59b6);
}

.campus :deep(.ant-card-head) {
  background: linear-gradient(to right, #1abc9c, #2ecc71);
}

.career :deep(.ant-card-head) {
  background: linear-gradient(to right, #d35400, #e67e22);
}

/* 响应式布局调整 */
@media (max-width: 1400px) {
  .examples-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .examples-grid {
    grid-template-columns: 1fr;
  }
  
  .example-card {
    height: 150px;
  }
}

@media (min-width: 1401px) {
  .examples-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1800px) {
  .examples-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .example-card {
    height: 200px;
  }
}
</style> 