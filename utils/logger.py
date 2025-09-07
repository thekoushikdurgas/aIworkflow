"""
Simple logging utilities for the GenAI Agent.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Global logger registry
_loggers = {}
_initialized = False

def setup_logging(log_level: str = "INFO", log_directory: str = "output/logs"):
    """Setup basic logging system."""
    global _initialized
    
    if _initialized:
        return
    
    # Create log directory
    Path(log_directory).mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(log_directory, "genai_agent.log"))
        ]
    )
    
    _initialized = True

def get_logger(name: str):
    """Get a logger instance."""
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]

def log_user_action(action: str, details: dict):
    """Log user actions."""
    logger = get_logger("user_actions")
    logger.info(f"USER_ACTION: {action} - {details}")

def log_performance(operation: str, duration: float, details: dict):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(f"PERFORMANCE: {operation} took {duration:.2f}s - {details}")