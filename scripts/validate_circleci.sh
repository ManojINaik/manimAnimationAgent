#!/bin/bash

# CircleCI Configuration Validation Script
# This script validates the CircleCI configuration

set -e

echo "🔍 Validating CircleCI configuration..."

# Check if CircleCI CLI is installed
if ! command -v circleci &> /dev/null; then
    echo "❌ CircleCI CLI not found. Installing..."
    
    # Install CircleCI CLI based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/master/install.sh | bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install circleci
    else
        echo "Please install CircleCI CLI manually: https://circleci.com/docs/local-cli/"
        exit 1
    fi
fi

# Validate the configuration
echo "📋 Validating .circleci/config.yml..."

if circleci config validate .circleci/config.yml; then
    echo "✅ CircleCI configuration is valid!"
else
    echo "❌ CircleCI configuration has errors. Please fix them before proceeding."
    exit 1
fi

# Process the configuration
echo "🔧 Processing configuration..."
circleci config process .circleci/config.yml > .circleci/processed-config.yml

echo "📄 Processed configuration saved to .circleci/processed-config.yml"

# Check for common issues
echo "🔍 Checking for common issues..."

# Check if required environment variables are documented
if grep -q "APPWRITE_ENDPOINT" .circleci/config.yml && grep -q "GEMINI_API_KEY" .circleci/config.yml; then
    echo "✅ Required environment variables are referenced"
else
    echo "⚠️  Some required environment variables might be missing"
fi

# Check for caching
if grep -q "restore_cache" .circleci/config.yml && grep -q "save_cache" .circleci/config.yml; then
    echo "✅ Caching is configured"
else
    echo "⚠️  Caching might not be properly configured"
fi

# Check for workflows
workflow_count=$(grep -c "workflows:" .circleci/config.yml || echo "0")
if [ "$workflow_count" -gt 0 ]; then
    echo "✅ Workflows are configured ($workflow_count found)"
else
    echo "⚠️  No workflows found"
fi

echo ""
echo "🎉 CircleCI configuration validation complete!"
echo ""
echo "Next steps:"
echo "1. Commit the configuration to your repository"
echo "2. Set up environment variables in CircleCI project settings"
echo "3. Trigger your first build"
echo ""
echo "Documentation: CIRCLECI_SETUP.md" 