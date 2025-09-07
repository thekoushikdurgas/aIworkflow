"""
Google GenAI client wrapper with enhanced functionality.

This module provides a high-level interface to the Google GenAI SDK
with additional features like error handling, logging, and caching.
"""

import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Iterator
from dataclasses import dataclass
import streamlit as st

# Google GenAI imports (using the correct current SDK)
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Local imports
from config.settings import AppSettings, get_api_key
from config.models import get_model_info, ModelInfo
from src.utils.logger import get_logger
from src.utils.helpers import retry_with_backoff, format_error_message

logger = get_logger(__name__)

@dataclass
class GenerationResult:
    """Result from content generation."""
    text: Optional[str] = None
    images: List[Any] = None
    videos: List[Any] = None
    audio: List[Any] = None
    function_calls: List[Any] = None
    usage_metadata: Dict[str, Any] = None
    thinking: Optional[str] = None
    error: Optional[str] = None
    cached: bool = False

class GenAIClient:
    """Enhanced Google GenAI client wrapper."""
    
    def __init__(self, settings: AppSettings):
        """Initialize the GenAI client."""
        self.settings = settings
        self._client = None
        self._chat_sessions = {}
        self._cache = {}
        
        # Initialize client
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the Google GenAI client."""
        try:
            if self.settings.use_vertex_ai:
                # Vertex AI configuration
                self._client = genai.Client(
                    vertexai=True,
                    project=self.settings.google_cloud_project,
                    location=self.settings.google_cloud_location
                )
                logger.info("Initialized Vertex AI client")
                
            else:
                # Gemini Developer API configuration
                api_key = get_api_key(self.settings)
                if not api_key:
                    raise ValueError("No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
                
                self._client = genai.Client(api_key=api_key)
                logger.info("Initialized Gemini Developer API client")
                
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {str(e)}")
            raise
    
    @property
    def client(self):
        """Get the underlying GenAI client."""
        if not self._client:
            self._initialize_client()
        return self._client
    
    def validate_connection(self) -> bool:
        """Validate that the client can connect to the API."""
        try:
            # Try to list models as a connectivity test
            models = list(self.client.models.list())
            logger.info(f"Connection validated. Found {len(models)} models.")
            return True
            
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def generate_content(
        self,
        model: str,
        contents: Union[str, List[Any]],
        config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> GenerationResult:
        """
        Generate content using the specified model.
        
        Args:
            model: Model name to use
            contents: Input content (text, images, etc.)
            config: Generation configuration
            use_cache: Whether to use caching
            
        Returns:
            GenerationResult with the generated content
        """
        try:
            # Check cache first
            if use_cache and self.settings.enable_caching:
                cache_key = self._get_cache_key(model, contents, config)
                if cache_key in self._cache:
                    logger.info("Returning cached result")
                    result = self._cache[cache_key]
                    result.cached = True
                    return result
            
            # Prepare configuration
            generation_config = self._prepare_config(config, model)
            
            # Log the request
            logger.info(f"Generating content with model: {model}")
            
            start_time = time.time()
            
            # Make the API call
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=generation_config
            )
            
            # Process the response
            result = self._process_response(response)
            result.usage_metadata = {
                "response_time": time.time() - start_time,
                "model": model,
                "cached": False
            }
            
            # Cache the result
            if use_cache and self.settings.enable_caching and not result.error:
                self._cache[cache_key] = result
            
            logger.info(f"Content generated successfully in {result.usage_metadata['response_time']:.2f}s")
            return result
            
        except APIError as e:
            logger.error(f"API error in generate_content: {str(e)}")
            return GenerationResult(error=format_error_message(e))
            
        except Exception as e:
            logger.error(f"Unexpected error in generate_content: {str(e)}")
            return GenerationResult(error=f"Unexpected error: {str(e)}")
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def generate_content_stream(
        self,
        model: str,
        contents: Union[str, List[Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> Iterator[GenerationResult]:
        """
        Generate content with streaming response.
        
        Args:
            model: Model name to use
            contents: Input content
            config: Generation configuration
            
        Yields:
            GenerationResult chunks as they arrive
        """
        try:
            generation_config = self._prepare_config(config, model)
            
            logger.info(f"Starting streaming generation with model: {model}")
            
            response_stream = self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generation_config
            )
            
            for chunk in response_stream:
                result = self._process_response(chunk)
                yield result
                
        except APIError as e:
            logger.error(f"API error in generate_content_stream: {str(e)}")
            yield GenerationResult(error=format_error_message(e))
            
        except Exception as e:
            logger.error(f"Unexpected error in generate_content_stream: {str(e)}")
            yield GenerationResult(error=f"Unexpected error: {str(e)}")
    
    def generate_images(
        self,
        model: str,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """Generate images using Imagen models."""
        try:
            logger.info(f"Generating images with model: {model}")
            
            # Default config for image generation
            image_config = {
                "number_of_images": 1,
                "output_mime_type": "image/jpeg",
                "aspect_ratio": "1:1"
            }
            
            if config:
                image_config.update(config)
            
            start_time = time.time()
            
            response = self.client.models.generate_images(
                model=model,
                prompt=prompt,
                config=image_config
            )
            
            result = GenerationResult(
                images=[img.image for img in response.generated_images],
                usage_metadata={
                    "response_time": time.time() - start_time,
                    "model": model,
                    "num_images": len(response.generated_images)
                }
            )
            
            logger.info(f"Generated {len(result.images)} images in {result.usage_metadata['response_time']:.2f}s")
            return result
            
        except APIError as e:
            logger.error(f"API error in generate_images: {str(e)}")
            return GenerationResult(error=format_error_message(e))
            
        except Exception as e:
            logger.error(f"Unexpected error in generate_images: {str(e)}")
            return GenerationResult(error=f"Unexpected error: {str(e)}")
    
    def generate_videos(
        self,
        model: str,
        prompt: str,
        image: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """Generate videos using Veo models."""
        try:
            logger.info(f"Generating videos with model: {model}")
            
            # Default config for video generation
            video_config = types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=8,
                aspect_ratio="16:9"
            )
            
            if config:
                for key, value in config.items():
                    if hasattr(video_config, key):
                        setattr(video_config, key, value)
            
            start_time = time.time()
            
            operation = self.client.models.generate_videos(
                model=model,
                prompt=prompt,
                image=image,
                config=video_config
            )
            
            # Poll for completion
            while not operation.done:
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            result = GenerationResult(
                videos=[video.video for video in operation.response.generated_videos],
                usage_metadata={
                    "response_time": time.time() - start_time,
                    "model": model,
                    "num_videos": len(operation.response.generated_videos)
                }
            )
            
            logger.info(f"Generated {len(result.videos)} videos in {result.usage_metadata['response_time']:.2f}s")
            return result
            
        except APIError as e:
            logger.error(f"API error in generate_videos: {str(e)}")
            return GenerationResult(error=format_error_message(e))
            
        except Exception as e:
            logger.error(f"Unexpected error in generate_videos: {str(e)}")
            return GenerationResult(error=f"Unexpected error: {str(e)}")
    
    def create_chat_session(self, model: str, session_id: Optional[str] = None) -> str:
        """Create a new chat session."""
        try:
            if not session_id:
                session_id = f"session_{int(time.time())}"
            
            chat = self.client.chats.create(model=model)
            self._chat_sessions[session_id] = chat
            
            logger.info(f"Created chat session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            raise
    
    def send_chat_message(
        self,
        session_id: str,
        message: Union[str, List[Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """Send a message in a chat session."""
        try:
            if session_id not in self._chat_sessions:
                raise ValueError(f"Chat session {session_id} not found")
            
            chat = self._chat_sessions[session_id]
            
            # Prepare configuration if provided
            if config:
                # Apply config to the chat session if supported
                pass
            
            start_time = time.time()
            response = chat.send_message(message)
            
            result = self._process_response(response)
            result.usage_metadata = {
                "response_time": time.time() - start_time,
                "session_id": session_id
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            return GenerationResult(error=f"Chat error: {str(e)}")
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session."""
        try:
            if session_id not in self._chat_sessions:
                return []
            
            chat = self._chat_sessions[session_id]
            history = []
            
            for message in chat.get_history():
                history.append({
                    "role": message.role,
                    "content": [part.text for part in message.parts if part.text],
                    "timestamp": time.time()  # Note: actual timestamp would need to be tracked separately
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def _prepare_config(self, config: Optional[Dict[str, Any]], model: str) -> Optional[types.GenerateContentConfig]:
        """Prepare generation configuration."""
        if not config:
            # Use model defaults
            model_info = get_model_info(model)
            if model_info:
                return types.GenerateContentConfig(
                    temperature=model_info.default_temperature,
                    max_output_tokens=model_info.max_output_tokens,
                    top_p=model_info.default_top_p,
                    top_k=model_info.default_top_k,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=model_info.default_thinking_budget
                    ) if model_info.supports_thinking and model_info.default_thinking_budget else None
                )
            return None
        
        # Convert config dict to GenerateContentConfig
        generation_config = types.GenerateContentConfig()
        
        for key, value in config.items():
            if hasattr(generation_config, key):
                if key == "thinking_budget" and value is not None:
                    generation_config.thinking_config = types.ThinkingConfig(thinking_budget=value)
                elif key == "safety_settings" and value:
                    # Convert safety settings
                    safety_settings = []
                    for setting in value:
                        safety_settings.append(types.SafetySetting(**setting))
                    generation_config.safety_settings = safety_settings
                elif key == "tools" and value:
                    generation_config.tools = value
                else:
                    setattr(generation_config, key, value)
        
        return generation_config
    
    def _process_response(self, response) -> GenerationResult:
        """Process API response into GenerationResult."""
        try:
            result = GenerationResult()
            
            # Extract text content
            if hasattr(response, 'text') and response.text:
                result.text = response.text
            
            # Extract function calls
            if hasattr(response, 'function_calls') and response.function_calls:
                result.function_calls = response.function_calls
            
            # Extract thinking (if available)
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'thought') and candidate.thought:
                    result.thinking = candidate.thought
            
            # Extract usage metadata
            if hasattr(response, 'usage_metadata'):
                result.usage_metadata = {
                    "input_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "output_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return GenerationResult(error=f"Response processing error: {str(e)}")
    
    def _get_cache_key(self, model: str, contents: Any, config: Any) -> str:
        """Generate cache key for request."""
        import hashlib
        
        # Create a string representation of the request
        cache_data = {
            "model": model,
            "contents": str(contents)[:1000],  # Truncate long content
            "config": str(config) if config else ""
        }
        
        cache_string = str(cache_data)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def count_tokens(self, model: str, contents: Union[str, List[Any]]) -> Dict[str, int]:
        """Count tokens for given content."""
        try:
            response = self.client.models.count_tokens(
                model=model,
                contents=contents
            )
            
            return {
                "total_tokens": response.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            return {"total_tokens": 0}
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            models = []
            for model in self.client.models.list():
                models.append({
                    "name": model.name,
                    "display_name": getattr(model, 'display_name', model.name),
                    "description": getattr(model, 'description', ''),
                    "input_token_limit": getattr(model, 'input_token_limit', 0),
                    "output_token_limit": getattr(model, 'output_token_limit', 0)
                })
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def upload_file(self, file_path: str, display_name: Optional[str] = None) -> Optional[Any]:
        """Upload a file to the service."""
        try:
            file = self.client.files.upload(
                file=file_path,
                config=types.UploadFileConfig(display_name=display_name) if display_name else None
            )
            
            logger.info(f"Uploaded file: {file.name}")
            return file
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    def delete_file(self, file_name: str) -> bool:
        """Delete an uploaded file."""
        try:
            self.client.files.delete(name=file_name)
            logger.info(f"Deleted file: {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def clear_cache(self):
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Response cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "active_sessions": len(self._chat_sessions)
        }
