# Deployment Guide: manimAnimationAgent

## Overview
This guide explains how to deploy the manimAnimationAgent to Hugging Face Spaces for actual video generation.

## Prerequisites
- Hugging Face account
- Gemini API key(s) from Google AI Studio
- Basic understanding of environment variables

## Quick Start

### 1. Create New Hugging Face Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure:
   - **Space name**: Your choice (e.g., "manimAnimationAgent")
   - **License**: MIT
   - **SDK**: Gradio
   - **Hardware**: CPU Basic (sufficient for most cases)
   - **Visibility**: Public or Private

### 2. Upload Files
Upload these files to your space:
- `app.py` (main application)
- `requirements_hf.txt` (rename to `requirements.txt`)
- `README_HUGGINGFACE.md` (rename to `README.md`)
- All source files from `src/`, `mllm_tools/`, etc.

### 3. Set Environment Variables
In your Hugging Face Space settings, add:

**For Single API Key:**
```bash
GEMINI_API_KEY=your-actual-gemini-api-key
DEMO_MODE=false
```

**For Multiple API Keys (Recommended):**
```bash
GEMINI_API_KEY=key1,key2,key3,key4
DEMO_MODE=false
```

**Optional Settings:**
```bash
ELEVENLABS_API_KEY=your-elevenlabs-key  # For TTS
ELEVENLABS_VOICE=false  # Set to true to enable voice generation, false to disable
LANGFUSE_SECRET_KEY=your-langfuse-key   # For logging
```

## Features Enabled

### ✅ Real Video Generation
- **DEMO_MODE=false**: Enables actual video generation
- **Gemini 2.0 Flash Exp**: Latest model for best results
- **Manim Integration**: Professional mathematical animations

### ✅ Comma-Separated API Keys
- **Load Balancing**: Distributes requests across multiple keys
- **Failover**: Automatic switching if one key fails
- **Cost Distribution**: Spreads usage across billing accounts

### ✅ Educational Focus
- **Mathematical Concepts**: Optimized for STEM education
- **Visual Learning**: Geometric proofs and demonstrations
- **Progressive Difficulty**: Suitable for various learning levels

## Usage Instructions

### 1. Access Your Space
Visit: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

### 2. Generate Videos
1. **Enter Topic**: e.g., "Pythagorean Theorem"
2. **Add Context**: Specify focus areas or audience
3. **Set Scenes**: 2-3 scenes for testing, up to 6 for full videos
4. **Click Generate**: Wait for processing (2-10 minutes)

### 3. Download Results
- Videos appear in the interface
- Download links provided for MP4 files
- Individual scene videos also available

## Troubleshooting

### Common Issues

**1. "Demo Mode" Message**
```
Problem: App shows demo simulation instead of real generation
Solution: Set DEMO_MODE=false in environment variables
```

**2. "No API Keys Found"**
```
Problem: Missing or incorrect API key configuration
Solution: Set GEMINI_API_KEY with valid key(s)
```

**3. "Import Error"**
```
Problem: Missing dependencies
Solution: Ensure requirements.txt includes all packages
```

**4. "Generation Failed"**
```
Problem: API quota exceeded or invalid topic
Solution: Check API limits, try different topic
```

### Verification Steps

**1. Test Local Setup:**
```bash
python test_video_generation.py
```

**2. Check API Keys:**
```bash
echo $GEMINI_API_KEY | tr ',' '\n' | wc -l
# Should show number of keys
```

**3. Verify Dependencies:**
```bash
pip install -r requirements.txt
python -c "from generate_video import VideoGenerator; print('✅ Imports work')"
```

## Performance Optimization

### API Key Management
- **4+ Keys**: Optimal for high usage
- **Rate Limiting**: 60 requests/minute per key
- **Monitoring**: Check usage in Google AI Studio

### Hardware Requirements
- **CPU Basic**: Sufficient for most educational videos
- **CPU Upgrade**: Consider for complex visualizations
- **Persistent Storage**: Enable for caching (optional)

### Content Guidelines
- **Educational Topics**: Math, science, engineering concepts
- **Clear Descriptions**: Specific learning objectives
- **Reasonable Scope**: 2-6 scenes per video

## Advanced Configuration

### Custom Model Settings
Edit `app.py` to modify:
```python
planner_model = LiteLLMWrapper(
    model_name="gemini/gemini-2.5-flash-exp",  # Model choice
    temperature=0.7,  # Creativity level
    print_cost=True,  # Cost tracking
    verbose=True      # Debug output
)
```

### Output Customization
Modify `GRADIO_OUTPUT_DIR` in `app.py`:
```python
GRADIO_OUTPUT_DIR = "custom_outputs"  # Change output folder
```

### Feature Toggles
```python
# In VideoGenerator initialization
use_rag=False,              # Retrieval augmented generation
use_context_learning=True,  # Few-shot learning
use_visual_fix_code=True,   # Visual debugging
verbose=True                # Detailed logging
```

## Security Considerations

### API Key Protection
- Never commit keys to version control
- Use HF Spaces environment variables
- Monitor usage regularly

### Content Moderation
- Educational content only
- Avoid sensitive topics
- Review generated content

## Support

### Getting Help
1. **Check Logs**: HF Spaces build logs
2. **Test Locally**: Use `test_video_generation.py`
3. **Issues**: Report problems with error messages
4. **Community**: HF Spaces forums

### Useful Resources
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Gradio Documentation](https://gradio.app/docs/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Manim Documentation](https://docs.manim.community/)

## Example Successful Deployment

**Space URL**: `https://huggingface.co/spaces/ManojINaik/menamiai`
**Features**: Full video generation with comma-separated API keys
**Status**: Operational with educational content focus

---

*This deployment guide ensures your manimAnimationAgent works with actual video generation capabilities on Hugging Face Spaces.* 