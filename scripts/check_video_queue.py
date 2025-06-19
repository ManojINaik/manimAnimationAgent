#!/usr/bin/env python3
"""
Check Appwrite database for videos that need rendering
"""

import os
import sys
import json
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query

def check_video_queue():
    """Check for videos in queue and set GitHub Actions output"""
    try:
        # Initialize Appwrite client
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        databases = Databases(client)
        
        # Query for videos that need rendering
        result = databases.list_documents(
            database_id="video_metadata",
            collection_id="videos",
            queries=[
                Query.equal("status", ["queued_for_render", "ready_for_render"]),
                Query.limit(10)  # Process up to 10 videos at a time
            ]
        )
        
        videos = result['documents']
        print(f"Found {len(videos)} videos in queue")
        
        if videos:
            # Set GitHub Actions output (if running in GitHub Actions)
            if 'GITHUB_OUTPUT' in os.environ:
                with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                    f.write(f"videos_found=true\n")
                    f.write(f"video_count={len(videos)}\n")
                    # Pass video IDs as JSON
                    video_ids = [video['$id'] for video in videos]
                    f.write(f"video_ids={json.dumps(video_ids)}\n")
            
            print("Videos found - will proceed to rendering")
            return True
        else:
            # No videos to process
            if 'GITHUB_OUTPUT' in os.environ:
                with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                    f.write(f"videos_found=false\n")
            
            print("No videos in queue")
            return False
            
    except Exception as e:
        print(f"Error checking video queue: {str(e)}")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"videos_found=false\n")
        return False

if __name__ == "__main__":
    check_video_queue() 