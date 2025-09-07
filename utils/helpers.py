"""
Helper functions and utilities for the GenAI Agent.

This module contains various utility functions for error handling,
file operations, formatting, and other common tasks.
"""

import re
import time
import functools
import mimetypes
from typing import Optional, Any, Callable, List, Dict
from pathlib import Path
import hashlib
import json

from google.genai.errors import APIError
from .logger import get_logger

logger = get_logger(__name__)

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        exceptions: Tuple of exceptions to catch and retry
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    delay = backoff_factor ** attempt
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}, retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
            
        return wrapper
    return decorator

def format_error_message(error: Exception) -> str:
    """
    Format error messages in a user-friendly way.
    
    Args:
        error: Exception to format
        
    Returns:
        Formatted error message
    """
    if isinstance(error, APIError):
        # Handle Google GenAI API errors
        error_msg = f"API Error ({error.code}): {error.message}"
        
        # Add specific guidance for common errors
        if error.code == 401:
            error_msg += "\n💡 Check your API key configuration."
        elif error.code == 403:
            error_msg += "\n💡 Check your API permissions and quotas."
        elif error.code == 429:
            error_msg += "\n💡 Rate limit exceeded. Please wait and try again."
        elif error.code == 400:
            error_msg += "\n💡 Check your request parameters and content."
        
        return error_msg
    
    elif isinstance(error, ConnectionError):
        return "🌐 Connection Error: Unable to connect to the API. Check your internet connection."
    
    elif isinstance(error, TimeoutError):
        return "⏱️ Timeout Error: The request took too long. Try again or use a shorter input."
    
    elif isinstance(error, ValueError):
        return f"❌ Value Error: {str(error)}"
    
    else:
        return f"❌ Unexpected Error: {str(error)}"

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to be safe for filesystem.
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    # Truncate if too long
    if len(filename) > max_length:
        name, ext = Path(filename).stem, Path(filename).suffix
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename

def estimate_tokens(text: str, model: str = "gemini") -> int:
    """
    Estimate token count for text (rough approximation).
    
    Args:
        text: Text to estimate tokens for
        model: Model type for estimation
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # Rough estimation: ~4 characters per token for English text
    # This is approximate and varies by model and language
    
    if model.startswith("gemini"):
        # Gemini models: roughly 4 characters per token
        return len(text) // 4
    else:
        # Default estimation
        return len(text) // 4

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    Validate if file type is allowed.
    
    Args:
        filename: File name to validate
        allowed_types: List of allowed file extensions
        
    Returns:
        True if file type is allowed
    """
    if not filename:
        return False
    
    file_extension = Path(filename).suffix.lower().lstrip('.')
    return file_extension in [t.lower() for t in allowed_types]

def get_file_mime_type(filename: str) -> Optional[str]:
    """
    Get MIME type for a file.
    
    Args:
        filename: File name
        
    Returns:
        MIME type string or None
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type

def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        Unique session ID string
    """
    import uuid
    return str(uuid.uuid4())

def generate_file_hash(file_path: str) -> str:
    """
    Generate MD5 hash for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash string
    """
    hash_md5 = hashlib.md5()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    except Exception as e:
        logger.error(f"Error generating file hash: {str(e)}")
        return ""

def truncate_text(text: str, max_length: int = 200, add_ellipsis: bool = True) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add ellipsis
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    
    if add_ellipsis:
        truncated += "..."
    
    return truncated

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def parse_model_config(config_string: str) -> Dict[str, Any]:
    """
    Parse model configuration from string.
    
    Args:
        config_string: Configuration string (JSON format)
        
    Returns:
        Parsed configuration dictionary
    """
    try:
        if not config_string.strip():
            return {}
        
        config = json.loads(config_string)
        
        # Validate and convert types
        validated_config = {}
        
        for key, value in config.items():
            if key == "temperature":
                validated_config[key] = float(value)
            elif key in ["max_tokens", "thinking_budget", "top_k"]:
                validated_config[key] = int(value)
            elif key == "top_p":
                validated_config[key] = float(value)
            else:
                validated_config[key] = value
        
        return validated_config
        
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in model config: {config_string}")
        return {}
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid value in model config: {str(e)}")
        return {}

def format_token_count(count: int) -> str:
    """
    Format token count in human-readable format.
    
    Args:
        count: Token count
        
    Returns:
        Formatted token count string
    """
    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f"{count / 1000:.1f}K"
    else:
        return f"{count / 1000000:.1f}M"

def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Estimate cost for API usage (rough approximation).
    
    Args:
        input_tokens: Input token count
        output_tokens: Output token count
        model: Model name
        
    Returns:
        Estimated cost in USD
    """
    # Pricing from the models configuration
    pricing_map = {
        "gemini-2.5-pro": {"input": 1.25, "output": 10.0},
        "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
        "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40}
    }
    
    # Default pricing if model not found
    default_pricing = {"input": 0.50, "output": 1.50}
    
    pricing = pricing_map.get(model, default_pricing)
    
    # Calculate cost per 1M tokens
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost

def format_cost(cost: float) -> str:
    """
    Format cost in human-readable format.
    
    Args:
        cost: Cost in USD
        
    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        return f"${cost * 1000:.2f}‰"  # Show in per-mille for very small costs
    elif cost < 1:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely load JSON string with fallback.
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely dump object to JSON string.
    
    Args:
        obj: Object to serialize
        default: Default value if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return default

def clean_text_for_display(text: str) -> str:
    """
    Clean text for safe display in UI.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove or replace potentially problematic characters
    text = text.replace('\x00', '')  # Remove null bytes
    text = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)  # Remove control chars
    
    return text

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: File name
        
    Returns:
        File extension (lowercase, without dot)
    """
    return Path(filename).suffix.lower().lstrip('.')

def is_image_file(filename: str) -> bool:
    """
    Check if file is an image based on extension.
    
    Args:
        filename: File name
        
    Returns:
        True if file is an image
    """
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'svg'}
    return get_file_extension(filename) in image_extensions

def is_video_file(filename: str) -> bool:
    """
    Check if file is a video based on extension.
    
    Args:
        filename: File name
        
    Returns:
        True if file is a video
    """
    video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', '3gp'}
    return get_file_extension(filename) in video_extensions

def is_audio_file(filename: str) -> bool:
    """
    Check if file is an audio file based on extension.
    
    Args:
        filename: File name
        
    Returns:
        True if file is an audio file
    """
    audio_extensions = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a'}
    return get_file_extension(filename) in audio_extensions

def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": str(Path.cwd()),
        "user": Path.home().name
    }
