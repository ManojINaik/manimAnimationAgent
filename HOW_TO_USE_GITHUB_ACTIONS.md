# How to Access and Monitor GitHub Actions

## 🚀 Accessing GitHub Actions

### 1. Navigate to Your Repository
1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Click on the **"Actions"** tab at the top of the repository

### 2. GitHub Actions Tab Layout
- **Left sidebar**: Lists all your workflows
- **Main area**: Shows workflow runs and their status
- **Search/Filter**: Filter by workflow, status, or time period

## 📊 Monitoring Video Rendering Workflow

### Workflow Name: "Video Renderer"
- **Location**: `.github/workflows/video-renderer.yml`
- **Triggers**: 
  - Every 5 minutes (automatic)
  - Manual trigger
  - Repository dispatch (webhook)

### Status Indicators
- 🟢 **Green checkmark**: Workflow completed successfully
- 🔴 **Red X**: Workflow failed
- 🟡 **Yellow circle**: Workflow is running
- ⚫ **Gray circle**: Workflow was cancelled

## 🔍 Viewing Workflow Details

### 1. Click on a Workflow Run
- Shows all jobs and steps
- View logs for each step
- Download artifacts (if any)

### 2. Key Steps to Monitor
1. **"Check for queued videos"** - Finds videos in database
2. **"Render videos"** - Processes videos with Manim
3. **"Upload artifacts"** - Saves logs and outputs

## 📋 Understanding Workflow Output

### Successful Run
```
✅ Check for queued videos
✅ Render videos  
✅ Upload artifacts
```

### No Videos to Process
```
✅ Check for queued videos (No videos found)
⏭️ Render videos (Skipped)
✅ Upload artifacts
```

### Failed Run
```
✅ Check for queued videos
❌ Render videos (Error in processing)
✅ Upload artifacts
```

## 🚨 Troubleshooting Common Issues

### "No videos in queue" (Normal)
- The workflow runs every 5 minutes
- Most runs will show "no videos" - this is expected
- Only shows videos when there are requests to process

### "Secrets not set" Error
1. Go to repository **Settings**
2. Click **Secrets and variables** → **Actions**
3. Add required secrets:
   - `APPWRITE_ENDPOINT`
   - `APPWRITE_PROJECT_ID`
   - `APPWRITE_API_KEY`
   - `GEMINI_API_KEY`

### "Permission denied" Error
- Check if repository is public or has Actions enabled
- Verify Appwrite API key has correct permissions

### "Workflow not triggering"
- Check if `.github/workflows/video-renderer.yml` exists
- Verify the workflow file syntax is correct
- Ensure repository has Actions enabled

## 📱 Notifications

### Enable Notifications
1. Go to your repository
2. Click **Watch** → **Custom**
3. Check **Actions** to get notified of workflow failures

### Email Notifications
- GitHub sends emails for failed workflows (if enabled)
- You can customize notification settings in your GitHub profile

## 📈 Monitoring Video Processing

### Database Status Flow
```
ready_for_render → queued_for_render → rendering → completed
                                                  ↓
                                               failed
```

### Check Processing Status
1. **In Appwrite Database**: Check `status` field in videos collection
2. **In GitHub Actions**: Look for workflow runs triggered around the time you submitted a video
3. **In Logs**: Check individual step outputs for detailed information

## ⚡ Manual Triggering

### Trigger Specific Video
1. Go to **Actions** tab
2. Select **"Video Renderer"** workflow
3. Click **"Run workflow"**
4. Enter the video ID to process
5. Click **"Run workflow"** button

### Force Queue Check
- The workflow runs automatically every 5 minutes
- You can manually trigger it to check for videos immediately

## 📊 Performance Monitoring

### Typical Processing Times
- **Queue check**: 10-30 seconds
- **Simple video (1 scene)**: 3-8 minutes
- **Complex video (multiple scenes)**: 10-30 minutes

### Resource Limits
- **Maximum runtime**: 6 hours per workflow
- **Concurrent jobs**: Limited by your GitHub plan
- **Storage**: Artifacts are kept for 90 days (configurable)

## 🎯 Success Indicators

### Video Successfully Processed
1. ✅ Workflow shows green checkmark
2. Database status changes to "completed"
3. Video file uploaded to Appwrite storage
4. No error messages in logs

### What to Check if Videos Aren't Processing
1. **Database**: Is video status "ready_for_render" or "queued_for_render"?
2. **Workflow**: Are workflows running every 5 minutes?
3. **Logs**: Any error messages in the workflow logs?
4. **Secrets**: Are all required environment variables set?

---

## 🆘 Getting Help

If you encounter issues:
1. Check the workflow logs first
2. Verify all secrets are correctly set
3. Ensure your Appwrite database is accessible
4. Check if your API keys have sufficient permissions

The system is designed to be self-healing and will retry failed operations automatically. 