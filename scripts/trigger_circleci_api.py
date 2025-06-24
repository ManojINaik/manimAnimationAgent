#!/usr/bin/env python3
"""
CircleCI API Trigger Script
Trigger CircleCI workflows programmatically via API
"""

import os
import sys
import json
import requests
import argparse
from typing import Optional, Dict, Any

class CircleCITrigger:
    def __init__(self, token: str, org_slug: str, project_slug: str):
        """
        Initialize CircleCI API client
        
        Args:
            token: CircleCI API token
            org_slug: Organization slug (e.g., 'gh/your-username')
            project_slug: Project slug (repository name)
        """
        self.token = token
        self.org_slug = org_slug
        self.project_slug = project_slug
        self.base_url = "https://circleci.com/api/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Circle-Token": token
        }
    
    def trigger_pipeline(
        self, 
        branch: str = "main",
        workflow: str = "ci-cd",
        video_id: Optional[str] = None,
        force_deploy: bool = False
    ) -> Dict[str, Any]:
        """
        Trigger a CircleCI pipeline
        
        Args:
            branch: Git branch to trigger on
            workflow: Workflow to run ('ci-cd' or 'video-rendering')
            video_id: Video ID for video rendering workflow
            force_deploy: Force deployment even on non-main branches
            
        Returns:
            API response dictionary
        """
        url = f"{self.base_url}/project/{self.org_slug}/{self.project_slug}/pipeline"
        
        # Build parameters
        parameters = {
            "workflow": workflow,
            "force_deploy": force_deploy
        }
        
        if video_id:
            parameters["video_id"] = video_id
        
        payload = {
            "branch": branch,
            "parameters": parameters
        }
        
        print(f"🚀 Triggering CircleCI pipeline...")
        print(f"   Branch: {branch}")
        print(f"   Workflow: {workflow}")
        if video_id:
            print(f"   Video ID: {video_id}")
        print(f"   Parameters: {json.dumps(parameters, indent=2)}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Pipeline triggered successfully!")
            print(f"   Pipeline ID: {result.get('id')}")
            print(f"   Pipeline Number: {result.get('number')}")
            print(f"   State: {result.get('state')}")
            
            # Generate CircleCI dashboard URL
            pipeline_url = f"https://app.circleci.com/pipelines/{self.org_slug}/{self.project_slug}/{result.get('number')}"
            print(f"   Dashboard: {pipeline_url}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to trigger pipeline: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            sys.exit(1)
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status by ID"""
        url = f"{self.base_url}/pipeline/{pipeline_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get pipeline status: {e}")
            return {}
    
    def list_recent_pipelines(self, limit: int = 10) -> Dict[str, Any]:
        """List recent pipelines for the project"""
        url = f"{self.base_url}/project/{self.org_slug}/{self.project_slug}/pipeline"
        params = {"page-token": "", "limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to list pipelines: {e}")
            return {}

def main():
    parser = argparse.ArgumentParser(description="Trigger CircleCI workflows via API")
    parser.add_argument("--token", required=True, help="CircleCI API token")
    parser.add_argument("--org", required=True, help="Organization slug (e.g., 'gh/username')")
    parser.add_argument("--project", required=True, help="Project slug (repository name)")
    parser.add_argument("--branch", default="main", help="Git branch to trigger on")
    parser.add_argument("--workflow", choices=["ci-cd", "video-rendering"], default="ci-cd", 
                       help="Workflow to trigger")
    parser.add_argument("--video-id", help="Video ID for video rendering workflow")
    parser.add_argument("--force-deploy", action="store_true", 
                       help="Force deployment even on non-main branches")
    parser.add_argument("--status", help="Get status of pipeline by ID")
    parser.add_argument("--list", action="store_true", help="List recent pipelines")
    
    args = parser.parse_args()
    
    # Initialize CircleCI client
    client = CircleCITrigger(args.token, args.org, args.project)
    
    if args.status:
        # Get pipeline status
        status = client.get_pipeline_status(args.status)
        print(json.dumps(status, indent=2))
    elif args.list:
        # List recent pipelines
        pipelines = client.list_recent_pipelines()
        print(json.dumps(pipelines, indent=2))
    else:
        # Trigger pipeline
        if args.workflow == "video-rendering" and not args.video_id:
            print("❌ Video ID is required for video-rendering workflow")
            sys.exit(1)
        
        client.trigger_pipeline(
            branch=args.branch,
            workflow=args.workflow,
            video_id=args.video_id,
            force_deploy=args.force_deploy
        )

if __name__ == "__main__":
    main() 