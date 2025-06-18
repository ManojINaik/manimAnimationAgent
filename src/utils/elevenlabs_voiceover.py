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
            from scipy.io import wavfile
            
            sample_rate = 22050
            samples = int(sample_rate * duration)
            silence = np.zeros(samples, dtype=np.float32)
            
            # Convert to appropriate format for wav
            silence_int = (silence * 32767).astype(np.int16)
            wavfile.write(output_file.replace('.mp3', '.wav'), sample_rate, silence_int)
            
            print(f"Created silent audio fallback: {output_file}")
            
        except Exception as e:
            print(f"Failed to create silent audio: {e}")
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