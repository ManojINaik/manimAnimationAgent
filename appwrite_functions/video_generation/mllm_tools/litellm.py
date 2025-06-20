import json
import re
from typing import List, Dict, Any, Union, Optional
import io
import os
import base64
from PIL import Image
import mimetypes
import litellm
from litellm import completion, completion_cost
from dotenv import load_dotenv
import random

load_dotenv()

class LiteLLMWrapper:
    """Wrapper for LiteLLM to support multiple models and logging"""
    
    def __init__(
        self,
        model_name: str = "gpt-4-vision-preview",
        temperature: float = 0.7,
        print_cost: bool = False,
        verbose: bool = False,
        use_langfuse: bool = False,
    ):
        """
        Initialize the LiteLLM wrapper
        
        Args:
            model_name: Name of the model to use (e.g. "azure/gpt-4", "vertex_ai/gemini-pro")
            temperature: Temperature for completion
            print_cost: Whether to print the cost of the completion
            verbose: Whether to print verbose output
            use_langfuse: Whether to enable Langfuse logging
        """
        self.model_name = model_name
        self.temperature = temperature
        self.print_cost = print_cost
        self.verbose = verbose
        self.accumulated_cost = 0
        
        # Handle Gemini API key fallback mechanism
        if "gemini" in model_name.lower():
            self._setup_gemini_api_key()

        if self.verbose:
            os.environ['LITELLM_LOG'] = 'DEBUG'
        
        # Set langfuse callback only if enabled and handle errors gracefully
        if use_langfuse:
            try:
                litellm.success_callback = ["langfuse"]
                litellm.failure_callback = ["langfuse"]
            except Exception as e:
                print(f"Warning: Failed to initialize Langfuse logging: {e}")
                print("Continuing without Langfuse logging...")
    
    def _setup_gemini_api_key(self):
        """Setup Gemini API key with fallback mechanism for multiple keys."""
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        gemini_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key_env:
            raise ValueError("No API_KEY found. Please set the `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable.")
        
        # Support comma-separated list of API keys with random selection
        if ',' in gemini_key_env:
            keys = [key.strip() for key in gemini_key_env.split(',') if key.strip()]
            if not keys:
                raise ValueError("No valid API keys found in GEMINI_API_KEY list.")
            api_key = random.choice(keys)
            print(f"Selected random Gemini API key from {len(keys)} available keys: {api_key[:20]}...")
        else:
            api_key = gemini_key_env
            print(f"Using single Gemini API key: {api_key[:20]}...")
        
        # Set the selected API key for LiteLLM
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key

    def _encode_file(self, file_path: Union[str, Image.Image]) -> str:
        """
        Encode local file or PIL Image to base64 string
        
        Args:
            file_path: Path to local file or PIL Image object
            
        Returns:
            Base64 encoded file string
        """
        if isinstance(file_path, Image.Image):
            buffered = io.BytesIO()
            file_path.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode("utf-8")

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

    def __call__(self, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process messages and return completion
        
        Args:
            messages: List of message dictionaries with 'type' and 'content' keys
            metadata: Optional metadata to pass to litellm completion, e.g. for Langfuse tracking
        
        Returns:
            Generated text response
        """
        if metadata is None:
            print("No metadata provided, using empty metadata")
            metadata = {}
        metadata["trace_name"] = f"litellm-completion-{self.model_name}"
        # Convert messages to LiteLLM format
        formatted_messages = []
        for msg in messages:
            if msg["type"] == "text":
                formatted_messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": msg["content"]}]
                })
            elif msg["type"] in ["image", "audio", "video"]:
                # Check if content is a local file path or PIL Image
                if isinstance(msg["content"], Image.Image) or os.path.isfile(msg["content"]):
                    try:
                        if isinstance(msg["content"], Image.Image):
                            mime_type = "image/png"
                        else:
                            mime_type = self._get_mime_type(msg["content"])
                        base64_data = self._encode_file(msg["content"])
                        data_url = f"data:{mime_type};base64,{base64_data}"
                    except ValueError as e:
                        print(f"Error processing file {msg['content']}: {e}")
                        continue
                else:
                    data_url = msg["content"]
                
                # Append the formatted message based on the model
                if "gemini" in self.model_name:
                    formatted_messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": data_url
                            }
                        ]
                    })
                elif "gpt" in self.model_name:
                    # GPT and other models expect a different format
                    if msg["type"] == "image":
                        # Default format for images and videos in GPT
                        formatted_messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": f"image_url", 
                                    f"{msg['type']}_url": {
                                        "url": data_url,
                                        "detail": "high"  
                                    }
                                }
                            ]
                        })
                    else:
                        raise ValueError("For GPT, only text and image inferencing are supported")
                else:
                    raise ValueError("Only support Gemini and Gpt for Multimodal capability now")

        try:
            # if it's openai o series model, set temperature to None and reasoning_effort to "medium"
            if (re.match(r"^o\d+.*$", self.model_name) or re.match(r"^openai/o.*$", self.model_name)):
                self.temperature = None
                self.reasoning_effort = "medium"
                response = completion(
                    model=self.model_name,
                    messages=formatted_messages,
                    temperature=self.temperature,
                    reasoning_effort=self.reasoning_effort,
                    metadata=metadata,
                    max_retries=99
                )
            else:
                response = completion(
                    model=self.model_name,
                    messages=formatted_messages,
                    temperature=self.temperature,
                    metadata=metadata,
                    max_retries=99
                )
            if self.print_cost:
                # pass your response from completion to completion_cost
                cost = completion_cost(completion_response=response)
                formatted_string = f"Cost: ${float(cost):.10f}"
                # print(formatted_string)
                self.accumulated_cost += cost
                print(f"Accumulated Cost: ${self.accumulated_cost:.10f}")
                
            content = response.choices[0].message.content
            if content is None:
                print(f"Got null response from model. Full response: {response}")
                raise ValueError(f"Model {self.model_name} returned None content. Full response: {response}")
            return content
        
        except Exception as e:
            print(f"Error in model completion: {e}")
            return str(e)
        
if __name__ == "__main__":
    pass