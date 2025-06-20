#!/usr/bin/env python3
"""
Setup GitHub Actions Delegation for Video Rendering

This script helps configure the environment for delegating video rendering to GitHub Actions
instead of processing videos locally.
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check current environment configuration"""
    print("🔍 Checking GitHub Actions Delegation Setup")
    print("=" * 50)
    
    # Check Appwrite configuration
    appwrite_endpoint = os.getenv('APPWRITE_ENDPOINT')
    appwrite_project = os.getenv('APPWRITE_PROJECT_ID') 
    appwrite_key = os.getenv('APPWRITE_API_KEY')
    
    print("📊 Appwrite Configuration:")
    print(f"  APPWRITE_ENDPOINT: {'✅ Set' if appwrite_endpoint else '❌ Missing'}")
    print(f"  APPWRITE_PROJECT_ID: {'✅ Set' if appwrite_project else '❌ Missing'}")
    print(f"  APPWRITE_API_KEY: {'✅ Set' if appwrite_key else '❌ Missing'}")
    
    # Check GitHub configuration
    github_token = os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    
    print("\n🐙 GitHub Configuration:")
    print(f"  GITHUB_TOKEN: {'✅ Set' if github_token else '❌ Missing (optional for scheduled processing)'}")
    print(f"  GITHUB_REPO: {'✅ Set' if github_repo else '❌ Missing (optional for scheduled processing)'}")
    
    # Check if delegation is properly configured
    delegation_ready = bool(appwrite_endpoint and appwrite_project and appwrite_key)
    
    print(f"\n🚀 GitHub Actions Delegation Status:")
    if delegation_ready:
        print("✅ Ready for GitHub Actions delegation!")
        if github_token and github_repo:
            print("✅ Immediate triggering enabled")
        else:
            print("⏰ Will use scheduled processing (every 5 minutes)")
    else:
        print("❌ Not ready - Missing Appwrite configuration")
    
    return delegation_ready

def show_setup_instructions():
    """Show setup instructions for GitHub Actions delegation"""
    print("\n📋 Setup Instructions for GitHub Actions Delegation")
    print("=" * 55)
    
    print("\n1. 🗃️ Appwrite Configuration (Required):")
    print("   Set these environment variables:")
    print("   - APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1")
    print("   - APPWRITE_PROJECT_ID=your_project_id")
    print("   - APPWRITE_API_KEY=your_api_key")
    
    print("\n2. 🐙 GitHub Configuration (Optional - for immediate triggering):")
    print("   - GITHUB_TOKEN=your_github_personal_access_token")
    print("   - GITHUB_REPO=username/repository-name")
    
    print("\n3. 🔧 How to Set Environment Variables (Windows):")
    print("   # For current session:")
    print("   $env:APPWRITE_ENDPOINT = \"https://cloud.appwrite.io/v1\"")
    print("   $env:APPWRITE_PROJECT_ID = \"your_project_id\"")
    print("   $env:APPWRITE_API_KEY = \"your_api_key\"")
    print("   ")
    print("   # Optional for immediate triggering:")
    print("   $env:GITHUB_TOKEN = \"your_github_token\"")
    print("   $env:GITHUB_REPO = \"username/repo\"")
    
    print("\n4. 🎯 How It Works:")
    print("   ✅ Your API server creates video records in Appwrite")
    print("   ✅ GitHub Actions picks up videos and renders them")
    print("   ✅ No local Manim rendering = No local errors!")
    print("   ✅ Frontend gets real-time updates via Appwrite subscriptions")
    
    print("\n5. 🔄 Processing Modes:")
    print("   - Immediate: If GITHUB_TOKEN/GITHUB_REPO set")
    print("   - Scheduled: Every 5 minutes via GitHub Actions cron")

def test_appwrite_connection():
    """Test Appwrite connection"""
    try:
        from src.core.appwrite_integration import AppwriteVideoManager
        
        print("\n🧪 Testing Appwrite Connection...")
        manager = AppwriteVideoManager()
        
        if manager.enabled:
            print("✅ Appwrite connection successful!")
            return True
        else:
            print("❌ Appwrite connection failed - check credentials")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Main function"""
    print("🎬 manimAnimationAgent - GitHub Actions Delegation Setup")
    print("=" * 60)
    
    # Check current environment
    is_ready = check_environment()
    
    # Test Appwrite connection if configured
    if is_ready:
        test_appwrite_connection()
    
    # Show setup instructions
    show_setup_instructions()
    
    print("\n" + "=" * 60)
    if is_ready:
        print("🎉 Your setup is ready for GitHub Actions delegation!")
        print("   Videos will be processed in the cloud, not locally.")
    else:
        print("⚠️  Complete the Appwrite setup to enable delegation.")
        print("   Currently videos will run in demo mode.")

if __name__ == "__main__":
    main() 