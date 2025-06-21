import os
import re
import subprocess
import asyncio
from PIL import Image
from typing import Optional, List
import traceback
import sys

from src.core.parse_video import (
    get_images_from_video,
    image_with_most_non_black_space
)
try:
    from mllm_tools.vertex_ai import VertexAIWrapper
except ImportError:
    VertexAIWrapper = None
from mllm_tools.gemini import GeminiWrapper

class VideoRenderer:
    """Class for rendering and combining Manim animation videos."""

    def __init__(self, output_dir="output", print_response=False, use_visual_fix_code=False):
        """Initialize the VideoRenderer.

        Args:
            output_dir (str, optional): Directory for output files. Defaults to "output".
            print_response (bool, optional): Whether to print responses. Defaults to False.
            use_visual_fix_code (bool, optional): Whether to use visual fix code. Defaults to False.
        """
        self.output_dir = output_dir
        self.print_response = print_response
        self.use_visual_fix_code = use_visual_fix_code

    async def render_scene(self, code: str, file_prefix: str, curr_scene: int, curr_version: int, code_dir: str, media_dir: str, max_retries: int = 3, use_visual_fix_code=False, visual_self_reflection_func=None, banned_reasonings=None, scene_trace_id=None, topic=None, session_id=None, on_success_callback=None):
        """Render a single Manim scene with the given code.

        Args:
            code (str): Python code to render
            file_prefix (str): Prefix for output files  
            curr_scene (int): Current scene number
            curr_version (int): Current version number
            code_dir (str): Directory to save code files
            media_dir (str): Directory for Manim media output
            max_retries (int, optional): Maximum retry attempts. Defaults to 3.
            use_visual_fix_code (bool, optional): Use visual error fixing. Defaults to False.
            visual_self_reflection_func: Function for visual reflection
            banned_reasonings: List of banned reasoning patterns
            scene_trace_id: Trace ID for this scene
            topic: Video topic
            session_id: Session ID
            on_success_callback: Async callback function to call on successful render

        Returns:
            tuple: (code, error_message) where error_message is None on success
        """
        retries = 0
        file_path = os.path.join(code_dir, f"{file_prefix}_scene{curr_scene}_v{curr_version}.py")
        scene_dir = os.path.join(self.output_dir, file_prefix, f"scene{curr_scene}")
        
        # Save code to file
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(code)

        # Render the scene
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            # Use 'manim' command directly since it's in the virtual environment
            manim_command = "manim"
            process_env = os.environ.copy()
            if 'PYTHONPATH' in process_env:
                process_env['PYTHONPATH'] = f"{project_root}{os.pathsep}{process_env['PYTHONPATH']}"
            else:
                process_env['PYTHONPATH'] = project_root
            result = subprocess.run(
                [manim_command, "-qh", file_path, "--media_dir", media_dir],
                capture_output=True,
                text=True,
                env=process_env
            )
            
            if result.returncode != 0:
                raise Exception(result.stderr)
                
        except Exception as e:
            print(f"Error: {e}")
            print(f"Retrying {retries+1} of {max_retries}...")

            with open(os.path.join(code_dir, f"{file_prefix}_scene{curr_scene}_v{curr_version}_error.log"), "a") as f:
                f.write(f"\nError in attempt {retries}:\n{str(e)}\n")
            retries += 1
            return code, str(e) # Indicate failure and return error message
        
        print(f"Successfully rendered {file_path}")
        with open(os.path.join(self.output_dir, file_prefix, f"scene{curr_scene}", "succ_rendered.txt"), "w") as f:
            f.write("")

        # Call the success callback if provided (for uploading scene videos)
        if on_success_callback:
            try:
                await on_success_callback(curr_scene, file_path, scene_dir)
            except Exception as e:
                print(f"⚠️ Scene upload callback failed: {e}")

        return code, None # Indicate success

    def run_manim_process(self,
                          topic: str):
        """Run manim on all generated manim code for a specific topic.

        Args:
            topic (str): Topic name to process

        Returns:
            subprocess.CompletedProcess: Result of the final manim process
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        search_path = os.path.join(self.output_dir, file_prefix)
        # Iterate through scene folders
        scene_folders = [f for f in os.listdir(search_path) if os.path.isdir(os.path.join(search_path, f))]
        scene_folders.sort()  # Sort to process scenes in order

        for folder in scene_folders:
            folder_path = os.path.join(search_path, folder)

            # Get all Python files in version order
            py_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
            py_files.sort(key=lambda x: int(x.split('_v')[-1].split('.')[0]))  # Sort by version number

            for file in py_files:
                file_path = os.path.join(folder_path, file)
                try:
                    media_dir = os.path.join(self.output_dir, file_prefix, "media")
                    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    # Use 'manim' command directly since it's in the virtual environment
                    manim_command = "manim"
                    process_env = os.environ.copy()
                    if 'PYTHONPATH' in process_env:
                        process_env['PYTHONPATH'] = f"{project_root}{os.pathsep}{process_env['PYTHONPATH']}"
                    else:
                        process_env['PYTHONPATH'] = project_root
                    result = subprocess.run(
                        [manim_command, "-qh", file_path, "--media_dir", media_dir],
                        capture_output=True,
                        text=True,
                        env=process_env
                    )
                    if result.returncode != 0:
                        raise Exception(result.stderr)
                    print(f"Successfully rendered {file}")
                    break  # Move to next scene folder if successful
                except Exception as e:
                    print(f"Error rendering {file}: {e}")
                    error_log_path = os.path.join(folder_path, f"{file.split('.')[0]}_error.log") # drop the extra py
                    with open(error_log_path, "w") as f:
                        f.write(f"Error:\n{str(e)}\n")
                    print(f"Error log saved to {error_log_path}")
        return result

    def create_snapshot_scene(self, topic: str, scene_number: int, version_number: int, return_type: str = "image"):
        """Create a snapshot of the video for a specific topic and scene.

        Args:
            topic (str): Topic name
            scene_number (int): Scene number
            version_number (int): Version number
            return_type (str, optional): Type of return value - "path" or "image". Defaults to "image".

        Returns:
            Union[str, PIL.Image]: Path to saved image or PIL Image object

        Raises:
            FileNotFoundError: If no mp4 files found in video folder
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        search_path = os.path.join(self.output_dir, file_prefix)
        video_folder_path = os.path.join(search_path, "media", "videos", f"{file_prefix}_scene{scene_number}_v{version_number}", "1080p60")
        os.makedirs(video_folder_path, exist_ok=True)
        snapshot_path = os.path.join(video_folder_path, "snapshot.png")
        # Get the mp4 video file from the video folder path
        video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]
        if not video_files:
            raise FileNotFoundError(f"No mp4 files found in {video_folder_path}")
        video_path = os.path.join(video_folder_path, video_files[0])
        saved_image = image_with_most_non_black_space(get_images_from_video(video_path), snapshot_path, return_type=return_type)
        return saved_image

    def combine_videos(self, topic: str):
        """Combine all videos and subtitle files for a specific topic using ffmpeg.

        Args:
            topic (str): Topic name to combine videos for

        This function will:
        - Find all scene videos and subtitles
        - Combine videos with or without audio
        - Merge subtitle files with correct timing
        - Save combined video and subtitles to output directory
        """
        file_prefix = topic.lower()
        file_prefix = re.sub(r'[^a-z0-9_]+', '_', file_prefix)
        search_path = os.path.join(self.output_dir, file_prefix, "media", "videos")

        # Create output directory if it doesn't exist
        video_output_dir = os.path.join(self.output_dir, file_prefix)
        os.makedirs(video_output_dir, exist_ok=True)

        output_video_path = os.path.join(video_output_dir, f"{file_prefix}_combined.mp4")
        output_srt_path = os.path.join(video_output_dir, f"{file_prefix}_combined.srt")
        
        if os.path.exists(output_video_path) and os.path.exists(output_srt_path):
            print(f"Combined video and subtitles already exist at {output_video_path}, not combining again.")
            return

        # Get scene count from outline
        scene_outline_path = os.path.join(self.output_dir, file_prefix, f"{file_prefix}_scene_outline.txt")
        if not os.path.exists(scene_outline_path):
            print(f"Warning: Scene outline file not found at {scene_outline_path}. Cannot determine scene count.")
            return
        
        with open(scene_outline_path) as f:
            plan = f.read()
        
        # Try to find scene outline in the old format first (with wrapper tags)
        scene_outline_match = re.search(r'(<SCENE_OUTLINE>.*?</SCENE_OUTLINE>)', plan, re.DOTALL)
        if scene_outline_match:
            scene_outline = scene_outline_match.group(1)
            scene_count = len(re.findall(r'<SCENE_(\d+)>[^<]', scene_outline))
        else:
            # New format: scenes are directly in the plan without wrapper tags
            scene_count = len(re.findall(r'<SCENE_(\d+)>[^<]', plan))
            if scene_count == 0:
                print(f"Warning: No scenes found in plan file. The plan generation might have failed.")
                print(f"Plan content preview: {plan[:500]}...")
                return
            print(f"Found {scene_count} scenes in plan file.")

        # Find all scene folders and videos
        scene_folders = []
        for root, dirs, files in os.walk(search_path):
            for dir in dirs:
                if dir.startswith(file_prefix + "_scene"):
                    scene_folders.append(os.path.join(root, dir))

        scene_videos = []
        scene_subtitles = []

        for scene_num in range(1, scene_count + 1):
            folders = [f for f in scene_folders if int(f.split("scene")[-1].split("_")[0]) == scene_num]
            if not folders:
                print(f"Warning: Missing scene {scene_num}")
                continue

            folders.sort(key=lambda f: int(f.split("_v")[-1]))
            folder = folders[-1]

            video_found = False
            subtitles_found = False
            for filename in os.listdir(os.path.join(folder, "1080p60")):
                if filename.endswith('.mp4'):
                    scene_videos.append(os.path.join(folder, "1080p60", filename))
                    video_found = True
                    print(f"Found video for scene {scene_num}: {filename}")
                elif filename.endswith('.srt'):
                    scene_subtitles.append(os.path.join(folder, "1080p60", filename))
                    subtitles_found = True

            if not video_found:
                print(f"Warning: Missing video for scene {scene_num}")
            if not subtitles_found:
                scene_subtitles.append(None)

        if len(scene_videos) == 0:
            print("No videos found for combination. Please ensure scenes are successfully rendered first.")
            return
        elif len(scene_videos) != scene_count:
            print(f"Warning: Expected {scene_count} videos but found {len(scene_videos)}. Proceeding with available videos.")

        try:
            import ffmpeg # You might need to install ffmpeg-python package: pip install ffmpeg-python
            from tqdm import tqdm

            print("Analyzing video streams...")
            # Check if videos have audio streams
            has_audio = []
            for video in tqdm(scene_videos, desc="Checking audio streams"):
                probe = ffmpeg.probe(video)
                audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
                has_audio.append(len(audio_streams) > 0)

            print("Preparing video combination...")
            
            # Simple approach: create a temporary file list for ffmpeg concat demuxer
            import tempfile
            temp_file_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            try:
                # Write file list for ffmpeg concat demuxer
                for video_path in scene_videos:
                    # Convert to absolute path and escape for ffmpeg
                    abs_path = os.path.abspath(video_path).replace('\\', '/')
                    temp_file_list.write(f"file '{abs_path}'\n")
                temp_file_list.close()
                
                print(f"Combining {len(scene_videos)} videos...")
                
                # Use simple ffmpeg concat demuxer (much more reliable)
                (
                    ffmpeg
                    .input(temp_file_list.name, format='concat', safe=0)
                    .output(output_video_path, 
                           **{'c': 'copy',  # Copy streams without re-encoding (much faster)
                              'avoid_negative_ts': 'make_zero'})
                    .overwrite_output()
                    .run()
                )
                
                print(f"Successfully combined videos into {output_video_path}")

            except ffmpeg.Error as e:
                print(f"FFmpeg concat failed, trying with re-encoding...")
                try:
                    # Fallback: re-encode if concat failed
                    inputs = [ffmpeg.input(video) for video in scene_videos]
                    (
                        ffmpeg
                        .concat(*inputs, v=1, a=1)
                        .output(output_video_path,
                               **{'c:v': 'libx264',
                                  'c:a': 'aac', 
                                  'preset': 'fast',
                                  'crf': '23'})
                        .overwrite_output()
                        .run()
                    )
                    print(f"Successfully combined videos with re-encoding into {output_video_path}")
                except ffmpeg.Error as e2:
                    print(f"FFmpeg re-encoding also failed. Error: {e2}")
                    raise
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_list.name)
                except OSError as e:
                    print(f"Warning: Could not delete temporary file {temp_file_list.name}: {e}")
                    pass

            # Handle subtitle combination (existing subtitle code remains the same)
            if scene_subtitles:
                with open(output_srt_path, 'w', encoding='utf-8') as outfile:
                    current_time_offset = 0
                    subtitle_index = 1

                    for srt_file, video_file in zip(scene_subtitles, scene_videos):
                        if srt_file is None:
                            continue

                        with open(srt_file, 'r', encoding='utf-8') as infile:
                            lines = infile.readlines()
                            i = 0
                            while i < len(lines):
                                line = lines[i].strip()
                                if line.isdigit():  # Subtitle index
                                    outfile.write(f"{subtitle_index}\n")
                                    subtitle_index += 1
                                    i += 1

                                    # Time codes line
                                    time_line = lines[i].strip()
                                    start_time, end_time = time_line.split(' --> ')

                                    # Convert time codes and add offset
                                    def adjust_time(time_str, offset):
                                        h, m, s = time_str.replace(',', '.').split(':')
                                        total_seconds = float(h) * 3600 + float(m) * 60 + float(s) + offset
                                        h = int(total_seconds // 3600)
                                        m = int((total_seconds % 3600) // 60)
                                        s = total_seconds % 60
                                        return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')

                                    new_start = adjust_time(start_time, current_time_offset)
                                    new_end = adjust_time(end_time, current_time_offset)
                                    outfile.write(f"{new_start} --> {new_end}\n")
                                    i += 1

                                    # Subtitle text (could be multiple lines)
                                    while i < len(lines) and lines[i].strip():
                                        outfile.write(lines[i])
                                        i += 1
                                    outfile.write('\n')
                                else:
                                    i += 1

                        # Update time offset using ffprobe
                        probe = ffmpeg.probe(video_file)
                        duration = float(probe['streams'][0]['duration'])
                        current_time_offset += duration

            print(f"Successfully combined videos into {output_video_path}")
            if scene_subtitles:
                print(f"Successfully combined subtitles into {output_srt_path}")

        except Exception as e:
            print(f"Error combining videos and subtitles: {e}")
            traceback.print_exc()