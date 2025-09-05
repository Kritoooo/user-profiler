import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from src.collectors import GitHubCollector, ZhihuCollector, SearchEngineCollector
from src.extractors import LLMExtractor  
from src.storage.database import db_manager
from src.config import config
from src.utils.logger import get_logger, LogContext

class UserProfiler:
    def __init__(self):
        self.collectors = {
            "github": GitHubCollector(),
            "zhihu": ZhihuCollector(),
        }
        self.search_collectors = {
            engine: SearchEngineCollector(engine) 
            for engine in config.SEARCH_ENGINES
        }
        self.llm_extractor = LLMExtractor()
        self.db = db_manager
    
    async def crawl_user_data(
        self, 
        user_id: str, 
        platforms: List[str] = None,
        search_engines: List[str] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        with LogContext(user_id=user_id, operation="crawl_user_data") as log_ctx:
            if not platforms:
                platforms = ["github", "zhihu"]
            if not search_engines:
                search_engines = ["google", "bing"]
            
            log_ctx.info(
                f"Starting data crawl for user: {user_id}",
                platforms=platforms,
                search_engines=search_engines,
                use_llm=use_llm
            )
            
            results = {
                "user_id": user_id,
                "crawl_timestamp": datetime.now().isoformat(),
                "collected_data": [],
                "errors": []
            }
            
            # Collect from platforms
            for platform in platforms:
                if platform in self.collectors:
                    try:
                        log_ctx.info(f"Starting {platform} data collection", platform=platform)
                        platform_start = time.time()
                        
                        platform_data = await self.collectors[platform].collect_user_data(user_id)
                        
                        platform_duration = time.time() - platform_start
                        log_ctx.info(
                            f"Collected {len(platform_data)} items from {platform}",
                            platform=platform,
                            items_count=len(platform_data),
                            duration=f"{platform_duration:.2f}s"
                        )
                        
                        for item in platform_data:
                            # Enhanced extraction with LLM if enabled
                            if use_llm and item.get("content"):
                                try:
                                    log_ctx.debug(f"Enhancing data with LLM for {item['url']}", url=item['url'])
                                    enhanced_data = self.llm_extractor.extract_structured_info(
                                        item["content"],
                                        item["platform"], 
                                        item["url"]
                                    )
                                    # Merge LLM extraction with original data
                                    item["extracted_data"].update(enhanced_data)
                                    log_ctx.debug(f"LLM extraction completed for {item['url']}")
                                except Exception as e:
                                    log_ctx.warning(f"LLM extraction failed for {item['url']}: {str(e)}", url=item['url'])
                            
                            # Store in database
                            await self.db.add_activity(item)
                            results["collected_data"].append(item)
                            log_ctx.debug(f"Stored activity: {item['title']}", url=item['url'])
                            
                    except Exception as e:
                        error_msg = f"Error crawling {platform}: {str(e)}"
                        log_ctx.error(error_msg, platform=platform)
                        results["errors"].append(error_msg)
        
        # Collect from search engines
        for engine in search_engines:
            if engine in self.search_collectors:
                try:
                    print(f"Searching {engine} for user: {user_id}")
                    search_data = await self.search_collectors[engine].collect_user_data(user_id)
                    
                    for item in search_data:
                        if use_llm and item.get("content"):
                            try:
                                enhanced_data = self.llm_extractor.extract_structured_info(
                                    item["content"],
                                    item["platform"],
                                    item["url"]
                                )
                                item["extracted_data"].update(enhanced_data)
                            except Exception as e:
                                print(f"LLM extraction error for search result: {str(e)}")
                        
                        await self.db.add_activity(item)
                        results["collected_data"].append(item)
                        
                except Exception as e:
                    error_msg = f"Error searching {engine}: {str(e)}"
                    print(error_msg)
                    results["errors"].append(error_msg)
        
        return results
    
    async def generate_user_profile(self, user_id: str) -> Dict[str, Any]:
        # Get all user activities
        activities = await self.db.get_user_activities(user_id)
        
        if not activities:
            return {
                "user_id": user_id,
                "error": "No activities found for user",
                "generated_at": datetime.now().isoformat()
            }
        
        # Convert to dict format for LLM processing
        activity_dicts = [
            {
                "platform": activity.platform,
                "url": activity.url,
                "title": activity.title,
                "content": activity.content,
                "extracted_data": activity.extracted_data,
                "timestamp": activity.timestamp.isoformat()
            }
            for activity in activities
        ]
        
        # Generate profile with LLM
        try:
            llm_profile = self.llm_extractor.generate_profile_summary(activity_dicts)
        except Exception as e:
            print(f"Error generating LLM profile: {str(e)}")
            llm_profile = {"error": str(e)}
        
        # Generate statistical analysis
        stats = await self._generate_statistics(activities)
        
        # Create comprehensive profile
        profile = {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "activity_summary": {
                "total_activities": len(activities),
                "platform_breakdown": stats["platform_breakdown"],
                "date_range": stats["date_range"],
                "activity_frequency": stats["activity_frequency"]
            },
            "ai_analysis": llm_profile,
            "timeline_highlights": self._extract_timeline_highlights(activity_dicts),
            "digital_footprint": {
                "platforms_active": list(stats["platform_breakdown"].keys()),
                "content_types": stats["content_types"],
                "engagement_patterns": stats["engagement_patterns"]
            }
        }
        
        # Save profile to database
        await self.db.save_user_profile(user_id, profile)
        
        return profile
    
    async def _generate_statistics(self, activities: List) -> Dict[str, Any]:
        stats = {
            "platform_breakdown": {},
            "content_types": {},
            "engagement_patterns": {},
            "date_range": {},
            "activity_frequency": {}
        }
        
        if not activities:
            return stats
        
        # Platform breakdown
        for activity in activities:
            platform = activity.platform
            stats["platform_breakdown"][platform] = stats["platform_breakdown"].get(platform, 0) + 1
        
        # Date range and frequency
        dates = [activity.timestamp for activity in activities]
        if dates:
            earliest = min(dates)
            latest = max(dates)
            stats["date_range"] = {
                "earliest_activity": earliest.isoformat(),
                "latest_activity": latest.isoformat(),
                "span_days": (latest - earliest).days
            }
            
            # Activity frequency by month
            monthly_counts = {}
            for date in dates:
                month_key = date.strftime("%Y-%m")
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            stats["activity_frequency"] = monthly_counts
        
        # Content types from extracted data
        for activity in activities:
            if activity.extracted_data:
                activity_type = activity.extracted_data.get("activity_type", "unknown")
                stats["content_types"][activity_type] = stats["content_types"].get(activity_type, 0) + 1
        
        return stats
    
    def _extract_timeline_highlights(self, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Extract significant events for timeline highlights
        highlights = []
        
        # Sort by timestamp
        sorted_activities = sorted(
            activities, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        
        # Take recent significant activities
        for activity in sorted_activities[:10]:
            if activity.get("extracted_data"):
                highlight = {
                    "date": activity["timestamp"][:10],
                    "platform": activity["platform"],
                    "title": activity.get("title", "Activity"),
                    "type": activity["extracted_data"].get("activity_type", "unknown"),
                    "significance": self._calculate_significance(activity)
                }
                highlights.append(highlight)
        
        return sorted(highlights, key=lambda x: x["significance"], reverse=True)[:5]
    
    def _calculate_significance(self, activity: Dict[str, Any]) -> float:
        # Simple significance scoring
        score = 0.0
        
        extracted = activity.get("extracted_data", {})
        
        # Boost score for certain platforms
        platform_boost = {
            "github": 1.2,
            "zhihu": 1.1,
            "search_google": 0.8
        }
        score += platform_boost.get(activity.get("platform", ""), 1.0)
        
        # Boost for engagement metrics
        if "followers" in extracted:
            score += min(float(extracted.get("followers", 0)) / 1000, 2.0)
        
        if "repositories_count" in extracted:
            score += min(float(extracted.get("repositories_count", 0)) / 10, 1.5)
            
        return score

# Global profiler instance
user_profiler = UserProfiler()