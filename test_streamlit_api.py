#!/usr/bin/env python3
"""
Test script for manimAnimationAgent Streamlit API
Usage: python test_streamlit_api.py
"""

import requests
import time
import json
import os
from typing import Dict, Any

class TheoremExplainClient:
    """Client for testing the manimAnimationAgent API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def generate_video(self, topic: str, context: str = "", max_scenes: int = 3) -> Dict[str, Any]:
        """Generate educational video"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "topic": topic,
                    "context": context,
                    "max_scenes": max_scenes
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def check_status(self, task_id: str) -> Dict[str, Any]:
        """Check task status"""
        try:
            response = requests.get(f"{self.base_url}/api/status/{task_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def wait_for_completion(self, task_id: str, timeout: int = 120) -> Dict[str, Any]:
        """Wait for task completion"""
        start_time = time.time()
        
        print(f"⏳ Waiting for task {task_id[:8]}... to complete")
        
        while time.time() - start_time < timeout:
            status = self.check_status(task_id)
            
            if "error" in status:
                return status
            
            print(f"   Status: {status['status']} - Progress: {status['progress']}% - {status['message']}")
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                return {"error": f"Task failed: {status.get('error', 'Unknown error')}"}
            
            time.sleep(3)
        
        return {"error": "Task did not complete within timeout"}

def test_api(base_url: str):
    """Test the API functionality"""
    print("🧪 Testing manimAnimationAgent API")
    print(f"🔗 Base URL: {base_url}")
    print("=" * 60)
    
    client = TheoremExplainClient(base_url)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    health = client.health_check()
    if "error" in health:
        print(f"❌ Health check failed: {health['error']}")
        return False
    else:
        print(f"✅ Health check passed")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Demo Mode: {health.get('demo_mode', 'unknown')}")
        print(f"   Dependencies: {health.get('dependencies_available', 'unknown')}")
    
    # Test 2: API Stats
    print("\n2️⃣ Testing API Stats...")
    stats = client.get_stats()
    if "error" in stats:
        print(f"⚠️ Stats failed: {stats['error']}")
    else:
        print(f"✅ Stats retrieved")
        print(f"   Total tasks: {stats.get('total_tasks', 0)}")
        print(f"   Demo mode: {stats.get('demo_mode', 'unknown')}")
    
    # Test 3: Video Generation
    print("\n3️⃣ Testing Video Generation...")
    
    test_cases = [
        {
            "topic": "Pythagorean Theorem",
            "context": "High school mathematics level",
            "max_scenes": 3
        },
        {
            "topic": "Newton's Laws of Motion",
            "context": "Introductory physics",
            "max_scenes": 2
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test Case {i}: {test_case['topic']}")
        
        # Generate video
        result = client.generate_video(**test_case)
        
        if not result.get("success", False):
            print(f"   ❌ Generation failed: {result.get('error', 'Unknown error')}")
            continue
        
        task_id = result.get("task_id")
        if not task_id:
            print(f"   ❌ No task ID returned")
            continue
        
        print(f"   ✅ Task created: {task_id[:8]}...")
        
        # Wait for completion
        final_result = client.wait_for_completion(task_id, timeout=60)
        
        if "error" in final_result:
            print(f"   ❌ Task failed: {final_result['error']}")
        else:
            print(f"   ✅ Task completed successfully!")
            
            # Print result summary
            if final_result.get("result"):
                result_data = final_result["result"]
                print(f"   📊 Result Summary:")
                print(f"      Topic: {result_data.get('topic', 'N/A')}")
                print(f"      Scenes: {result_data.get('scenes_planned', 'N/A')}")
                print(f"      Success: {result_data.get('success', 'N/A')}")
                
                if result_data.get('demo_note'):
                    print(f"      Note: {result_data['demo_note']}")
    
    print("\n" + "=" * 60)
    print("🎉 API testing completed!")
    
    # Final stats
    print("\n📊 Final Stats...")
    final_stats = client.get_stats()
    if "error" not in final_stats:
        print(f"   Total tasks processed: {final_stats.get('total_tasks', 0)}")
        if final_stats.get('status_breakdown'):
            for status, count in final_stats['status_breakdown'].items():
                print(f"   {status}: {count}")
    
    return True

def main():
    """Main test function"""
    # Test configurations
    test_configs = [
        {
            "name": "Local Streamlit (default port)",
            "url": "http://localhost:8501"
        },
        {
            "name": "Local FastAPI (default port)",
            "url": "http://localhost:8000"
        }
    ]
    
    # Check for custom URL
    custom_url = os.getenv("TEST_API_URL")
    if custom_url:
        test_configs.insert(0, {
            "name": "Custom URL",
            "url": custom_url
        })
    
    print("🎓 manimAnimationAgent - API Test Suite")
    print("=" * 60)
    
    # Test each configuration
    for config in test_configs:
        print(f"\n🔍 Testing: {config['name']}")
        print(f"🔗 URL: {config['url']}")
        
        try:
            success = test_api(config['url'])
            if success:
                print(f"✅ {config['name']} - All tests passed!")
                break
            else:
                print(f"❌ {config['name']} - Some tests failed")
        except KeyboardInterrupt:
            print("\n⏹️ Testing interrupted by user")
            break
        except Exception as e:
            print(f"❌ {config['name']} - Unexpected error: {e}")
        
        print("\n" + "-" * 40)
    
    print("\n🏁 Testing complete!")
    print("\nℹ️ Usage tips:")
    print("   - Set TEST_API_URL environment variable to test custom endpoints")
    print("   - For Streamlit: streamlit run streamlit_app.py")
    print("   - For FastAPI: python api_server.py")
    print("   - For deployed app: TEST_API_URL=https://your-app.streamlit.app python test_streamlit_api.py")

if __name__ == "__main__":
    main() 