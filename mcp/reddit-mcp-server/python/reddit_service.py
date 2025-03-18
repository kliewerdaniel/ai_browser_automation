#!/usr/bin/env python3
import json
import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("reddit_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)

# Add the parent directory to Python path to import reddit_fetch module
backend_dir = Path(__file__).resolve().parents[3] / 'backend'
sys.path.append(str(backend_dir))

try:
    from reddit_fetch import RedditMonitor
    logging.info("Successfully imported RedditMonitor")
except ImportError as e:
    logging.error(f"Failed to import RedditMonitor: {e}")
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        error_msg = {"error": "Invalid arguments. Expected: method and params"}
        print(json.dumps(error_msg))
        sys.exit(1)
    
    method = sys.argv[1]
    try:
        params = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        error_msg = {"error": f"Invalid JSON parameters: {e}"}
        print(json.dumps(error_msg))
        sys.exit(1)
    
    logging.info(f"Called with method: {method}, params: {params}")
    
    try:
        # Initialize Reddit monitor
        monitor = RedditMonitor()
        if not monitor.username:
            error_msg = {"error": "Reddit authentication failed"}
            print(json.dumps(error_msg))
            sys.exit(1)
        
        # Process the request
        if method == "fetch_posts":
            limit = params.get("limit", 10)
            subreddit = params.get("subreddit")
            # TODO: Add subreddit filtering when enhanced
            result = monitor.fetch_recent_posts(limit=limit)
            print(json.dumps(result))
            
        elif method == "fetch_comments":
            limit = params.get("limit", 10)
            subreddit = params.get("subreddit")
            # TODO: Add subreddit filtering when enhanced
            result = monitor.fetch_recent_comments(limit=limit)
            print(json.dumps(result))
            
        elif method == "fetch_activity":
            limit = params.get("limit", 20)
            include_posts = params.get("include_posts", True)
            include_comments = params.get("include_comments", True)
            
            if include_posts and include_comments:
                result = monitor.fetch_all_recent_activity(limit=limit)
            elif include_posts:
                result = monitor.fetch_recent_posts(limit=limit)
            elif include_comments:
                result = monitor.fetch_recent_comments(limit=limit)
            else:
                result = []
                
            print(json.dumps(result))
            
        elif method == "search_reddit":
            # Note: This is a placeholder for future implementation
            # The current RedditMonitor doesn't have search functionality
            error_msg = {"error": "Search functionality not yet implemented"}
            print(json.dumps(error_msg))
            sys.exit(1)
            
        else:
            error_msg = {"error": f"Unknown method: {method}"}
            print(json.dumps(error_msg))
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        error_msg = {"error": f"Error processing request: {str(e)}"}
        print(json.dumps(error_msg))
        sys.exit(1)

if __name__ == "__main__":
    main()
