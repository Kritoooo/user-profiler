import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.profiler.user_profiler import UserProfiler

@pytest.mark.asyncio
class TestUserProfiler:
    def setup_method(self):
        self.profiler = UserProfiler()
    
    @patch('src.profiler.user_profiler.db_manager')
    @patch('src.profiler.user_profiler.LLMExtractor')
    async def test_crawl_user_data_success(self, mock_llm_extractor, mock_db):
        # Mock collectors
        mock_collector = Mock()
        mock_collector.collect_user_data = AsyncMock(return_value=[
            {
                "platform": "github",
                "url": "https://github.com/testuser",
                "title": "Profile",
                "content": "Test content",
                "extracted_data": {"type": "profile"}
            }
        ])
        self.profiler.collectors["github"] = mock_collector
        
        # Mock database
        mock_db.add_activity = AsyncMock()
        
        # Mock LLM extractor
        mock_extractor = Mock()
        mock_extractor.extract_structured_info = Mock(return_value={"enhanced": True})
        mock_llm_extractor.return_value = mock_extractor
        
        result = await self.profiler.crawl_user_data("testuser", ["github"], [], True)
        
        assert result["user_id"] == "testuser"
        assert len(result["collected_data"]) == 1
        assert len(result["errors"]) == 0
        assert result["collected_data"][0]["extracted_data"]["enhanced"] == True
    
    async def test_crawl_user_data_excluded_id(self):
        result = await self.profiler.crawl_user_data("abc", ["github"], [])
        
        assert result["user_id"] == "abc"
        assert len(result["collected_data"]) == 0
    
    @patch('src.profiler.user_profiler.db_manager')
    @patch('src.profiler.user_profiler.LLMExtractor')
    async def test_generate_user_profile_success(self, mock_llm_extractor, mock_db):
        # Mock activities
        mock_activities = [
            Mock(
                platform="github",
                url="https://github.com/testuser",
                title="Profile",
                content="Test content",
                extracted_data={"type": "profile"},
                timestamp=datetime(2024, 1, 1)
            )
        ]
        mock_db.get_user_activities.return_value = mock_activities
        mock_db.save_user_profile = AsyncMock()
        
        # Mock LLM extractor
        mock_extractor = Mock()
        mock_extractor.generate_profile_summary = Mock(return_value={
            "personality_traits": ["analytical", "creative"],
            "interests": ["programming", "technology"]
        })
        mock_llm_extractor.return_value = mock_extractor
        
        result = await self.profiler.generate_user_profile("testuser")
        
        assert result["user_id"] == "testuser"
        assert "activity_summary" in result
        assert "ai_analysis" in result
        assert result["activity_summary"]["total_activities"] == 1
        assert "personality_traits" in result["ai_analysis"]
    
    async def test_generate_user_profile_no_activities(self):
        with patch('src.profiler.user_profiler.db_manager') as mock_db:
            mock_db.get_user_activities.return_value = []
            
            result = await self.profiler.generate_user_profile("testuser")
            
            assert result["user_id"] == "testuser"
            assert "error" in result
            assert "No activities found" in result["error"]
    
    def test_calculate_significance(self):
        activity = {
            "platform": "github",
            "extracted_data": {
                "followers": 1000,
                "repositories_count": 50
            }
        }
        
        significance = self.profiler._calculate_significance(activity)
        
        assert significance > 1.0  # Should be boosted by followers and repos
    
    def test_extract_timeline_highlights(self):
        activities = [
            {
                "platform": "github",
                "title": "New Repository",
                "timestamp": "2024-01-01T00:00:00",
                "extracted_data": {
                    "activity_type": "repository_creation",
                    "repositories_count": 10
                }
            },
            {
                "platform": "zhihu", 
                "title": "Answer Posted",
                "timestamp": "2024-01-02T00:00:00",
                "extracted_data": {
                    "activity_type": "answer",
                    "followers": 500
                }
            }
        ]
        
        highlights = self.profiler._extract_timeline_highlights(activities)
        
        assert len(highlights) <= 5
        assert all("significance" in h for h in highlights)
        assert all("date" in h for h in highlights)