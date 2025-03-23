"""
Logging utilities for court scrapers.

This module provides logging functionality for court scrapers.
"""
import os
import sys
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_to_console: bool = True,
    log_to_file: bool = True,
    rotation: bool = False,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (if None, a default path will be used)
        level: Logging level
        log_format: Log format string
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        rotation: Whether to use rotating file handler
        max_bytes: Maximum bytes for rotating file handler
        backup_count: Number of backup files for rotating file handler
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
    
    # Default format if not specified
    if not log_format:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(log_format)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        if not log_file:
            # Default log file in logs directory
            log_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(log_dir, exist_ok=True)
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(log_dir, f"{name}_{date_str}.log")
        
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        if rotation:
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_file, 
                    maxBytes=max_bytes, 
                    backupCount=backup_count
                )
            except ImportError:
                # Fallback to regular file handler if RotatingFileHandler is not available
                file_handler = logging.FileHandler(log_file)
        else:
            file_handler = logging.FileHandler(log_file)
            
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(
    name: str,
    config: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """
    Get a logger with configuration from a config dictionary.
    
    Args:
        name: Logger name
        config: Configuration dictionary
    
    Returns:
        Configured logger
    """
    if config is None:
        config = {}
    
    log_level_str = config.get("log_level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    log_file = config.get("log_file")
    log_format = config.get("log_format")
    log_to_console = config.get("log_to_console", True)
    log_to_file = config.get("log_to_file", True)
    rotation = config.get("log_rotation", False)
    max_bytes = config.get("log_max_bytes", 10485760)  # 10MB
    backup_count = config.get("log_backup_count", 5)
    
    return setup_logger(
        name=name,
        log_file=log_file,
        level=log_level,
        log_format=log_format,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
        rotation=rotation,
        max_bytes=max_bytes,
        backup_count=backup_count
    )


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter to add context to log messages.
    """
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        """
        Initialize the logger adapter.
        
        Args:
            logger: Logger to adapt
            extra: Extra context to add to log messages
        """
        if extra is None:
            extra = {}
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process the log message to add context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
        
        Returns:
            Tuple of (message, kwargs)
        """
        # Add context from extra dict
        context_items = []
        for key, value in self.extra.items():
            if value is not None:
                context_items.append(f"{key}={value}")
        
        # If we have context items, add them to the message
        if context_items:
            context_str = " ".join(context_items)
            msg = f"[{context_str}] {msg}"
        
        return msg, kwargs


def get_logger_with_context(
    name: str,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> LoggerAdapter:
    """
    Get a logger adapter with context.
    
    Args:
        name: Logger name
        context: Context dictionary
        config: Configuration dictionary
    
    Returns:
        Logger adapter with context
    """
    logger = get_logger(name, config)
    return LoggerAdapter(logger, context)
