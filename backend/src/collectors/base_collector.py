from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import time
from crawl4ai import AsyncWebCrawler
from src.config import config

class BaseCollector(ABC):
    def __init__(self, platform: str):
        self.platform = platform
        self.config = config.PLATFORMS.get(platform, {})
        self.rate_limit = self.config.get("rate_limit", 1.0)
        self.last_request_time = 0
    
    async def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    @abstractmethod
    def build_search_urls(self, user_id: str) -> List[str]:
        pass
    
    @abstractmethod
    def extract_user_info(self, html_content: str, url: str) -> Dict[str, Any]:
        pass
    
    async def collect_user_data(self, user_id: str) -> List[Dict[str, Any]]:
        if user_id.lower() in config.EXCLUDED_IDS:
            return []
            
        urls = self.build_search_urls(user_id)
        results = []
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            for url in urls:
                try:
                    await self._rate_limit_wait()
                    result = await crawler.arun(url=url)
                    
                    if result.success:
                        extracted_info = self.extract_user_info(result.markdown, url)
                        if extracted_info:
                            results.append({
                                "platform": self.platform,
                                "url": url,
                                "title": extracted_info.get("title", ""),
                                "content": result.markdown[:2000],  # Limit content size
                                "extracted_data": extracted_info,
                                "timestamp": extracted_info.get("timestamp")
                            })
                except Exception as e:
                    print(f"Error crawling {url}: {str(e)}")
                    continue
        
        return results