// 配置后端API地址
// 自动检测：如果通过外网访问则使用外网IP，否则使用localhost
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5888'
    : `http://${window.location.hostname}:5888`;

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
        <div class="flex justify-end message-enter">
            <div class="max-w-xl lg:max-w-2xl">
                <div class="user-message p-4 text-white rounded-2xl shadow-lg">
                    <p class="leading-relaxed">${escapeHTML(messageText)}</p>
                </div>
                <p class="text-xs text-gray-500 text-right mt-2 flex items-center justify-end">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    李指挥 · ${new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                </p>
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
        <div class="flex justify-start message-enter" id="${aiMessageId}">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-emergency-blue-600 via-blue-600 to-blue-500 text-white flex items-center justify-center font-bold text-sm flex-shrink-0 mr-4 shadow-lg shadow-blue-500/30 ring-2 ring-blue-500/20 relative">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zM7.5 11.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5S9 9.17 9 10s-.67 1.5-1.5 1.5zM12 17c-2.33 0-4.32-1.45-5.12-3.5h1.67c.69 1.19 1.97 2 3.45 2s2.75-.81 3.45-2h1.67c-.8 2.05-2.79 3.5-5.12 3.5zm4.5-5.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                </svg>
                <span class="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white animate-pulse"></span>
            </div>
            <div class="max-w-xl lg:max-w-2xl flex-1">
                <div class="ai-message p-5 rounded-2xl shadow-xl">
                    <div class="text-gray-800 whitespace-pre-wrap leading-relaxed" id="${aiMessageId}-content">
                        <span class="inline-flex items-center text-gray-500 animate-thinking">
                            <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            AI正在思考中...
                        </span>
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-2 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    智能体 · ${new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                </p>
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
        contentDiv.innerHTML = `
            <div class="flex items-start space-x-3 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                    <p class="text-red-800 font-semibold">抱歉，获取回复时出现错误</p>
                    <p class="text-red-600 text-sm mt-1">${escapeHTML(error.message)}</p>
                </div>
            </div>
        `;
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

// 格式化AI响应内容（支持完整Markdown）
function formatAIResponse(text) {
    try {
        // 首先检查marked是否可用
        if (typeof marked !== 'undefined') {
            console.log('使用Marked.js渲染Markdown');
            
            // 配置marked选项以支持表格和其他功能
            marked.setOptions({
                breaks: true,        // 支持换行
                gfm: true,          // GitHub风格Markdown
                tables: true,       // 支持表格
                sanitize: false,    // 不清理HTML（我们已经有XSS防护）
                smartLists: true,   // 智能列表
                smartypants: false  // 不转换引号
            });
            
            const rendered = marked.parse(text);
            console.log('Markdown渲染完成，检测到的特征:', {
                '包含表格': text.includes('|'),
                '包含代码块': text.includes('```'),
                '包含列表': /^[\-\*\+\d+\.]\s/m.test(text),
                '包含标题': /^#+\s/m.test(text)
            });
            
            return rendered;
        }

        // 如果marked不可用，使用增强的正则表达式处理
        console.log('Marked.js不可用，使用增强基础渲染');
        return enhancedMarkdownRender(text);

    } catch (error) {
        console.error('渲染错误:', error);
        // 降级到纯文本显示
        return `<div class="text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
            <p class="font-semibold">Markdown渲染出错</p>
            <p class="text-sm mt-1">错误: ${escapeHTML(error.message)}</p>
            <details class="mt-2">
                <summary class="cursor-pointer text-sm">查看原始内容</summary>
                <pre class="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">${escapeHTML(text)}</pre>
            </details>
        </div>`;
    }
}

// 增强的基础Markdown渲染器
function enhancedMarkdownRender(text) {
    let html = escapeHTML(text);
    
    // 处理代码块（必须在其他处理之前）
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
        const language = lang ? ` data-language="${lang}"` : '';
        return `<pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto my-4"><code${language}>${code.trim()}</code></pre>`;
    });
    
    // 处理表格
    html = html.replace(/^\|(.+)\|\s*$/gm, function(match, content) {
        const cells = content.split('|').map(cell => cell.trim());
        return `<tr>${cells.map(cell => `<td class="border border-gray-300 px-3 py-2">${cell}</td>`).join('')}</tr>`;
    });
    
    // 包装表格
    html = html.replace(/(<tr>.*<\/tr>\s*)+/g, function(match) {
        return `<table class="w-full border-collapse border border-gray-300 my-4">${match}</table>`;
    });
    
    // 处理标题
    html = html.replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold mt-6 mb-3 text-gray-800">$1</h3>');
    html = html.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-8 mb-4 text-gray-800">$1</h2>');
    html = html.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-10 mb-6 text-gray-900">$1</h1>');
    
    // 处理强调
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-gray-900">$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em class="italic text-gray-700">$1</em>');
    
    // 处理行内代码
    html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-100 text-red-600 px-2 py-1 rounded text-sm font-mono">$1</code>');
    
    // 处理列表
    html = html.replace(/^[\-\*\+] (.*$)/gm, '<li class="ml-6 mb-1">• $1</li>');
    html = html.replace(/^\d+\. (.*$)/gm, '<li class="ml-6 mb-1 list-decimal">$1</li>');
    
    // 处理引用
    html = html.replace(/^> (.*$)/gm, '<blockquote class="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4">$1</blockquote>');
    
    // 处理段落和换行
    html = html.replace(/\n\n/g, '</p><p class="mb-4 leading-relaxed">');
    html = html.replace(/\n/g, '<br>');
    
    return `<div class="prose max-w-none"><p class="mb-4 leading-relaxed">${html}</p></div>`;
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
        messageContainer.innerHTML = `
            <div class="flex justify-center">
                <div class="max-w-md">
                    <div class="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-gray-200/50 text-center">
                        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-emergency-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30 ring-2 ring-blue-500/20">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-9 w-9 text-white" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zM7.5 11.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5S9 9.17 9 10s-.67 1.5-1.5 1.5zM12 17c-2.33 0-4.32-1.45-5.12-3.5h1.67c.69 1.19 1.97 2 3.45 2s2.75-.81 3.45-2h1.67c-.8 2.05-2.79 3.5-5.12 3.5zm4.5-5.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-900 mb-2">欢迎使用应急智能体</h3>
                        <p class="text-gray-600 text-sm leading-relaxed">
                            我是您的AI应急助手，可以帮助您快速处理各类应急事件。<br>
                            请输入您的问题或选择下方的快捷指令开始。
                        </p>
                        <div class="mt-4 flex items-center justify-center space-x-2 text-xs text-gray-500">
                            <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            <span>系统运行正常</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        console.log('已开始新会话');
    }
});

// 移动端菜单切换功能
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const sidebar = document.querySelector('aside');

if (mobileMenuBtn && sidebar) {
    // 创建遮罩层
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 bg-black bg-opacity-50 z-40 hidden sm:hidden backdrop-blur-sm transition-opacity duration-300';
    overlay.id = 'mobile-menu-overlay';
    document.body.appendChild(overlay);
    
    // 为侧边栏添加移动端样式
    sidebar.classList.add('fixed', 'inset-y-0', 'left-0', 'z-50', 'transform', '-translate-x-full', 'transition-transform', 'duration-300', 'ease-in-out', 'sm:translate-x-0', 'sm:static');
    
    // 切换菜单
    function toggleMenu() {
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
        document.body.classList.toggle('overflow-hidden');
    }
    
    mobileMenuBtn.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);
}

