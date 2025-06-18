import os
from tqdm import tqdm


def call_parse_prompt():
    """
    Locates the prompts_raw directory and generates an __init__.py file containing prompt texts.

    Searches for prompts_raw directory in current and parent directories. Once found, calls
    create_python_file_with_texts() to generate the __init__.py file.
    """
    current_file_path = os.path.abspath(__file__)
    current_folder_path = os.path.dirname(current_file_path)
    folder_path = os.path.join(current_folder_path, "prompts_raw")
    
    # If prompts_raw not found in current directory, search parent directories
    if not os.path.exists(folder_path):
        parent_dir = current_folder_path
        while parent_dir != os.path.dirname(parent_dir):  # Stop at root directory
            parent_dir = os.path.dirname(parent_dir)
            test_path = os.path.join(parent_dir, "prompts_raw")
            if os.path.exists(test_path):
                folder_path = test_path
                break
    
    output_file = os.path.join(folder_path, "__init__.py")
    create_python_file_with_texts(folder_path, output_file)


def create_python_file_with_texts(folder_path, output_file):
    """
    Creates a Python file containing prompt texts from .txt files.

    Args:
        folder_path (str): Path to directory containing prompt .txt files
        output_file (str): Path where the output __init__.py file will be created

    The function reads all .txt files in the given folder, converts their contents into
    Python variables, and writes them to the output file. Variable names are derived from
    file paths with special characters replaced.
    """
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write("# This file is generated automatically through parse_prompt.py\n\n")
        txt_files = [file for root, dirs, files in os.walk(folder_path) for file in files if file.endswith(".txt")]
        for file in tqdm(txt_files, desc="Processing files"):
            file_path = os.path.join(folder_path, file)
            var_name = "_" + file_path.replace(folder_path, "").replace(os.sep, "_").replace(".txt", "").strip("_")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().replace('"""', '\"\"\"')
                out_file.write(f'{var_name} = """{content}"""\n\n')


if __name__ == "__main__":
    call_parse_prompt()