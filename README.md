# User Profiler System

A modular system for tracking and analyzing user digital footprints across multiple platforms.

## Architecture

- **Backend**: Python-based system with FastAPI and async SQLAlchemy
- **Frontend**: Next.js with TypeScript for timeline visualization
- **Data Flow**: Web Scraping → LLM Extraction → JSON Storage → Profile Generation → Timeline Visualization

## Features

- Multi-platform data collection (GitHub, Zhihu, search engines)
- AI-powered information extraction using OpenAI
- Timeline-based activity tracking
- Comprehensive user profiling
- Responsive web interface with SSR

## Quick Start

### 🔍 System Check
```bash
# Validate environment and dependencies
./start.sh --check
```

### 🚀 Launch System
```bash
# Auto-detect and start (Docker or manual)
./start.sh

# Force manual startup with Python venv
./start.sh --manual

# Start with live log monitoring
./start.sh --logs
```

### 🧪 Testing
```bash
# Run comprehensive test suite
./start.sh --test
```

### 📋 Log Management
```bash
# View recent logs
./start.sh --view-logs

# Follow logs in real-time
./start.sh --view-logs follow

# View last 50 lines
./start.sh --view-logs recent 50

# View error logs only
./start.sh --view-logs error
```

### 🛑 Stop Services
```bash
./start.sh --stop
```

## Manual Setup

### Backend (Python + FastAPI + uv)
```bash
cd backend

# Setup uv environment and dependencies
uv sync

# Configure environment
cp .env.example .env

# Start API server
uv run python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

# Run tests
uv run pytest -v
```

### Frontend (Next.js + TypeScript)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Configuration

### Environment Variables (backend/.env)
```bash
OPENAI_API_KEY=your_api_key_here  # Required for LLM features
DATABASE_URL=sqlite+aiosqlite:///./user_profiler.db
LOG_LEVEL=INFO
```

## API Usage

```bash
# Health check
curl http://localhost:8000/health

# Start crawling
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser", "platforms": ["github"]}'

# Get user activities
curl http://localhost:8000/users/testuser/activities

# Get timeline
curl http://localhost:8000/users/testuser/timeline
```

## Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs