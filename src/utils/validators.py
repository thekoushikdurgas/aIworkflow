"""
Input validation and sanitization utilities for the GenAI Agent.

This module contains functions to validate and sanitize user inputs,
API configurations, and other data to ensure security and correctness.
"""

import re
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)

def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate Google API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"
    
    if not isinstance(api_key, str):
        return False, "API key must be a string"
    
    # Remove whitespace
    api_key = api_key.strip()
    
    if len(api_key) < 10:
        return False, "API key is too short"
    
    if len(api_key) > 200:
        return False, "API key is too long"
    
    # Check for valid characters (alphanumeric, dashes, underscores)
    if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
        return False, "API key contains invalid characters"
    
    # Google API keys typically start with specific patterns
    # This is a basic check and may need adjustment
    if not (api_key.startswith('AI') or api_key.startswith('ya29')):
        logger.warning("API key format may not be standard for Google APIs")
    
    return True, ""

def validate_model_config(config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate and sanitize model configuration.
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message, sanitized_config)
    """
    sanitized_config = {}
    
    try:
        # Temperature validation
        if 'temperature' in config:
            temp = float(config['temperature'])
            if not 0.0 <= temp <= 2.0:
                return False, "Temperature must be between 0.0 and 2.0", {}
            sanitized_config['temperature'] = temp
        
        # Max tokens validation
        if 'max_tokens' in config:
            max_tokens = int(config['max_tokens'])
            if not 1 <= max_tokens <= 2000000:
                return False, "Max tokens must be between 1 and 2,000,000", {}
            sanitized_config['max_tokens'] = max_tokens
        
        # Top-p validation
        if 'top_p' in config:
            top_p = float(config['top_p'])
            if not 0.0 <= top_p <= 1.0:
                return False, "Top-p must be between 0.0 and 1.0", {}
            sanitized_config['top_p'] = top_p
        
        # Top-k validation
        if 'top_k' in config:
            top_k = int(config['top_k'])
            if not 1 <= top_k <= 100:
                return False, "Top-k must be between 1 and 100", {}
            sanitized_config['top_k'] = top_k
        
        # Thinking budget validation
        if 'thinking_budget' in config:
            if config['thinking_budget'] is not None:
                thinking_budget = int(config['thinking_budget'])
                if not 0 <= thinking_budget <= 50000:
                    return False, "Thinking budget must be between 0 and 50,000", {}
                sanitized_config['thinking_budget'] = thinking_budget
        
        # System instruction validation
        if 'system_instruction' in config:
            instruction = str(config['system_instruction'])
            if len(instruction) > 10000:
                return False, "System instruction is too long (max 10,000 characters)", {}
            sanitized_config['system_instruction'] = sanitize_input(instruction)
        
        # Safety settings validation
        if 'safety_settings' in config:
            safety_settings = config['safety_settings']
            if not isinstance(safety_settings, list):
                return False, "Safety settings must be a list", {}
            
            for setting in safety_settings:
                if not isinstance(setting, dict):
                    return False, "Each safety setting must be a dictionary", {}
                
                if 'category' not in setting or 'threshold' not in setting:
                    return False, "Safety settings must have 'category' and 'threshold'", {}
            
            sanitized_config['safety_settings'] = safety_settings
        
        return True, "", sanitized_config
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid configuration value: {str(e)}", {}

def validate_file_upload(
    file_path: str,
    allowed_types: List[str],
    max_size_mb: int = 100
) -> Tuple[bool, str]:
    """
    Validate file upload.
    
    Args:
        file_path: Path to the uploaded file
        allowed_types: List of allowed file extensions
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        return False, "File does not exist"
    
    # Check file extension
    file_extension = file_path.suffix.lower().lstrip('.')
    if file_extension not in [t.lower() for t in allowed_types]:
        return False, f"File type '{file_extension}' not allowed. Allowed types: {', '.join(allowed_types)}"
    
    # Check file size
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
    
    # Check for potentially dangerous file names
    dangerous_names = ['.env', 'config', 'secret', 'key', '.git', '.ssh']
    if any(dangerous in file_path.name.lower() for dangerous in dangerous_names):
        return False, "File name contains potentially sensitive information"
    
    return True, ""

def sanitize_input(text: str, max_length: int = 100000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove null bytes and control characters
    text = text.replace('\x00', '')
    text = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input text truncated to {max_length} characters")
    
    return text

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid
    """
    if not session_id or not isinstance(session_id, str):
        return False
    
    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[A-Za-z0-9_-]+$', session_id):
        return False
    
    # Reasonable length limits
    if not 3 <= len(session_id) <= 50:
        return False
    
    return True

def validate_model_name(model_name: str) -> bool:
    """
    Validate model name format.
    
    Args:
        model_name: Model name to validate
        
    Returns:
        True if valid
    """
    if not model_name or not isinstance(model_name, str):
        return False
    
    # Allow alphanumeric, hyphens, underscores, and dots
    if not re.match(r'^[A-Za-z0-9._-]+$', model_name):
        return False
    
    # Reasonable length limits
    if not 3 <= len(model_name) <= 100:
        return False
    
    return True

def validate_prompt(prompt: str) -> Tuple[bool, str]:
    """
    Validate prompt text.
    
    Args:
        prompt: Prompt text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt:
        return False, "Prompt cannot be empty"
    
    if not isinstance(prompt, str):
        return False, "Prompt must be text"
    
    # Check length
    if len(prompt) > 1000000:  # 1M characters
        return False, "Prompt is too long (max 1M characters)"
    
    # Check for potentially problematic content
    if '\x00' in prompt:
        return False, "Prompt contains null bytes"
    
    return True, ""

def validate_image_config(config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate image generation configuration.
    
    Args:
        config: Image generation configuration
        
    Returns:
        Tuple of (is_valid, error_message, sanitized_config)
    """
    sanitized_config = {}
    
    try:
        # Number of images
        if 'number_of_images' in config:
            num_images = int(config['number_of_images'])
            if not 1 <= num_images <= 4:
                return False, "Number of images must be between 1 and 4", {}
            sanitized_config['number_of_images'] = num_images
        
        # Aspect ratio
        if 'aspect_ratio' in config:
            aspect_ratio = str(config['aspect_ratio'])
            valid_ratios = ['1:1', '3:4', '4:3', '9:16', '16:9']
            if aspect_ratio not in valid_ratios:
                return False, f"Aspect ratio must be one of: {', '.join(valid_ratios)}", {}
            sanitized_config['aspect_ratio'] = aspect_ratio
        
        # Output format
        if 'output_mime_type' in config:
            mime_type = str(config['output_mime_type'])
            valid_types = ['image/jpeg', 'image/png', 'image/webp']
            if mime_type not in valid_types:
                return False, f"Output MIME type must be one of: {', '.join(valid_types)}", {}
            sanitized_config['output_mime_type'] = mime_type
        
        return True, "", sanitized_config
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid image configuration: {str(e)}", {}

def validate_video_config(config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate video generation configuration.
    
    Args:
        config: Video generation configuration
        
    Returns:
        Tuple of (is_valid, error_message, sanitized_config)
    """
    sanitized_config = {}
    
    try:
        # Duration
        if 'duration_seconds' in config:
            duration = int(config['duration_seconds'])
            if not 5 <= duration <= 8:
                return False, "Duration must be between 5 and 8 seconds", {}
            sanitized_config['duration_seconds'] = duration
        
        # Number of videos
        if 'number_of_videos' in config:
            num_videos = int(config['number_of_videos'])
            if not 1 <= num_videos <= 4:
                return False, "Number of videos must be between 1 and 4", {}
            sanitized_config['number_of_videos'] = num_videos
        
        # Aspect ratio
        if 'aspect_ratio' in config:
            aspect_ratio = str(config['aspect_ratio'])
            valid_ratios = ['16:9', '9:16']
            if aspect_ratio not in valid_ratios:
                return False, f"Video aspect ratio must be one of: {', '.join(valid_ratios)}", {}
            sanitized_config['aspect_ratio'] = aspect_ratio
        
        return True, "", sanitized_config
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid video configuration: {str(e)}", {}

def validate_environment_variables() -> List[str]:
    """
    Validate required environment variables.
    
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Check for API key
    google_api_key = os.getenv('GOOGLE_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    use_vertex_ai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').lower() == 'true'
    
    if not use_vertex_ai and not google_api_key and not gemini_api_key:
        errors.append("No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
    
    # Validate API key format if present
    if google_api_key:
        is_valid, error_msg = validate_api_key(google_api_key)
        if not is_valid:
            errors.append(f"Invalid GOOGLE_API_KEY: {error_msg}")
    
    if gemini_api_key:
        is_valid, error_msg = validate_api_key(gemini_api_key)
        if not is_valid:
            errors.append(f"Invalid GEMINI_API_KEY: {error_msg}")
    
    # Check Vertex AI configuration
    if use_vertex_ai:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION')
        
        if not project_id:
            errors.append("GOOGLE_CLOUD_PROJECT is required when using Vertex AI")
        
        if not location:
            errors.append("GOOGLE_CLOUD_LOCATION is required when using Vertex AI")
    
    return errors

def validate_json_schema(data: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate data against a JSON schema (basic validation).
    
    Args:
        data: Data to validate
        schema: Schema to validate against
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Basic type checking
        if 'type' in schema:
            expected_type = schema['type']
            
            if expected_type == 'object' and not isinstance(data, dict):
                return False, "Expected object"
            elif expected_type == 'array' and not isinstance(data, list):
                return False, "Expected array"
            elif expected_type == 'string' and not isinstance(data, str):
                return False, "Expected string"
            elif expected_type == 'number' and not isinstance(data, (int, float)):
                return False, "Expected number"
            elif expected_type == 'integer' and not isinstance(data, int):
                return False, "Expected integer"
            elif expected_type == 'boolean' and not isinstance(data, bool):
                return False, "Expected boolean"
        
        # Required properties for objects
        if isinstance(data, dict) and 'required' in schema:
            for required_field in schema['required']:
                if required_field not in data:
                    return False, f"Missing required field: {required_field}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Schema validation error: {str(e)}"

def sanitize_file_path(file_path: str, base_directory: str) -> Optional[str]:
    """
    Sanitize file path to prevent directory traversal attacks.
    
    Args:
        file_path: File path to sanitize
        base_directory: Base directory to restrict to
        
    Returns:
        Sanitized path or None if invalid
    """
    try:
        # Normalize paths
        base_path = Path(base_directory).resolve()
        full_path = (base_path / file_path).resolve()
        
        # Check that the file is within the base directory
        if not str(full_path).startswith(str(base_path)):
            logger.warning(f"Path traversal attempt detected: {file_path}")
            return None
        
        return str(full_path)
        
    except Exception as e:
        logger.error(f"Error sanitizing file path: {str(e)}")
        return None

def validate_tool_name(tool_name: str) -> bool:
    """
    Validate tool name for function calling.
    
    Args:
        tool_name: Tool name to validate
        
    Returns:
        True if valid
    """
    if not tool_name or not isinstance(tool_name, str):
        return False
    
    # Allow alphanumeric and underscores (Python function name style)
    if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', tool_name):
        return False
    
    # Reasonable length limits
    if not 1 <= len(tool_name) <= 50:
        return False
    
    # Avoid reserved words
    reserved_words = ['def', 'class', 'if', 'else', 'while', 'for', 'import', 'return']
    if tool_name.lower() in reserved_words:
        return False
    
    return True
