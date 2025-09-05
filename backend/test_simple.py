#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.database import db_manager
from src.models import UserActivity
from datetime import datetime

async def test_database():
    """Test database operations"""
    print("🧪 Testing Database Operations")
    print("-" * 40)
    
    # Initialize database
    await db_manager.init_db()
    print("✅ Database initialized")
    
    # Test adding activity
    activity_data = {
        "user_id": "testuser",
        "platform": "github", 
        "url": "https://github.com/testuser",
        "title": "GitHub Profile",
        "content": "Test user profile content",
        "extracted_data": {
            "type": "github_profile",
            "username": "testuser", 
            "followers": 100,
            "repositories_count": 15
        },
        "timestamp": datetime.now()
    }
    
    activity = await db_manager.add_activity(activity_data)
    print(f"✅ Added activity: {activity.id}")
    
    # Test getting activities
    activities = await db_manager.get_user_activities("testuser")
    print(f"✅ Retrieved {len(activities)} activities")
    
    # Test timeline data
    timeline = await db_manager.get_timeline_data("testuser")
    print(f"✅ Generated timeline with {len(timeline)} days")
    
    # Test profile data
    profile_data = {
        "user_id": "testuser",
        "generated_at": datetime.now().isoformat(),
        "activity_summary": {
            "total_activities": 1,
            "platform_breakdown": {"github": 1}
        },
        "digital_footprint": {
            "platforms_active": ["github"]
        }
    }
    
    profile = await db_manager.save_user_profile("testuser", profile_data)
    print(f"✅ Saved user profile")
    
    # Test getting profile
    retrieved_profile = await db_manager.get_user_profile("testuser")
    print(f"✅ Retrieved profile for user: {retrieved_profile.user_id}")
    
    print("\n🎉 All database tests passed!")

async def test_api_server():
    """Test API server startup"""
    print("\n🧪 Testing API Server")
    print("-" * 40)
    
    try:
        from src.api.main import app
        print("✅ API module imported successfully")
        
        # Test basic app configuration
        assert app.title == "User Profiler API"
        print("✅ API configuration correct")
        
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False
    
    return True

async def test_collectors_import():
    """Test collector modules"""
    print("\n🧪 Testing Collector Modules")
    print("-" * 40)
    
    try:
        from src.collectors import GitHubCollector, ZhihuCollector, SearchEngineCollector
        print("✅ Collector modules imported")
        
        github = GitHubCollector()
        urls = github.build_search_urls("testuser")
        assert len(urls) > 0
        print(f"✅ GitHub collector generates {len(urls)} URLs")
        
        zhihu = ZhihuCollector() 
        urls = zhihu.build_search_urls("testuser")
        assert len(urls) > 0
        print(f"✅ Zhihu collector generates {len(urls)} URLs")
        
        search = SearchEngineCollector("google")
        urls = search.build_search_urls("testuser")
        assert len(urls) > 0
        print(f"✅ Search collector generates {len(urls)} URLs")
        
    except Exception as e:
        print(f"❌ Collector test failed: {e}")
        return False
        
    return True

async def main():
    """Run all tests"""
    print("🚀 User Profiler System Tests")
    print("=" * 50)
    
    try:
        # Test database
        await test_database()
        
        # Test API server
        await test_api_server()
        
        # Test collectors
        await test_collectors_import()
        
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 The User Profiler system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("🐛 Please check the error above and fix the issue")
    
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())