import json
import re
from math import prod
from typing import List

def extract_json(response: str) -> dict:
    """
    Extract JSON content from a string response.

    Args:
        response (str): String containing JSON content, possibly within code blocks.

    Returns:
        dict: Extracted and parsed JSON content.

    Raises:
        ValueError: If no valid JSON content could be extracted.
    """
    try:
        evaluation_json = json.loads(response)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract the content between ```json and ```
        match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if not match:
            # If no match for ```json, try to extract content between ``` and ```
            match = re.search(r'```\n(.*?)\n```', response, re.DOTALL)
        
        if match:
            evaluation_content = match.group(1)
            evaluation_json = json.loads(evaluation_content)
        else:
            raise ValueError("Failed to extract valid JSON content")
    return evaluation_json


def convert_score_fields(data: dict) -> dict:
    """
    Convert score fields in a dictionary to integers recursively.

    Args:
        data (dict): Dictionary containing score fields to convert.

    Returns:
        dict: Dictionary with score fields converted to integers.

    Raises:
        ValueError: If a score value cannot be converted to integer.
    """
    # Create a new dictionary with the converted values
    converted_data = {}
    for key, value in data.items():
        if key == "score":
            if isinstance(value, int):
                converted_data[key] = value
            elif isinstance(value, str) and value.isdigit():
                converted_data[key] = int(value)
            else:
                raise ValueError(f"Invalid score value: {value!r}")
        elif isinstance(value, dict):
            converted_data[key] = convert_score_fields(value)
        else:
            converted_data[key] = value
    return converted_data


def calculate_geometric_mean(scores: List[int]) -> float:
    """
    Calculate the geometric mean of a list of scores.

    Args:
        scores (List[int]): List of integer scores, may contain None values.

    Returns:
        float: Geometric mean of non-None scores. Returns 0.0 if list is empty
            or contains only None values.
    """
    scores = [s for s in scores if s is not None]
    if not scores:
        return 0.0
    product = prod(scores)
    return product ** (1 / len(scores))
