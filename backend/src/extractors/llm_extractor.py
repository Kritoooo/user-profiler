import json
import openai
from typing import Dict, Any, List, Optional
from src.config import config

class LLMExtractor:
    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        openai.api_key = config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    def extract_structured_info(self, content: str, platform: str, url: str) -> Dict[str, Any]:
        prompt = self._build_extraction_prompt(content, platform, url)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from web content for user profiling."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                return json.loads(extracted_text)
            except json.JSONDecodeError:
                # If not valid JSON, return as structured text
                return self._parse_structured_text(extracted_text)
                
        except Exception as e:
            print(f"Error extracting with LLM: {str(e)}")
            return {"error": str(e), "raw_content": content[:500]}
    
    def _build_extraction_prompt(self, content: str, platform: str, url: str) -> str:
        return f"""
Extract key information from this {platform} profile/content for user profiling:

URL: {url}
Content: {content[:3000]}

Please extract and return a JSON object with the following information:
- username/display_name
- bio/description
- skills/interests (as array)
- activity_type (post, comment, profile, repository, etc.)
- activity_date (if available)
- key_metrics (followers, posts, stars, etc.)
- topics/tags mentioned
- any other relevant profile information

Return only valid JSON. If information is not available, omit the field or use null.
"""
    
    def _parse_structured_text(self, text: str) -> Dict[str, Any]:
        # Simple structured text parser as fallback
        result = {}
        lines = text.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Try to parse arrays
                if value.startswith('[') and value.endswith(']'):
                    try:
                        result[key] = json.loads(value)
                    except:
                        result[key] = value
                else:
                    result[key] = value
        
        return result
    
    def generate_profile_summary(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not activities:
            return {"summary": "No activities found"}
        
        # Prepare activity summary for LLM
        activity_summary = []
        for activity in activities[-20:]:  # Use last 20 activities
            summary_item = {
                "platform": activity.get("platform"),
                "type": activity.get("extracted_data", {}).get("activity_type", "unknown"),
                "date": activity.get("timestamp"),
                "content_preview": activity.get("content", "")[:100]
            }
            activity_summary.append(summary_item)
        
        prompt = f"""
Analyze these user activities and create a comprehensive user profile:

Activities: {json.dumps(activity_summary, indent=2)}

Generate a JSON profile with:
- personality_traits: array of inferred traits
- interests: array of main interests/topics
- activity_pattern: description of posting patterns
- technical_skills: array of technical skills (if applicable)
- social_presence: description of online presence
- engagement_style: how they interact online
- content_themes: main themes in their content

Return only valid JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating user profiles from digital footprint analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            profile_text = response.choices[0].message.content.strip()
            return json.loads(profile_text)
            
        except Exception as e:
            print(f"Error generating profile summary: {str(e)}")
            return {
                "error": str(e),
                "activity_count": len(activities),
                "platforms": list(set(a.get("platform") for a in activities))
            }