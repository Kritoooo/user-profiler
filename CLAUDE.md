# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start
The integrated `start.sh` script provides all functionality in one place:

```bash
# System integrity check
./start.sh --check

# Start full system (auto-detects Docker or manual setup)
./start.sh

# Force manual startup with Python venv
./start.sh --manual

# Manual startup with live logs
./start.sh --logs

# Run comprehensive test suite
./start.sh --test

# Stop all running services
./start.sh --stop

# View logs with various options
./start.sh --view-logs
./start.sh --view-logs follow     # Live log following
./start.sh --view-logs recent 50  # Last 50 lines
./start.sh --view-logs error      # Error logs only

# Get help
./start.sh --help
```

### Integrated Script Features
The `start.sh` script consolidates the functionality of multiple previous scripts:

| Old Script | New Command | Description |
|------------|-------------|-------------|
| `check_system.sh` | `./start.sh --check` | System integrity validation |
| `start_manual.sh` | `./start.sh --manual` | Force manual Python startup |
| `start_with_logs.sh` | `./start.sh --logs` | Start with live log monitoring |
| `run_tests.sh` | `./start.sh --test` | Comprehensive test suite |
| `stop.sh` | `./start.sh --stop` | Stop all running services |
| `view_logs.sh` | `./start.sh --view-logs` | Log viewing with multiple options |

**Command Line Options:**
- Short flags: `-h`, `-c`, `-t`, `-s`, `-m`, `-l`, `-v`
- Long flags: `--help`, `--check`, `--test`, `--stop`, `--manual`, `--logs`, `--view-logs`
- Auto-completion friendly with descriptive help text

### Backend Development (Python + FastAPI)
```bash
cd backend

# Setup uv environment and install dependencies
uv sync

# Setup environment
cp .env.example .env

# Start API server (production method)
uv run python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

# Run simple functionality test
uv run python test_simple.py

# Run unit tests
uv run pytest -v

# Add new dependencies
uv add package_name

# Update dependencies
uv sync
```

### Frontend Development (Next.js)
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

### Frontend Architecture (Next.js)
- **App Router**: File-based routing with `src/app/` directory structure
- **TypeScript**: Full type safety with `src/services/api.ts` centralized API client
- **API Proxy**: Next.js rewrites `/api/*` to `http://localhost:8000/*` for seamless backend integration
- **Responsive design**: Tailwind CSS with interactive timeline visualization
- **Server-Side Rendering**: Next.js SSR capabilities with client-side interactivity

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
- uv environment is required for proper module resolution
- Main entry points: `src/api/main.py` (API server), `src/main.py` (CLI)
- Dependencies managed via `pyproject.toml` and `uv.lock`

## Testing Strategy

### Test Execution Order
1. **System Check**: `./start.sh --check` - Validates environment
2. **Simple Tests**: `uv run python test_simple.py` - Core functionality 
3. **Unit Tests**: `uv run pytest` - Individual components
4. **Integration Tests**: `./start.sh --test` - Full system validation

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
uv run playwright install
uv run playwright install-deps  # May require sudo
```

### LLM Features
- Requires OpenAI API key in `.env`
- Falls back to basic extraction without LLM

## Development Notes

- **Port Usage**: Backend (8000), Frontend (3000)  
- **Python Environment**: Always use `uv` for Python development and dependency management
- **Module Resolution**: Backend requires absolute imports from `src/`
- **Database**: Auto-initializes on startup, no migrations needed
- **API Integration**: Frontend uses Next.js proxy configuration, not CORS
- **Background Tasks**: Crawling runs asynchronously, monitor via `/logs/stream` endpoint

## Common Issues

### Frontend Loading Problems
If frontend shows "Loading..." indefinitely after `./start.sh --manual`:

1. **Proxy Interference**: System HTTP proxy may block localhost access
   ```bash
   # Clear proxy variables
   unset http_proxy https_proxy
   # Or export empty values
   export http_proxy="" https_proxy=""
   ```

2. **Service Status Check**: Verify both services are running
   ```bash
   # Check processes
   ps aux | grep -E "(uvicorn|next-server)"
   
   # Check listening ports
   ss -tlpn | grep -E ":8000|:3000"
   
   # Test API proxy
   curl http://localhost:3000/api/health
   ```

3. **Quick Troubleshooting**: Use integrated commands
   ```bash
   # Stop any existing services
   ./start.sh --stop
   
   # Check system integrity
   ./start.sh --check
   
   # Start with live logs to monitor issues
   ./start.sh --logs
   
   # View error logs if needed
   ./start.sh --view-logs error
   ```