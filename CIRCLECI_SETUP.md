# CircleCI Setup Guide

This document outlines the CircleCI configuration for the Manim Animation Agent project.

## 🎯 Recent Updates (Fixed PyGraphViz Issue)

**Major improvements based on GitHub Actions setup:**
- ✅ **Fixed PyGraphViz build failures** - Added GraphViz development headers (`graphviz-dev`, `libgraphviz-dev`)
- ✅ **Complete system dependencies** - Added all required build tools and libraries
- ✅ **Enhanced dependency installation** - Using `requirements-github-actions.txt` with legacy resolver
- ✅ **Comprehensive validation** - Added dependency verification and environment checks
- ✅ **Improved error handling** - 2-hour timeouts, disk space monitoring, proper cleanup
- ✅ **Enhanced testing** - Better validation of Manim and critical components

## Overview

The CircleCI configuration provides:
- Automated testing for both backend and frontend with comprehensive dependency validation
- Video rendering capabilities triggered manually or on schedule (2-hour timeout)
- Complete system dependency installation (including GraphViz for PyGraphViz)
- Enhanced error handling and disk space management
- Deployment pipelines for staging environments
- Build artifacts and comprehensive logging

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

### scheduled-video-check (Scheduled) - Currently Disabled
- **Note**: Commented out due to CircleCI cron format requirements
- To enable: Uncomment the workflow and test with a simple cron expression
- Suggested format: `"0 12 * * *"` (daily at noon)
- Only runs on main and circleci branches when enabled

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

## Triggering Workflows via API

CircleCI supports API triggers similar to GitHub Actions. The configuration includes pipeline parameters for programmatic control.

### API Endpoints
- **Trigger Pipeline**: `POST https://circleci.com/api/v2/project/{org}/{project}/pipeline`
- **Get Pipeline Status**: `GET https://circleci.com/api/v2/pipeline/{pipeline-id}`
- **List Pipelines**: `GET https://circleci.com/api/v2/project/{org}/{project}/pipeline`

### Using the Trigger Scripts

#### Python Script
```bash
# Trigger CI/CD workflow
python scripts/trigger_circleci_api.py \
  --token YOUR_TOKEN \
  --org gh/your-username \
  --project manimAnimationAgent \
  --workflow ci-cd

# Trigger video rendering
python scripts/trigger_circleci_api.py \
  --token YOUR_TOKEN \
  --org gh/your-username \
  --project manimAnimationAgent \
  --workflow video-rendering \
  --video-id abc123

# Get pipeline status
python scripts/trigger_circleci_api.py \
  --token YOUR_TOKEN \
  --org gh/your-username \
  --project manimAnimationAgent \
  --status pipeline-id-here
```

#### Bash Script (Linux/Mac)
```bash
# Set environment variables
export CIRCLECI_TOKEN="your-token"
export CIRCLECI_ORG="gh/your-username"
export CIRCLECI_PROJECT="manimAnimationAgent"

# Trigger CI/CD workflow
./scripts/trigger_circleci.sh --workflow ci-cd

# Trigger video rendering
./scripts/trigger_circleci.sh --workflow video-rendering --video-id abc123

# List recent pipelines
./scripts/trigger_circleci.sh --list
```

#### PowerShell Script (Windows)
```powershell
# Trigger CI/CD workflow
.\scripts\trigger_circleci.ps1 -Token "your-token" -Workflow ci-cd

# Trigger video rendering
.\scripts\trigger_circleci.ps1 -Token "your-token" -Workflow video-rendering -VideoId "abc123"

# Get pipeline status
.\scripts\trigger_circleci.ps1 -Token "your-token" -Status "pipeline-id"
```

### Direct API Examples

#### Trigger CI/CD Pipeline
```bash
curl -X POST \
  https://circleci.com/api/v2/project/gh/your-username/manimAnimationAgent/pipeline \
  -H "Circle-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {
      "workflow": "ci-cd",
      "force_deploy": false
    }
  }'
```

