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
    
    # AI Model configurations - configurable from environment variables
    DEFAULT_PLANNER_MODEL = os.getenv('DEFAULT_PLANNER_MODEL', 'gemini/gemini-2.5-pro')
    DEFAULT_SCENE_MODEL = os.getenv('DEFAULT_SCENE_MODEL', 'gemini/gemini-2.5-pro')
    DEFAULT_HELPER_MODEL = os.getenv('DEFAULT_HELPER_MODEL', 'gemini/gemini-2.5-pro')
    DEFAULT_EVALUATION_TEXT_MODEL = os.getenv('DEFAULT_EVALUATION_TEXT_MODEL', 'azure/gpt-4o')
    DEFAULT_EVALUATION_VIDEO_MODEL = os.getenv('DEFAULT_EVALUATION_VIDEO_MODEL', 'gemini/gemini-2.5-pro')
    DEFAULT_EVALUATION_IMAGE_MODEL = os.getenv('DEFAULT_EVALUATION_IMAGE_MODEL', 'azure/gpt-4o')
    
    # Temperature and model parameters - configurable from environment variables
    DEFAULT_MODEL_TEMPERATURE = float(os.getenv('DEFAULT_MODEL_TEMPERATURE', '0.7'))
    DEFAULT_MAX_RETRIES = int(os.getenv('DEFAULT_MAX_RETRIES', '5'))
    DEFAULT_MAX_SCENE_CONCURRENCY = int(os.getenv('DEFAULT_MAX_SCENE_CONCURRENCY', '5'))
    
    # ElevenLabs TTS configurations
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_DEFAULT_VOICE_ID = os.getenv('ELEVENLABS_DEFAULT_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
    _voice_flag = os.getenv('ELEVENLABS_VOICE', os.getenv('ELEVENLABS', 'false')).lower()
    ELEVENLABS_VOICE = _voice_flag == 'true' 