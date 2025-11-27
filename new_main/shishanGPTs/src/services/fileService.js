import axios from 'axios';

// 设置API基础URL
const BASE_URL = 'http://218.199.69.86:5888';

// 创建axios实例
const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // 允许跨域请求携带凭证
});

// 获取规章制度文件列表
export const getRegulationFiles = async () => {
  try {
    const response = await apiClient.get('/api/files');
    return response.data;
  } catch (error) {
    console.error('获取文件列表失败:', error);
    return {
      code: 500,
      message: '获取文件列表失败',
      data: []
    };
  }
};

// 获取文件下载链接
export const getFileDownloadUrl = async (filename) => {
  try {
    const response = await apiClient.post('/api/files/download', {
      filename: filename
    });
    return response.data;
  } catch (error) {
    console.error('获取下载链接失败:', error);
    return {
      code: 500,
      message: '获取下载链接失败',
      data: null
    };
  }
};

// 执行文件下载
export const downloadFile = async (filename) => {
  try {
    // 第一步：获取下载链接
    const response = await getFileDownloadUrl(filename);
    
    if (response.code !== 200) {
      throw new Error(response.message || '获取下载链接失败');
    }
    
    // 第二步：使用完整下载URL
    const downloadUrl = `${BASE_URL}${response.data.downloadUrl}`;
    
    // 第三步：创建下载链接元素并触发点击
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename; // 使用原始文件名
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    return {
      code: 200,
      message: '下载请求已发送',
      data: { 
        filename: filename,
        downloadUrl: downloadUrl 
      }
    };
  } catch (error) {
    console.error('文件下载失败:', error);
    return {
      code: 500,
      message: `文件下载失败: ${error.message}`,
      data: null
    };
  }
}; 