#### Trigger Video Rendering
```bash
curl -X POST \
  https://circleci.com/api/v2/project/gh/your-username/manimAnimationAgent/pipeline \
  -H "Circle-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {
      "workflow": "video-rendering",
      "video_id": "your-video-id"
    }
  }'
```

### Manual Trigger via UI
1. Go to CircleCI project page
2. Click "Trigger Pipeline"
3. Select parameters:
   - `workflow`: "ci-cd" or "video-rendering"
   - `video_id`: Required for video-rendering workflow
   - `force_deploy`: Optional boolean for forced deployment

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

#### PyGraphViz Build Failure ✅ FIXED
If you see `fatal error: graphviz/cgraph.h: No such file or directory`:
- ✅ **Fixed in current configuration** - GraphViz development headers are now included
- Required packages: `graphviz`, `graphviz-dev`, `libgraphviz-dev`
- For local development: `sudo apt-get install graphviz graphviz-dev libgraphviz-dev`

#### Dependency Installation Issues
If Python packages fail to install:
- ✅ **Enhanced** - Now using `requirements-github-actions.txt` with `--use-deprecated=legacy-resolver`
- Comprehensive system dependencies are pre-installed
- Added dependency verification steps after installation

#### Timeout Issues During Video Rendering
- ✅ **Improved** - Extended timeout to 2 hours (`no_output_timeout: 2h`)
- Added disk space monitoring and cleanup
- Enhanced error handling with proper exit codes

#### Python Dependencies Installation Fails
- Check requirements-github-actions.txt exists
- Verify Python version compatibility

#### Frontend Build Fails
- Check Node.js version compatibility
- Verify all dependencies are in package.json

#### Video Rendering Timeout
- Increase `no_output_timeout` in render-video job
- Check Manim scene complexity

#### Cron Expression Validation Errors
- CircleCI requires POSIX-compliant cron expressions
- Use explicit values instead of shorthand (e.g., `"0 6,12,18 * * *"` instead of `"0 */6 * * *"`)
- Test expressions using CircleCI CLI: `circleci config validate`
- Common valid formats:
  - Daily: `"0 12 * * *"`
  - Every 6 hours: `"0 0,6,12,18 * * *"`
  - Weekly: `"0 12 * * 0"`

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

## Validation and Testing

### Validate Your Setup
Use the provided validation scripts to check your configuration:

#### Linux/Mac
```bash
# Make executable and run
chmod +x scripts/validate_circleci.sh
./scripts/validate_circleci.sh
```

#### Windows
```powershell
# Run validation script
.\scripts\validate_circleci.ps1

# For detailed output
.\scripts\validate_circleci.ps1 -Detailed
```

### What the Validation Checks
- ✅ CircleCI configuration file exists and is valid YAML
- ✅ Required files are present (`requirements-github-actions.txt`, scripts, etc.)
- ✅ Environment variables are properly set
- ✅ System dependencies are available (on compatible systems)
- ✅ Python and pip are properly installed
- ✅ CircleCI CLI is available (optional)
- ✅ Configuration uses correct requirements file
- ✅ GraphViz development headers are included
- ✅ Timeout configurations are present

### Local Testing
To test the setup locally (similar to CircleCI environment):

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y pkg-config libcairo2-dev libgirepository1.0-dev ffmpeg \
  libpango1.0-dev portaudio19-dev libasound2-dev libsndfile1-dev libfftw3-dev \
  libatlas-base-dev graphviz graphviz-dev libgraphviz-dev gcc g++ build-essential

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements-github-actions.txt --use-deprecated=legacy-resolver

# Test critical imports
python -c "import manim; print('✅ Manim:', manim.__version__)"
python -c "import pygraphviz; print('✅ PyGraphViz installed successfully')"
python -c "import appwrite; print('✅ Appwrite SDK installed')"
```

## Support

For issues with this CircleCI setup:
1. Run the validation scripts first (`validate_circleci.sh` or `validate_circleci.ps1`)
2. Check the troubleshooting section above
3. Review CircleCI documentation
4. Check project-specific logs and artifacts
5. Contact the development team 