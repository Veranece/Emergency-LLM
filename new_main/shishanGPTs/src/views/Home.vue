<template>
  <div class="right-area">
    <!-- 顶部区域 -->
    <div class="top">
      <h2 class="title">教育大模型v1.0</h2>
      <div class="tool-bar">
        <search-bar v-model="searchInput" @focus="clearSearchPlaceholder" @blur="resetSearchPlaceholder" />
        <i class="enter-icon" @click="searchRegulations"></i>
        <img class="profile" src="@/assets/images/profile_default.svg" alt="用户头像">
      </div>
    </div>
    
    <div class="version"></div>
    
    <!-- 聊天界面 -->
    <chat-interface :messages="messages" ref="chatInterface" />
    
    <!-- 输入区域 -->
    <input-area 
      v-model="userInput" 
      :sending="sending" 
      @focus="clearUserInputPlaceholder" 
      @blur="resetUserInputPlaceholder" 
      @send="sendMessage" 
      @stop="stopGeneration" 
    />
    
    <!-- 页脚 -->
    <app-footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import SearchBar from '../components/common/SearchBar.vue';
import ChatInterface from '../components/chat/ChatInterface.vue';
import InputArea from '../components/chat/InputArea.vue';
import AppFooter from '../components/layout/Footer.vue';
import { configureMarked, sendMessageToServer, searchRegulations as searchRegs, renderMarkdown } from '../utils/chatUtils';

// 响应式状态
const userInput = ref('');
const searchInput = ref('');
const userInputPlaceholder = ref('请在此输入问题...');
const searchPlaceholder = ref('搜索华农官网信息');
const messages = ref([]);
const sending = ref(false);
const controller = ref(null);
const loadingElement = ref(null);
const characterCount = ref(0);
const chatInterface = ref(null);

// 检查并处理从示例页面选择的问题
const processSelectedQuestion = () => {
  const selectedQuestion = localStorage.getItem('selectedQuestion');
  const timestamp = localStorage.getItem('questionTimestamp');
  
  if (selectedQuestion) {
    console.log('Found selected question:', selectedQuestion);
    userInput.value = selectedQuestion;
    
    // 清除localStorage中的问题和时间戳
    localStorage.removeItem('selectedQuestion');
    localStorage.removeItem('questionTimestamp');
    
    // 自动发送消息
    setTimeout(() => {
      sendMessage();
    }, 300);
  }
};

// 初始化
onMounted(() => {
  console.log("Home component mounted");
  processSelectedQuestion();
  
  // 监听storage事件，以便在同一页面也能响应变化
  window.addEventListener('storage', (event) => {
    if (event.key === 'questionTimestamp') {
      processSelectedQuestion();
    }
  });
  
  // 监听直接问题事件
  window.addEventListener('directQuestion', (event) => {
    console.log('Direct question event received:', event.detail);
    if (event.detail && event.detail.question) {
      // 将问题设置到输入框
      userInput.value = event.detail.question;
      // 直接发送消息
      setTimeout(() => {
        sendMessage();
      }, 100);
    }
  });
});

// 清理工作
onBeforeUnmount(() => {
  // 如果有未完成的请求，中止它
  if (controller.value) {
    controller.value.abort();
    controller.value = null;
  }
  
  // 移除监听器
  window.removeEventListener('storage', processSelectedQuestion);
  window.removeEventListener('directQuestion', null);
});

// 输入框相关方法
const clearUserInputPlaceholder = () => {
  userInputPlaceholder.value = '';
};

const resetUserInputPlaceholder = () => {
  userInputPlaceholder.value = '请在此输入问题...';
};

const clearSearchPlaceholder = () => {
  searchPlaceholder.value = '';
};

const resetSearchPlaceholder = () => {
  searchPlaceholder.value = '搜索华农官网信息';
};

// 搜索功能
const searchRegulations = () => {
  console.log('Searching with input:', searchInput.value);
  
  if (!searchInput.value.trim()) {
    alert("请输入搜索关键词");
    return;
  }
  
  searchRegs(searchInput.value)
    .then(data => {
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
      } else {
        alert("未找到结果");
      }
    })
    .catch(error => {
      console.error('Search failed:', error);
      alert("搜索失败，请稍后重试");
    });
  
  searchInput.value = '';
};

