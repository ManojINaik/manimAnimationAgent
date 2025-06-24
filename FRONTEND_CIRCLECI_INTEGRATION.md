# Frontend CircleCI Integration Guide

## 🎯 Overview

This guide explains how your frontend now supports **both GitHub Actions and CircleCI** for video rendering. Users can choose their preferred platform when submitting video generation requests.

## 🔄 How It Works

### 1. **User Flow**
```
User Input → Frontend → API → Appwrite Database → Trigger Platform(s) → Video Rendering
```

### 2. **Video ID Generation**
- User provides `topic` and `description`
- Frontend calls `/api/generate` with platform choice
- Appwrite generates unique video ID with `ID.unique()`
- Video document created with status `queued_for_render`
- Selected platform(s) triggered with the video ID

### 3. **Platform Processing**
- **GitHub Actions**: Uses `video-renderer.yml` workflow
- **CircleCI**: Uses `video-rendering` workflow
- **Both**: Triggers both platforms for redundancy

## 🛠️ Setup Instructions

### 1. **Environment Variables**

Copy `.env.example` to `.env.local` in the `frontend_example` directory:

```bash
cd frontend_example
cp .env.example .env.local
```

Update the values:

```env
# Appwrite Configuration
NEXT_PUBLIC_APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
NEXT_PUBLIC_APPWRITE_PROJECT_ID=your-project-id
APPWRITE_API_KEY=your-server-api-key

# GitHub Actions Integration
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=manimAnimationAgent
GITHUB_WORKFLOW_FILENAME=video-renderer.yml
GH_PAT=your-github-personal-access-token

# CircleCI Integration
CIRCLECI_TOKEN=your-circleci-api-token
CIRCLECI_ORG=gh/your-github-username
CIRCLECI_PROJECT=manimAnimationAgent
CIRCLECI_BRANCH=main
```

### 2. **Get Required Tokens**

#### **GitHub Personal Access Token (PAT)**
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`
4. Copy the token to `GH_PAT`

#### **CircleCI API Token**
1. Go to [CircleCI Personal API Tokens](https://app.circleci.com/settings/user/tokens)
2. Click "Create New Token"
3. Copy the token to `CIRCLECI_TOKEN`

### 3. **Install Dependencies**

```bash
cd frontend_example
npm install
```

### 4. **Run the Frontend**

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🎮 Using the Frontend

### 1. **Basic Usage**
1. Enter a **topic** (required)
2. Add **description** (optional)
3. Choose **platform**:
   - **GitHub Actions** (recommended)
   - **CircleCI** (alternative)
   - **Both** (redundancy)
4. Click "Generate Video"

### 2. **Platform Options**

| Platform | Description | Use Case |
|----------|-------------|----------|
| **GitHub Actions** | Fast, reliable, recommended | Standard video generation |
| **CircleCI** | Alternative cloud platform | When GitHub is unavailable |
| **Both** | Triggers both platforms | Critical projects requiring redundancy |

### 3. **Video ID Tracking**
- Video ID is auto-generated (e.g., `65f4a2b1c3d4e5f6g7h8i9j0`)
- Status tracked in real-time via Appwrite subscriptions
- Progress shown for each scene

## 🔧 API Endpoints

### **POST /api/generate**

**Request:**
```json
{
  "topic": "Newton's Laws of Motion",
  "description": "Explain the three laws with visual demonstrations",
  "platform": "circleci"
}
```

**Response:**
```json
{
  "success": true,
  "videoId": "65f4a2b1c3d4e5f6g7h8i9j0",
  "platform": "circleci",
  "message": "Video generation task has been successfully queued for circleci processing."
}
```

## 🔄 Platform Trigger Details

### **GitHub Actions Trigger**
```typescript
// Triggers workflow_dispatch event
fetch(`https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`, {
  method: 'POST',
  headers: {
    Authorization: `token ${ghPat}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ref: 'main',
    inputs: { video_id: videoId },
  }),
});
```

### **CircleCI Trigger**
```typescript
// Triggers pipeline with parameters
fetch(`https://circleci.com/api/v2/project/${org}/${project}/pipeline`, {
  method: 'POST',
  headers: {
    'Circle-Token': token,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    branch: 'main',
    parameters: {
      workflow: 'video-rendering',
      video_id: videoId
    }
  }),
});
```

## 🚨 Troubleshooting

### **Common Issues**

1. **"Platform must be github, circleci, or both"**
   - Ensure platform parameter is correctly set

2. **"CircleCI token not available"**
   - Check `CIRCLECI_TOKEN` environment variable
   - Verify token has correct permissions

3. **"GitHub PAT not available"**
   - Check `GH_PAT` environment variable
   - Verify token has `repo` and `workflow` scopes

4. **"Failed to trigger workflow"**
   - Check network connectivity
   - Verify repository and organization names
   - Check API rate limits

### **Debug Mode**

Enable detailed logging by checking browser console for:
- `📥 API /generate POST request received`
- `🎯 All workflow triggers completed`
- `✅ Successfully triggered [platform] workflow`

### **Testing Triggers**

You can test triggers manually:

```bash
# Test CircleCI trigger
curl -X POST \
  "https://circleci.com/api/v2/project/gh/YOUR_USERNAME/manimAnimationAgent/pipeline" \
  -H "Circle-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {
      "workflow": "video-rendering",
      "video_id": "test-video-id"
    }
  }'
```

## 🎯 Best Practices

1. **Platform Selection**
   - Use **GitHub Actions** for most cases (faster, more reliable)
   - Use **CircleCI** as backup or when GitHub is down
   - Use **Both** for critical/production videos

2. **Error Handling**
   - Frontend handles API failures gracefully
   - Retries network errors automatically
   - Documents are created even if triggers fail

3. **Monitoring**
   - Check platform dashboards for build status
   - Monitor Appwrite database for video status
   - Use browser console for debugging

## 🔗 Related Files

- `frontend_example/src/app/api/generate/route.ts` - API endpoint
- `frontend_example/src/app/components/VideoGenerator.tsx` - UI component
- `.circleci/config.yml` - CircleCI configuration
- `.github/workflows/video-renderer.yml` - GitHub Actions workflow

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify environment variables are set correctly
3. Check platform dashboards for build status
4. Review browser console for error messages 