import re
from datetime import datetime
from typing import List, Dict, Any
from .base_collector import BaseCollector

class ZhihuCollector(BaseCollector):
    def __init__(self):
        super().__init__("zhihu")
    
    def build_search_urls(self, user_id: str) -> List[str]:
        base_url = self.config["base_url"]
        return [
            f"{base_url}/people/{user_id}",
            f"{base_url}/people/{user_id}/answers",
            f"{base_url}/people/{user_id}/articles"
        ]
    
    def extract_user_info(self, markdown_content: str, url: str) -> Dict[str, Any]:
        info = {
            "type": "zhihu_profile", 
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract display name
        name_match = re.search(r'# ([^\n]+)', markdown_content)
        if name_match:
            info["display_name"] = name_match.group(1).strip()
        
        # Extract description/headline
        desc_match = re.search(r'\*\*个人简介:\*\*\s*([^\n]+)', markdown_content)
        if not desc_match:
            desc_match = re.search(r'\*\*Headline:\*\*\s*([^\n]+)', markdown_content)
        if desc_match:
            info["description"] = desc_match.group(1).strip()
        
        # Extract follower counts
        followers_match = re.search(r'(\d+)\s*关注者', markdown_content)
        if not followers_match:
            followers_match = re.search(r'(\d+)\s*followers', markdown_content, re.IGNORECASE)
        if followers_match:
            info["followers"] = int(followers_match.group(1))
        
        # Extract answer/article counts
        answers_match = re.search(r'(\d+)\s*个回答', markdown_content)
        if not answers_match:
            answers_match = re.search(r'(\d+)\s*answers', markdown_content, re.IGNORECASE)
        if answers_match:
            info["answers_count"] = int(answers_match.group(1))
            
        articles_match = re.search(r'(\d+)\s*篇文章', markdown_content)
        if not articles_match:
            articles_match = re.search(r'(\d+)\s*articles', markdown_content, re.IGNORECASE)
        if articles_match:
            info["articles_count"] = int(articles_match.group(1))
        
        # Extract recent posts titles
        title_matches = re.findall(r'## ([^\n]+)', markdown_content)
        if title_matches:
            info["recent_posts"] = title_matches[:5]
        
        return info if len(info) > 2 else None