from typing import List, Dict, Any, Union, Optional
import io
import os
import base64
from PIL import Image
import mimetypes
import google.generativeai as genai
import tempfile
import time
from urllib.parse import urlparse
import requests
from io import BytesIO

class GeminiWrapper:
    """Wrapper for Gemini to support multiple models and logging"""
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-pro-002",
        temperature: float = 0.7,
        print_cost: bool = False,
        verbose: bool = False,
        use_langfuse: bool = False
    ):
        """
        Initialize the Gemini wrapper
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for completion
            print_cost: Whether to print the cost of the completion
            verbose: Whether to print verbose output
            use_langfuse: Whether to enable Langfuse logging
        """
        self.model_name = model_name.split('/')[-1] if '/' in model_name else model_name
        self.temperature = temperature
        self.print_cost = print_cost
        self.verbose = verbose
        self.accumulated_cost = 0

        # Implement fallback mechanism for multiple API keys
        gemini_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key_env:
            raise ValueError("No API_KEY found. Please set the `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable.")
        
        # Support comma-separated list of API keys with random selection
        import random
        if ',' in gemini_key_env:
            # If GEMINI_API_KEY includes commas, treat it as a list of keys and choose a random one
            keys = gemini_key_env.split(',')
            keys = [key.strip() for key in keys if key.strip()]  # Clean whitespace and filter empty keys
            if not keys:
                raise ValueError("No valid API keys found in GEMINI_API_KEY list.")
            api_key = random.choice(keys)
        else:
            # Otherwise, treat it as a single key
            api_key = gemini_key_env
            
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": self.temperature,
            "top_p": 0.95,
            "response_mime_type": "text/plain",
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=safety_settings,
            generation_config=generation_config,
        )

    def _get_mime_type(self, file_path: str) -> str:
        """
        Get the MIME type of a file based on its extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type as a string (e.g., "image/jpeg", "audio/mp3")
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            raise ValueError(f"Unsupported file type: {file_path}")
        return mime_type

    def _download_file(self, url: str) -> str:
        """
        Download a file from a URL and save it as a temporary file
        
        Args:
            url: URL of the file to download
            
        Returns:
            Path to the temporary file
        """
        response = requests.get(url)
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name
        else:
            raise ValueError(f"Failed to download file from URL: {url}")

    def _save_image_to_temp(self, image: Image.Image) -> str:
        """
        Save a PIL Image to a temporary file
        
        Args:
            image: PIL Image object
            
        Returns:
            Path to the temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.save(temp_file, format="PNG")
        temp_file.close()
        return temp_file.name

    def _upload_to_gemini(self, file_path: str, mime_type: Optional[str] = None):
        """
        Uploads the given file to Gemini.
        
        Args:
            file_path: Path to the file
            mime_type: MIME type of the file
            
        Returns:
            Uploaded file object
        """
        return genai.upload_file(file_path, mime_type=mime_type)

    def __call__(self, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process messages and return completion
        
        Args:
            messages: List of message dictionaries with 'type' and 'content' keys
            metadata: Optional metadata to pass to Gemini completion
        
        Returns:
            Generated text response
        """
        contents = []
        for msg in messages:
            if msg["type"] == "text":
                contents.append(msg["content"])
            elif msg["type"] in ["image", "audio", "video"]:
                if isinstance(msg["content"], Image.Image):
                    file_path = self._save_image_to_temp(msg["content"])
                    mime_type = "image/png"
                elif isinstance(msg["content"], str):
                    if msg["content"].startswith("http"):
                        file_path = self._download_file(msg["content"])
                        mime_type = self._get_mime_type(msg["content"])
                    else:
                        file_path = msg["content"]
                        mime_type = self._get_mime_type(file_path)
                else:
                    raise ValueError("Unsupported content type")

                uploaded_file = self._upload_to_gemini(file_path, mime_type)

                while uploaded_file.state.name == "PROCESSING":
                    print('.', end='')
                    time.sleep(3)
                    uploaded_file = genai.get_file(uploaded_file.name)
                if uploaded_file.state.name == "FAILED":
                    raise ValueError(uploaded_file.state.name)
                print("Upload successfully")
                contents.append(uploaded_file)
            else:
                raise ValueError("Unsupported message type")

        response = self.model.generate_content(contents, request_options={"timeout": 600})
        try:
            return response.text
        except Exception as e:
            print(e)
            print(response.prompt_feedback)
            return str(response.prompt_feedback)

if __name__ == "__main__":
    pass