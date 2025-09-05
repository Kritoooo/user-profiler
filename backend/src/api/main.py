from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import uvicorn
import asyncio
import json
import signal
import sys
from datetime import datetime
from pathlib import Path

from src.models import CrawlRequest, ActivityResponse, ProfileResponse
from src.storage.database import db_manager
from src.profiler.user_profiler import user_profiler
from src.config import config
from src.utils.logger import setup_logging, get_logger, LogContext

# Setup logging
logger = setup_logging(
    log_level=config.LOG_LEVEL,
    log_file=config.LOG_FILE,
    json_format=config.LOG_JSON_FORMAT
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting User Profiler API server")
    await db_manager.init_db()
    logger.info("✅ Database initialized successfully")
    
    # Setup graceful shutdown
    setup_signal_handlers()
    
    yield
    # Shutdown
    logger.info("🛑 Shutting down User Profiler API server")
    await graceful_shutdown()

app = FastAPI(
    title="User Profiler API",
    description="API for tracking and analyzing user digital footprints",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "User Profiler API", "version": "1.0.0"}

@app.post("/crawl")
async def crawl_user(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Start crawling user data across platforms"""
    
    with LogContext(user_id=request.user_id, operation="crawl_request") as log_ctx:
        # Validate user_id
        if not request.user_id or len(request.user_id) < 2:
            log_ctx.error("Invalid user_id provided", user_id=request.user_id)
            raise HTTPException(status_code=400, detail="Invalid user_id")
        
        log_ctx.info(
            f"Starting crawl request for user: {request.user_id}",
            platforms=request.platforms,
            search_engines=request.search_engines
        )
        
        # Add crawling task to background
        background_tasks.add_task(
            user_profiler.crawl_user_data,
            request.user_id,
            request.platforms,
            request.search_engines,
            True  # use_llm
        )
        
        log_ctx.info(f"Background crawl task scheduled for user: {request.user_id}")
        
        return {
            "message": f"Started crawling data for user: {request.user_id}",
            "user_id": request.user_id,
            "platforms": request.platforms,
            "search_engines": request.search_engines
        }

@app.get("/users/{user_id}/activities", response_model=List[ActivityResponse])
async def get_user_activities(user_id: str, platform: str = None, limit: int = 100):
    """Get user activities with optional platform filter"""
    
    activities = await db_manager.get_user_activities(user_id, platform, limit)
    return activities

@app.get("/users/{user_id}/timeline")
async def get_user_timeline(user_id: str):
    """Get user timeline organized by dates"""
    
    timeline = await db_manager.get_timeline_data(user_id)
    return {"user_id": user_id, "timeline": timeline}

@app.get("/users/{user_id}/profile", response_model=ProfileResponse) 
async def get_user_profile(user_id: str):
    """Get existing user profile"""
    
    profile = await db_manager.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@app.post("/users/{user_id}/profile/generate")
async def generate_user_profile(user_id: str, background_tasks: BackgroundTasks):
    """Generate new user profile from collected activities"""
    
    # Check if activities exist
    activities = await db_manager.get_user_activities(user_id, limit=1)
    if not activities:
        raise HTTPException(
            status_code=404, 
            detail="No activities found. Please crawl user data first."
        )
    
    # Generate profile in background
    background_tasks.add_task(user_profiler.generate_user_profile, user_id)
    
    return {
        "message": f"Started generating profile for user: {user_id}",
        "user_id": user_id
    }

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user platform statistics"""
    
    stats = await db_manager.get_platform_statistics(user_id)
    activities = await db_manager.get_user_activities(user_id, limit=1000)
    
    return {
        "user_id": user_id,
        "total_activities": len(activities),
        "platform_stats": stats,
        "last_activity": activities[0].timestamp.isoformat() if activities else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/logs/stream")
async def stream_logs():
    """Stream real-time logs"""
    
    async def generate_logs():
        log_file_path = Path(config.LOG_FILE)
        
        # Send recent logs first
        if log_file_path.exists():
            try:
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    # Get last 50 lines
                    lines = f.readlines()
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    
                    for line in recent_lines:
                        if line.strip():
                            yield f"data: {json.dumps({'log': line.strip(), 'type': 'history'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'log': f'Error reading log file: {str(e)}', 'type': 'error'})}\n\n"
        
        # Stream new logs
        if log_file_path.exists():
            try:
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    # Go to end of file
                    f.seek(0, 2)
                    
                    while True:
                        line = f.readline()
                        if line:
                            yield f"data: {json.dumps({'log': line.strip(), 'type': 'live'})}\n\n"
                        else:
                            await asyncio.sleep(0.1)
            except Exception as e:
                yield f"data: {json.dumps({'log': f'Error streaming logs: {str(e)}', 'type': 'error'})}\n\n"
    
    return StreamingResponse(
        generate_logs(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/logs/recent")
async def get_recent_logs(lines: int = 100):
    """Get recent log entries"""
    
    log_file_path = Path(config.LOG_FILE)
    
    if not log_file_path.exists():
        return {"logs": [], "message": "Log file not found"}
    
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            logs = []
            for line in recent_lines:
                if line.strip():
                    logs.append({
                        "message": line.strip(),
                        "timestamp": datetime.now().isoformat()
                    })
            
            return {
                "logs": logs,
                "total_lines": len(all_lines),
                "returned_lines": len(logs)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

# Graceful shutdown handling
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    signal_name = signal.Signals(signum).name
    logger.info(f"🔔 Received {signal_name} signal, initiating graceful shutdown...")
    shutdown_event.set()

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        logger.info("📡 Signal handlers configured for graceful shutdown")

async def graceful_shutdown():
    """Perform graceful shutdown operations"""
    logger.info("🧹 Starting graceful shutdown sequence...")
    
    # Close database connections
    try:
        await db_manager.close()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")
    
    # Wait for any background tasks to complete (with timeout)
    try:
        await asyncio.wait_for(asyncio.sleep(0.5), timeout=5.0)
        logger.info("✅ Background tasks completed")
    except asyncio.TimeoutError:
        logger.warning("⚠️ Some background tasks may not have completed")
    
    logger.info("✅ Graceful shutdown completed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)