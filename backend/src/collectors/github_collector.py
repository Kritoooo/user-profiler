import re
from datetime import datetime
from typing import List, Dict, Any
from .base_collector import BaseCollector

class GitHubCollector(BaseCollector):
    def __init__(self):
        super().__init__("github")
    
    def build_search_urls(self, user_id: str) -> List[str]:
        base_url = self.config["base_url"]
        return [
            f"{base_url}/{user_id}",
            f"{base_url}/{user_id}?tab=repositories",
            f"{base_url}/{user_id}?tab=followers",
            f"{base_url}/{user_id}?tab=following"
        ]
    
    def extract_user_info(self, markdown_content: str, url: str) -> Dict[str, Any]:
        info = {
            "type": "github_profile",
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract username from markdown
        username_match = re.search(r'# ([^\n]+)', markdown_content)
        if username_match:
            info["username"] = username_match.group(1).strip()
        
        # Extract bio
        bio_match = re.search(r'\*\*Bio:\*\*\s*([^\n]+)', markdown_content)
        if bio_match:
            info["bio"] = bio_match.group(1).strip()
        
        # Extract repositories count
        repos_match = re.search(r'(\d+)\s*repositories', markdown_content, re.IGNORECASE)
        if repos_match:
            info["repositories_count"] = int(repos_match.group(1))
        
        # Extract followers/following
        followers_match = re.search(r'(\d+)\s*followers', markdown_content, re.IGNORECASE)
        if followers_match:
            info["followers"] = int(followers_match.group(1))
            
        following_match = re.search(r'(\d+)\s*following', markdown_content, re.IGNORECASE)
        if following_match:
            info["following"] = int(following_match.group(1))
        
        # Extract recent activity
        activity_matches = re.findall(r'(Created|Updated|Pushed to)\s+([^\n]+)', markdown_content)
        if activity_matches:
            info["recent_activities"] = [
                {"action": match[0], "target": match[1]} 
                for match in activity_matches[:5]
            ]
        
        return info if len(info) > 2 else None  # Return None if no meaningful data extracted