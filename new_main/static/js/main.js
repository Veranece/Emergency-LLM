// static/js/main.js

// 配置 marked.js（检测版本，使用相应的 API）
if (typeof marked.parse === 'undefined') {
  // 旧版 API
  marked.setOptions({
    pedantic: false,
    gfm: true,
    breaks: true,
    sanitize: false,
    smartypants: false,
    xhtml: false
  });
} else {
  // 新版 API
  marked.use({
    renderer: new marked.Renderer(),
    pedantic: false,
    gfm: true,
    breaks: true
  });
}

class userMessageData {
  constructor(userMessage) {
    this.userMessage = userMessage;
  }
}

const userInput = document.querySelector('.text-input');
const messagesContainer = document.querySelector('.chat-box');
const stopButton = document.querySelector('.stop-button');
// const url = "http://127.0.0.1:5001/getMessage"
const url = "http://218.199.69.58:5888/getMessage"
let enSend = true;
let loadingElement = null; // 存储加载动画元素
let controller = null; // 存储AbortController实例
 
// 添加发送按钮事件监听
sendButton.addEventListener('click', () => {
    sendButton.blur();
    const userMessage = userInput.value;
    console.log(userMessage);
    if (userMessage.trim() === '' ) {
      alert("输入不能为空");
      return;
    }
    if (!enSend) {
      alert("发送过快");
      return;
    }
    // 禁止用户发送内容
    enSend = false;
    
    // 显示停止按钮
    stopButton.style.display = 'flex';
    sendButton.style.display = 'none';

    // 显示用户消息
    appendUserMessage(userMessage);

    // 清空输入框
    userInput.value = '';

    // 发送ajax请求
    getModelResponse(new userMessageData(userMessage));
});

// 添加停止按钮事件监听
stopButton.addEventListener('click', () => {
    stopButton.blur(); 
    
    // 如果存在controller，中止请求
    if (controller) {
        controller.abort();
        controller = null;
    }
    
    // 如果消息正在加载，添加"已停止生成"提示
    if (loadingElement && !enSend) {
        const textContentEl = loadingElement.querySelector(".text-container .text-content");
        if (textContentEl) {
            // 先移除加载动画类
            textContentEl.classList.remove('loading-animation');
            
            // 获取当前内容
            let currentContent = textContentEl.innerHTML;
            
            // 判断当前内容状态：
            // 1. 如果是初始的"思考中..."（还没有接收到任何实际内容）
            // 2. 如果已经有了生成的实际内容
            // 3. 如果已经添加了停止生成提示，避免重复添加
            
            if (currentContent === "思考中..." || currentContent === "") {
                // 初始状态，直接替换为静态文本和停止提示
                textContentEl.innerHTML = "思考中...<div class='stop-generation-notice'>(已停止生成)</div>";
            } else if (!currentContent.includes("stop-generation-notice")) {
                // 已有内容但尚未添加停止提示，添加停止提示
                textContentEl.innerHTML = currentContent + 
                    "<div class='stop-generation-notice'>(已停止生成)</div>";
            }
            
            // 确保类名包含markdown-content，以便正确应用样式
            if (!textContentEl.className.includes('markdown-content')) {
                textContentEl.className = 'text-content markdown-content';
            }
            
            // 添加滚动到底部，确保用户能看到"已停止生成"的提示
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 100);
        }
    }
    
    // 恢复发送状态
    enSend = true;
    
    // 隐藏停止按钮，显示发送按钮
    stopButton.style.display = 'none';
    sendButton.style.display = 'flex';
    
    // 聚焦到输入框
    setTimeout(() => {
        userInput.focus();
    }, 300);
});

