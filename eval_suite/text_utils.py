from typing import Union

import pysrt

from mllm_tools.litellm import LiteLLMWrapper
from mllm_tools.gemini import GeminiWrapper
from mllm_tools.utils import _prepare_text_inputs
from eval_suite.prompts_raw import _fix_transcript, _text_eval_new
from eval_suite.utils import extract_json, convert_score_fields


def parse_srt_to_text(srt_path) -> str:
    """
    Parse an SRT subtitle file into plain text.

    Args:
        srt_path: Path to the SRT subtitle file.

    Returns:
        str: The subtitle text with duplicates removed and ellipses replaced.
    """
    subs = pysrt.open(srt_path)
    full_text = []
    for sub in subs:
        sub.text = sub.text.replace("...", ".")
        for line in sub.text.splitlines():
            # .srt can contain repeated lines
            if full_text and full_text[-1] == line:
                continue
            full_text.append(line)
    return "\n".join(full_text)


def fix_transcript(text_eval_model: Union[LiteLLMWrapper, GeminiWrapper], transcript: str) -> str:
    """
    Fix and clean up a transcript using an LLM model.

    Args:
        text_eval_model: The LLM model wrapper to use for fixing the transcript.
        transcript: The input transcript text to fix.

    Returns:
        str: The fixed and cleaned transcript text.
    """
    print("Fixing transcript...")
    
    prompt = _fix_transcript.format(transcript=transcript)
    response = text_eval_model(_prepare_text_inputs(prompt))
    fixed_script = response.split("<SCRIPT>", maxsplit=1)[1].split("</SCRIPT>")[0]

    return fixed_script


def evaluate_text(text_eval_model: LiteLLMWrapper, transcript: str, retry_limit: int) -> dict:
    """
    Evaluate transcript text using an LLM model with retry logic.

    Args:
        text_eval_model: The LLM model wrapper to use for evaluation.
        transcript: The transcript text to evaluate.
        retry_limit: Maximum number of retry attempts on failure.

    Returns:
        dict: The evaluation results as a JSON object.

    Raises:
        ValueError: If all retry attempts fail.
    """
    # prompt = _text_eval.format(transcript=transcript)
    prompt = _text_eval_new.format(transcript=transcript)
    for attempt in range(retry_limit):
        try:
            evaluation = text_eval_model(_prepare_text_inputs(prompt))
            evaluation_json = extract_json(evaluation)
            evaluation_json = convert_score_fields(evaluation_json)
            return evaluation_json
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e.__class__.__name__}: {e}")
            if attempt + 1 == retry_limit:
                raise ValueError("Reached maximum retry limit. Evaluation failed.") from None
