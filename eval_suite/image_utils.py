import os
import tempfile

import numpy as np
from PIL import Image, ImageOps
from moviepy import VideoFileClip

from eval_suite.prompts_raw import _image_eval
from eval_suite.utils import extract_json, convert_score_fields, calculate_geometric_mean
from mllm_tools.utils import _prepare_text_image_inputs
from src.core.parse_video import image_with_most_non_black_space

def extract_key_frames(video_path, output_dir, num_chunks):
    """Extract key frames from a video by dividing it into chunks and selecting representative frames.

    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory where extracted frames will be saved
        num_chunks (int): Number of chunks to divide the video into

    Returns:
        list: List of paths to the extracted key frames
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract all frames from the video
    clip = VideoFileClip(video_path)
    frames = list(clip.iter_frames(fps=1))  # one frame every second
    
    total_frames = len(frames)
    if total_frames == 0:
        print("No frames extracted from the video.")
        return []
    
    # Determine the number of frames per chunk
    frames_per_chunk = total_frames // num_chunks
    num_chunks = min(num_chunks, (total_frames + frames_per_chunk - 1) // frames_per_chunk)
    
    key_frames = []
    
    # Process each chunk of frames
    for i in range(num_chunks):
        start_idx = i * frames_per_chunk
        end_idx = min((i + 1) * frames_per_chunk, total_frames)
        chunk_frames = frames[start_idx:end_idx]
        
        if chunk_frames:
            # Save the frame with most non-black space
            output_path = os.path.join(output_dir, f"key_frame_{i+1}.jpg")
            result = image_with_most_non_black_space(chunk_frames, output_path)
        else:
            print(f"No frames in chunk {i+1}. Skipping.")
            result = None
        
        if result is not None:
            key_frames.append(output_path)
    clip.close()
    
    return key_frames


def evaluate_sampled_images(model, video_path, description="No description provided", num_chunks=10, output_folder=None):
    """Evaluate sampled frames from a video using an image evaluation model.

    Args:
        model: The image evaluation model to use
        video_path (str): Path to the input video file
        description (str, optional): Description of the video content. Defaults to "No description provided"
        num_chunks (int, optional): Number of chunks to divide the video into. Defaults to 10
        output_folder (str, optional): Directory for temporary files. Defaults to None

    Returns:
        dict: Dictionary containing evaluation scores and individual frame assessments with keys:
            - evaluation: Dictionary of averaged scores for each criterion
            - image_chunks: List of individual frame evaluation results
    """
    with tempfile.TemporaryDirectory(dir=output_folder) as temp_dir:
        key_frames = extract_key_frames(video_path, temp_dir, num_chunks)

        prompt = _image_eval.format(description=description)

        responses = []
        for key_frame in key_frames:
            inputs = _prepare_text_image_inputs(prompt, key_frame)
            response = model(inputs)
            response_json = extract_json(response)
            response_json = convert_score_fields(response_json)
            responses.append(response_json)

    criteria = list(responses[0]["evaluation"].keys())
    scores_dict = {c: [] for c in criteria}
    for response in responses:
        for key, val in response["evaluation"].items():
            scores_dict[key].append(val["score"])

    res_score = {}
    for key, scores in scores_dict.items():
        res_score[key] = {"score": calculate_geometric_mean(scores)}

    return {
        "evaluation": res_score,
        "image_chunks": responses
    }
