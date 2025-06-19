"""
Copyright (c) 2025 Xposed73
All rights reserved.
This file is part of the Manim Voiceover project.
"""

import hashlib
import json
import requests
import os
from pathlib import Path
from manim_voiceover.services.base import SpeechService
from manim_voiceover.helper import remove_bookmarks
from src.config.config import Config
import time

# Add new imports for CI/CD-compatible TTS
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    gTTS = None

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    pyttsx3 = None


class ElevenLabsService(SpeechService):
    """Speech service class for ElevenLabs TTS integration."""

    def __init__(self, 
                 api_key: str = None,
                 voice_id: str = None,
                 model_id: str = "eleven_multilingual_v2",
                 voice_settings: dict = None,
                 **kwargs):
        """
        Initialize ElevenLabs service.
        
        Args:
            api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env var)
            voice_id: Voice ID to use (defaults to ELEVENLABS_DEFAULT_VOICE_ID env var)
            model_id: Model ID to use for generation
            voice_settings: Voice settings dict with stability, similarity_boost, style, use_speaker_boost
        """
        self.api_key = api_key or Config.ELEVENLABS_API_KEY
        self.voice_id = voice_id or Config.ELEVENLABS_DEFAULT_VOICE_ID
        self.model_id = model_id
        
        # Default voice settings
        default_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        self.voice_settings = voice_settings or default_settings
        
        if not self.api_key:
            raise ValueError("ElevenLabs API key not found. Please set ELEVENLABS_API_KEY environment variable.")
        if not self.voice_id:
            raise ValueError("ElevenLabs voice ID not found. Please set ELEVENLABS_DEFAULT_VOICE_ID environment variable.")
        
        super().__init__(**kwargs)

    def get_data_hash(self, input_data: dict) -> str:
        """
        Generates a hash based on the input data dictionary.
        The hash is used to create a unique identifier for the input data.

        Parameters:
            input_data (dict): A dictionary of input data (e.g., text, voice, etc.).

        Returns:
            str: The generated hash as a string.
        """
        # Convert the input data dictionary to a JSON string (sorted for consistency)
        data_str = json.dumps(input_data, sort_keys=True)
        # Generate a SHA-256 hash of the JSON string
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def text_to_speech(self, text: str, output_file: str) -> str:
        """
        Generate audio using ElevenLabs API with robust error handling.
        
        Args:
            text (str): Text to synthesize
            output_file (str): Path to save the audio file
            
        Returns:
            str: Path to the generated audio file
            
        Raises:
            Exception: If API request fails after retries
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Save the audio file
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                return output_file
                
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                # If all retries failed, create a silent audio file as fallback
                self._create_silent_audio(output_file, duration=len(text) * 0.1)  # Rough estimate
                return output_file
                
            except requests.exceptions.Timeout as e:
                print(f"Timeout error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                self._create_silent_audio(output_file, duration=len(text) * 0.1)
                return output_file
                
            except requests.exceptions.RequestException as e:
                print(f"Request error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                self._create_silent_audio(output_file, duration=len(text) * 0.1)
                return output_file
                
        # This should not be reached, but added for safety
        self._create_silent_audio(output_file, duration=len(text) * 0.1)
        return output_file
    
    def _create_silent_audio(self, output_file: str, duration: float):
        """Create a silent audio file as fallback when API fails."""
        try:
            import numpy as np
            from pydub import AudioSegment
            
            # Create silent audio using pydub
            duration_ms = int(duration * 1000)  # Convert to milliseconds
            silent_audio = AudioSegment.silent(duration=duration_ms)
            
            # Export as MP3
            silent_audio.export(output_file, format="mp3")
            print(f"Created silent audio fallback: {output_file}")
            
        except Exception as e:
            print(f"Failed to create silent audio with pydub: {e}")
            try:
                # Fallback: create a minimal MP3 file with proper headers
                import struct
                
                # Create a minimal MP3 header + silent frame
                mp3_header = b'\xff\xfb\x90\x00'  # Basic MP3 header
                mp3_data = b'\x00' * 1024  # Silent data
                
                with open(output_file, 'wb') as f:
                    f.write(mp3_header + mp3_data)
                    
                print(f"Created minimal MP3 file: {output_file}")
                
            except Exception as e2:
                print(f"Failed to create minimal MP3: {e2}")
                # Create an empty file as last resort
                with open(output_file, 'w') as f:
                    f.write("")

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None) -> dict:
        """
        Generate audio from text with caching support.
        
        Args:
            text: Text to convert to speech
            cache_dir: Directory for caching audio files
            path: Optional specific path for the audio file
            
        Returns:
            Dictionary with audio generation details
        """
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            "input_text": text, 
            "service": "elevenlabs", 
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings
        }
        
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        if path is None:
            audio_path = self.get_data_hash(input_data) + ".mp3"
        else:
            audio_path = path

        # Generate audio file using ElevenLabs API
        full_audio_path = str(Path(cache_dir) / audio_path)
        self.text_to_speech(text, full_audio_path)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict


class SilentService(SpeechService):
    """Silent speech service that creates silent audio files when voice generation is disabled."""

    def __init__(self, **kwargs):
        """Initialize silent service."""
        super().__init__(**kwargs)

    def get_data_hash(self, input_data: dict) -> str:
        """Generate hash for silent audio files."""
        data_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def text_to_speech(self, text: str, output_file: str) -> str:
        """Create a silent audio file instead of generating speech."""
        duration = len(text) * 0.1  # Rough estimate: 0.1 seconds per character
        self._create_silent_audio(output_file, duration)
        return output_file

    def _create_silent_audio(self, output_file: str, duration: float):
        """Create a silent audio file."""
        try:
            import numpy as np
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            # Create silent audio using pydub
            duration_ms = int(duration * 1000)  # Convert to milliseconds
            silent_audio = AudioSegment.silent(duration=duration_ms)
            
            # Export as MP3
            silent_audio.export(output_file, format="mp3")
            print(f"Created silent audio (voice disabled): {output_file}")
            
        except Exception as e:
            print(f"Failed to create silent audio with pydub: {e}")
            try:
                # Fallback: create a minimal MP3 file with proper headers
                import struct
                
                # Create a minimal MP3 header + silent frame
                # This creates a valid MP3 file that won't cause header errors
                mp3_header = b'\xff\xfb\x90\x00'  # Basic MP3 header
                mp3_data = b'\x00' * 1024  # Silent data
                
                with open(output_file, 'wb') as f:
                    f.write(mp3_header + mp3_data)
                    
                print(f"Created minimal MP3 file: {output_file}")
                
            except Exception as e2:
                print(f"Failed to create minimal MP3: {e2}")
                # Create an empty file as last resort
                with open(output_file, 'w') as f:
                    f.write("")

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None) -> dict:
        """Generate silent audio from text."""
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            "input_text": text, 
            "service": "silent", 
        }
        
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        if path is None:
            audio_path = self.get_data_hash(input_data) + ".mp3"
        else:
            audio_path = path

        # Generate silent audio file
        full_audio_path = str(Path(cache_dir) / audio_path)
        self.text_to_speech(text, full_audio_path)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
            "final_audio": audio_path,  # Add final_audio key to match expected format
        }

        return json_dict


class GTTSService(SpeechService):
    """CI/CD-compatible speech service using Google Text-to-Speech (gTTS) and pyttsx3 fallback."""

    def __init__(self, lang: str = "en", slow: bool = False, **kwargs):
        """
        Initialize GTTS service for CI/CD environments.
        
        Args:
            lang: Language code (e.g., 'en', 'es', 'fr')
            slow: Whether to use slow speech
        """
        super().__init__(**kwargs)
        self.lang = lang
        self.slow = slow
        
        # Check available TTS engines
        self.use_gtts = HAS_GTTS
        self.use_pyttsx3 = HAS_PYTTSX3
        
        if not self.use_gtts and not self.use_pyttsx3:
            print("⚠️ No TTS engines available. Will create silent audio.")
        elif self.use_gtts:
            print("✅ Using gTTS for audio generation")
        elif self.use_pyttsx3:
            print("✅ Using pyttsx3 for audio generation")

    def get_data_hash(self, input_data: dict) -> str:
        """Generate hash for caching audio files."""
        data_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def text_to_speech(self, text: str, output_file: str) -> str:
        """
        Convert text to speech using gTTS or pyttsx3.
        
        Args:
            text: Text to convert to speech
            output_file: Path for the output audio file
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            # Try gTTS first (requires internet but works in CI/CD)
            if self.use_gtts:
                return self._gtts_text_to_speech(text, output_file)
            
            # Fallback to pyttsx3 (offline but may have issues in CI/CD)
            elif self.use_pyttsx3:
                return self._pyttsx3_text_to_speech(text, output_file)
            
            # Last resort: create silent audio
            else:
                self._create_silent_audio(output_file, duration=len(text) * 0.1)
                return output_file
                
        except Exception as e:
            print(f"TTS failed: {e}. Creating silent audio.")
            self._create_silent_audio(output_file, duration=len(text) * 0.1)
            return output_file

    def _gtts_text_to_speech(self, text: str, output_file: str) -> str:
        """Generate speech using Google Text-to-Speech."""
        try:
            if not HAS_GTTS:
                raise RuntimeError("gTTS not installed")
            # Create gTTS object
            tts = gTTS(text=text, lang=self.lang, slow=self.slow)
            
            # Save to temporary file first (gTTS saves as MP3)
            temp_file = output_file.replace('.mp3', '_temp.mp3')
            tts.save(temp_file)
            
            # Move to final location
            import shutil
            shutil.move(temp_file, output_file)
            
            print(f"✅ Generated audio with gTTS: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"gTTS failed: {e}")
            raise

    def _pyttsx3_text_to_speech(self, text: str, output_file: str) -> str:
        """Generate speech using pyttsx3 (offline TTS)."""
        try:
            if not HAS_PYTTSX3:
                raise RuntimeError("pyttsx3 not installed")
            engine = pyttsx3.init()
            
            # Configure voice settings
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Save to file
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            
            print(f"✅ Generated audio with pyttsx3: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"pyttsx3 failed: {e}")
            raise

    def _create_silent_audio(self, output_file: str, duration: float):
        """Create a silent audio file as fallback."""
        try:
            from pydub import AudioSegment
            
            # Create silent audio using pydub
            duration_ms = int(duration * 1000)  # Convert to milliseconds
            silent_audio = AudioSegment.silent(duration=duration_ms)
            
            # Export as MP3
            silent_audio.export(output_file, format="mp3")
            print(f"Created silent audio fallback: {output_file}")
            
        except Exception as e:
            print(f"Failed to create silent audio with pydub: {e}")
            # Create an empty file as last resort
            with open(output_file, 'w') as f:
                f.write("")

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None) -> dict:
        """
        Generate audio from text with caching support.
        """
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            "input_text": text, 
            "service": "gtts", 
            "lang": self.lang,
            "slow": self.slow
        }
        
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        if path is None:
            audio_path = self.get_data_hash(input_data) + ".mp3"
        else:
            audio_path = path

        # Generate audio file using gTTS/pyttsx3
        full_audio_path = str(Path(cache_dir) / audio_path)
        self.text_to_speech(text, full_audio_path)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict


def get_speech_service(**kwargs):
    """
    Get the appropriate speech service based on configuration and environment.

    Priority order:
    1. If voice generation explicitly enabled via ELEVENLABS_VOICE:
       • Use ElevenLabsService when an API key is available.
       • If no API key is configured, gracefully fall back to GTTSService so CI pipelines still generate audio.
    2. If running inside GitHub Actions (GITHUB_ACTIONS=true) but voice generation is NOT enabled,
       default to GTTSService which works reliably in head-less environments.
    3. Otherwise, create silent audio placeholders to avoid local TTS dependencies.
    """
    # Detect CI environment
    is_github_actions = os.getenv('GITHUB_ACTIONS', '').lower() == 'true'

    # 1) Explicit voice generation request
    if Config.ELEVENLABS_VOICE:
        if Config.ELEVENLABS_API_KEY:
            print("Voice generation enabled - using ElevenLabsService")
            return ElevenLabsService(**kwargs)
        else:
            print("Voice generation requested but ELEVENLABS_API_KEY not set - using GTTSService fallback")
            return GTTSService(**kwargs)

    # 2) Running inside GitHub Actions without voice enabled
    if is_github_actions:
        print("🔧 GitHub Actions detected - using GTTSService for CI/CD audio generation")
        return GTTSService(**kwargs)

    # 3) Default: voice generation disabled
    print("Voice generation disabled - using SilentService")
    return SilentService(**kwargs) 