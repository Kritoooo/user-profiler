from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    platform = Column(String)
    url = Column(String)
    title = Column(String)
    content = Column(Text)
    extracted_data = Column(JSON)
    timestamp = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    profile_data = Column(JSON)
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

# Pydantic models for API
class ActivityCreate(BaseModel):
    user_id: str
    platform: str
    url: str
    title: Optional[str] = None
    content: Optional[str] = None

class ActivityResponse(BaseModel):
    id: int
    user_id: str
    platform: str
    url: str
    title: Optional[str]
    content: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    user_id: str
    profile_data: Dict[str, Any]
    last_updated: datetime
    
    class Config:
        from_attributes = True

class CrawlRequest(BaseModel):
    user_id: str
    platforms: List[str] = ["github", "zhihu", "xiaohongshu"]
    search_engines: List[str] = ["google", "bing"]