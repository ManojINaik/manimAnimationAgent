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
    EMBEDDING_MODEL = "gemini/text-embedding-004"
    
    # ElevenLabs TTS configurations
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_DEFAULT_VOICE_ID = os.getenv('ELEVENLABS_DEFAULT_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
    _voice_flag = os.getenv('ELEVENLABS_VOICE', os.getenv('ELEVENLABS', 'false')).lower()
    ELEVENLABS_VOICE = _voice_flag == 'true' 