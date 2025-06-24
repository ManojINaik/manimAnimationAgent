#!/bin/bash

# CircleCI Configuration Validation Script
# This script validates the CircleCI setup and dependencies

set -e  # Exit on error

echo "🔍 CircleCI Configuration Validation"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$1" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $2${NC}"
    elif [ "$1" = "ERROR" ]; then
        echo -e "${RED}❌ $2${NC}"
    else
        echo "ℹ️  $2"
    fi
}

# Check if CircleCI config exists
echo "🔧 Checking CircleCI Configuration..."
if [ -f ".circleci/config.yml" ]; then
    print_status "SUCCESS" "CircleCI config file found"
else
    print_status "ERROR" "CircleCI config file not found at .circleci/config.yml"
    exit 1
fi

# Validate YAML syntax
echo "📝 Validating YAML syntax..."
if command -v python3 &> /dev/null; then
    if python3 -c "import yaml; yaml.safe_load(open('.circleci/config.yml'))" 2>/dev/null; then
        print_status "SUCCESS" "YAML syntax is valid"
    else
        print_status "ERROR" "YAML syntax is invalid"
        exit 1
    fi
else
    print_status "WARNING" "Python3 not available - skipping YAML validation"
fi

# Check for required files
echo "📁 Checking required files..."
required_files=(
    "requirements-github-actions.txt"
    "scripts/check_video_queue.py"
    "scripts/github_video_renderer.py"
    "test_simple_manim.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "SUCCESS" "Required file found: $file"
    else
        print_status "ERROR" "Required file missing: $file"
    fi
done

# Check environment variables
echo "🌍 Checking environment variables..."
required_env_vars=(
    "APPWRITE_ENDPOINT"
    "APPWRITE_PROJECT_ID"
    "APPWRITE_API_KEY"
    "GEMINI_API_KEY"
)

optional_env_vars=(
    "OPENAI_API_KEY"
    "MEM0_API_KEY"
    "TAVILY_API_KEY"
    "ELEVENLABS_API_KEY"
)

for var in "${required_env_vars[@]}"; do
    if [ -n "${!var}" ]; then
        print_status "SUCCESS" "Required environment variable set: $var"
    else
        print_status "ERROR" "Required environment variable missing: $var"
    fi
done

for var in "${optional_env_vars[@]}"; do
    if [ -n "${!var}" ]; then
        print_status "SUCCESS" "Optional environment variable set: $var"
    else
        print_status "WARNING" "Optional environment variable missing: $var"
    fi
done

# Check system dependencies (if running on compatible system)
echo "🔧 Checking system dependencies..."
if command -v apt-get &> /dev/null; then
    dependencies=(
        "pkg-config"
        "libcairo2-dev"
        "ffmpeg"
        "graphviz"
        "graphviz-dev"
        "gcc"
        "g++"
        "build-essential"
    )
    
    for dep in "${dependencies[@]}"; do
        if dpkg -l | grep -q "^ii  $dep "; then
            print_status "SUCCESS" "System dependency installed: $dep"
        else
            print_status "WARNING" "System dependency missing: $dep (install with: sudo apt-get install $dep)"
        fi
    done
else
    print_status "WARNING" "Not on apt-based system - skipping system dependency check"
fi

# Check Python and pip
echo "🐍 Checking Python environment..."
if command -v python3.11 &> /dev/null; then
    print_status "SUCCESS" "Python 3.11 found: $(python3.11 --version)"
else
    print_status "ERROR" "Python 3.11 not found"
fi

if command -v pip &> /dev/null; then
    print_status "SUCCESS" "pip found: $(pip --version)"
else
    print_status "ERROR" "pip not found"
fi

# Test CircleCI CLI if available
echo "🔄 Checking CircleCI CLI..."
if command -v circleci &> /dev/null; then
    print_status "SUCCESS" "CircleCI CLI found: $(circleci version)"
    
    echo "🧪 Validating CircleCI config with CLI..."
    if circleci config validate .circleci/config.yml; then
        print_status "SUCCESS" "CircleCI configuration is valid"
    else
        print_status "ERROR" "CircleCI configuration validation failed"
    fi
else
    print_status "WARNING" "CircleCI CLI not found - install from: https://circleci.com/docs/local-cli/"
fi

# Check for common issues
echo "🔍 Checking for common issues..."

# Check if using correct requirements file
if grep -q "requirements-github-actions.txt" .circleci/config.yml; then
    print_status "SUCCESS" "Using correct requirements file (requirements-github-actions.txt)"
else
    print_status "ERROR" "Not using requirements-github-actions.txt in CircleCI config"
fi

# Check for GraphViz dependencies
if grep -q "graphviz-dev" .circleci/config.yml; then
    print_status "SUCCESS" "GraphViz development headers included"
else
    print_status "ERROR" "GraphViz development headers missing (needed for pygraphviz)"
fi

# Check for timeout configurations
if grep -q "no_output_timeout" .circleci/config.yml; then
    print_status "SUCCESS" "Timeout configurations found"
else
    print_status "WARNING" "No timeout configurations found"
fi

echo ""
echo "🎯 Validation Summary"
echo "===================="
echo "✅ Check the output above for any ERROR messages"
echo "⚠️  WARNING messages are optional but recommended to address"
echo "💡 Install missing dependencies before running CircleCI jobs"
echo ""
echo "📚 For setup instructions, see: CIRCLECI_SETUP.md"
echo "🔧 For API triggers, see: scripts/circleci_api_examples.md" 