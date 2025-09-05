import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, desc
from src.models import Base, UserActivity, UserProfile, ActivityCreate
from src.config import config

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(config.DATABASE_URL)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def add_activity(self, activity_data: Dict[str, Any]) -> UserActivity:
        async with self.async_session() as session:
            activity = UserActivity(
                user_id=activity_data["user_id"],
                platform=activity_data["platform"],
                url=activity_data["url"],
                title=activity_data.get("title"),
                content=activity_data.get("content"),
                extracted_data=activity_data.get("extracted_data"),
                timestamp=datetime.fromisoformat(activity_data["timestamp"]) 
                    if isinstance(activity_data.get("timestamp"), str)
                    else activity_data.get("timestamp", datetime.now())
            )
            
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            return activity
    
    async def get_user_activities(
        self, 
        user_id: str, 
        platform: Optional[str] = None,
        limit: int = 100
    ) -> List[UserActivity]:
        async with self.async_session() as session:
            query = select(UserActivity).where(UserActivity.user_id == user_id)
            
            if platform:
                query = query.where(UserActivity.platform == platform)
                
            query = query.order_by(desc(UserActivity.timestamp)).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_timeline_data(self, user_id: str) -> List[Dict[str, Any]]:
        activities = await self.get_user_activities(user_id)
        timeline = []
        
        for activity in activities:
            timeline_item = {
                "id": activity.id,
                "platform": activity.platform,
                "url": activity.url,
                "title": activity.title,
                "content_preview": activity.content[:200] if activity.content else "",
                "extracted_data": activity.extracted_data,
                "timestamp": activity.timestamp.isoformat(),
                "date": activity.timestamp.strftime("%Y-%m-%d"),
                "time": activity.timestamp.strftime("%H:%M:%S")
            }
            timeline.append(timeline_item)
        
        # Group by date for timeline visualization
        grouped_timeline = {}
        for item in timeline:
            date = item["date"]
            if date not in grouped_timeline:
                grouped_timeline[date] = []
            grouped_timeline[date].append(item)
        
        return [
            {
                "date": date,
                "activities": activities
            }
            for date, activities in sorted(grouped_timeline.items(), reverse=True)
        ]
    
    async def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        async with self.async_session() as session:
            # Check if profile exists
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if profile:
                profile.profile_data = profile_data
                profile.last_updated = datetime.now()
            else:
                profile = UserProfile(
                    user_id=user_id,
                    profile_data=profile_data
                )
                session.add(profile)
            
            await session.commit()
            await session.refresh(profile)
            return profile
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        async with self.async_session() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def get_platform_statistics(self, user_id: str) -> Dict[str, int]:
        async with self.async_session() as session:
            activities = await self.get_user_activities(user_id)
            
            stats = {}
            for activity in activities:
                platform = activity.platform
                stats[platform] = stats.get(platform, 0) + 1
            
            return stats
    
    async def close(self):
        await self.engine.dispose()

# Global database instance
db_manager = DatabaseManager()