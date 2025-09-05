import re
from datetime import datetime
from typing import List, Dict, Any
from .base_collector import BaseCollector

class SearchEngineCollector(BaseCollector):
    def __init__(self, search_engine: str):
        super().__init__(f"search_{search_engine}")
        self.search_engine = search_engine
    
    def build_search_urls(self, user_id: str) -> List[str]:
        search_queries = [
            f'"{user_id}" site:github.com',
            f'"{user_id}" site:zhihu.com', 
            f'"{user_id}" site:xiaohongshu.com',
            f'"{user_id}" blog',
            f'"{user_id}" portfolio'
        ]
        
        urls = []
        for query in search_queries:
            if self.search_engine == "google":
                urls.append(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            elif self.search_engine == "bing":
                urls.append(f"https://www.bing.com/search?q={query.replace(' ', '+')}")
            elif self.search_engine == "baidu":
                urls.append(f"https://www.baidu.com/s?wd={query.replace(' ', '+')}")
        
        return urls
    
    def extract_user_info(self, markdown_content: str, url: str) -> Dict[str, Any]:
        info = {
            "type": f"{self.search_engine}_search_results",
            "timestamp": datetime.now().isoformat(),
            "search_url": url
        }
        
        # Extract search result links
        link_patterns = [
            r'\[([^\]]+)\]\((https?://[^\)]+)\)',  # Markdown links
            r'(https?://[^\s]+)',  # Direct URLs
        ]
        
        found_links = []
        for pattern in link_patterns:
            matches = re.findall(pattern, markdown_content)
            found_links.extend(matches)
        
        # Filter relevant links
        relevant_domains = ["github.com", "zhihu.com", "xiaohongshu.com", "blog", "portfolio"]
        relevant_links = []
        
        for link in found_links:
            link_url = link[1] if isinstance(link, tuple) else link
            if any(domain in link_url.lower() for domain in relevant_domains):
                relevant_links.append({
                    "title": link[0] if isinstance(link, tuple) else "No title",
                    "url": link_url
                })
        
        if relevant_links:
            info["relevant_links"] = relevant_links[:10]  # Limit to 10 results
            
        # Extract snippets
        snippet_matches = re.findall(r'>\s*([^<\n]{50,200})', markdown_content)
        if snippet_matches:
            info["snippets"] = snippet_matches[:5]
        
        return info if "relevant_links" in info or "snippets" in info else None