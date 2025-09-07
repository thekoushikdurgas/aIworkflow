"""
Utility functions and helpers for the GenAI Agent.
"""

# Simple logger that works without external dependencies
import logging
import sys
from datetime import datetime

# Simple logger setup
def get_logger(name: str):
    """Get a simple logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def setup_logging(level: str = "INFO", directory: str = "output/logs"):
    """Setup basic logging."""
    import os
    os.makedirs(directory, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"{directory}/app.log")
        ]
    )