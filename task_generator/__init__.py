from .prompts_raw import (
    _prompt_code_generation,
    _prompt_fix_error,
    _prompt_visual_fix_error,
    _prompt_scene_plan,
    _prompt_scene_vision_storyboard,
    _prompt_scene_technical_implementation,
    _prompt_scene_animation_narration,
    _prompt_animation_simple,
    _prompt_animation_fix_error,
    _prompt_animation_rag_query_generation,
    _prompt_animation_rag_query_generation_fix_error,
    _banned_reasonings,
    _prompt_context_learning_scene_plan,
    _prompt_context_learning_vision_storyboard,
    _prompt_context_learning_technical_implementation,
    _prompt_context_learning_animation_narration,
    _prompt_context_learning_code,
    _prompt_detect_plugins,
    _prompt_rag_query_generation_code,
    _prompt_rag_query_generation_vision_storyboard,
    _prompt_rag_query_generation_technical,
    _prompt_rag_query_generation_narration,
    _prompt_rag_query_generation_fix_error
)
from typing import Union, List
  
def get_prompt_scene_plan(topic: str, description: str) -> str:
    """
    Generate a prompt for scene planning based on the given parameters.

    Args:
        topic (str): The topic of the video.
        description (str): A brief description of the video content.

    Returns:
        str: The formatted prompt for scene planning.
    """
    prompt = _prompt_scene_plan.format(topic=topic, description=description)
    return prompt

def get_prompt_scene_vision_storyboard(scene_number: int, topic: str, description: str, scene_outline: str, relevant_plugins: List[str]) -> str:
    prompt = _prompt_scene_vision_storyboard.format(
        scene_number=scene_number,
        topic=topic,
        description=description,
        scene_outline=scene_outline,
        relevant_plugins=", ".join(relevant_plugins)
    )
    return prompt

def get_prompt_scene_technical_implementation(scene_number: int, topic: str, description: str, scene_outline: str, scene_vision_storyboard: str, relevant_plugins: List[str], additional_context: Union[str, List[str]] = None) -> str:
    prompt = _prompt_scene_technical_implementation.format(
        scene_number=scene_number,
        topic=topic,
        description=description,
        scene_outline=scene_outline,
        scene_vision_storyboard=scene_vision_storyboard,
        relevant_plugins=", ".join(relevant_plugins)
    )
    if additional_context is not None:
        if isinstance(additional_context, str):
            prompt += f"\nAdditional context: {additional_context}"
        elif isinstance(additional_context, list):
            prompt += f"\nAdditional context: {additional_context[0]}"
            if len(additional_context) > 1:
                prompt += f"\n" + "\n".join(additional_context[1:])
    return prompt

def get_prompt_scene_animation_narration(scene_number: int, topic: str, description: str, scene_outline: str, scene_vision_storyboard: str, technical_implementation_plan: str, relevant_plugins: List[str]) -> str:
    prompt = _prompt_scene_animation_narration.format(
        scene_number=scene_number,
        topic=topic,
        description=description,
        scene_outline=scene_outline,
        scene_vision_storyboard=scene_vision_storyboard,
        technical_implementation_plan=technical_implementation_plan,
        relevant_plugins=", ".join(relevant_plugins)
    )
    return prompt

def get_prompt_code_generation(topic: str,
                               description: str,
                               scene_outline: str,
                               scene_implementation: str,
                               scene_number: int,
                               additional_context: Union[str, List[str]] = None) -> str:
    """
    Generate a prompt for code generation based on the given video plan and implementation details.

    Args:
        topic (str): The topic of the video.
        description (str): A brief description of the video content.
        scene_outline (str): The scene outline.
        scene_implementation (str): The detailed scene implementation.
        scene_number (int): The scene number
        additional_context (Union[str, List[str]]): Additional context to include in the prompt
    Returns:
        str: The formatted prompt for code generation.
    """
    prompt = _prompt_code_generation.format(
        topic=topic,
        description=description,
        scene_outline=scene_outline,
        scene_implementation=scene_implementation,
        scene_number=scene_number
    )
    if additional_context is not None:
        if isinstance(additional_context, str):
            prompt += f"\nAdditional context: {additional_context}"
        elif isinstance(additional_context, list):
            prompt += f"\nAdditional context: {additional_context[0]}"
            if len(additional_context) > 1:
                prompt += f"\n" + "\n".join(additional_context[1:])
    return prompt

def get_prompt_fix_error(implementation_plan: str, manim_code: str, error: str, additional_context: Union[str, List[str]] = None) -> str:
    """
    Generate a prompt to fix errors in the given manim code.

    Args:
        implementation_plan (str): The implementation plan of the scene.
        code (str): The manim code with errors.
        error (str): The error message encountered.

    Returns:
        str: The formatted prompt to fix the code errors.
    """
    prompt = _prompt_fix_error.format(
        implementation_plan=implementation_plan,
        manim_code=manim_code,
        error_message=error
    )
    if additional_context is not None:
        if isinstance(additional_context, str):
            prompt += f"\nAdditional context: {additional_context}"
        elif isinstance(additional_context, list) and additional_context:
            prompt += f"\nAdditional context: {additional_context[0]}"
            if len(additional_context) > 1:
                prompt += f"\n" + "\n".join(additional_context[1:])
    return prompt

