import { marked } from 'marked';

/**
 * 配置Markdown解析器
 */
export function configureMarked() {
  // 配置 marked.js
  if (typeof marked.parse === 'undefined') {
    // 旧版 API
    marked.setOptions({
      highlight: function(code, language) {
        const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
        return hljs.highlight(code, { language: validLanguage }).value;
      },
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
      highlight: function(code, language) {
        const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
        return hljs.highlight(code, { language: validLanguage }).value;
      },
      pedantic: false,
      gfm: true,
      breaks: true
    });
  }
}

/**
 * 将文本转换为base64
 * @param {string} str 需要转换的字符串
 * @returns {string} base64编码的字符串
 */
export function toBase64(str) {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  let binary = '';
  const len = data.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(data[i]);
  }
  return btoa(binary);
}

/**
 * 发送消息到服务器并处理流式响应
 * @param {string} userMessage 用户消息
 * @param {Function} onChunkReceived 接收到数据块时的回调
 * @param {Function} onComplete 完成时的回调
 * @param {Function} onError 错误时的回调
 * @param {AbortController} controller 用于取消请求的AbortController实例
 * @returns {Promise} 请求Promise
 */
export function sendMessageToServer(userMessage, onChunkReceived, onComplete, onError, controller) {
  // const url = "http://127.0.0.1:5001/getMessage";
  const url = "http://shizi.hzau.edu.cn:5888/getMessage";
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8'
    },
    body: JSON.stringify({ userMessage }),
    signal: controller ? controller.signal : null
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = "";
    
    const readStream = () => {
      return reader.read().then(({ done, value }) => {
        if (done) {
          onComplete && onComplete(fullText);
          return fullText;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        fullText += chunk;
        
        onChunkReceived && onChunkReceived(chunk, fullText);
        
        return readStream();
      });
    };
    
    return readStream();
  })
  .catch(error => {
    onError && onError(error);
    throw error;
  });
}

/**
 * 搜索规章制度
 * @param {string} keyWord 搜索关键词
 * @returns {Promise} 搜索结果Promise
 */
export function searchRegulations(keyWord) {
  const searchData = {
    keyWord: keyWord,
    owner: "2027508739",
    token: "tourist",
    urlPrefix: "/aop_component/",
    lang: "i18n_zh_CN"
  };
  
  return fetch("http://shizi.hzau.edu.cn:5888/proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(searchData)
  })
  .then(res => res.json());
}

/**
 * 渲染Markdown
 * @param {string} text Markdown文本
 * @returns {string} 渲染后的HTML
 */
export function renderMarkdown(text) {
  return typeof marked.parse !== 'undefined'
    ? marked.parse(text)
    : marked(text);
} 