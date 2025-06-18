#!/usr/bin/env python3
"""
manimAnimationAgent - Gradio Interface
A web interface for generating educational videos explaining mathematical theorems and concepts.
"""

import gradio as gr

def generate_explanation(topic, context, max_scenes):
    """Generate educational content explanation."""
    if not topic.strip():
        return "❌ Please enter a topic to explain"
    
    result = f"""🎓 **manimAnimationAgent**

📚 **Topic:** {topic}
📋 **Context:** {context if context else "None specified"}
🎬 **Scenes:** {max_scenes}

✅ **Demo Generation Complete!**

🎯 **Generated Educational Content:**
• Introduction to {topic}
• Fundamental concepts and definitions  
• Step-by-step mathematical derivation
• Visual demonstrations and proofs
• Real-world applications and examples
• Practice problems and solutions

📊 **Video Specifications:**
• Duration: ~{max_scenes * 0.8:.1f} minutes
• Scene count: {max_scenes}
• Style: Mathematical animations
• Voiceover: AI-generated narration

⚠️ **Demo Mode Active**
This is a simulation showing the interface capabilities. 
In production mode, actual Manim animations would be generated.

🚀 **Production Features:**
✓ Manim mathematical animations
✓ AI-powered script generation  
✓ Professional voiceover synthesis
✓ Multiple output formats
✓ Custom styling and branding
"""
    return result

# Define the interface explicitly
iface = gr.Interface(
    fn=generate_explanation,
    inputs=[
        gr.Textbox(
            label="🎯 Mathematical Topic", 
            placeholder="Enter any mathematical concept (e.g., Pythagorean Theorem, Derivatives, etc.)",
            value=""
        ),
        gr.Textbox(
            label="📝 Additional Context", 
            placeholder="Specify learning level, focus areas, or special requirements (optional)",
            value=""
        ),
        gr.Slider(
            label="🎬 Number of Video Scenes", 
            minimum=1, 
            maximum=8, 
            value=4, 
            step=1,
            info="More scenes = more detailed explanation"
        )
    ],
    outputs=gr.Textbox(
        label="📊 Generated Educational Content", 
        lines=20,
        show_copy_button=True
    ),
    title="🎓 manimAnimationAgent",
    description="🚀 Generate educational videos explaining mathematical theorems and concepts using AI-powered animations",
    examples=[
        ["Pythagorean Theorem", "Include visual proof and real-world applications", 4],
        ["Calculus Derivatives", "Focus on geometric interpretation for beginners", 5], 
        ["Newton's Laws of Motion", "Physics applications with practical examples", 3],
        ["Quadratic Formula", "Step-by-step derivation with examples", 4],
        ["Probability Distributions", "Visual explanations with real-world data", 5]
    ],
    theme=gr.themes.Soft(),
    css="footer {visibility: hidden}"
)

# Export for HF Spaces
demo = iface

if __name__ == "__main__":
    demo.launch() 