# 🎓 manimAnimationAgent - Streamlit Deployment Guide

## Overview

This guide explains how to deploy your TheoremExplainAgent on Streamlit Cloud and use it as a backend API for your web applications.

## 🚀 Quick Start

### Option 1: Streamlit App with Built-in API Features
Deploy `streamlit_app.py` for a web interface with API testing capabilities.

### Option 2: Dedicated FastAPI Server
Deploy `api_server.py` for a pure REST API backend.

## 📦 Deployment Options

### 1. Streamlit Cloud Deployment

#### Step 1: Prepare Repository
```bash
# Ensure these files are in your repository:
- streamlit_app.py          # Main Streamlit application
- requirements_streamlit.txt # Dependencies for Streamlit Cloud
- .streamlit/config.toml    # Streamlit configuration (optional)
```

#### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file path: `streamlit_app.py`
4. Set requirements file: `requirements_streamlit.txt`

#### Step 3: Configure Environment Variables
In Streamlit Cloud settings, add:
```
GEMINI_API_KEY=your-key-1,your-key-2,your-key-3
DEMO_MODE=true  # Set to false for full functionality (requires system deps)
```

### 2. Local Development Setup

#### Full Functionality (with video generation)
```bash
# Clone repository
git clone <your-repo>
cd TheoremExplainAgent

# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-api-key-1,your-api-key-2"
export DEMO_MODE=false

# Run Streamlit app
streamlit run streamlit_app.py

# Or run FastAPI server
python api_server.py
```

#### Demo Mode (Streamlit Cloud compatible)
```bash
# Install minimal dependencies
pip install -r requirements_streamlit.txt

# Set environment variables
export GEMINI_API_KEY="your-api-key"
export DEMO_MODE=true

# Run application
streamlit run streamlit_app.py
```

## 🔌 Using as API Backend

### API Endpoints

Your deployed Streamlit app provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Start video generation |
| `/api/status/{task_id}` | GET | Check task status |
| `/api/health` | GET | Health check |
| `/api/stats` | GET | API statistics |
| `/api/example` | GET | Usage examples |

### Example Client Code

#### Python Client
```python
import requests
import time
import json

class TheoremExplainClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def generate_video(self, topic, context="", max_scenes=3):
        """Generate educational video"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "topic": topic,
                "context": context,
                "max_scenes": max_scenes
            }
        )
        return response.json()
    
    def check_status(self, task_id):
        """Check task status"""
        response = requests.get(f"{self.base_url}/api/status/{task_id}")
        return response.json()
    
    def wait_for_completion(self, task_id, timeout=300):
        """Wait for task completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_status(task_id)
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"Task failed: {status.get('error', 'Unknown error')}")
            
            time.sleep(2)
        
        raise TimeoutError("Task did not complete within timeout")

# Usage example
client = TheoremExplainClient("https://your-streamlit-app.streamlit.app")

# Generate video
result = client.generate_video(
    topic="Pythagorean Theorem",
    context="High school mathematics level",
    max_scenes=3
)

print(f"Task ID: {result['task_id']}")

# Wait for completion
final_result = client.wait_for_completion(result['task_id'])
print(json.dumps(final_result, indent=2))
```