function appendUserMessage(message) {
    const userMessageElement = document.createElement('div');
    userMessageElement.className = 'user-chat-item chat-item';
    userMessageElement.innerHTML = `
        <div class="text-container">
            <div class="text-content">${message}</div>
        </div>
        <div class="user-profile">
            <i class="icon-user-profile"></i>
        </div>
    `;
    messagesContainer.appendChild(userMessageElement);
    // 用户提问后立即滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 发送ajax请求
function getModelResponse(userMessageData) {
  // 添加加载动画
  loadingElement = appendRobotLoading();
  
  // 创建AbortController实例
  controller = new AbortController();
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8'
    },
    body: JSON.stringify(userMessageData),
    signal: controller.signal // 添加中止信号
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // 获取响应的可读流
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = ""; // 存储已收到的全部文本
    let characterCount = 0; // 字符计数器，用于跟踪累积的字符数
    
    // 递归处理流
    function readStream() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          // 流结束，允许用户再次发送消息
          enSend = true;
          // 恢复按钮状态
          stopButton.style.display = 'none';
          sendButton.style.display = 'flex';
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
          controller = null;
          return;
        }
        
        // 解码收到的数据片段
        const chunk = decoder.decode(value, { stream: true });
        fullText += chunk;
        characterCount += chunk.length;
        
        // 更新UI显示，使用 marked 渲染 Markdown
        if (loadingElement) {
          const textContentEl = loadingElement.querySelector(".text-container .text-content");
          
          // 确保textContentEl存在且不包含停止生成提示，避免覆盖已停止的内容
          if (textContentEl && !textContentEl.innerHTML.includes("stop-generation-notice")) {
            textContentEl.className = 'text-content markdown-content';
            textContentEl.innerHTML = typeof marked.parse !== 'undefined'
              ? marked.parse(fullText)
              : marked(fullText);
            
            // 字符计数达到约20个时滚动到底部，然后重置计数器
            if (characterCount >= 20 || done) {
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
              characterCount = 0; // 重置计数器
            }
          }
        }
        
        // 继续读取下一个数据块
        return readStream();
      });
    }
    
    // 移除加载动画的文本并准备接收流式内容
    if (loadingElement) {
      const textContentEl = loadingElement.querySelector(".text-container .text-content");
      // 先延迟一段时间再清除加载动画，确保能看到"思考中..."的状态
      return new Promise(resolve => {
        setTimeout(() => {
          textContentEl.classList.remove('loading-animation');
          textContentEl.innerText = "";
          // 开始读取流
          resolve(readStream());
        }, 800); 
      });
    } else {
      // 如果不存在loadingElement，则直接开始读取流
      return readStream();
    }
  })
  .catch(error => {
    console.error("请求失败:", error);
    
    // 如果是用户中止请求，不显示错误信息
    if (error.name === 'AbortError') {
      console.log('用户停止了请求');
    } else {
      // 显示错误信息
      if (loadingElement) {
        const textContentEl = loadingElement.querySelector(".text-container .text-content");
        textContentEl.classList.remove('loading-animation');
        textContentEl.innerText = "请求失败，请稍后再试";
      }
    }
    // 允许用户再次发送消息
    enSend = true;
    
    // 隐藏停止按钮，显示发送按钮
    stopButton.style.display = 'none';
    sendButton.style.display = 'flex';
  });
}

// 添加等待动画
function appendRobotLoading(){
  // 确保滚动到底部以显示加载动画
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  const robotMessageElement = document.createElement('div');
  robotMessageElement.className = 'robot-chat-item chat-item';
  robotMessageElement.innerHTML = `
        <div class="robot-profile">
            <i class="icon-robot-profile"></i>
        </div>
        <div class="text-container">
            <div class="text-content loading-animation">思考中...</div>
        </div>
    `;
  messagesContainer.appendChild(robotMessageElement);
  // 确保滚动到底部，能看到"思考中..."
  setTimeout(() => {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }, 50);
  return robotMessageElement; // 返回加载动画元素
}

// 修改 appendRobotMessage 为创建新消息元素的函数（渲染 Markdown 格式）
function appendRobotMessage(message) {
  // 如果是新消息（而不是流式更新），则创建新的消息元素
  if (!loadingElement) {
    const robotMessageElement = document.createElement('div');
    robotMessageElement.className = 'robot-chat-item chat-item';
    robotMessageElement.innerHTML = `
      <div class="robot-profile">
        <i class="icon-robot-profile"></i>
      </div>
      <div class="text-container">
        <div class="text-content markdown-content">${
          typeof marked.parse !== 'undefined'
            ? marked.parse(message || "")
            : marked(message || "")
        }</div>
      </div>
    `;
    messagesContainer.appendChild(robotMessageElement);
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return;
  }

 
}

