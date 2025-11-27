<template>
  <div class="regulations-container">
    <h2 class="page-title">规章制度文件</h2>
    <p class="page-desc">华中农业大学各项规章制度文件，点击可下载查看</p>
    
    <div class="files-section">
      <!-- 文件搜索框 -->
      <div class="search-section">
        <a-input-search
          v-model:value="searchKeyword"
          placeholder="搜索文件名称"
          style="width: 300px"
          @search="onSearch"
          allow-clear
        >
         
        </a-input-search>
      </div>
      
      <!-- 文件列表 -->
      <a-list
        class="file-list"
        :loading="loading"
        item-layout="horizontal"
        :data-source="filteredFiles"
        :grid="{ gutter: 24, xs: 1, sm: 1, md: 1, lg: 1, xl: 1, xxl: 1 }"
      >
        <template #renderItem="{ item }">
          <a-list-item @click="downloadFile(item)" class="file-item">
            <div class="file-item-content">
              <div class="file-icon">
                <a-avatar :style="{ backgroundColor: getColorByType(item.type) }">
                  <template #icon>
                    <file-pdf-outlined v-if="item.format === 'pdf'" />
                    <file-word-outlined v-else-if="item.format === 'doc' || item.format === 'docx'" />
                    <file-excel-outlined v-else-if="item.format === 'xls' || item.format === 'xlsx'" />
                    <file-outlined v-else />
                  </template>
                </a-avatar>
              </div>
              <div class="file-info">
                <div class="file-title">{{ item.name }}</div>
                <div class="file-desc">
                  <span class="file-date">更新日期: {{ item.updateDate }}</span>
                  <span class="file-size">{{ item.size }}</span>
                </div>
              </div>
              <div class="file-actions">
                <a-button type="primary" shape="round" @click.stop="downloadFile(item)">
                  <template #icon><download-outlined /></template>
                  下载
                </a-button>
              </div>
            </div>
          </a-list-item>
        </template>
      </a-list>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <a-pagination
          v-model:current="current"
          :total="totalFiles"
          :pageSize="pageSize"
          show-size-changer
          :pageSizeOptions="['10', '20', '30', '50']"
          @showSizeChange="onShowSizeChange"
          @change="onPageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  SearchOutlined,
  DownloadOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FileOutlined,
  FilePptOutlined,
  FileZipOutlined,
  FileImageOutlined,
  FileTextOutlined,
  FileMarkdownOutlined
} from '@ant-design/icons-vue';
import { getRegulationFiles, getFileDownloadUrl, downloadFile as fileDownload } from '../services/fileService';

// 页面状态
const loading = ref(false);
const searchKeyword = ref('');
const fileType = ref('all');
const current = ref(1);
const pageSize = ref(10);

// 文件数据
const allFiles = ref([]);

// 根据筛选条件过滤文件
const filteredFiles = computed(() => {
  let result = allFiles.value;
  
  // 根据类型筛选
  if (fileType.value !== 'all') {
    result = result.filter(file => file.type === fileType.value);
  }
  
  // 根据关键字搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(file => 
      file.name.toLowerCase().includes(keyword)
    );
  }
  
  // 计算总文件数（用于分页）
  totalFiles.value = result.length;
  
  // 根据当前页码和每页数量截取文件
  const startIndex = (current.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;
  return result.slice(startIndex, endIndex);
});

// 总文件数
const totalFiles = ref(0);

// 获取文件类型名称
const getTypeName = (type) => {
  const types = {
    'academic': '学术规范',
    'administration': '行政管理',
    'student': '学生事务',
    'teaching': '教学管理'
  };
  return types[type] || '其他';
};

// 根据文件类型获取颜色
const getColorByType = (type) => {
  const colors = {
    'academic': '#1890ff',
    'administration': '#52c41a',
    'student': '#fa8c16',
    'teaching': '#722ed1'
  };
  return colors[type] || '#bfbfbf';
};

// 搜索文件
const onSearch = (value) => {
  current.value = 1; // 重置为第一页
};

// 切换文件类型
const onTypeChange = () => {
  current.value = 1; // 重置为第一页
};

// 切换页码
const onPageChange = (page) => {
  current.value = page;
};

// 切换每页显示数量
const onShowSizeChange = (current, size) => {
  pageSize.value = size;
};

// 下载文件
const downloadFile = async (file) => {
  console.log('Downloading file:', file.name);
  message.loading({ content: '准备下载文件...', key: 'download' });
  
  try {
    // 使用新的下载函数
    const result = await fileDownload(file.name);
    
    if (result.code === 200) {
      message.success({ 
        content: `文件"${file.name}"开始下载`,
        key: 'download',
        duration: 2
      });
    } else {
      message.error({ 
        content: result.message || '下载失败，请重试',
        key: 'download'
      });
    }
  } catch (error) {
    console.error('Download error:', error);
    message.error({ 
      content: '下载文件时发生错误，请重试',
      key: 'download'
    });
  }
};

// 获取文件列表
const fetchFiles = async () => {
  loading.value = true;
  
  try {
    const response = await getRegulationFiles();
    
    if (response.code === 200) {
      allFiles.value = response.data;
      totalFiles.value = response.data.length;
    } else {
      message.error('获取文件列表失败');
    }
  } catch (error) {
    console.error('Failed to fetch files:', error);
    message.error('获取文件列表时发生错误');
  } finally {
    loading.value = false;
  }
};

// 页面初始化
onMounted(() => {
  // 获取文件列表
  fetchFiles();
});
</script>

<style scoped>
.regulations-container {
  padding: 30px;
  height: calc(100vh - 60px);
  width: calc(100% - 60px); /* 修改宽度计算方式，确保不挤压左侧边栏 */
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

.files-section {
  background: #fff;
  border-radius: 15px;
  box-shadow: 0px 8px 20px rgba(112, 144, 176, 0.1);
  padding: 24px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.search-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.file-list {
  flex-grow: 1;
  width: 100%;
}

.file-item {
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
  cursor: pointer;
  background-color: #fafafa;
}

.file-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #e6f7f0;
  background-color: #fff;
}

.file-item-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.file-icon {
  margin-right: 16px;
}

.file-info {
  flex: 1;
  overflow: hidden;
}

.file-title {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-desc {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.file-date, .file-size {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

.file-actions {
  margin-left: 16px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

/* 横屏响应式调整 */
@media (min-width: 1200px) {
  .regulations-container {
    padding: 30px 40px;
  }
  
  .file-item-content {
    padding: 0 8px;
  }
  
  .file-title {
    font-size: 18px;
  }
}

@media (min-width: 1600px) {
  .regulations-container {
    padding: 30px 60px;
  }
}

@media (max-height: 800px) {
  .regulations-container {
    padding: 20px 30px;
  }

  .page-title {
    margin-bottom: 10px;
  }

  .page-desc {
    margin-bottom: 20px;
  }
}
</style> 