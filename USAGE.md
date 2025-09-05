# 用户画像系统使用说明

## 🚀 快速开始

### 1. 启动系统
```bash
./start.sh
```

系统会自动：
- 创建Python虚拟环境 (venv)
- 安装所有依赖
- 启动后端API服务器 (端口8000)
- 启动前端开发服务器 (端口3000)

### 2. 访问系统
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 💻 基本使用流程

### 第一步：输入用户ID
1. 打开前端界面 (http://localhost:3000)
2. 在首页输入要分析的用户ID (如: "testuser", GitHub用户名等)
3. 选择要搜索的平台 (GitHub, 知乎等)
4. 选择搜索引擎 (Google, Bing)
5. 点击"开始分析"

### 第二步：查看时间轴
1. 系统会自动跳转到时间轴页面
2. 查看用户在各平台的活动记录
3. 按时间顺序浏览用户的数字足迹
4. 可以按平台筛选活动

### 第三步：查看用户画像
1. 点击"查看画像"或"生成画像"
2. 系统会分析用户活动生成综合画像
3. 查看AI分析的用户特征和兴趣
4. 浏览用户的数字足迹总结

## 🔧 高级配置

### 启用LLM功能
1. 编辑 `backend/.env` 文件
2. 设置 `OPENAI_API_KEY=your_api_key_here`
3. 重启后端服务

### 启用实际网络爬取
```bash
cd backend
source venv/bin/activate
playwright install-deps
```

### 数据库位置
- SQLite数据库文件: `backend/user_profiler.db`
- 包含用户活动和画像数据

## 🧪 测试系统

### 运行完整测试
```bash
./run_tests.sh
```

### 手动测试API
```bash
# 健康检查
curl http://localhost:8000/health

# 开始爬取
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser", "platforms": ["github"]}'

# 查看活动
curl http://localhost:8000/users/testuser/activities
```

## 📂 项目结构

```
user-profiler/
├── backend/                 # Python后端
│   ├── src/
│   │   ├── api/            # FastAPI路由
│   │   ├── collectors/     # 数据收集器
│   │   ├── extractors/     # 信息提取器  
│   │   ├── storage/        # 数据存储
│   │   └── profiler/       # 用户画像生成
│   ├── tests/              # 测试文件
│   └── venv/               # Python虚拟环境
├── frontend/               # Vue.js前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── services/       # API服务
│   │   └── components/     # UI组件
│   └── node_modules/       # Node.js依赖
├── start.sh               # 启动脚本
├── run_tests.sh          # 测试脚本
└── docker-compose.yml    # Docker配置
```

## 🛠️ 常见问题

### Q: 启动失败怎么办？
A: 
1. 确保Python 3.10+和Node.js 18+已安装
2. 检查端口8000和3000是否被占用
3. 运行 `./run_tests.sh` 检查系统状态

### Q: 爬取数据为空？
A: 
1. 检查网络连接
2. 某些平台可能需要特殊配置
3. 查看后端日志获取详细错误信息

### Q: 如何停止服务？
A: 
1. 在启动终端按 Ctrl+C
2. 或者使用 `pkill -f "uvicorn\|vite"`

### Q: 如何重置数据？
A: 删除 `backend/user_profiler.db` 文件，重启系统即可

## 📞 获取支持

- 查看 `test_report.md` 了解系统测试状态
- 查看API文档: http://localhost:8000/docs
- 检查后端日志了解详细错误信息