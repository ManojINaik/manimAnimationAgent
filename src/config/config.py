import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    OUTPUT_DIR = "output"
    THEOREMS_PATH = os.path.join("data", "easy_20.json")
    CONTEXT_LEARNING_PATH = "data/context_learning"
    CHROMA_DB_PATH = "data/rag/chroma_db"
    MANIM_DOCS_PATH = "data/rag/manim_docs"
    EMBEDDING_MODEL = "azure/text-embedding-3-large"
    
    # ElevenLabs TTS configurations
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_DEFAULT_VOICE_ID = os.getenv('ELEVENLABS_DEFAULT_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Default: Bella voice 
    ELEVENLABS_VOICE = os.getenv('ELEVENLABS_VOICE', 'true').lower() == 'true'  # Control voice generation 