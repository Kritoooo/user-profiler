# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start
```bash
# System integrity check
./check_system.sh

# Start full system (auto-detects Docker or manual setup)
./start.sh

# Force manual startup with Python venv
./start_manual.sh

# Run comprehensive test suite
./run_tests.sh
```

### Backend Development (Python + FastAPI)
```bash
cd backend

# Setup virtual environment (required)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Start API server (production method)
python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

# Run simple functionality test
python test_simple.py

# Run unit tests
pytest -v
```

### Frontend Development (Vue.js 3)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

### Database Operations
- SQLite database location: `backend/user_profiler.db`
- Reset data: Delete the database file and restart
- Database is automatically initialized on startup

## Architecture Overview

### Data Flow
**Web Scraping → LLM Extraction → JSON Storage → Profile Generation → Timeline Visualization**

### Backend Architecture (Python)
The backend uses a modular collector pattern:

- **`src/collectors/`**: Platform-specific data collectors inheriting from `BaseCollector`
  - Each collector implements `build_search_urls()` and `extract_user_info()`
  - Built-in rate limiting and error handling
  - Supports GitHub, Zhihu, search engines

- **`src/extractors/`**: LLM-powered information extraction using OpenAI
  - Converts raw web content to structured JSON
  - Generates user profiles from collected activities

- **`src/storage/`**: Async SQLAlchemy with SQLite
  - Two main entities: `UserActivity` and `UserProfile`
  - JSON column storage for flexible data structures

- **`src/profiler/`**: Core business logic orchestrating the entire pipeline
  - Coordinates collectors, extractors, and storage
  - Generates timeline data and comprehensive user profiles

- **`src/api/`**: FastAPI REST endpoints with background task processing
  - Async endpoints for crawling, activities, timelines, profiles
  - CORS configured for frontend integration

### Frontend Architecture (Vue.js 3)
- **Router-based SPA**: Home → Timeline → Profile workflow
- **`src/services/api.js`**: Centralized API client using Axios
- **Responsive design**: Tailwind CSS with timeline visualization
- **Real-time updates**: Background processing status handling

### Key Design Patterns

1. **Async Collector Pattern**: All data collectors are async and inherit from `BaseCollector`
2. **Background Task Processing**: FastAPI background tasks for long-running crawl operations  
3. **JSON-First Storage**: Flexible schema using SQLAlchemy JSON columns
4. **Rate-Limited Crawling**: Built-in delays and error handling for web scraping
5. **Modular Platform Support**: Easy to add new platforms by implementing collector interface

## Important Configuration

### Environment Variables (backend/.env)
```bash
OPENAI_API_KEY=your_api_key_here  # Required for LLM features
DATABASE_URL=sqlite+aiosqlite:///./user_profiler.db
LOG_LEVEL=INFO
```

### Platform Configuration (src/config.py)
- Rate limits and base URLs for each platform
- Excluded common usernames (abc, admin, test, etc.)
- Search engine endpoints

### Python Import Structure
- All imports use absolute paths: `from src.module import ...`
- Virtual environment is required for proper module resolution
- Main entry points: `src/api/main.py` (API server), `src/main.py` (CLI)

## Testing Strategy

### Test Execution Order
1. **System Check**: `./check_system.sh` - Validates environment
2. **Simple Tests**: `backend/test_simple.py` - Core functionality 
3. **Unit Tests**: `pytest` - Individual components
4. **Integration Tests**: `./run_tests.sh` - Full system validation

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Start crawling
curl -X POST http://localhost:8000/crawl -H "Content-Type: application/json" -d '{"user_id": "testuser", "platforms": ["github"]}'

# Get activities
curl http://localhost:8000/users/testuser/activities

# Get timeline
curl http://localhost:8000/users/testuser/timeline
```

## Optional Dependencies

### Full Web Scraping (requires system packages)
```bash
cd backend
source venv/bin/activate
playwright install
playwright install-deps  # May require sudo
```

### LLM Features
- Requires OpenAI API key in `.env`
- Falls back to basic extraction without LLM

## Development Notes

- **Port Usage**: Backend (8000), Frontend (3000)  
- **Virtual Environment**: Always use `venv` for Python development
- **Module Resolution**: Backend requires absolute imports from `src/`
- **Database**: Auto-initializes on startup, no migrations needed
- **CORS**: Pre-configured for localhost development
- **Background Tasks**: Crawling runs asynchronously, check logs for progress