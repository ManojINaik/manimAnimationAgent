#!/bin/bash

# CircleCI API Trigger Script (Bash)
# Quick script to trigger CircleCI workflows via API

set -e

# Configuration
CIRCLECI_TOKEN="${CIRCLECI_TOKEN:-}"
ORG_SLUG="${CIRCLECI_ORG:-gh/your-username}"  # e.g., gh/username
PROJECT_SLUG="${CIRCLECI_PROJECT:-manimAnimationAgent}"  # repository name
BRANCH="${CIRCLECI_BRANCH:-main}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Trigger CircleCI workflows via API"
    echo ""
    echo "Options:"
    echo "  -t, --token TOKEN       CircleCI API token (or set CIRCLECI_TOKEN env var)"
    echo "  -o, --org ORG          Organization slug (default: $ORG_SLUG)"
    echo "  -p, --project PROJECT  Project slug (default: $PROJECT_SLUG)"
    echo "  -b, --branch BRANCH    Git branch (default: $BRANCH)"
    echo "  -w, --workflow TYPE    Workflow type: ci-cd or video-rendering (default: ci-cd)"
    echo "  -v, --video-id ID      Video ID for video rendering workflow"
    echo "  -f, --force-deploy     Force deployment on any branch"
    echo "  -s, --status ID        Get pipeline status by ID"
    echo "  -l, --list             List recent pipelines"
    echo "  -h, --help             Show this help"
    echo ""
    echo "Examples:"
    echo "  # Trigger CI/CD pipeline"
    echo "  $0 --token YOUR_TOKEN --workflow ci-cd"
    echo ""
    echo "  # Trigger video rendering"
    echo "  $0 --token YOUR_TOKEN --workflow video-rendering --video-id abc123"
    echo ""
    echo "  # Get pipeline status"
    echo "  $0 --token YOUR_TOKEN --status pipeline-id-here"
}

trigger_pipeline() {
    local token="$1"
    local org="$2" 
    local project="$3"
    local branch="$4"
    local workflow="$5"
    local video_id="$6"
    local force_deploy="$7"
    
    local url="https://circleci.com/api/v2/project/$org/$project/pipeline"
    
    # Build parameters JSON
    local params='{"workflow":"'$workflow'","force_deploy":'$force_deploy'}'
    if [[ -n "$video_id" ]]; then
        params='{"workflow":"'$workflow'","video_id":"'$video_id'","force_deploy":'$force_deploy'}'
    fi
    
    local payload='{"branch":"'$branch'","parameters":'$params'}'
    
    echo -e "${BLUE}🚀 Triggering CircleCI pipeline...${NC}"
    echo -e "   Branch: ${YELLOW}$branch${NC}"
    echo -e "   Workflow: ${YELLOW}$workflow${NC}"
    if [[ -n "$video_id" ]]; then
        echo -e "   Video ID: ${YELLOW}$video_id${NC}"
    fi
    echo -e "   Parameters: $params"
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Circle-Token: $token" \
        -d "$payload" \
        "$url")
    
    if [[ $? -eq 0 ]]; then
        local pipeline_id=$(echo "$response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        local pipeline_number=$(echo "$response" | grep -o '"number":[0-9]*' | cut -d':' -f2)
        local state=$(echo "$response" | grep -o '"state":"[^"]*"' | cut -d'"' -f4)
        
        echo -e "${GREEN}✅ Pipeline triggered successfully!${NC}"
        echo -e "   Pipeline ID: ${YELLOW}$pipeline_id${NC}"
        echo -e "   Pipeline Number: ${YELLOW}$pipeline_number${NC}"
        echo -e "   State: ${YELLOW}$state${NC}"
        echo -e "   Dashboard: ${BLUE}https://app.circleci.com/pipelines/$org/$project/$pipeline_number${NC}"
    else
        echo -e "${RED}❌ Failed to trigger pipeline${NC}"
        echo "Response: $response"
        exit 1
    fi
}

get_pipeline_status() {
    local token="$1"
    local pipeline_id="$2"
    
    local url="https://circleci.com/api/v2/pipeline/$pipeline_id"
    
    echo -e "${BLUE}🔍 Getting pipeline status...${NC}"
    
    local response=$(curl -s -H "Circle-Token: $token" "$url")
    
    if [[ $? -eq 0 ]]; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Failed to get pipeline status${NC}"
        exit 1
    fi
}

list_pipelines() {
    local token="$1"
    local org="$2"
    local project="$3"
    
    local url="https://circleci.com/api/v2/project/$org/$project/pipeline?limit=10"
    
    echo -e "${BLUE}📋 Listing recent pipelines...${NC}"
    
    local response=$(curl -s -H "Circle-Token: $token" "$url")
    
    if [[ $? -eq 0 ]]; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Failed to list pipelines${NC}"
        exit 1
    fi
}

# Parse command line arguments
WORKFLOW="ci-cd"
VIDEO_ID=""
FORCE_DEPLOY="false"
STATUS_ID=""
LIST_PIPELINES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--token)
            CIRCLECI_TOKEN="$2"
            shift 2
            ;;
        -o|--org)
            ORG_SLUG="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_SLUG="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -w|--workflow)
            WORKFLOW="$2"
            shift 2
            ;;
        -v|--video-id)
            VIDEO_ID="$2"
            shift 2
            ;;
        -f|--force-deploy)
            FORCE_DEPLOY="true"
            shift
            ;;
        -s|--status)
            STATUS_ID="$2"
            shift 2
            ;;
        -l|--list)
            LIST_PIPELINES=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Validate token
if [[ -z "$CIRCLECI_TOKEN" ]]; then
    echo -e "${RED}❌ CircleCI token is required${NC}"
    echo "Set CIRCLECI_TOKEN environment variable or use --token option"
    exit 1
fi

# Execute based on action
if [[ -n "$STATUS_ID" ]]; then
    get_pipeline_status "$CIRCLECI_TOKEN" "$STATUS_ID"
elif [[ "$LIST_PIPELINES" == true ]]; then
    list_pipelines "$CIRCLECI_TOKEN" "$ORG_SLUG" "$PROJECT_SLUG"
else
    # Validate workflow-specific requirements
    if [[ "$WORKFLOW" == "video-rendering" && -z "$VIDEO_ID" ]]; then
        echo -e "${RED}❌ Video ID is required for video-rendering workflow${NC}"
        exit 1
    fi
    
    trigger_pipeline "$CIRCLECI_TOKEN" "$ORG_SLUG" "$PROJECT_SLUG" "$BRANCH" "$WORKFLOW" "$VIDEO_ID" "$FORCE_DEPLOY"
fi 