import os
import glob
from memvid import MemvidEncoder
from tqdm import tqdm

def split_into_chunks(text, max_chars=2000):
    """Split text into chunks of max_chars size, trying to break at sentence boundaries."""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    while text:
        if len(text) <= max_chars:
            chunks.append(text)
            break
            
        # Try to find a sentence break near max_chars
        split_point = text.rfind('. ', 0, max_chars)
        if split_point == -1:  # No sentence break found
            split_point = text.rfind(' ', 0, max_chars)
            if split_point == -1:  # No space found
                split_point = max_chars
        else:
            split_point += 2  # Include the period and space
            
        chunks.append(text[:split_point])
        text = text[split_point:].strip()
    
    return chunks

def build_memory():
    """Build the video memory from Markdown documentation files."""
    print("Finding Manim documentation files...")
    md_files = glob.glob("*.md")
    print(f"Found {len(md_files)} documentation files to process.")
    
    print("Reading file contents...")
    chunks = []
    for filename in tqdm(md_files, desc="Reading files"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split content into smaller chunks
                for chunk in split_into_chunks(content):
                    if len(chunk.strip()) > 50:  # Skip very small chunks
                        chunks.append(chunk.strip())
        except Exception as e:
            print(f"Could not read {filename}: {e}")
    
    if not chunks:
        print("No content to encode. Aborting.")
        return
    
    print(f"Encoding {len(chunks)} chunks into video memory. This may take a while...")
    encoder = MemvidEncoder()
    encoder.add_chunks(chunks)
    
    output_video = "manim_memory.mp4"
    output_index = "manim_memory_index.json"
    encoder.build_video(output_video, output_index)
    
    print("\n✅ Memory files created successfully!")
    print(f"   Video file: {output_video}")
    print(f"   Index file: {output_index}")

if __name__ == "__main__":
    build_memory() 