#### JavaScript Client
```javascript
class TheoremExplainClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async generateVideo(topic, context = '', maxScenes = 3) {
        const response = await fetch(`${this.baseUrl}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic,
                context,
                max_scenes: maxScenes
            })
        });
        
        return await response.json();
    }
    
    async checkStatus(taskId) {
        const response = await fetch(`${this.baseUrl}/api/status/${taskId}`);
        return await response.json();
    }
    
    async waitForCompletion(taskId, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const status = await this.checkStatus(taskId);
            
            if (status.status === 'completed') {
                return status;
            } else if (status.status === 'failed') {
                throw new Error(`Task failed: ${status.error || 'Unknown error'}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        throw new Error('Task did not complete within timeout');
    }
}

// Usage example
const client = new TheoremExplainClient('https://your-streamlit-app.streamlit.app');

async function generateEducationalContent() {
    try {
        // Generate video
        const result = await client.generateVideo(
            'Pythagorean Theorem',
            'High school mathematics level',
            3
        );
        
        console.log(`Task ID: ${result.task_id}`);
        
        // Wait for completion
        const finalResult = await client.waitForCompletion(result.task_id);
        console.log(JSON.stringify(finalResult, null, 2));
        
    } catch (error) {
        console.error('Error:', error);
    }
}

generateEducationalContent();
```

#### React Component Example
```jsx
import React, { useState } from 'react';

const TheoremExplainGenerator = () => {
    const [topic, setTopic] = useState('');
    const [context, setContext] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    
    const API_BASE = 'https://your-streamlit-app.streamlit.app';
    
    const generateContent = async () => {
        setLoading(true);
        setError(null);
        
        try {
            // Start generation
            const response = await fetch(`${API_BASE}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic,
                    context,
                    max_scenes: 3
                })
            });
            
            const data = await response.json();
            const taskId = data.task_id;
            
            // Poll for completion
            const pollStatus = async () => {
                const statusResponse = await fetch(`${API_BASE}/api/status/${taskId}`);
                const status = await statusResponse.json();
                
                if (status.status === 'completed') {
                    setResult(status.result);
                    setLoading(false);
                } else if (status.status === 'failed') {
                    setError(status.error);
                    setLoading(false);
                } else {
                    setTimeout(pollStatus, 2000);
                }
            };
            
            pollStatus();
            
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };
    
    return (
        <div className="theorem-explain-generator">
            <h2>Educational Content Generator</h2>
            
            <div className="form">
                <input
                    type="text"
                    placeholder="Educational Topic"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                />
                
                <textarea
                    placeholder="Context (optional)"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                />
                
                <button 
                    onClick={generateContent}
                    disabled={loading || !topic}
                >
                    {loading ? 'Generating...' : 'Generate Content'}
                </button>
            </div>
            
            {error && (
                <div className="error">
                    Error: {error}
                </div>
            )}
            
            {result && (
                <div className="result">
                    <h3>Generated Content</h3>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default TheoremExplainGenerator;
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Comma-separated Gemini API keys | Required |
| `DEMO_MODE` | Enable demo mode (no video generation) | `false` |
| `PORT` | Server port (for FastAPI) | `8000` |

### API Key Setup

1. Get Gemini API keys from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. For better reliability, use multiple keys:
   ```
   GEMINI_API_KEY=key1,key2,key3,key4
   ```

## 📊 Monitoring and Debugging

### Health Check
```bash
curl https://your-streamlit-app.streamlit.app/api/health
```

### View API Stats
```bash
curl https://your-streamlit-app.streamlit.app/api/stats
```

### Check All Tasks
```bash
curl https://your-streamlit-app.streamlit.app/api/tasks
```

## 🚨 Limitations

### Streamlit Cloud Limitations
- ✅ Educational content planning
- ✅ AI-powered curriculum generation
- ❌ Video rendering (requires system dependencies)
- ❌ Audio generation (limited processing power)

### Local Development
- ✅ Full video generation
- ✅ Audio synthesis
- ✅ Complete pipeline
- ✅ File downloads

## 🔄 Scaling Considerations

### For Production Use

1. **Database Storage**: Replace in-memory task storage with Redis/PostgreSQL
2. **File Storage**: Use cloud storage (AWS S3, Google Cloud Storage)
3. **Task Queue**: Implement Celery or similar for background processing
4. **Load Balancing**: Use multiple instances behind a load balancer
5. **Monitoring**: Add proper logging and monitoring (Sentry, DataDog)

### Example Production Architecture
```
Web App → Load Balancer → [API Instance 1, API Instance 2, ...] 
                                    ↓
                              Redis (Task Queue)
                                    ↓
                           Background Workers (Video Generation)
                                    ↓
                           Cloud Storage (Generated Files)
```

## 📝 Troubleshooting

### Common Issues

1. **Dependencies Missing**
   - Solution: Check `requirements_streamlit.txt` and ensure all packages are included

2. **API Keys Not Working**
   - Solution: Verify keys are valid and have sufficient quota

3. **Timeout Issues**
   - Solution: Increase timeout values in client code

4. **CORS Errors**
   - Solution: Ensure your domain is allowed in CORS settings

### Debug Mode
Set `DEMO_MODE=true` to test without full dependencies.

## 🤝 Contributing

1. Test locally with `DEMO_MODE=false`
2. Ensure Streamlit Cloud compatibility with `DEMO_MODE=true`
3. Update requirements files as needed
4. Test API endpoints thoroughly

## 📞 Support

For issues or questions:
- Check the Streamlit app logs
- Test API endpoints manually
- Verify environment variables
- Check system dependencies (for local setup)

---

**Ready to deploy your educational content generation API! 🚀** 