# Appwrite Function Deployment Guide

This guide walks you through deploying the asynchronous video generation function to Appwrite.

## Prerequisites

1. **Appwrite CLI**: Install the Appwrite CLI
   ```bash
   npm install -g appwrite-cli
   ```

2. **Appwrite Account**: Create an account at [cloud.appwrite.io](https://cloud.appwrite.io)

3. **Project Setup**: Create a new project in Appwrite Console

## Step 1: Initialize Appwrite CLI

```bash
# Login to Appwrite
appwrite login

# Initialize project in current directory
appwrite init project

# When prompted:
# - Select your project or create new one
# - Choose your preferred region
```

## Step 2: Create the Function

### Option A: Using Appwrite Console (Easier)

1. Go to [Appwrite Console](https://cloud.appwrite.io)
2. Navigate to **Functions** section
3. Click **Create Function**
4. Configure:
   - **Name**: Video Generation
   - **ID**: video_generation
   - **Runtime**: Python 3.12
   - **Entrypoint**: main.py
   - **Timeout**: 1800 (30 minutes)
   - **Execute Access**: Any

### Option B: Using CLI

```bash
appwrite functions create \
    --functionId="video_generation" \
    --name="Video Generation" \
    --runtime="python-3.12" \
    --execute="any" \
    --timeout=1800
```

## Step 3: Set Environment Variables

### In Appwrite Console:

1. Go to your function in the Console
2. Click on **Settings** tab
3. Scroll to **Environment Variables**
4. Add these variables:

```bash
# Core Appwrite Config
APPWRITE_API_KEY=<your_api_key>
APPWRITE_PROJECT_ID=<your_project_id>
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1

# AI Model Keys
GEMINI_API_KEY=<your_gemini_key>
OPENAI_API_KEY=<your_openai_key>

# Optional Services
ELEVENLABS_API_KEY=<your_elevenlabs_key>
LANGFUSE_PUBLIC_KEY=<your_langfuse_public_key>
LANGFUSE_SECRET_KEY=<your_langfuse_secret_key>
LANGFUSE_HOST=https://cloud.langfuse.com
mem0_api_key=<your_mem0_key>

# Default Models (optional)
DEFAULT_PLANNER_MODEL=gemini/gemini-2.5-pro
DEFAULT_SCENE_MODEL=gemini/gemini-2.5-pro
```

### Getting API Keys:

1. **Appwrite API Key**:
   - Go to Console → Settings → API Keys
   - Create new key with these scopes:
     - `databases.read`
     - `databases.write`
     - `storage.read`
     - `storage.write`
     - `functions.read`
     - `functions.write`

2. **Project ID**:
   - Found in Console → Settings → Project ID

## Step 4: Deploy the Function

### Prepare the deployment package:

```bash
# From project root
cd appwrite_functions/video_generation

# Create a deployment package
# The function needs access to the main project modules
cp -r ../../src ./
cp -r ../../mllm_tools ./
cp -r ../../task_generator ./
cp -r ../../eval_suite ./
cp -r ../../data ./
```

### Deploy using CLI:

```bash
# From appwrite_functions/video_generation directory
appwrite functions createDeployment \
    --functionId="video_generation" \
    --activate=true \
    --entrypoint="main.py" \
    --code="."
```

### Or deploy using Console:

1. Go to your function in Console
2. Click **Deploy** button
3. Upload the `appwrite_functions/video_generation` folder
4. Click **Activate after build**

## Step 5: Setup Database

Run the setup script to create collections:

```bash
# From project root
cd .venv/Scripts
activate
cd ../..
python scripts/setup_appwrite_db.py
```

This creates:
- Database: `video_metadata`
- Collections: `videos`, `scenes`, `agent_memory`
- Storage buckets for videos and files

## Step 6: Test the Function

### Using Appwrite Console:

1. Go to your function
2. Click **Execute** button
3. Add test payload:
   ```json
   {
     "topic": "Test Video",
     "description": "A simple test",
     "userId": "test-user"
   }
   ```
4. Click **Execute**

### Using curl:

```bash
curl -X POST https://cloud.appwrite.io/v1/functions/video_generation/executions \
  -H "X-Appwrite-Project: YOUR_PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "{\"topic\":\"Test Video\",\"description\":\"A simple test\"}"
  }'
```

## Step 7: Setup Frontend

```bash
# From project root
cd frontend_example

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your values:
# NEXT_PUBLIC_APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
# NEXT_PUBLIC_APPWRITE_PROJECT_ID=your_project_id

# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the frontend.

## Troubleshooting

### Function Build Errors

If you see "Module not found" errors:
1. Ensure all required directories are copied to the function folder
2. Check that `requirements.txt` includes all dependencies

### Timeout Issues

For large videos:
1. Increase function timeout (max 900 seconds in Appwrite Cloud)
2. Consider breaking into smaller scenes
3. Use Appwrite Cloud Functions Pro for longer timeouts

### Permission Errors

Ensure your API key has all required scopes:
- Database read/write
- Storage read/write
- Functions read/write

### Real-time Not Working

1. Check that your project ID is correct in frontend
2. Ensure you're subscribed to the correct collection
3. Check browser console for WebSocket errors

## Monitoring

### View Logs:
- Console → Functions → Your Function → Logs

### Track Executions:
- Console → Functions → Your Function → Executions

### Database Records:
- Console → Databases → video_metadata → Browse collections

## Production Considerations

1. **Rate Limiting**: Implement rate limiting for API calls
2. **Authentication**: Add proper user authentication
3. **Error Recovery**: Implement retry logic for failed scenes
4. **Cost Management**: Monitor API usage for AI services
5. **Storage Cleanup**: Implement old file deletion policy

## Next Steps

1. Test with different video topics
2. Monitor performance and costs
3. Implement user authentication
4. Add webhook notifications
5. Build admin dashboard for monitoring 