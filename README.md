# User Profiler System

A modular system for tracking and analyzing user digital footprints across multiple platforms.

## Architecture

- **Backend**: Python-based system with Crawl4AI for web scraping
- **Frontend**: Vue.js for timeline visualization
- **Data Flow**: Web Scraping → LLM Extraction → JSON Storage → Profile Generation

## Features

- Multi-platform data collection (GitHub, Zhihu, Xiaohongshu, personal blogs)
- Search engine aggregation (Google, Bing, Baidu)
- Timeline-based activity tracking
- AI-powered information extraction
- Comprehensive user profiling

## Quick Start

### 🚀 一键启动
```bash
# 自动检测环境并启动
./start.sh

# 强制手动启动方式
./start_manual.sh

# 启动并显示实时日志
./start_with_logs.sh
```

### 🧪 运行测试
```bash
./run_tests.sh
```

### 📋 查看日志
```bash
# 查看最近日志
./view_logs.sh

# 实时跟踪日志
./view_logs.sh follow

# 查看错误日志
./view_logs.sh error

# 查看特定用户日志
./view_logs.sh user testuser
```

### 📋 手动启动

#### 后端 (Python + FastAPI)
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动API服务
python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

#### 前端 (Vue.js 3)
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### Docker 方式
```bash
docker-compose up -d
```