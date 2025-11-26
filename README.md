# 应急智能体 Web API 服务

基于 RAG（检索增强生成）技术的应急管理领域智能问答系统。

## 功能特点

- 🤖 基于大语言模型的智能问答
- 📚 支持应急管理领域专业知识检索
- 💬 流式响应，实时显示AI回复
- 🌐 支持本地和外网访问
- 📱 响应式Web界面

## 快速启动

### 1. 启动后端服务

```bash
cd /home/liuyingchang/code/Emergency-LLM
python app.py
```

### 2. 访问Web界面

**本地访问：**
- 前端页面: http://localhost:5001
- 健康检查: http://localhost:5001/health

**外网访问：**
- 前端页面: http://218.199.69.58:5001
- 健康检查: http://218.199.69.58:5001/health

## 防火墙配置

如果外网无法访问，需要开放5001端口：

### Ubuntu/Debian (ufw)
```bash
sudo ufw allow 5001/tcp
sudo ufw reload
```

### CentOS/RHEL (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

### 查看端口监听状态
```bash
sudo netstat -tlnp | grep 5001
# 或
sudo ss -tlnp | grep 5001
```

## API 接口说明

### POST /getMessageWeb

获取AI智能体回复（流式响应）

**请求体：**
```json
{
  "userMessage": "用户消息内容",
  "history": [
    {"role": "user", "content": "历史消息1"},
    {"role": "assistant", "content": "AI回复1"}
  ]
}
```

**响应：** 流式返回文本内容（text/plain）

### GET /health

健康检查接口

**响应：**
```json
{
  "status": "ok",
  "message": "应急智能体 API 服务运行正常"
}
```

## 技术栈

- **后端框架**: Flask
- **AI模型**: OpenAI API (vLLM)
- **RAG引擎**: LangChain + ChromaDB
- **前端**: HTML + Tailwind CSS + Vanilla JS

## 依赖服务

需要确保以下服务正常运行：

1. **vLLM 服务** (端口8000)
   - 模型: Qwen3-32B-AWQ
   - 接口: http://localhost:8000/v1

2. **ChromaDB 向量数据库**
   - 存储路径: `/New_Disk/liuyingchang/...`

## 故障排查

### 问题1: "Failed to fetch" 或 "network error"

**原因：** 前端无法连接到后端API

**解决方法：**
1. 确认后端服务正在运行: `ps aux | grep "python.*app.py"`
2. 检查端口是否监听: `sudo netstat -tlnp | grep 5001`
3. 测试健康检查: `curl http://localhost:5001/health`

### 问题2: "AssertionError: applications must write bytes"

**原因：** Flask流式响应要求返回字节类型

**解决方法：** 已在代码中修复，确保所有yield的内容都经过`.encode('utf-8')`处理

### 问题3: 外网无法访问

**原因：** 防火墙阻止或服务未绑定0.0.0.0

**解决方法：**
1. 检查Flask是否绑定到0.0.0.0（已配置）
2. 开放防火墙5001端口（见上文）
3. 如果在云服务器，检查安全组规则

### 问题4: AI回复慢或超时

**原因：** 模型推理时间长或vLLM服务异常

**解决方法：**
1. 检查vLLM服务状态: `curl http://localhost:8000/v1/models`
2. 查看GPU使用情况: `nvidia-smi`
3. 前端已设置120秒超时，模型响应超时会自动提示

## 项目结构

```
Emergency-LLM/
├── app.py              # Flask后端服务
├── static/
│   ├── test.html       # 前端页面
│   ├── js/
│   │   └── main.js     # 前端JavaScript
│   └── css/
│       └── style.css   # 样式文件
└── README.md           # 说明文档
```

## 许可证

本项目仅供学习和研究使用。