def get_prompt_visual_fix_error(implementation: str, generated_code: str) -> str:
    prompt = _prompt_visual_fix_error.format(
        implementation=implementation,
        generated_code=generated_code
    )
    return prompt

def get_banned_reasonings() -> List[str]:
    return _banned_reasonings.split("\n")

def get_prompt_rag_query_generation_vision_storyboard(scene_plan: str, relevant_plugins: str) -> str:
    prompt = _prompt_rag_query_generation_vision_storyboard.format(
        scene_plan=scene_plan,
        relevant_plugins=relevant_plugins
    )
    return prompt

def get_prompt_rag_query_generation_technical(storyboard: str, relevant_plugins: str) -> str:
    """For generating RAG queries during storyboard to technical implementation stage"""
    prompt = _prompt_rag_query_generation_technical.format(
        storyboard=storyboard,
        relevant_plugins=relevant_plugins
    )
    return prompt

def get_prompt_rag_query_generation_narration(storyboard: str, relevant_plugins: str) -> str:
    """For generating RAG queries during storyboard to narration stage"""
    prompt = _prompt_rag_query_generation_narration.format(
        storyboard=storyboard,
        relevant_plugins=relevant_plugins
    )
    return prompt

def get_prompt_rag_query_generation_code(implementation_plan: str, relevant_plugins: str) -> str:
    """For generating RAG queries during technical implementation to code generation stage"""
    prompt = _prompt_rag_query_generation_code.format(
        implementation_plan=implementation_plan,
        relevant_plugins=relevant_plugins
    )
    return prompt

def get_prompt_rag_query_generation_fix_error(error: str, code: str, relevant_plugins: str) -> str:
    prompt = _prompt_rag_query_generation_fix_error.format(
        error=error,
        code=code,
        relevant_plugins=relevant_plugins
    )
    return prompt

def get_prompt_context_learning_scene_plan(examples: str) -> str:
    prompt = _prompt_context_learning_scene_plan.format(
        examples=examples
    )
    return prompt

def get_prompt_context_learning_vision_storyboard(examples: str) -> str:
    prompt = _prompt_context_learning_vision_storyboard.format(
        examples=examples
    )
    return prompt

def get_prompt_context_learning_technical_implementation(examples: str) -> str:
    prompt = _prompt_context_learning_technical_implementation.format(
        examples=examples
    )
    return prompt

def get_prompt_context_learning_animation_narration(examples: str) -> str:
    prompt = _prompt_context_learning_animation_narration.format(
        examples=examples
    )
    return prompt

def get_prompt_context_learning_code(examples: str) -> str:
    prompt = _prompt_context_learning_code.format(
        examples=examples
    )
    return prompt

def get_prompt_detect_plugins(topic: str, description: str, plugin_descriptions: str) -> str:
    """
    Generate a prompt for detecting relevant plugins based on topic and description.

    Args:
        topic (str): The video topic
        description (str): The video description
        plugin_descriptions (str): JSON string of available plugin descriptions

    Returns:
        str: The formatted prompt for plugin detection
    """
    prompt = _prompt_detect_plugins.format(
        topic=topic,
        description=description,
        plugin_descriptions=plugin_descriptions
    )
    return prompt

def get_prompt_animation(topic: str, description: str, additional_context: Union[str, List[str]] = None) -> str:
    prompt = _prompt_animation_simple.format(
        topic=topic,
        description=description
    )
    if additional_context is not None:
        if isinstance(additional_context, str):
            prompt += f"\nAdditional context: {additional_context}"
        elif isinstance(additional_context, list) and additional_context:
            prompt += f"\nAdditional context: {additional_context[0]}"
            if len(additional_context) > 1:
                prompt += f"\n" + "\n".join(additional_context[1:])
    return prompt

def get_prompt_animation_fix_error(text_explanation: str, manim_code: str, error: str, additional_context: Union[str, List[str]] = None) -> str:
    """
    Generate a prompt to fix errors in the given manim code.

    Args:
        text_explanation (str): The implementation plan of the scene.
        code (str): The manim code with errors.
        error (str): The error message encountered.

    Returns:
        str: The formatted prompt to fix the code errors.
    """
    prompt = _prompt_animation_fix_error.format(
        text_explanation=text_explanation,
        manim_code=manim_code,
        error_message=error
    )
    if additional_context is not None:
        if isinstance(additional_context, str):
            prompt += f"\nAdditional context: {additional_context}"
        elif isinstance(additional_context, list):
            prompt += f"\nAdditional context: {additional_context[0]}"
            if len(additional_context) > 1:
                prompt += f"\n" + "\n".join(additional_context[1:])
    return prompt

def get_prompt_animation_rag_query_generation(topic: str, context: str, relevant_plugins: str) -> str:
    if context is None:
        context = ""
    prompt = _prompt_animation_rag_query_generation.format(
        topic=topic,
        context=context,
        relevant_plugins=relevant_plugins
    )
    return prompt

def get_prompt_animation_rag_query_generation_fix_error(text_explanation: str, error: str, code: str) -> str:
    prompt = _prompt_animation_rag_query_generation_fix_error.format(
        text_explanation=text_explanation,
        error=error,
        code=code
    )
    return prompt