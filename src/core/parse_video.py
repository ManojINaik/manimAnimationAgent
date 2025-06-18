import os
import pysrt
from moviepy import VideoFileClip
import shutil
from PIL import Image, ImageOps
import numpy as np
import speech_recognition as sr

def get_images_from_video(video_path, fps=0.2):
    """Extract frames from a video file at specified FPS.

    Args:
        video_path (str): Path to the video file.
        fps (float, optional): Frames per second to extract. Defaults to 0.2.

    Returns:
        list: List of frames as numpy arrays.
    """
    clip = VideoFileClip(video_path)
    images = clip.iter_frames(fps=fps)
    return images

def image_with_most_non_black_space(images, output_path, return_type="path"):
    """Find and save the image with the most non-black space from a list of images.

    Args:
        images (list): List of image file paths, PIL Image objects, or numpy arrays.
        output_path (str): Path where the output image should be saved.
        return_type (str, optional): Type of return value - "path" or "image". Defaults to "path".

    Returns:
        Union[str, PIL.Image, None]: Path to saved image, PIL Image object, or None if no valid image found.
    """
    max_non_black_area = 0
    image_with_max_non_black_space = None

    for img in images:
        try:
            # If img is a path, open the image
            if isinstance(img, str):
                image = Image.open(img)
            elif isinstance(img, Image.Image):
                image = img
            elif isinstance(img, np.ndarray):
                image = Image.fromarray(img)
            else:
                print(f"Unsupported type: {type(img)}. Skipping.")
                continue

            # Convert to grayscale
            gray = ImageOps.grayscale(image)

            # Convert to numpy array
            gray_array = np.array(gray)

            # Count non-black pixels (threshold to consider near-black as black)
            non_black_pixels = np.sum(gray_array > 10)  # Threshold 10 to account for slight variations in black

            if non_black_pixels > max_non_black_area:
                max_non_black_area = non_black_pixels
                image_with_max_non_black_space = image

        except Exception as e:
            print(f"Warning: Unable to process image {img}: {e}")

    if image_with_max_non_black_space is not None:
        image_with_max_non_black_space.save(output_path)
        print(f"Saved image with most non-black space to {output_path}")
        
        if return_type == "path":
            return output_path
        else:
            return image_with_max_non_black_space
    return image_with_max_non_black_space

def parse_srt_to_text(output_dir, topic_name):
    """Convert SRT subtitle file to plain text.

    Args:
        output_dir (str): Directory containing the topic folders.
        topic_name (str): Name of the topic/video.
    """
    topic_name = topic_name.replace(" ", "_").lower()
    srt_path = os.path.join(output_dir, topic_name, f"{topic_name}_combined.srt")
    txt_path = os.path.join(output_dir, topic_name, f"{topic_name}_combined.txt")
    subs = pysrt.open(srt_path)
    
    with open(txt_path, 'w') as f:
        full_text = ""
        for sub in subs:
            sub.text = sub.text.replace("...", ".")
            full_text += sub.text + " "
        f.write(full_text.strip())

def parse_srt_and_extract_frames(output_dir, topic_name):
    """Extract frames from video at subtitle timestamps and save with corresponding text.

    Args:
        output_dir (str): Directory containing the topic folders.
        topic_name (str): Name of the topic/video.
    """
    topic_name = topic_name.replace(" ", "_").lower()
    video_path = os.path.join(output_dir, topic_name, f"{topic_name}_combined.mp4")
    srt_path = os.path.join(output_dir, topic_name, f"{topic_name}_combined.srt")
    subs = pysrt.open(srt_path)
    
    # Create extract_images folder if it doesn't exist
    images_dir = os.path.join(output_dir, topic_name, "extract_images")
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    os.makedirs(images_dir)
    
    # Load the video file
    video = VideoFileClip(video_path)
    
    # Dictionary to store image-text pairs
    pairs = {}
    
    i = 0
    while i < len(subs):
        sub = subs[i]
        text = sub.text
        sub_indexes = [sub.index]
        
        # Check if we need to concatenate with next subtitle
        while i < len(subs) - 1 and not text.strip().endswith('.'):
            i += 1
            next_sub = subs[i]
            text += " " + next_sub.text
            sub_indexes.append(next_sub.index)
        
        # Get the end time of the last concatenated subtitle
        end_time = sub.end.to_time()
        # Convert end time to seconds
        end_time_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second + end_time.microsecond / 1e6
        
        # Save the frame as an image in extract_images folder
        frame_path = os.path.join(images_dir, f"{sub.index}.jpg")
        video.save_frame(frame_path, t=end_time_seconds)
        
        # Save the subtitle text to a txt file
        text_path = os.path.join(images_dir, f"{sub.index}.txt")
        with open(text_path, 'w') as f:
            f.write(text)

        # Add pair to dictionary
        pairs[str(sub.index)] = {
            "image_path": f"{sub.index}.jpg",
            "text": text,
            "text_path": f"{sub.index}.txt",
            "srt_index": sub_indexes,
        }
        
        i += 1
    
    # Save pairs to json file
    import json
    json_path = os.path.join(images_dir, "pairs.json")
    with open(json_path, 'w') as f:
        json.dump(pairs, f, indent=4)
    
    # Close the video file
    video.close()

def extract_trasnscript(video_path):
    """Extract transcript from video audio using Google Speech Recognition.

    Args:
        video_path (str): Path to the video file.

    Returns:
        str: Transcribed text from the video audio.

    Raises:
        FileNotFoundError: If video file does not exist.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    clip = VideoFileClip(video_path)

    # write the video to a temporary audio file
    audio_path = os.path.join(os.path.dirname(video_path), "audio.wav")
    clip.audio.write_audiofile(audio_path)

    try:
        # extract the subtitles from the audio file
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    finally:
        # clean up the temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    import argparse
    
    def process_all_topics(output_folder):
        """Process all topic folders in the output directory.

        Args:
            output_folder (str): Directory containing the topic folders.
        """
        # Only get immediate subdirectories
        topics = [d for d in os.listdir(output_folder) 
                 if os.path.isdir(os.path.join(output_folder, d))]
        
        for topic in topics:
            print(f"\nProcessing topic: {topic}")
            try:
                parse_srt_to_text(output_folder, topic)
                parse_srt_and_extract_frames(output_folder, topic)
            except Exception as e:
                print(f"Error processing {topic}: {str(e)}")
                continue

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process video files and extract frames with subtitles')
    parser.add_argument('--output_dir', type=str, default="output",
                      help='Directory containing the topic folders')
    
    args = parser.parse_args()
    
    # Process topics using provided output directory
    process_all_topics(args.output_dir)