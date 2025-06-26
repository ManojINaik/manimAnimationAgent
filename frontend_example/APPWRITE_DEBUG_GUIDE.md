# Appwrite Debug Guide

## Video History Stuck Loading? Here's How to Fix It

If your video history is stuck on "Loading video history..." screen, follow these steps:

### 1. Check Environment Variables

Create a `.env.local` file in the `frontend_example` folder with your Appwrite configuration:

```bash
# Copy from .env.example and update with your values
NEXT_PUBLIC_APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
NEXT_PUBLIC_APPWRITE_PROJECT_ID=your_actual_project_id_here
```

### 2. Verify Appwrite Project Setup

Make sure you have:
- ✅ An Appwrite project created at https://cloud.appwrite.io
- ✅ Database named `video_metadata` 
- ✅ Collection named `videos` inside that database
- ✅ Proper permissions set on the collection (read access for guests/users)

### 3. Check Browser Console

1. Open Developer Tools (F12)
2. Go to Console tab
3. Switch to History tab and look for error messages
4. Look for messages starting with `🎬 VideoHistory:` or `❌ Failed to get all videos:`

### 4. Common Issues & Solutions

#### Issue: "Missing Appwrite configuration"
- **Solution**: Create `.env.local` file with correct values

#### Issue: "Collection not found" or "Database not found"
- **Solution**: Verify database and collection names in Appwrite dashboard
- Database ID should be: `video_metadata`
- Collection ID should be: `videos`

#### Issue: "Permission denied"
- **Solution**: In Appwrite dashboard, go to your collection settings and add read permissions

#### Issue: Network errors
- **Solution**: Check if Appwrite endpoint is accessible and project ID is correct

### 5. Test Connection

If you see debug information in the error section, check:
- `endpoint`: Should be `https://cloud.appwrite.io/v1`
- `projectId`: Should match your Appwrite project ID
- `success`: Should be `true`

### 6. Manual Testing

You can test the connection by opening browser console and running:
```javascript
// This will show debug information
console.log('Testing Appwrite connection...');
```

### 7. Still Having Issues?

1. Check if you have any videos in your database
2. Try creating a test video first using the "Create Video" tab
3. Check Appwrite dashboard for any error logs
4. Verify your project isn't suspended or over limits

## Quick Setup Checklist

- [ ] `.env.local` file created with correct values
- [ ] Appwrite project exists and is accessible
- [ ] Database `video_metadata` created
- [ ] Collection `videos` created with proper permissions
- [ ] Browser console shows no errors
- [ ] Network connection is working

If all above steps are completed and you're still having issues, check the debug information that appears when you click "Try Again" on the error screen. 