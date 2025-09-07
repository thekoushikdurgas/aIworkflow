"""
Model definitions and configuration for the GenAI Agent.

This module contains comprehensive information about all available models,
their capabilities, pricing, and recommended use cases.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class ModelCategory(Enum):
    """Model category types."""
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"

class ModelProvider(Enum):
    """Model provider types."""
    GEMINI = "gemini"
    IMAGEN = "imagen"
    VEO = "veo"

@dataclass
class ModelCapability:
    """Individual model capability definition."""
    name: str
    description: str
    supported: bool = True
    limitations: Optional[str] = None

@dataclass
class ModelPricing:
    """Model pricing information."""
    input_cost: Optional[float] = None  # Per 1M tokens
    output_cost: Optional[float] = None  # Per 1M tokens
    per_image: Optional[float] = None  # Per image
    per_second: Optional[float] = None  # Per second (video)
    context_caching: Optional[float] = None  # Per 1M tokens cached
    currency: str = "USD"
    free_tier: bool = False
    free_tier_limits: Optional[str] = None

@dataclass
class ModelInfo:
    """Comprehensive model information."""
    name: str
    display_name: str
    provider: ModelProvider
    category: ModelCategory
    description: str
    
    # Technical specifications
    max_input_tokens: int
    max_output_tokens: int
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_thinking: bool = False
    supports_system_instructions: bool = True
    
    # Default parameters
    default_temperature: float = 0.7
    default_top_p: float = 0.95
    default_top_k: int = 40
    default_thinking_budget: Optional[int] = None
    
    # Capabilities
    capabilities: List[ModelCapability] = field(default_factory=list)
    
    # Pricing
    pricing: ModelPricing = field(default_factory=ModelPricing)
    
    # Usage recommendations
    best_for: List[str] = field(default_factory=list)
    not_recommended_for: List[str] = field(default_factory=list)
    
    # Status
    deprecated: bool = False
    experimental: bool = False
    available_regions: List[str] = field(default_factory=lambda: ["global"])

# Model Categories for UI organization
MODEL_CATEGORIES = {
    "Text Generation": {
        "icon": "🗣️",
        "description": "Models for text generation, chat, and reasoning",
        "models": [
            "gemini-2.5-pro",
            "gemini-2.5-flash", 
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash"
        ]
    },
    "Image Generation": {
        "icon": "🎨",
        "description": "Models for creating and editing images",
        "models": [
            "imagen-4.0-fast-generate-001",
            "imagen-4.0-generate-001",
            "imagen-4.0-ultra-generate-001",
            "imagen-3-generate-001"
        ]
    },
    "Video Generation": {
        "icon": "🎬",
        "description": "Models for creating videos",
        "models": [
            "veo-3.0-fast-generate-preview",
            "veo-3.0-generate-preview",
            "veo-2-generate-preview"
        ]
    },
    "Audio & Speech": {
        "icon": "🎵",
        "description": "Models for audio processing and text-to-speech",
        "models": [
            "gemini-2.5-flash-preview-tts",
            "gemini-2.5-pro-preview-tts"
        ]
    }
}

def create_model_definitions() -> Dict[str, ModelInfo]:
    """Create comprehensive model definitions."""
    models = {}
    
    # Gemini 2.5 Pro
    models["gemini-2.5-pro"] = ModelInfo(
        name="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        provider=ModelProvider.GEMINI,
        category=ModelCategory.MULTIMODAL,
        description="Most powerful thinking model with maximum response accuracy and state-of-the-art performance",
        max_input_tokens=1048576,
        max_output_tokens=65536,
        supports_function_calling=True,
        supports_thinking=True,
        default_temperature=0.3,
        default_thinking_budget=5000,
        capabilities=[
            ModelCapability("text", "Text generation and understanding"),
            ModelCapability("images", "Image understanding and analysis"),
            ModelCapability("video", "Video analysis and understanding"),
            ModelCapability("audio", "Audio processing and transcription"),
            ModelCapability("pdf", "PDF document processing"),
            ModelCapability("thinking", "Enhanced reasoning with thinking budgets"),
            ModelCapability("function_calling", "Custom tool and function integration"),
            ModelCapability("structured_output", "JSON schema and Pydantic model support"),
            ModelCapability("search_grounding", "Google Search integration"),
            ModelCapability("caching", "Context caching for cost optimization")
        ],
        pricing=ModelPricing(
            input_cost=1.25,
            output_cost=10.0,
            context_caching=0.31,
            free_tier=True,
            free_tier_limits="Limited requests per day"
        ),
        best_for=[
            "Complex reasoning and analysis",
            "Advanced coding tasks",
            "Large document processing",
            "Multi-step problem solving",
            "Academic and research tasks"
        ],
        not_recommended_for=[
            "Simple queries",
            "High-volume basic tasks",
            "Real-time applications requiring low latency"
        ]
    )
    
    # Gemini 2.5 Flash
    models["gemini-2.5-flash"] = ModelInfo(
        name="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash", 
        provider=ModelProvider.GEMINI,
        category=ModelCategory.MULTIMODAL,
        description="Best model in terms of price-performance, offering well-rounded capabilities",
        max_input_tokens=1048576,
        max_output_tokens=65536,
        supports_function_calling=True,
        supports_thinking=True,
        default_temperature=0.7,
        default_thinking_budget=1000,
        capabilities=[
            ModelCapability("text", "Text generation and understanding"),
            ModelCapability("images", "Image understanding and analysis"),
            ModelCapability("video", "Video analysis and understanding"),
            ModelCapability("audio", "Audio processing and transcription"),
            ModelCapability("thinking", "Adaptive thinking budgets"),
            ModelCapability("function_calling", "Custom tool and function integration"),
            ModelCapability("structured_output", "JSON schema and Pydantic model support"),
            ModelCapability("search_grounding", "Google Search integration"),
            ModelCapability("caching", "Context caching for cost optimization"),
            ModelCapability("streaming", "Real-time response streaming")
        ],
        pricing=ModelPricing(
            input_cost=0.30,
            output_cost=2.50,
            context_caching=0.075,
            free_tier=True,
            free_tier_limits="500 requests per day for search grounding"
        ),
        best_for=[
            "General chat and conversations",
            "Content creation and writing",
            "Code generation and debugging",
            "Image and video analysis",
            "Balanced performance tasks"
        ],
        not_recommended_for=[
            "Extremely complex reasoning (use Pro)",
            "High-volume simple tasks (use Lite)"
        ]
    )
    
    # Gemini 2.5 Flash-Lite
    models["gemini-2.5-flash-lite"] = ModelInfo(
        name="gemini-2.5-flash-lite",
        display_name="Gemini 2.5 Flash-Lite",
        provider=ModelProvider.GEMINI,
        category=ModelCategory.MULTIMODAL,
        description="Most cost-efficient model supporting high throughput",
        max_input_tokens=1048576,
        max_output_tokens=65536,
        supports_function_calling=True,
        supports_thinking=True,
        default_temperature=0.5,
        default_thinking_budget=500,
        capabilities=[
            ModelCapability("text", "Text generation and understanding"),
            ModelCapability("images", "Image understanding and analysis"),
            ModelCapability("video", "Video analysis and understanding"),
            ModelCapability("audio", "Audio processing and transcription"),
            ModelCapability("thinking", "Basic thinking capabilities"),
            ModelCapability("function_calling", "Custom tool and function integration"),
            ModelCapability("structured_output", "JSON schema and Pydantic model support"),
            ModelCapability("search_grounding", "Google Search integration"),
            ModelCapability("caching", "Context caching for cost optimization")
        ],
        pricing=ModelPricing(
            input_cost=0.10,
            output_cost=0.40,
            context_caching=0.025,
            free_tier=True,
            free_tier_limits="500 requests per day for search grounding"
        ),
        best_for=[
            "High-volume simple tasks",
            "Real-time applications",
            "Cost-sensitive projects",
            "Basic chat and Q&A",
            "Simple content generation"
        ],
        not_recommended_for=[
            "Complex reasoning tasks",
            "Advanced analysis",
            "Heavy multimedia processing"
        ]
    )
    
    # Gemini 2.0 Flash
    models["gemini-2.0-flash"] = ModelInfo(
        name="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        provider=ModelProvider.GEMINI,
        category=ModelCategory.MULTIMODAL,
        description="Latest stable model with next-gen features and improved capabilities",
        max_input_tokens=1048576,
        max_output_tokens=8192,
        supports_function_calling=True,
        supports_thinking=False,
        default_temperature=0.7,
        capabilities=[
            ModelCapability("text", "Text generation and understanding"),
            ModelCapability("images", "Image understanding and analysis"),
            ModelCapability("video", "Video analysis and understanding"),
            ModelCapability("audio", "Audio processing and transcription"),
            ModelCapability("function_calling", "Native tool use"),
            ModelCapability("structured_output", "JSON schema and Pydantic model support"),
            ModelCapability("search_grounding", "Google Search integration"),
            ModelCapability("caching", "Context caching for cost optimization"),
            ModelCapability("live_api", "Real-time bidirectional interactions")
        ],
        pricing=ModelPricing(
            input_cost=0.10,
            output_cost=0.40,
            context_caching=0.025,
            free_tier=True,
            free_tier_limits="500 requests per day for search grounding"
        ),
        best_for=[
            "Agent-based applications",
            "Real-time interactions",
            "Native tool integration",
            "Speed-focused tasks",
            "Modern app development"
        ]
    )
    
    # Imagen Models
    models["imagen-4.0-fast-generate-001"] = ModelInfo(
        name="imagen-4.0-fast-generate-001",
        display_name="Imagen 4.0 Fast",
        provider=ModelProvider.IMAGEN,
        category=ModelCategory.IMAGE,
        description="Fast image generation with good quality",
        max_input_tokens=8000,
        max_output_tokens=0,
        supports_streaming=False,
        supports_function_calling=False,
        supports_thinking=False,
        capabilities=[
            ModelCapability("image_generation", "Fast high-quality image creation"),
            ModelCapability("text_rendering", "Improved text in images"),
            ModelCapability("style_control", "Various artistic styles")
        ],
        pricing=ModelPricing(
            per_image=0.02,
            free_tier=False
        ),
        best_for=[
            "Quick image prototyping",
            "High-volume image generation",
            "Cost-effective image creation",
            "Real-time applications"
        ]
    )
    
    models["imagen-4.0-generate-001"] = ModelInfo(
        name="imagen-4.0-generate-001",
        display_name="Imagen 4.0 Standard",
        provider=ModelProvider.IMAGEN,
        category=ModelCategory.IMAGE,
        description="Standard quality image generation with balanced speed and quality",
        max_input_tokens=8000,
        max_output_tokens=0,
        supports_streaming=False,
        supports_function_calling=False,
        supports_thinking=False,
        capabilities=[
            ModelCapability("image_generation", "High-quality image creation"),
            ModelCapability("text_rendering", "Excellent text in images"),
            ModelCapability("style_control", "Advanced artistic styles"),
            ModelCapability("composition", "Better scene composition")
        ],
        pricing=ModelPricing(
            per_image=0.04,
            free_tier=False
        ),
        best_for=[
            "Professional image creation",
            "Marketing materials",
            "Detailed artwork",
            "Publication-ready images"
        ]
    )
    
    models["imagen-4.0-ultra-generate-001"] = ModelInfo(
        name="imagen-4.0-ultra-generate-001",
        display_name="Imagen 4.0 Ultra",
        provider=ModelProvider.IMAGEN,
        category=ModelCategory.IMAGE,
        description="Highest quality image generation with maximum detail and accuracy",
        max_input_tokens=8000,
        max_output_tokens=0,
        supports_streaming=False,
        supports_function_calling=False,
        supports_thinking=False,
        capabilities=[
            ModelCapability("image_generation", "Ultra high-quality image creation"),
            ModelCapability("text_rendering", "Perfect text rendering"),
            ModelCapability("fine_details", "Exceptional detail preservation"),
            ModelCapability("photorealism", "Near-photographic quality"),
            ModelCapability("artistic_styles", "Premium artistic styles")
        ],
        pricing=ModelPricing(
            per_image=0.06,
            free_tier=False
        ),
        best_for=[
            "Premium artwork creation",
            "Professional photography replacement",
            "High-end marketing campaigns",
            "Print-quality materials"
        ]
    )
    
    # Veo Models
    models["veo-3.0-fast-generate-preview"] = ModelInfo(
        name="veo-3.0-fast-generate-preview",
        display_name="Veo 3.0 Fast",
        provider=ModelProvider.VEO,
        category=ModelCategory.VIDEO,
        description="Fast video generation optimized for speed and business use cases",
        max_input_tokens=32000,
        max_output_tokens=0,
        supports_streaming=False,
        supports_function_calling=False,
        supports_thinking=False,
        experimental=True,
        capabilities=[
            ModelCapability("video_generation", "Fast video creation"),
            ModelCapability("text_to_video", "Text prompt to video"),
            ModelCapability("image_to_video", "Image animation"),
            ModelCapability("style_control", "Various video styles")
        ],
        pricing=ModelPricing(
            per_second=0.15,
            free_tier=False
        ),
        best_for=[
            "Quick video prototypes",
            "Social media content",
            "Fast turnaround projects",
            "Business presentations"
        ],
        not_recommended_for=[
            "Cinematic quality videos",
            "Long-form content",
            "Professional productions"
        ]
    )
    
    models["veo-3.0-generate-preview"] = ModelInfo(
        name="veo-3.0-generate-preview",
        display_name="Veo 3.0 Standard",
        provider=ModelProvider.VEO,
        category=ModelCategory.VIDEO,
        description="High-quality video generation for professional use",
        max_input_tokens=32000,
        max_output_tokens=0,
        supports_streaming=False,
        supports_function_calling=False,
        supports_thinking=False,
        experimental=True,
        capabilities=[
            ModelCapability("video_generation", "High-quality video creation"),
            ModelCapability("text_to_video", "Advanced text prompt to video"),
            ModelCapability("image_to_video", "High-quality image animation"),
            ModelCapability("video_to_video", "Video transformation and editing"),
            ModelCapability("cinematic_quality", "Professional video quality"),
            ModelCapability("complex_scenes", "Multi-object scene generation")
        ],
        pricing=ModelPricing(
            per_second=0.40,
            free_tier=False
        ),
        best_for=[
            "Professional video content",
            "Marketing campaigns",
            "Educational content",
            "Creative projects"
        ],
        not_recommended_for=[
            "High-volume basic videos",
            "Real-time applications",
            "Budget-constrained projects"
        ]
    )
    
    return models

# Global model registry
AVAILABLE_MODELS = create_model_definitions()

def get_available_models(category: Optional[str] = None) -> Dict[str, ModelInfo]:
    """Get available models, optionally filtered by category."""
    if category is None:
        return AVAILABLE_MODELS
    
    return {
        name: model for name, model in AVAILABLE_MODELS.items()
        if model.category.value == category
    }

def get_model_info(model_name: str) -> Optional[ModelInfo]:
    """Get information for a specific model."""
    return AVAILABLE_MODELS.get(model_name)

def get_models_by_provider(provider: str) -> Dict[str, ModelInfo]:
    """Get all models from a specific provider."""
    return {
        name: model for name, model in AVAILABLE_MODELS.items()
        if model.provider.value == provider
    }

def get_recommended_models() -> Dict[str, str]:
    """Get recommended models for different use cases."""
    return {
        "general_chat": "gemini-2.5-flash",
        "complex_reasoning": "gemini-2.5-pro", 
        "high_volume": "gemini-2.5-flash-lite",
        "image_generation": "imagen-4.0-fast-generate-001",
        "video_generation": "veo-3.0-fast-generate-preview",
        "cost_effective": "gemini-2.5-flash-lite",
        "latest_features": "gemini-2.0-flash"
    }

def estimate_cost(model_name: str, input_tokens: int = 0, output_tokens: int = 0, 
                 images: int = 0, video_seconds: int = 0) -> Optional[float]:
    """Estimate cost for using a model with given parameters."""
    model = get_model_info(model_name)
    if not model or not model.pricing:
        return None
    
    cost = 0.0
    pricing = model.pricing
    
    # Text costs (per 1M tokens)
    if pricing.input_cost and input_tokens > 0:
        cost += (input_tokens / 1_000_000) * pricing.input_cost
    
    if pricing.output_cost and output_tokens > 0:
        cost += (output_tokens / 1_000_000) * pricing.output_cost
    
    # Image costs
    if pricing.per_image and images > 0:
        cost += images * pricing.per_image
    
    # Video costs (per second)
    if pricing.per_second and video_seconds > 0:
        cost += video_seconds * pricing.per_second
    
    return cost

def get_model_capabilities(model_name: str) -> List[str]:
    """Get list of capability names for a model."""
    model = get_model_info(model_name)
    if not model:
        return []
    
    return [cap.name for cap in model.capabilities if cap.supported]

def is_model_deprecated(model_name: str) -> bool:
    """Check if a model is deprecated."""
    model = get_model_info(model_name)
    return model.deprecated if model else False

def get_models_for_capability(capability: str) -> List[str]:
    """Get all models that support a specific capability."""
    models = []
    for name, model in AVAILABLE_MODELS.items():
        if capability in get_model_capabilities(name):
            models.append(name)
    return models
