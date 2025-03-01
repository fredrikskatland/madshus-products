"""
Logging module for the Madshus Products Pipeline.

This module provides a configured logger instance that can be used throughout the application.
"""

import sys
from pathlib import Path
from typing import Optional, Union

from loguru import logger

from madshus.config.settings import settings


def setup_logging(log_file: Optional[Union[str, Path]] = None) -> None:
    """
    Configure the logger with the specified settings.
    
    Args:
        log_file: Path to the log file. If None, logs will only be sent to stderr.
    """
    # Remove default logger
    logger.remove()
    
    # Add stderr logger with the configured log level
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    
    # Add file logger if a log file is specified
    if log_file:
        try:
            # Convert to Path object
            log_file_path = Path(log_file)
            
            # Create parent directories if they don't exist
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add file logger
            logger.add(
                str(log_file_path),
                level=settings.log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="10 MB",
                retention="1 week",
            )
        except Exception as e:
            logger.error(f"Error setting up file logger: {str(e)}")
            logger.warning("Continuing without file logging")


# Set up logging with default settings
setup_logging()
