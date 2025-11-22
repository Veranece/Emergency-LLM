<template>
  <div class="chat-box" ref="messagesContainer">
    <div class="robot-chat-item chat-item">
      <div class="robot-profile">
        <i class="icon-robot-profile"></i>
      </div>
      <div class="text-container">
        <div class="text-content">您好！我是华中农业大学研发的教育助手，请问有什么教育、管理、政策相关的疑惑？</div>
      </div>
    </div>
    
    <chat-message 
      v-for="(message, index) in messages" 
      :key="index" 
      :message="message"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';

// 定义props
const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
});

// refs
const messagesContainer = ref(null);

// 方法
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 监听消息变化
watch(() => props.messages, () => {
  scrollToBottom();
}, { deep: true });

// 初始化后滚动到底部
onMounted(() => {
  scrollToBottom();
});

// 暴露方法给父组件
defineExpose({
  scrollToBottom
});
</script>

<style scoped>
.chat-box {
  padding: 0 50px;
  margin: 20px auto 0;
  width: 100%;
  max-width: 80vw;
  height: 100%;
  max-height: 85%;
  overflow-y: scroll;
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: rgba(1, 114, 48, 0.3) transparent; /* Firefox */
}

/* 自定义滚动条样式 - Webkit浏览器 */
.chat-box::-webkit-scrollbar {
  width: 8px;
}

.chat-box::-webkit-scrollbar-track {
  background: transparent;
}

.chat-box::-webkit-scrollbar-thumb {
  background-color: rgba(1, 114, 48, 0.3);
  border-radius: 10px;
}

.chat-box::-webkit-scrollbar-thumb:hover {
  background-color: rgba(1, 114, 48, 0.5);
}

/* 欢迎消息样式 */
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

.chat-item {
  margin-top: 15px;
  max-width: 90%;
}
</style> 