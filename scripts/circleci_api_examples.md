# CircleCI API Examples

Quick reference for triggering CircleCI workflows via API.

## Setup

Get your API token from [CircleCI Personal API Tokens](https://app.circleci.com/settings/user/tokens).

Set environment variables:
```bash
export CIRCLECI_TOKEN="your-api-token"
export CIRCLECI_ORG="gh/your-username"  # or bb/username for Bitbucket
export CIRCLECI_PROJECT="manimAnimationAgent"
```

## Trigger Workflows

### CI/CD Pipeline
```bash
curl -X POST \
  "https://circleci.com/api/v2/project/$CIRCLECI_ORG/$CIRCLECI_PROJECT/pipeline" \
  -H "Circle-Token: $CIRCLECI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {
      "workflow": "ci-cd",
      "force_deploy": false
    }
  }'
```

### Video Rendering
```bash
curl -X POST \
  "https://circleci.com/api/v2/project/$CIRCLECI_ORG/$CIRCLECI_PROJECT/pipeline" \
  -H "Circle-Token: $CIRCLECI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {
      "workflow": "video-rendering",
      "video_id": "your-video-id-here"
    }
  }'
```

### Force Deploy on Feature Branch
```bash
curl -X POST \
  "https://circleci.com/api/v2/project/$CIRCLECI_ORG/$CIRCLECI_PROJECT/pipeline" \
  -H "Circle-Token: $CIRCLECI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "feature-branch",
    "parameters": {
      "workflow": "ci-cd",
      "force_deploy": true
    }
  }'
```

## Monitor Pipelines

### Get Pipeline Status
```bash
# Replace PIPELINE_ID with actual pipeline ID from trigger response
curl -H "Circle-Token: $CIRCLECI_TOKEN" \
  "https://circleci.com/api/v2/pipeline/PIPELINE_ID"
```

### List Recent Pipelines
```bash
curl -H "Circle-Token: $CIRCLECI_TOKEN" \
  "https://circleci.com/api/v2/project/$CIRCLECI_ORG/$CIRCLECI_PROJECT/pipeline?limit=10"
```

### Get Workflow Status
```bash
# Replace PIPELINE_ID with actual pipeline ID
curl -H "Circle-Token: $CIRCLECI_TOKEN" \
  "https://circleci.com/api/v2/pipeline/PIPELINE_ID/workflow"
```

## Response Examples

### Successful Trigger Response
```json
{
  "number": 123,
  "state": "created",
  "id": "5f2cc7c9-c50a-4c39-8c33-2b2c8a5a4567",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Pipeline Status Response
```json
{
  "id": "5f2cc7c9-c50a-4c39-8c33-2b2c8a5a4567",
  "number": 123,
  "state": "success",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

## Integration Examples

### From Python Application
```python
import requests

def trigger_video_rendering(video_id: str, token: str):
    url = f"https://circleci.com/api/v2/project/{org}/{project}/pipeline"
    headers = {
        "Circle-Token": token,
        "Content-Type": "application/json"
    }
    payload = {
        "branch": "main",
        "parameters": {
            "workflow": "video-rendering",
            "video_id": video_id
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

### From Node.js Application
```javascript
const axios = require('axios');

async function triggerCIPipeline(workflow, videoId = null) {
  const url = `https://circleci.com/api/v2/project/${org}/${project}/pipeline`;
  const headers = {
    'Circle-Token': process.env.CIRCLECI_TOKEN,
    'Content-Type': 'application/json'
  };
  
  const parameters = { workflow };
  if (videoId) parameters.video_id = videoId;
  
  const payload = {
    branch: 'main',
    parameters
  };
  
  try {
    const response = await axios.post(url, payload, { headers });
    return response.data;
  } catch (error) {
    console.error('Failed to trigger pipeline:', error.response?.data);
    throw error;
  }
}
```

### Webhook Integration
If you need to trigger builds from external webhooks:

```bash
# Example webhook handler that triggers video rendering
curl -X POST \
  "https://circleci.com/api/v2/project/$CIRCLECI_ORG/$CIRCLECI_PROJECT/pipeline" \
  -H "Circle-Token: $CIRCLECI_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"branch\": \"main\",
    \"parameters\": {
      \"workflow\": \"video-rendering\",
      \"video_id\": \"$VIDEO_ID_FROM_WEBHOOK\"
    }
  }"
```

## Error Handling

Common error responses:

### Invalid Token (401)
```json
{
  "message": "Permission denied"
}
```

### Project Not Found (404)
```json
{
  "message": "Project not found"
}
```

### Invalid Parameters (400)
```json
{
  "message": "Invalid parameters",
  "errors": [
    "video_id is required for video-rendering workflow"
  ]
}
``` 