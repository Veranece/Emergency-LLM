<template>
  <div :class="messageClass">
    <template v-if="message.type === 'user'">
      <div class="text-container">
        <div class="text-content">{{ message.content }}</div>
      </div>
      <div class="user-profile">
        <i class="icon-user-profile"></i>
      </div>
    </template>
    <template v-else>
      <div class="robot-profile">
        <i class="icon-robot-profile"></i>
      </div>
      <div class="text-container">
        <div :class="contentClass" v-html="message.content"></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// 定义props
const props = defineProps({
  message: {
    type: Object,
    required: true
  }
});

// 计算属性
const messageClass = computed(() => {
  return {
    'chat-item': true,
    'user-chat-item': props.message.type === 'user',
    'robot-chat-item': props.message.type !== 'user'
  };
});

const contentClass = computed(() => {
  return {
    'text-content': true,
    'markdown-content': props.message.rendered,
    'loading-animation': props.message.loading
  };
});
</script>

<style scoped>
/* 用户提问样式 */
.user-chat-item {
  display: flex;
  justify-content: right;
  margin-bottom: 15px;
}

.user-chat-item .user-profile {
  flex-shrink: 0;
  width: 33px;
  height: 33px;
}

.user-chat-item .user-profile .icon-user-profile {
  display: block;
  width: 100%;
  height: 100%;
  background: url("@/assets/images/profile_user_default.png") no-repeat;
  background-size: 100% 100%;
  border-radius: 50%;
}

.user-chat-item .text-container {
  margin-right: 20px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  background-color: rgb(244 244 244);
  border-radius: 4px;
  box-shadow: rgba(200, 200, 200, 0.1) 0 21px 8px -10px;
}

.user-chat-item .text-container .text-content {
  position: relative;
  padding: 10px 15px;
  box-sizing: border-box;
  color: rgb(31, 41, 55);
  font-size: 16px;
  line-height: 25px;
  letter-spacing: .5px;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

/* 大模型回答样式 */
.robot-chat-item {
  display: flex;
  justify-content: left;
  margin-bottom: 15px;
}

.robot-chat-item .robot-profile {
  flex-shrink: 0;
  width: 33px;
  height: 33px;
}

.robot-chat-item .robot-profile .icon-robot-profile {
  display: block;
  width: 100%;
  height: 100%;
  background: url("@/assets/images/profile_robot_default.png") no-repeat;
  background-size: 100% 100%;
  border-radius: 50%;
}

.robot-chat-item .text-container {
  margin-right: 35px;
  box-sizing: border-box;
  margin-left: 20px;
  display: flex;
  justify-content: center;
  background-color: rgb(235, 255, 243);
  border: 0.8px solid rgb(1, 114, 48);
  border-radius: 4px;
  box-shadow: rgba(149, 240, 187, 0.1) 0 21px 8px -10px;
}

.robot-chat-item .text-container .text-content {
  position: relative;
  padding: 10px 15px;
  box-sizing: border-box;
  color: rgb(31, 41, 55);
  font-size: 16px;
  line-height: 25px;
  letter-spacing: .5px;
  white-space: normal;
  overflow-wrap: break-word;
}

/* 统一样式 */
.chat-item {
  margin-top: 15px;
  max-width: 90%;
}

/* 加载动画 */
.loading-animation::after {
  content: '...';
  animation: loadingDots 1s steps(3, end) infinite;
}

@keyframes loadingDots {
  0%, 20% {
    content: ' ';
  }
  40% {
    content: '.';
  }
  60% {
    content: '..';
  }
  100% {
    content: '...';
  }
}

/* 停止生成提示样式 */
.stop-generation-notice {
  margin-top: 8px;
  padding: 4px 10px;
  color: #a94442;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  font-size: 13px;
  display: inline-block;
  font-weight: bold;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style> 