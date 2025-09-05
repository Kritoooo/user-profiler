import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./user_profiler.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/user_profiler.log")
    LOG_JSON_FORMAT: bool = os.getenv("LOG_JSON_FORMAT", "false").lower() == "true"
    
    # Platform configurations
    PLATFORMS = {
        "github": {
            "base_url": "https://github.com",
            "rate_limit": 1.0  # seconds between requests
        },
        "zhihu": {
            "base_url": "https://www.zhihu.com",
            "rate_limit": 2.0
        },
        "xiaohongshu": {
            "base_url": "https://www.xiaohongshu.com",
            "rate_limit": 3.0
        }
    }
    
    # Search engines
    SEARCH_ENGINES = ["google", "bing", "baidu"]
    
    # Common IDs to exclude
    EXCLUDED_IDS = ["abc", "admin", "user", "test", "demo", "example"]

config = Config()