import pytest
import asyncio
from unittest.mock import Mock, patch
from src.collectors import GitHubCollector, ZhihuCollector, SearchEngineCollector

@pytest.mark.asyncio
class TestGitHubCollector:
    def setup_method(self):
        self.collector = GitHubCollector()
    
    def test_build_search_urls(self):
        urls = self.collector.build_search_urls("testuser")
        
        assert len(urls) == 4
        assert "https://github.com/testuser" in urls
        assert "https://github.com/testuser?tab=repositories" in urls
        assert "https://github.com/testuser?tab=followers" in urls
        assert "https://github.com/testuser?tab=following" in urls
    
    def test_extract_user_info_with_valid_markdown(self):
        markdown_content = """
        # TestUser
        **Bio:** Software Developer
        10 repositories
        100 followers
        50 following
        Created new-repo
        Updated old-repo
        """
        
        result = self.collector.extract_user_info(markdown_content, "https://github.com/testuser")
        
        assert result["type"] == "github_profile"
        assert result["username"] == "TestUser"
        assert result["bio"] == "Software Developer"
        assert result["repositories_count"] == 10
        assert result["followers"] == 100
        assert result["following"] == 50
        assert len(result["recent_activities"]) == 2
    
    def test_extract_user_info_with_empty_markdown(self):
        result = self.collector.extract_user_info("", "https://github.com/testuser")
        assert result is None
    
    @patch('src.collectors.base_collector.AsyncWebCrawler')
    async def test_collect_user_data_success(self, mock_crawler_class):
        mock_crawler = Mock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# TestUser\n10 repositories"
        mock_crawler.arun.return_value = mock_result
        
        results = await self.collector.collect_user_data("testuser")
        
        assert len(results) == 4  # 4 URLs
        assert all(result["platform"] == "github" for result in results)

@pytest.mark.asyncio
class TestZhihuCollector:
    def setup_method(self):
        self.collector = ZhihuCollector()
    
    def test_build_search_urls(self):
        urls = self.collector.build_search_urls("testuser")
        
        assert len(urls) == 3
        assert "https://www.zhihu.com/people/testuser" in urls
        assert "https://www.zhihu.com/people/testuser/answers" in urls
        assert "https://www.zhihu.com/people/testuser/articles" in urls
    
    def test_extract_user_info_with_valid_markdown(self):
        markdown_content = """
        # 测试用户
        **个人简介:** Python开发者
        1000 关注者
        50 个回答
        10 篇文章
        ## 如何学习Python
        ## Vue.js最佳实践
        """
        
        result = self.collector.extract_user_info(markdown_content, "https://www.zhihu.com/people/testuser")
        
        assert result["type"] == "zhihu_profile"
        assert result["display_name"] == "测试用户"
        assert result["description"] == "Python开发者"
        assert result["followers"] == 1000
        assert result["answers_count"] == 50
        assert result["articles_count"] == 10
        assert len(result["recent_posts"]) == 2

@pytest.mark.asyncio
class TestSearchEngineCollector:
    def setup_method(self):
        self.collector = SearchEngineCollector("google")
    
    def test_build_search_urls(self):
        urls = self.collector.build_search_urls("testuser")
        
        assert len(urls) == 5
        assert all("google.com/search" in url for url in urls)
        assert any("site:github.com" in url for url in urls)
        assert any("site:zhihu.com" in url for url in urls)
    
    def test_extract_user_info_with_search_results(self):
        markdown_content = """
        [TestUser on GitHub](https://github.com/testuser)
        [TestUser - Zhihu](https://www.zhihu.com/people/testuser)
        > Software developer with 5 years experience
        > Python and JavaScript expert
        """
        
        result = self.collector.extract_user_info(markdown_content, "https://google.com/search?q=testuser")
        
        assert result["type"] == "google_search_results"
        assert "relevant_links" in result
        assert len(result["relevant_links"]) == 2
        assert "snippets" in result
        assert len(result["snippets"]) == 2