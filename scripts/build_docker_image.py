#!/usr/bin/env python3
"""
Docker Image Build and Test Script

This script helps build and test the optimized Docker image locally
before deploying to GitHub Container Registry.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, capture_output=False):
    """Run a shell command and return the result."""
    print(f"🔄 Running: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, ""
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, ""

def build_image():
    """Build the Docker image."""
    print("\n🏗️  Building Docker image...")
    start_time = time.time()
    
    success, _ = run_command("docker build -t manim-animation-agent .")
    
    if success:
        build_time = time.time() - start_time
        print(f"✅ Docker image built successfully in {build_time:.1f} seconds")
        return True
    else:
        print("❌ Docker image build failed")
        return False

def test_image():
    """Test the Docker image with key dependency imports."""
    print("\n🧪 Testing Docker image...")
    
    # Test Python version
    success, output = run_command(
        'docker run --rm manim-animation-agent python3.11 --version',
        capture_output=True
    )
    if success:
        print(f"✅ Python: {output}")
    else:
        print("❌ Python test failed")
        return False
    
    # Test key dependencies
    test_script = """
import sys
print(f'Python: {sys.version}')

test_results = []

# Test Manim
try:
    import manim
    test_results.append(f'✅ Manim: {manim.__version__}')
except Exception as e:
    test_results.append(f'❌ Manim: {e}')

# Test NumPy
try:
    import numpy as np
    test_results.append(f'✅ NumPy: {np.__version__}')
except Exception as e:
    test_results.append(f'❌ NumPy: {e}')

# Test Cairo
try:
    import cairo
    test_results.append('✅ Cairo: Import successful')
except Exception as e:
    test_results.append(f'❌ Cairo: {e}')

# Test OpenCV
try:
    import cv2
    test_results.append(f'✅ OpenCV: {cv2.__version__}')
except Exception as e:
    test_results.append(f'❌ OpenCV: {e}')

# Test FFmpeg Python
try:
    import ffmpeg
    test_results.append('✅ FFmpeg-Python: Import successful')
except Exception as e:
    test_results.append(f'❌ FFmpeg-Python: {e}')

# Test audio libraries
try:
    import pydub
    test_results.append('✅ Pydub: Import successful')
except Exception as e:
    test_results.append(f'❌ Pydub: {e}')

for result in test_results:
    print(result)
"""
    
    success, output = run_command(
        f'docker run --rm manim-animation-agent python3.11 -c "{test_script}"',
        capture_output=True
    )
    
    if success:
        print("Test Results:")
        for line in output.split('\n'):
            print(f"  {line}")
        
        # Check if any tests failed
        if '❌' in output:
            print("⚠️  Some dependency tests failed")
            return False
        else:
            print("✅ All dependency tests passed")
            return True
    else:
        print("❌ Dependency test failed")
        return False

def check_image_size():
    """Check the size of the built image."""
    print("\n📏 Checking image size...")
    
    success, output = run_command(
        'docker images manim-animation-agent --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}"',
        capture_output=True
    )
    
    if success:
        print("Image Information:")
        for line in output.split('\n'):
            print(f"  {line}")
    else:
        print("❌ Could not get image size information")

def interactive_test():
    """Run interactive test session."""
    print("\n🔧 Starting interactive test session...")
    print("You can now test the image interactively.")
    print("Type 'exit' to return to this script.")
    
    run_command("docker run -it --rm manim-animation-agent /bin/bash")

def cleanup():
    """Clean up Docker resources."""
    print("\n🧹 Cleaning up...")
    
    # Remove dangling images
    run_command("docker image prune -f")
    print("✅ Cleaned up dangling images")

def main():
    """Main function."""
    print("🐳 Docker Image Build and Test Script")
    print("="*50)
    
    # Check if Docker is available
    success, _ = run_command("docker --version", capture_output=True)
    if not success:
        print("❌ Docker is not available. Please install Docker first.")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("Dockerfile").exists():
        print("❌ Dockerfile not found. Please run this script from the project root.")
        sys.exit(1)
    
    if not Path("requirements-github-actions.txt").exists():
        print("❌ requirements-github-actions.txt not found.")
        sys.exit(1)
    
    # Build the image
    if not build_image():
        sys.exit(1)
    
    # Test the image
    if not test_image():
        print("⚠️  Image built but tests failed. Consider fixing issues before deployment.")
    
    # Check image size
    check_image_size()
    
    # Ask for interactive testing
    while True:
        choice = input("\n🤔 Would you like to run interactive tests? (y/n/q): ").lower().strip()
        if choice in ['y', 'yes']:
            interactive_test()
        elif choice in ['n', 'no']:
            break
        elif choice in ['q', 'quit']:
            break
        else:
            print("Please enter 'y', 'n', or 'q'")
    
    # Cleanup
    cleanup_choice = input("\n🧹 Clean up dangling Docker images? (y/n): ").lower().strip()
    if cleanup_choice in ['y', 'yes']:
        cleanup()
    
    print("\n✨ Docker image build and test completed!")
    print("\nNext steps:")
    print("1. Commit Dockerfile and related files to your repository")
    print("2. The Docker build workflow will automatically create the image")
    print("3. The video renderer workflow will use the optimized container")
    print("4. Enjoy ~95% faster GitHub Actions setup times! 🚀")

if __name__ == "__main__":
    main() 