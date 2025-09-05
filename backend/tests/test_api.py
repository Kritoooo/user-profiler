import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.api.main import app

class TestAPI:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "User Profiler API"
    
    def test_health_check(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_crawl_user_endpoint(self):
        crawl_data = {
            "user_id": "testuser",
            "platforms": ["github"],
            "search_engines": ["google"]
        }
        
        response = self.client.post("/crawl", json=crawl_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "testuser"
        assert data["platforms"] == ["github"]
        assert "Started crawling data for user" in data["message"]
    
    def test_crawl_user_invalid_id(self):
        crawl_data = {
            "user_id": "",
            "platforms": ["github"],
            "search_engines": ["google"]
        }
        
        response = self.client.post("/crawl", json=crawl_data)
        assert response.status_code == 400
        assert "Invalid user_id" in response.json()["detail"]
    
    @patch('src.api.main.db_manager.get_user_activities')
    def test_get_user_activities(self, mock_get_activities):
        mock_activities = [
            Mock(
                id=1,
                user_id="testuser",
                platform="github",
                url="https://github.com/testuser",
                title="Profile",
                content="Test content",
                extracted_data={"type": "profile"},
                timestamp="2024-01-01T00:00:00"
            )
        ]
        mock_get_activities.return_value = mock_activities
        
        response = self.client.get("/users/testuser/activities")
        assert response.status_code == 200
    
    @patch('src.api.main.db_manager.get_timeline_data')
    def test_get_user_timeline(self, mock_get_timeline):
        mock_timeline = [
            {
                "date": "2024-01-01",
                "activities": [
                    {
                        "id": 1,
                        "platform": "github",
                        "title": "Profile",
                        "timestamp": "2024-01-01T00:00:00"
                    }
                ]
            }
        ]
        mock_get_timeline.return_value = mock_timeline
        
        response = self.client.get("/users/testuser/timeline")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "testuser"
        assert len(data["timeline"]) == 1
    
    @patch('src.api.main.db_manager.get_user_profile')
    def test_get_user_profile_not_found(self, mock_get_profile):
        mock_get_profile.return_value = None
        
        response = self.client.get("/users/nonexistent/profile")
        assert response.status_code == 404
        assert "Profile not found" in response.json()["detail"]
    
    @patch('src.api.main.db_manager.get_user_activities')
    def test_generate_profile_no_activities(self, mock_get_activities):
        mock_get_activities.return_value = []
        
        response = self.client.post("/users/testuser/profile/generate")
        assert response.status_code == 404
        assert "No activities found" in response.json()["detail"]