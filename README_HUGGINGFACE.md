# 🎓 manimAnimationAgent - Hugging Face Spaces

This is a Gradio web interface for generating educational videos that explain mathematical theorems and scientific concepts using AI.

## 🚀 Features

- **AI-Powered Video Generation**: Uses Gemini 2.0 Flash to create educational content
- **Automatic API Key Rotation**: Supports multiple Gemini API keys with fallback mechanism
- **Educational Focus**: Specializes in mathematical and scientific explanations
- **Interactive Interface**: Clean, user-friendly Gradio interface
- **Demo Mode**: Works without API keys for demonstration purposes

## 🔑 Setting Up API Keys on Hugging Face Spaces

### Step 1: Get Your Gemini API Keys

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create one or more API keys
3. Copy the keys (they look like: `AIzaSyA...`)

### Step 2: Configure Secrets on Hugging Face Spaces

1. Go to your Space's **Settings** tab
2. Click on **Repository secrets**
3. Add the following secrets:

#### For Multiple API Keys (Recommended)
```
Name: GEMINI_API_KEY
Value: AIzaSyA...,AIzaSyB...,AIzaSyC...,AIzaSyD...
```

#### For Single API Key
```
Name: GEMINI_API_KEY  
Value: AIzaSyA...
```

#### Optional: Text-to-Speech
```
Name: ELEVENLABS_API_KEY
Value: your_elevenlabs_api_key
```

#### Enable Full Mode
```
Name: DEMO_MODE
Value: false
```

### Step 3: How the Fallback System Works

The app automatically handles multiple API keys:

1. **Comma-Separated Keys**: When you provide multiple keys separated by commas, the system randomly selects one for each request
2. **Automatic Rotation**: This helps avoid rate limits and distributes load
3. **Error Handling**: If one key fails, the system continues working
4. **Usage Tracking**: Each key selection is logged for monitoring

## 📝 Example Usage

### Basic Topics
- "Velocity" - Physics concepts with examples
- "Pythagorean Theorem" - Mathematical proofs
- "Derivatives" - Calculus with geometric interpretation

### Advanced Topics  
- "Newton's Laws" - Physics with demonstrations
- "Chemical Bonding" - Chemistry with molecular examples
- "Probability" - Statistics with practical examples

## 🛠️ Configuration Options

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API key(s) - supports comma-separated multiple keys | `key1,key2,key3` |
| `ELEVENLABS_API_KEY` | Optional: ElevenLabs API key for TTS | `your_elevenlabs_key` |
| `DEMO_MODE` | Set to "false" to enable full functionality | `false` |

### Video Generation Settings

- **Max Scenes**: 1-6 scenes per video (more scenes = longer videos, higher cost)
- **Context**: Optional additional requirements or focus areas
- **Topic**: Any mathematical or scientific concept

## 💡 Tips for Best Results

1. **Use Clear Topics**: "velocity in physics" works better than just "motion"
2. **Provide Context**: Specify difficulty level, target audience, or focus areas
3. **Start Simple**: Try basic concepts first, then move to advanced topics
4. **Multiple Keys**: Use 3-4 API keys for better rate limit handling

## 🔧 Troubleshooting

### Common Issues

1. **"No API keys found"**: Check that `GEMINI_API_KEY` is set in Secrets
2. **Rate limit errors**: Add more API keys separated by commas
3. **Generation fails**: Try simpler topics or shorter context
4. **Slow response**: Normal for complex topics, progress bar shows status

### Error Messages

- **"Demo mode active"**: API keys not configured properly
- **"Generation failed"**: Check topic validity and API key status
- **"Rate limit exceeded"**: Add more API keys for rotation

## 📊 Cost Considerations

- Each scene costs approximately $0.001-0.01 in API calls
- Multiple API keys help distribute costs
- Demo mode is completely free but only simulates generation
- Monitor usage through Google Cloud Console

## 🚀 Deployment Checklist

- [ ] Fork/clone the repository
- [ ] Set up Gemini API key(s) in Secrets
- [ ] Set `DEMO_MODE=false` if you want full functionality
- [ ] Test with simple topics first
- [ ] Monitor API usage and costs

## 📞 Support

For issues with:
- **API Keys**: Check Google AI Studio documentation
- **Rate Limits**: Add more API keys or wait before retrying  
- **Video Generation**: Verify topic is educational/mathematical
- **Hugging Face**: Check Spaces documentation

---

**Note**: This app is designed for educational content generation. The AI models work best with mathematical, scientific, and educational topics. 