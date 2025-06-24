# CircleCI Setup Guide

This document outlines the CircleCI configuration for the Manim Animation Agent project.

## Overview

The CircleCI configuration provides:
- Automated testing for both backend and frontend
- Video rendering capabilities triggered manually or on schedule
- Deployment pipelines for staging environments
- Build artifacts and logging

## Configuration Structure

### Executors
- **python-executor**: Python 3.11 environment for backend tasks
- **node-executor**: Node.js 18.17 environment for frontend tasks

### Commands
- **install-system-deps**: Installs system dependencies for Manim
- **setup-python-env**: Sets up Python environment with caching
- **setup-node-env**: Sets up Node.js environment with caching

### Jobs

#### 1. test-backend
- Runs Python tests
- Tests Manim installation
- Validates backend functionality

#### 2. test-frontend
- Runs frontend linting
- Builds the Next.js application
- Validates frontend build

#### 3. render-video
- Processes video rendering requests
- Can be triggered manually with video ID parameter
- Runs on scheduled intervals to check queue

#### 4. deploy-frontend-staging
- Builds frontend for production
- Prepares deployment artifacts
- Deploys to staging environment

#### 5. deploy-backend-staging
- Packages backend application
- Prepares deployment package
- Deploys to staging environment

## Workflows

### ci-cd (Main CI/CD Pipeline)
- Runs on all branches
- Tests both frontend and backend
- Deploys to staging on specific branches (main, circleci, staging)

### video-rendering (Manual Trigger)
- Manual workflow for rendering specific videos
- Accepts video_id parameter

### scheduled-video-check (Scheduled)
- Runs every 10 minutes
- Checks for queued videos and processes them
- Only runs on main and circleci branches

## Environment Variables

Set these in your CircleCI project settings:

### Required
```
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your-project-id
APPWRITE_API_KEY=your-api-key
GEMINI_API_KEY=your-gemini-key
```

### Optional
```
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE=true
```

## Setup Instructions

### 1. Connect Your Repository
1. Log in to [CircleCI](https://app.circleci.com/)
2. Click "Set Up Project" for your repository
3. Choose "Use Existing Config" and point to `.circleci/config.yml`

### 2. Configure Environment Variables
1. Go to Project Settings → Environment Variables
2. Add all required environment variables listed above

### 3. Configure Context (Optional)
Create a context for shared environment variables:
1. Go to Organization Settings → Contexts
2. Create a new context (e.g., "manim-agent-prod")
3. Add environment variables to the context
4. Reference the context in your workflows

### 4. Configure SSH Keys (If Deploying)
If you're deploying to servers:
1. Go to Project Settings → SSH Keys
2. Add your deployment server's SSH key

## Frontend Features

The updated frontend includes:

### Build Optimizations
- Static export capability for easier deployment
- Bundle analysis support
- Production optimizations (console log removal)
- Security headers

### CircleCI Integration Components
- **DeploymentStatus**: Shows build information in production
- **CircleCIStatus**: Interactive pipeline status widget
- Environment-based feature flags

### Development Scripts
```bash
# Standard development
npm run dev

# Build with analysis
npm run build:analyze

# Static export for deployment
npm run build:export

# Type checking
npm run type-check

# Preview built application
npm run preview
```

## Triggering Video Rendering

### Manual Trigger via UI
1. Go to CircleCI project page
2. Click "Trigger Pipeline"
3. Select the "video-rendering" workflow
4. Provide video_id parameter if needed

### API Trigger
```bash
curl -X POST \
  https://circleci.com/api/v2/project/github/your-org/your-repo/pipeline \
  -H "Circle-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {
      "video_id": "your-video-id"
    }
  }'
```

## Monitoring and Debugging

### Build Artifacts
Each job stores relevant artifacts:
- Frontend builds in `frontend-build/`
- Video outputs in `video-output/`
- Logs in `logs/`

### Status Monitoring
The frontend includes real-time status components that show:
- Build information
- Pipeline status
- Deployment details

### Log Access
Access logs through:
1. CircleCI web interface
2. Stored artifacts
3. Frontend status components (in production)

## Caching Strategy

The configuration uses aggressive caching:
- **Python dependencies**: Cached by requirements file hash
- **Node.js dependencies**: Cached by package-lock.json hash
- **System dependencies**: Cached by workflow file hash

Cache keys are versioned and environment-specific for reliability.

## Troubleshooting

### Common Issues

#### Build Fails on System Dependencies
- Check if all required packages are in the install-system-deps command
- Verify Ubuntu package names are correct

#### Python Dependencies Installation Fails
- Check requirements-github-actions.txt exists
- Verify Python version compatibility

#### Frontend Build Fails
- Check Node.js version compatibility
- Verify all dependencies are in package.json

#### Video Rendering Timeout
- Increase `no_output_timeout` in render-video job
- Check Manim scene complexity

### Debug Mode
Enable debug output by setting:
```yaml
VERBOSE: true
DEBUG: true
```

## Performance Optimization

### Parallel Jobs
The configuration runs tests in parallel where possible:
- Backend and frontend tests run simultaneously
- Independent deployment jobs can run in parallel

### Resource Classes
For heavy workloads, consider upgrading resource classes:
```yaml
resource_class: large  # or xlarge
```

## Security Considerations

- Environment variables are properly scoped
- Secrets are not logged
- SSH keys are encrypted
- Build artifacts have retention limits

## Support

For issues with this CircleCI setup:
1. Check the troubleshooting section above
2. Review CircleCI documentation
3. Check project-specific logs and artifacts
4. Contact the development team 