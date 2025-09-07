"""
Application settings and configuration management.

This module handles loading and managing all application settings,
including environment variables, model configurations, and user preferences.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import ast
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    display_name: str
    provider: str  # 'gemini', 'imagen', 'veo'
    category: str  # 'text', 'image', 'video', 'audio'
    temperature: float = 0.7
    max_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40
    thinking_budget: Optional[int] = None
    safety_settings: Dict[str, str] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    pricing: Dict[str, float] = field(default_factory=dict)
    deprecated: bool = False

@dataclass
class AppSettings:
    """Main application settings."""
    
    # Basic app configuration
    app_title: str = "GenAI Agent"
    app_icon: str = "🤖"
    debug_mode: bool = False
    
    # API Configuration
    google_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    use_vertex_ai: bool = False
    google_cloud_project: Optional[str] = None
    google_cloud_location: str = "us-central1"
    
    # Default model settings
    default_model: str = "gemini-2.5-flash"
    default_temperature: float = 0.7
    default_max_tokens: int = 8192
    default_thinking_budget: int = 1000
    
    # Performance settings
    request_timeout: int = 60
    retry_attempts: int = 3
    rate_limit_rpm: int = 60
    max_concurrent_requests: int = 5
    
    # File handling
    max_file_size_mb: int = 100
    max_files_per_upload: int = 10
    allowed_file_types: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'gif', 'webp',
        'mp4', 'mov', 'avi', 'mp3', 'wav',
        'pdf', 'txt', 'md'
    ])
    
    # UI Configuration
    theme: str = "auto"
    sidebar_state: str = "expanded"
    wide_mode: bool = True
    show_sidebar_navigation: bool = True
    
    # Feature flags
    enable_dark_mode: bool = True
    enable_file_upload: bool = True
    enable_image_generation: bool = True
    enable_video_generation: bool = True
    enable_function_calling: bool = True
    enable_search_grounding: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    log_directory: str = "output/logs"
    
    # Storage paths
    output_directory: str = "output"
    sessions_directory: str = "output/sessions"
    media_directory: str = "output/media"
    exports_directory: str = "output/exports"
    cache_directory: str = "output/cache"
    
    # Session management
    session_timeout_minutes: int = 30
    max_chat_history: int = 100
    auto_save_sessions: bool = True
    
    # Security
    enable_api_key_validation: bool = True
    require_authentication: bool = False
    session_secret_key: Optional[str] = None
    
    # Caching
    enable_caching: bool = True
    cache_ttl_hours: int = 1
    cache_max_size_mb: int = 500
    
    # Model-specific settings
    model_configs: Dict[str, ModelConfig] = field(default_factory=dict)

def load_environment_variables() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}
    
    # API Configuration
    config['google_api_key'] = os.getenv('GOOGLE_API_KEY')
    config['gemini_api_key'] = os.getenv('GEMINI_API_KEY')
    config['use_vertex_ai'] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'false').lower() == 'true'
    config['google_cloud_project'] = os.getenv('GOOGLE_CLOUD_PROJECT')
    config['google_cloud_location'] = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    # App Settings
    config['app_title'] = os.getenv('APP_TITLE', 'GenAI Agent')
    config['app_icon'] = os.getenv('APP_ICON', '🤖')
    config['debug_mode'] = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # Default Model Settings
    config['default_model'] = os.getenv('DEFAULT_MODEL', 'gemini-2.5-flash')
    config['default_temperature'] = float(os.getenv('DEFAULT_TEMPERATURE', '0.7'))
    config['default_max_tokens'] = int(os.getenv('DEFAULT_MAX_TOKENS', '8192'))
    config['default_thinking_budget'] = int(os.getenv('DEFAULT_THINKING_BUDGET', '1000'))
    
    # Performance Settings
    config['request_timeout'] = int(os.getenv('REQUEST_TIMEOUT', '60'))
    config['retry_attempts'] = int(os.getenv('RETRY_ATTEMPTS', '3'))
    config['rate_limit_rpm'] = int(os.getenv('RATE_LIMIT_RPM', '60'))
    config['max_concurrent_requests'] = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
    
    # File Handling
    config['max_file_size_mb'] = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
    config['max_files_per_upload'] = int(os.getenv('MAX_FILES_PER_UPLOAD', '10'))
    
    allowed_types = os.getenv('ALLOWED_FILE_TYPES', 'jpg,jpeg,png,gif,webp,mp4,mov,avi,mp3,wav,pdf,txt,md')
    config['allowed_file_types'] = [t.strip() for t in allowed_types.split(',')]
    
    # UI Configuration
    config['theme'] = os.getenv('THEME', 'auto')
    config['sidebar_state'] = os.getenv('SIDEBAR_STATE', 'expanded')
    config['wide_mode'] = os.getenv('WIDE_MODE', 'true').lower() == 'true'
    config['show_sidebar_navigation'] = os.getenv('SHOW_SIDEBAR_NAVIGATION', 'true').lower() == 'true'
    
    # Feature Flags
    config['enable_dark_mode'] = os.getenv('ENABLE_DARK_MODE', 'true').lower() == 'true'
    config['enable_file_upload'] = os.getenv('ENABLE_FILE_UPLOAD', 'true').lower() == 'true'
    config['enable_image_generation'] = os.getenv('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true'
    config['enable_video_generation'] = os.getenv('ENABLE_VIDEO_GENERATION', 'true').lower() == 'true'
    config['enable_function_calling'] = os.getenv('ENABLE_FUNCTION_CALLING', 'true').lower() == 'true'
    config['enable_search_grounding'] = os.getenv('ENABLE_SEARCH_GROUNDING', 'true').lower() == 'true'
    
    # Logging
    config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
    config['log_to_file'] = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
    config['log_to_console'] = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
    config['log_directory'] = os.getenv('LOG_DIRECTORY', 'output/logs')
    
    # Storage Paths
    config['output_directory'] = os.getenv('OUTPUT_DIRECTORY', 'output')
    config['sessions_directory'] = os.getenv('SESSIONS_DIRECTORY', 'output/sessions')
    config['media_directory'] = os.getenv('MEDIA_DIRECTORY', 'output/media')
    config['exports_directory'] = os.getenv('EXPORTS_DIRECTORY', 'output/exports')
    config['cache_directory'] = os.getenv('CACHE_DIRECTORY', 'output/cache')
    
    # Session Management
    config['session_timeout_minutes'] = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    config['max_chat_history'] = int(os.getenv('MAX_CHAT_HISTORY', '100'))
    config['auto_save_sessions'] = os.getenv('AUTO_SAVE_SESSIONS', 'true').lower() == 'true'
    
    # Security
    config['enable_api_key_validation'] = os.getenv('ENABLE_API_KEY_VALIDATION', 'true').lower() == 'true'
    config['require_authentication'] = os.getenv('REQUIRE_AUTHENTICATION', 'false').lower() == 'true'
    config['session_secret_key'] = os.getenv('SESSION_SECRET_KEY')
    
    # Caching
    config['enable_caching'] = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    config['cache_ttl_hours'] = int(os.getenv('CACHE_TTL_HOURS', '1'))
    config['cache_max_size_mb'] = int(os.getenv('CACHE_MAX_SIZE_MB', '500'))
    
    return config

def load_json_config(json_file: str = "datasets/config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    config = {}
    
    if not Path(json_file).exists():
        print(f"Config file {json_file} not found, using defaults")
        return config
    
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
            
        # Remove metadata if present (internal use only)
        if '_metadata' in config:
            del config['_metadata']
            
    except Exception as e:
        print(f"Error loading JSON config: {e}")
    
    return config

def load_settings() -> AppSettings:
    """Load application settings from CSV config and environment variables."""
    try:
        # Load from JSON first
        json_config = load_json_config()
        
        # Load environment variables (these can override CSV)
        env_config = load_environment_variables()
        
        # Map JSON config to AppSettings format
        mapped_config = {}
        
        # Auth settings
        if 'auth' in json_config:
            auth = json_config['auth']
            mapped_config['google_api_key'] = auth.get('api_key') or env_config.get('google_api_key')
            mapped_config['use_vertex_ai'] = auth.get('use_vertex_ai', False)
            mapped_config['google_cloud_project'] = auth.get('project_id') or env_config.get('google_cloud_project')
            mapped_config['google_cloud_location'] = auth.get('location', 'us-central1')
        
        # Model settings
        if 'model' in json_config:
            model = json_config['model']
            mapped_config['default_model'] = model.get('selected_model', 'gemini-2.5-flash')
            mapped_config['default_temperature'] = model.get('temperature', 0.7)
            mapped_config['default_max_tokens'] = model.get('max_output_tokens', 8192)
            mapped_config['default_thinking_budget'] = model.get('thinking_budget', 1000)
        
        # UI settings
        if 'ui' in json_config:
            ui = json_config['ui']
            mapped_config['debug_mode'] = ui.get('debug_mode', False)
            mapped_config['theme'] = ui.get('theme', 'auto')
            mapped_config['auto_save_sessions'] = ui.get('auto_save', True)
        
        # Chat settings
        if 'chat' in json_config:
            chat = json_config['chat']
            mapped_config['enable_function_calling'] = chat.get('enable_function_calling', False)
        
        # Merge with environment config (env takes precedence)
        final_config = {**mapped_config, **env_config}
        
        # Create settings object
        settings = AppSettings(**final_config)
        
        # Store JSON config for UI access
        settings._json_config = json_config
        
        # Ensure required directories exist
        for directory in [
            settings.output_directory,
            settings.log_directory,
            settings.sessions_directory,
            settings.media_directory,
            settings.exports_directory,
            settings.cache_directory
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Load model configurations
        settings.model_configs = load_model_configs()
        
        return settings
        
    except Exception as e:
        print(f"Error loading settings: {e}")
        # Return default settings on error
        return AppSettings()

def load_model_configs() -> Dict[str, ModelConfig]:
    """Load model configurations from config files."""
    configs = {}
    
    # Default model configurations
    default_configs = {
        "gemini-2.5-pro": ModelConfig(
            name="gemini-2.5-pro",
            display_name="Gemini 2.5 Pro",
            provider="gemini",
            category="text",
            temperature=0.3,
            max_tokens=65536,
            thinking_budget=5000,
            capabilities=["text", "images", "video", "audio", "pdf", "thinking", "function_calling"],
            pricing={"input": 1.25, "output": 10.0}
        ),
        "gemini-2.5-flash": ModelConfig(
            name="gemini-2.5-flash",
            display_name="Gemini 2.5 Flash",
            provider="gemini",
            category="text",
            temperature=0.7,
            max_tokens=65536,
            thinking_budget=1000,
            capabilities=["text", "images", "video", "audio", "thinking", "function_calling"],
            pricing={"input": 0.30, "output": 2.50}
        ),
        "gemini-2.5-flash-lite": ModelConfig(
            name="gemini-2.5-flash-lite",
            display_name="Gemini 2.5 Flash-Lite",
            provider="gemini",
            category="text",
            temperature=0.5,
            max_tokens=65536,
            thinking_budget=500,
            capabilities=["text", "images", "video", "audio", "thinking", "function_calling"],
            pricing={"input": 0.10, "output": 0.40}
        ),
        "gemini-2.0-flash": ModelConfig(
            name="gemini-2.0-flash",
            display_name="Gemini 2.0 Flash",
            provider="gemini",
            category="text",
            temperature=0.7,
            max_tokens=8192,
            capabilities=["text", "images", "video", "audio", "function_calling"],
            pricing={"input": 0.10, "output": 0.40}
        ),
        "imagen-4.0-fast-generate-001": ModelConfig(
            name="imagen-4.0-fast-generate-001",
            display_name="Imagen 4.0 Fast",
            provider="imagen",
            category="image",
            capabilities=["image_generation"],
            pricing={"per_image": 0.02}
        ),
        "imagen-4.0-generate-001": ModelConfig(
            name="imagen-4.0-generate-001",
            display_name="Imagen 4.0 Standard",
            provider="imagen",
            category="image",
            capabilities=["image_generation"],
            pricing={"per_image": 0.04}
        ),
        "imagen-4.0-ultra-generate-001": ModelConfig(
            name="imagen-4.0-ultra-generate-001",
            display_name="Imagen 4.0 Ultra",
            provider="imagen",
            category="image",
            capabilities=["image_generation"],
            pricing={"per_image": 0.06}
        ),
        "veo-3.0-fast-generate-preview": ModelConfig(
            name="veo-3.0-fast-generate-preview",
            display_name="Veo 3.0 Fast",
            provider="veo",
            category="video",
            capabilities=["video_generation"],
            pricing={"per_second": 0.15}
        ),
        "veo-3.0-generate-preview": ModelConfig(
            name="veo-3.0-generate-preview",
            display_name="Veo 3.0 Standard",
            provider="veo",
            category="video",
            capabilities=["video_generation"],
            pricing={"per_second": 0.40}
        )
    }
    
    configs.update(default_configs)
    
    # Try to load custom configurations from file
    config_file = Path("config/custom_models.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                custom_configs = json.load(f)
                for name, config_data in custom_configs.items():
                    configs[name] = ModelConfig(**config_data)
        except Exception as e:
            print(f"Error loading custom model configs: {e}")
    
    return configs

def save_json_config(config_updates: Dict[str, Dict[str, Any]], json_file: str = "datasets/config.json") -> bool:
    """Save configuration updates to JSON file."""
    try:
        # Read existing config
        config = {}
        if Path(json_file).exists():
            with open(json_file, 'r', encoding='utf-8') as file:
                config = json.load(file)
        
        # Update config with new values
        current_time = datetime.now().isoformat()
        
        for category, updates in config_updates.items():
            if category not in config:
                config[category] = {}
            
            for key, value in updates.items():
                config[category][key] = value
        
        # Update metadata
        if '_metadata' not in config:
            config['_metadata'] = {}
        
        config['_metadata']['last_updated'] = current_time
        config['_metadata']['version'] = config['_metadata'].get('version', '1.0.0')
        config['_metadata']['format'] = 'json'
        
        # Write back to file
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"Error saving JSON config: {e}")
        return False

def save_settings(settings: AppSettings, file_path: str = "config/user_settings.json"):
    """Save current settings to JSON file (legacy support)."""
    try:
        config_dir = Path(file_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert settings to dictionary (excluding sensitive data)
        settings_dict = {
            'app_title': settings.app_title,
            'app_icon': settings.app_icon,
            'default_model': settings.default_model,
            'default_temperature': settings.default_temperature,
            'default_max_tokens': settings.default_max_tokens,
            'default_thinking_budget': settings.default_thinking_budget,
            'theme': settings.theme,
            'sidebar_state': settings.sidebar_state,
            'wide_mode': settings.wide_mode,
            'enable_dark_mode': settings.enable_dark_mode,
            'enable_file_upload': settings.enable_file_upload,
            'enable_image_generation': settings.enable_image_generation,
            'enable_video_generation': settings.enable_video_generation,
            'enable_function_calling': settings.enable_function_calling,
            'enable_search_grounding': settings.enable_search_grounding,
            'max_chat_history': settings.max_chat_history,
            'auto_save_sessions': settings.auto_save_sessions
        }
        
        with open(file_path, 'w') as f:
            json.dump(settings_dict, f, indent=2)
            
        return True
        
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def save_settings_to_json(settings: AppSettings) -> bool:
    """Save current settings to JSON config file."""
    config_updates = {
        'model': {
            'selected_model': settings.default_model,
            'temperature': settings.default_temperature,
            'max_output_tokens': settings.default_max_tokens,
            'thinking_budget': settings.default_thinking_budget
        },
        'ui': {
            'debug_mode': settings.debug_mode,
            'theme': settings.theme,
            'auto_save': settings.auto_save_sessions
        },
        'chat': {
            'enable_function_calling': settings.enable_function_calling
        }
    }
    
    return save_json_config(config_updates)

def get_api_key(settings: AppSettings) -> Optional[str]:
    """Get the appropriate API key based on configuration."""
    if settings.google_api_key:
        return settings.google_api_key
    elif settings.gemini_api_key:
        return settings.gemini_api_key
    else:
        return None

def validate_settings(settings: AppSettings) -> List[str]:
    """Validate settings and return list of issues."""
    issues = []
    
    # Check API configuration
    if not settings.use_vertex_ai and not get_api_key(settings):
        issues.append("No API key configured for Gemini Developer API")
    
    if settings.use_vertex_ai and not settings.google_cloud_project:
        issues.append("Google Cloud project not configured for Vertex AI")
    
    # Check model configuration
    if settings.default_model not in settings.model_configs:
        issues.append(f"Default model '{settings.default_model}' not found in configurations")
    
    # Check file size limits
    if settings.max_file_size_mb > 1000:
        issues.append("File size limit is very high (>1GB)")
    
    # Check rate limits
    if settings.rate_limit_rpm > 1000:
        issues.append("Rate limit is very high (>1000 RPM)")
    
    return issues
