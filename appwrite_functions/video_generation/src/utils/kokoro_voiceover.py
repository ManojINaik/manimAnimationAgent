"""
Copyright (c) 2025 Xposed73
All rights reserved.
This file is part of the Manim Voiceover project.

DEPRECATED: This file is deprecated. Use ElevenLabsService from src.utils.elevenlabs_voiceover instead.
This wrapper is maintained for backward compatibility only.
"""

import warnings
from src.utils.elevenlabs_voiceover import ElevenLabsService

class KokoroService(ElevenLabsService):
    """
    DEPRECATED: Backward compatibility wrapper for ElevenLabsService.
    
    This class now redirects to ElevenLabsService. Please update your code to use:
    from src.utils.elevenlabs_voiceover import ElevenLabsService
    """
    
    def __init__(self, **kwargs):
        warnings.warn(
            "KokoroService is deprecated. Please use ElevenLabsService from "
            "src.utils.elevenlabs_voiceover instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Pass all arguments to ElevenLabsService
        super().__init__(**kwargs)