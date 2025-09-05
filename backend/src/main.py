#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path

# Add project root and src to Python path  
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# Change to backend directory
os.chdir(project_root)

from src.storage.database import db_manager
from src.profiler.user_profiler import user_profiler

async def main():
    """Main entry point for the application"""
    
    # Initialize database
    print("Initializing database...")
    await db_manager.init_db()
    print("Database initialized successfully!")
    
    # Example usage
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        print(f"Running example crawl for user: {user_id}")
        
        try:
            # Crawl user data
            results = await user_profiler.crawl_user_data(
                user_id=user_id,
                platforms=["github"],  # Start with GitHub only for testing
                search_engines=["google"],
                use_llm=False  # Disable LLM for testing without API key
            )
            
            print(f"Crawl completed. Found {len(results['collected_data'])} activities")
            
            # Generate profile
            profile = await user_profiler.generate_user_profile(user_id)
            print(f"Profile generated for {user_id}")
            print(f"Total activities: {profile['activity_summary']['total_activities']}")
            
        except Exception as e:
            print(f"Error during crawl: {str(e)}")
    
    else:
        print("Usage: python src/main.py <user_id>")
        print("Or run the API server with: uvicorn src.api.main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    asyncio.run(main())