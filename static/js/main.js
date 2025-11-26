// 配置后端API地址
// 自动检测：如果通过外网访问则使用外网IP，否则使用localhost
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5001'
    : `http://${window.location.hostname}:5001`;

// 存储对话历史
let chatHistory = [];

// 当前是否正在等待AI响应
let isWaitingForResponse = false;

// JS: 使文本框根据内容自动调整高度
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
}

// JS: 处理发送消息并调用后端API
const sendButton = document.getElementById('send-button');
const messageInput = document.getElementById('message-input');
const messageContainer = document.getElementById('message-container');

// 页面加载时滚动到底部
messageContainer.scrollTop = messageContainer.scrollHeight;

async function sendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText === '' || isWaitingForResponse) return;

    // 设置等待状态
    isWaitingForResponse = true;
    sendButton.disabled = true;
    sendButton.classList.add('opacity-50', 'cursor-not-allowed');

    // 1. 创建用户消息并添加到历史记录
    const userMessage = {
        role: 'user',
        content: messageText
    };
    chatHistory.push(userMessage);

    // 2. 显示用户消息
    const userMessageHTML = `
        <div class="flex justify-end">
            <div class="max-w-xl lg:max-w-2xl">
                <div class="p-3 bg-emergency-blue-600 text-white rounded-xl shadow-md">
                    <p>${escapeHTML(messageText)}</p>
                </div>
                <p class="text-xs text-gray-500 text-right mt-1">李指挥 - ${new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</p>
            </div>
        </div>
    `;
    messageContainer.innerHTML += userMessageHTML;

    // 3. 清空输入框并重置高度
    messageInput.value = '';
    autoResize(messageInput);

    // 4. 滚动到底部
    messageContainer.scrollTop = messageContainer.scrollHeight;

    // 5. 创建AI响应容器
    const aiMessageId = 'ai-message-' + Date.now();
    const aiResponseHTML = `
        <div class="flex justify-start" id="${aiMessageId}">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emergency-blue-600 to-blue-500 text-white flex items-center justify-center font-bold text-sm flex-shrink-0 mr-3 shadow-lg">
                AI
            </div>
            <div class="max-w-xl lg:max-w-2xl">
                <div class="p-4 bg-white rounded-xl shadow-md">
                    <div class="text-gray-800 whitespace-pre-wrap" id="${aiMessageId}-content">
                        <span class="inline-block animate-pulse">正在思考...</span>
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-1">智能体 - ${new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</p>
            </div>
        </div>
    `;
    messageContainer.innerHTML += aiResponseHTML;
    messageContainer.scrollTop = messageContainer.scrollHeight;

    // 6. 调用后端API获取AI回复
    try {
        await getAIResponse(messageText, aiMessageId);
    } catch (error) {
        console.error('获取AI回复失败:', error);
        const contentDiv = document.getElementById(`${aiMessageId}-content`);
        contentDiv.innerHTML = `<p class="text-red-600">抱歉，获取回复时出现错误: ${escapeHTML(error.message)}</p>`;
    } finally {
        // 恢复发送按钮状态
        isWaitingForResponse = false;
        sendButton.disabled = false;
        sendButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// 调用后端API并处理流式响应
async function getAIResponse(message, aiMessageId) {
    const contentDiv = document.getElementById(`${aiMessageId}-content`);
    let aiResponseText = '';

    try {
        // 创建一个AbortController来支持超时
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 120秒超时

        const response = await fetch(`${API_BASE_URL}/getMessageWeb`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userMessage: message,
                history: chatHistory
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('服务器返回错误:', errorText);
            throw new Error(`HTTP错误! 状态: ${response.status}, 详情: ${errorText}`);
        }

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        contentDiv.innerHTML = '';

        // 设置读取超时
        let lastChunkTime = Date.now();
        const checkTimeout = setInterval(() => {
            if (Date.now() - lastChunkTime > 60000) { // 60秒没有新数据
                reader.cancel();
                clearInterval(checkTimeout);
                throw new Error('响应超时：长时间未收到数据');
            }
        }, 5000);

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                clearInterval(checkTimeout);
                break;
            }

            lastChunkTime = Date.now();

            // 解码数据块
            const chunk = decoder.decode(value, { stream: true });
            aiResponseText += chunk;

            // 更新显示内容（支持换行）
            contentDiv.innerHTML = formatAIResponse(aiResponseText);

            // 自动滚动到底部
            messageContainer.scrollTop = messageContainer.scrollHeight;
        }

        // 将AI回复添加到历史记录
        if (aiResponseText.trim()) {
            chatHistory.push({
                role: 'assistant',
                content: aiResponseText
            });
        }

    } catch (error) {
        console.error('流式响应处理错误:', error);
        
        // 详细的错误信息
        if (error.name === 'AbortError') {
            throw new Error('请求超时，服务器响应时间过长');
        } else if (error.message.includes('Failed to fetch')) {
            throw new Error('无法连接到服务器，请确保后端服务正在运行');
        } else {
            throw error;
        }
    }
}

// 格式化AI响应内容（支持Markdown格式）
function formatAIResponse(text) {
    // 转义HTML特殊字符
    let formatted = escapeHTML(text);
    
    // 处理 Markdown 标题（需要在换行处理之前，从长到短匹配避免混淆）
    formatted = formatted.replace(/^#### (.*?)$/gm, '<h4 class="text-base font-bold mt-2 mb-1.5 text-emergency-blue-600">$1</h4>');
    formatted = formatted.replace(/^### (.*?)$/gm, '<h3 class="text-lg font-bold mt-3 mb-2 text-emergency-blue-700">$1</h3>');
    formatted = formatted.replace(/^## (.*?)$/gm, '<h2 class="text-xl font-bold mt-4 mb-2 text-emergency-blue-700">$1</h2>');
    formatted = formatted.replace(/^# (.*?)$/gm, '<h1 class="text-2xl font-bold mt-4 mb-3 text-emergency-blue-800">$1</h1>');
    
    // 处理无序列表（支持 •、-、* 符号）
    formatted = formatted.replace(/^• (.*?)$/gm, '<li class="ml-4 mb-1 list-none">• $1</li>');
    formatted = formatted.replace(/^[•\-\*] (.*?)$/gm, '<li class="ml-4 mb-1 list-none">• $1</li>');
    
    // 处理有序列表（如 1. 2. 3.）
    formatted = formatted.replace(/^(\d+)\. (.*?)$/gm, '<li class="ml-4 mb-1 list-none">$1. $2</li>');
    
    // 处理加粗标记 **text** (先处理加粗，避免与斜体冲突)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');
    
    // 处理斜体 *text* (使用更简单的匹配方式)
    formatted = formatted.replace(/\*([^\*<>]+?)\*/g, '<em class="italic">$1</em>');
    
    // 处理行内代码 `code`
    formatted = formatted.replace(/`([^`]+?)`/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-red-600">$1</code>');
    
    // 处理换行（保持段落分隔）
    formatted = formatted.replace(/\n\n/g, '<br><br>');  // 双换行变成段落分隔
    formatted = formatted.replace(/\n/g, '<br>');        // 单换行变成换行
    
    return formatted;
}

// 绑定发送按钮事件
sendButton.addEventListener('click', sendMessage);

// 绑定Enter键发送 (Shift+Enter 换行)
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 辅助函数：防止XSS
function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[m];
    });
}

// 新会话按钮功能
document.querySelector('aside button').addEventListener('click', function() {
    if (confirm('确定要开始新的会话吗？当前对话历史将被清空。')) {
        chatHistory = [];
        messageContainer.innerHTML = '';
        console.log('已开始新会话');
    }
});