// 发送消息
const sendMessage = () => {
  console.log("sendMessage called, current userInput:", userInput.value);
  
  const userMsg = userInput.value.trim();
  
  if (userMsg === '') {
    alert("输入不能为空");
    return;
  }
  
  if (sending.value) {
    alert("发送过快");
    return;
  }
  
  // 禁止用户发送内容
  sending.value = true;
  
  // 显示用户消息
  messages.value.push({
    type: 'user',
    content: userMsg
  });
  
  // 清空输入框
  userInput.value = '';
  
  // 添加等待消息
  appendRobotLoading();
  
  // 发送请求
  getModelResponse(userMsg);
};

// 添加机器人"思考中"消息
const appendRobotLoading = () => {
  const loadingMsg = {
    type: 'robot',
    content: '思考中...',
    loading: true,
    rendered: false
  };
  messages.value.push(loadingMsg);
  loadingElement.value = loadingMsg;
};

// 获取模型响应
const getModelResponse = (userMsg) => {
  console.log('Getting model response for:', userMsg);
  
  // 创建AbortController实例
  controller.value = new AbortController();
  
  // 开始流式响应
  characterCount.value = 0;
  let hasReceivedFirstChunk = false;
  
  sendMessageToServer(
    userMsg,
    // 收到数据块回调
    (chunk, fullText) => {
      if (loadingElement.value) {
        // 只有在收到第一个实际内容时才更改加载状态
        if (!hasReceivedFirstChunk) {
          console.log('First chunk received, updating loading status');
          hasReceivedFirstChunk = true;
        }
        
        // 确保不覆盖已经添加的停止生成提示
        if (!loadingElement.value.content.includes("stop-generation-notice")) {
          // 内容不为空时才取消loading动画，否则保持动画
          if (fullText.trim() !== '') {
            loadingElement.value.loading = false;
          }
          loadingElement.value.rendered = true;
          loadingElement.value.content = renderMarkdown(fullText);
          
          characterCount.value += chunk.length;
          if (characterCount.value >= 20) {
            chatInterface.value?.scrollToBottom();
            characterCount.value = 0;
          }
        }
      }
    },
    // 完成回调
    () => {
      sending.value = false;
      controller.value = null;
      
      // 确保加载动画被关闭
      if (loadingElement.value && loadingElement.value.loading) {
        loadingElement.value.loading = false;
      }
      
      chatInterface.value?.scrollToBottom();
    },
    // 错误回调
    (error) => {
      console.error("请求失败:", error);
      
      if (error.name === 'AbortError') {
        console.log('用户停止了请求');
      } else {
        if (loadingElement.value) {
          loadingElement.value.loading = false;
          loadingElement.value.content = "请求失败，请稍后再试";
        }
      }
      
      sending.value = false;
    },
    controller.value
  );
};

// 停止生成
const stopGeneration = () => {
  console.log('Stopping generation');
  
  // 如果存在controller，中止请求
  if (controller.value) {
    controller.value.abort();
    controller.value = null;
  }
  
  // 如果消息正在加载，添加"已停止生成"提示
  if (loadingElement.value && sending.value) {
    // 先移除加载动画类
    loadingElement.value.loading = false;
    
    // 获取当前内容
    let currentContent = loadingElement.value.content;
    
    // 判断当前内容状态
    if (currentContent === "思考中..." || currentContent === "") {
      // 初始状态，直接替换为静态文本和停止提示
      loadingElement.value.content = "思考中...<div class='stop-generation-notice'>(已停止生成)</div>";
    } else if (!currentContent.includes("stop-generation-notice")) {
      // 已有内容但尚未添加停止提示，添加停止提示
      loadingElement.value.content = currentContent + 
        "<div class='stop-generation-notice'>(已停止生成)</div>";
    }
    
    // 确保类名包含markdown-content，以便正确应用样式
    loadingElement.value.rendered = true;
    
    // 添加滚动到底部，确保用户能看到"已停止生成"的提示
    chatInterface.value?.scrollToBottom();
  }
  
  // 恢复发送状态
  sending.value = false;
};
</script>

<style scoped>
/* 样式保持不变，与App.vue中相同 */
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