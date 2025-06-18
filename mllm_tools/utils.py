from typing import Union, List, Dict, Any, Optional
from PIL import Image
import google.generativeai as genai
import tempfile
import os
from .gemini import GeminiWrapper
try:
    from .vertex_ai import VertexAIWrapper
except ImportError:
    VertexAIWrapper = None


def _prepare_text_inputs(texts: List[str]) -> List[Dict[str, str]]:
    """
    Converts a list of text strings into the input format for the Agent model.

    Args:
        texts (List[str]): The list of text strings to be processed.

    Returns:
        List[Dict[str, str]]: A list of dictionaries formatted for the Agent model.
    """
    inputs = []
    # Add each text string to the inputs
    if isinstance(texts, str):
        texts = [texts]
    for text in texts:
        inputs.append({
            "type": "text",
            "content": text
        })
    return inputs

def _prepare_text_image_inputs(texts: Union[str, List[str]], images: Union[str, Image.Image, List[Union[str, Image.Image]]]) -> List[Dict[str, str]]:
    """
    Converts text strings and images into the input format for the Agent model.

    Args:
        texts (Union[str, List[str]]): Text string(s) to be processed.
        images (Union[str, Image.Image, List[Union[str, Image.Image]]]): Image file path(s) or PIL Image object(s).
    Returns:
        List[Dict[str, str]]: A list of dictionaries formatted for the Agent model.
    """
    inputs = []
    # Add each text string to the inputs
    if isinstance(texts, str):
        texts = [texts]
    for text in texts:
        inputs.append({
            "type": "text",
            "content": text
        })
    if isinstance(images, (str, Image.Image)):
        images = [images]
    for image in images:
        inputs.append({
            "type": "image",
            "content": image
        })
    return inputs

def _prepare_text_video_inputs(texts: Union[str, List[str]], videos: Union[str, List[str]]) -> List[Dict[str, str]]:
    """
    Converts text strings and video file paths into the input format for the Agent model.

    Args:
        texts (Union[str, List[str]]): Text string(s) to be processed.
        videos (Union[str, List[str]]): Video file path(s).
    Returns:
        List[Dict[str, str]]: A list of dictionaries formatted for the Agent model.
    """
    inputs = []
    # Add each text string to the inputs
    if isinstance(texts, str):
        texts = [texts]
    for text in texts:
        inputs.append({
            "type": "text",
            "content": text
        })
    # Add each video file path to the inputs
    if isinstance(videos, str):
        videos = [videos]
    for video in videos:
        inputs.append({
            "type": "video",
            "content": video
        })
    return inputs

def _prepare_text_audio_inputs(texts: Union[str, List[str]], audios: Union[str, List[str]]) -> List[Dict[str, str]]:
    """
    Converts text strings and audio file paths into the input format for the Agent model.

    Args:
        texts (Union[str, List[str]]): Text string(s) to be processed.
        audios (Union[str, List[str]]): Audio file path(s).
    Returns:
        List[Dict[str, str]]: A list of dictionaries formatted for the Agent model.
    """
    inputs = []
    # Add each text string to the inputs
    if isinstance(texts, str):
        texts = [texts]
    for text in texts:
        inputs.append({
            "type": "text",
            "content": text
        })
    # Add each audio file path to the inputs
    if isinstance(audios, str):
        audios = [audios]
    for audio in audios:
        inputs.append({
            "type": "audio",
            "content": audio
        })
    return inputs

def _extract_code(text: str) -> str:
    """Helper to extract code block from model response, support Gemini style and OpenAI style"""
    try:
        # Find code between ```python and ``` tags
        start = text.split("```python\n")[-1]
        end = start.split("```")[0]
        return end.strip()
    except IndexError:
        return text
    
def _upload_to_gemini(input, mime_type=None):
    """Uploads the given file or PIL image to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    if isinstance(input, str):
        # Input is a file path
        file = genai.upload_file(input, mime_type=mime_type)
    elif isinstance(input, Image.Image):
        # Input is a PIL image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            input.save(tmp_file, format="JPEG")
            tmp_file_path = tmp_file.name
        file = genai.upload_file(tmp_file_path, mime_type=mime_type or "image/jpeg")
        os.remove(tmp_file_path)
    else:
        raise ValueError("Unsupported input type. Must be a file path or PIL Image.")

    #print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def get_media_wrapper(model_name: str) -> Optional[Union[GeminiWrapper, VertexAIWrapper]]:
    """Get appropriate wrapper for media handling based on model name"""
    if model_name.startswith('gemini/'):
        return GeminiWrapper(model_name=model_name.split('/')[-1])
    elif model_name.startswith('vertex_ai/'):
        return VertexAIWrapper(model_name=model_name.split('/')[-1])
    return None

def prepare_media_messages(prompt: str, media_path: Union[str, Image.Image], model_name: str) -> List[Dict[str, Any]]:
    """Prepare messages for media input based on model type"""
    is_video = isinstance(media_path, str) and media_path.endswith('.mp4')
    
    if is_video and (model_name.startswith('gemini/') or model_name.startswith('vertex_ai/')):
        return [
            {"type": "text", "content": prompt},
            {"type": "video", "content": media_path}
        ]
    else:
        # For images or non-Gemini/Vertex models
        if isinstance(media_path, str):
            media = Image.open(media_path)
        else:
            media = media_path
        return [
            {"type": "text", "content": prompt},
            {"type": "image", "content": media}
        ]