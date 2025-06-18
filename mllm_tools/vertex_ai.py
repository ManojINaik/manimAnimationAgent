import os
from typing import List, Dict, Any, Optional
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    from google.auth import default
    HAS_VERTEXAI = True
except ImportError:
    HAS_VERTEXAI = False
    vertexai = None
    GenerativeModel = None
    Part = None
    default = None
try:
    from google.auth.transport import requests
except ImportError:
    requests = None


# TODO: check if this is the correct way to use Vertex AI
# TODO: add langfuse support
class VertexAIWrapper:
    """Wrapper for Vertex AI to support Gemini models."""
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        print_cost: bool = False,
        verbose: bool = False,
        use_langfuse: bool = False
    ):
        """Initialize the Vertex AI wrapper.
        
        Args:
            model_name: Name of the model to use (e.g. "gemini-1.5-pro")
            temperature: Temperature for generation between 0 and 1
            print_cost: Whether to print the cost of the completion
            verbose: Whether to print verbose output
            use_langfuse: Whether to enable Langfuse logging
        """
        if not HAS_VERTEXAI:
            raise ImportError("Vertex AI dependencies not available. Install with: pip install google-cloud-aiplatform")
            
        self.model_name = model_name
        self.temperature = temperature
        self.print_cost = print_cost
        self.verbose = verbose
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project_id:
            raise ValueError("No GOOGLE_CLOUD_PROJECT found in environment variables")
            
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        
    def __call__(self, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Process messages and return completion.
        
        Args:
            messages: List of message dictionaries containing type and content
            metadata: Optional metadata dictionary to pass to the model
            
        Returns:
            Generated text response from the model
            
        Raises:
            ValueError: If message type is not supported
        """
        parts = []
        
        for msg in messages:
            if msg["type"] == "text":
                parts.append(Part.from_text(msg["content"]))
            elif msg["type"] in ["image", "video"]:
                mime_type = "video/mp4" if msg["type"] == "video" else "image/jpeg"
                if isinstance(msg["content"], str):
                    # Handle GCS URI
                    parts.append(Part.from_uri(
                        msg["content"],
                        mime_type=mime_type
                    ))
                else:
                    # Handle file path or bytes
                    parts.append(Part.from_data(
                        msg["content"],
                        mime_type=mime_type
                    ))
                    
        response = self.model.generate_content(
            parts,
            generation_config={
                "temperature": self.temperature,
                "top_p": 0.95,
            }
        )
        
        return response.text