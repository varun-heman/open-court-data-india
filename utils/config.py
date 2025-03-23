"""
Configuration utilities for court scrapers.

This module provides configuration management for court scrapers.
"""
import os
import yaml
import json
from typing import Dict, Any, Optional, Union, List, cast
import logging


logger = logging.getLogger(__name__)


class ScraperConfig:
    """
    Configuration manager for court scrapers.
    
    This class provides configuration management for court scrapers,
    loading configuration from YAML or JSON files and providing
    access to configuration values.
    """
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        court_name: Optional[str] = None,
        defaults: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
            court_name: Name of the court (used to access court-specific config)
            defaults: Default configuration values
        """
        self.config: Dict[str, Any] = {}
        self.court_name = court_name
        
        # Set defaults
        if defaults:
            self.config.update(defaults)
        else:
            # Default configuration
            self.config = {
                # General settings
                "output_dir": "data",
                "cache_dir": ".cache",
                "log_level": "INFO",
                "log_file": None,
                "log_to_console": True,
                "log_to_file": True,
                
                # HTTP settings
                "timeout": 30,
                "retries": 3,
                "retry_delay": 1,
                "max_retry_delay": 60,
                "backoff_factor": 2,
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                
                # Rate limiting
                "rate_limit": 1,  # requests per second
                "rate_limit_enabled": True,
                
                # Caching
                "cache_enabled": True,
                "cache_expiry": 86400,  # 24 hours
                
                # Scraper behavior
                "follow_redirects": True,
                "verify_ssl": True,
                "download_pdf": True,
                "extract_text": True,
                "extract_metadata": True,
                
                # Courts specific settings
                "courts": {}
            }
        
        # Load configuration from file if provided
        if config_file:
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(config_file):
            logger.warning(f"Configuration file not found: {config_file}")
            return False
        
        try:
            # Determine file type from extension
            _, ext = os.path.splitext(config_file)
            
            if ext.lower() in ['.yaml', '.yml']:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
            elif ext.lower() == '.json':
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
            else:
                logger.error(f"Unsupported configuration file format: {ext}")
                return False
            
            # Update configuration with values from file
            if file_config:
                self._update_config_recursive(self.config, file_config)
            
            logger.info(f"Loaded configuration from {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {e}")
            return False
    
    def _update_config_recursive(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Update configuration recursively.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                # Recursively update nested dictionaries
                self._update_config_recursive(target[key], value)
            else:
                # Update or add value
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot notation for nested keys)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        # Check court-specific configuration first
        if self.court_name:
            court_config = self.config.get("courts", {}).get(self.court_name, {})
            court_value = self._get_nested_value(court_config, key)
            if court_value is not None:
                return court_value
        
        # Check global configuration
        return self._get_nested_value(self.config, key, default)
    
    def _get_nested_value(self, config: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Get a nested configuration value.
        
        Args:
            config: Configuration dictionary
            key: Configuration key (dot notation for nested keys)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        if '.' not in key:
            return config.get(key, default)
        
        parts = key.split('.')
        current = config
        
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation for nested keys)
            value: Configuration value
        """
        if '.' not in key:
            self.config[key] = value
            return
        
        parts = key.split('.')
        current = self.config
        
        # Navigate to the nested dictionary
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
    
    def set_court_config(self, court_name: str, key: str, value: Any) -> None:
        """
        Set a court-specific configuration value.
        
        Args:
            court_name: Name of the court
            key: Configuration key
            value: Configuration value
        """
        if "courts" not in self.config:
            self.config["courts"] = {}
        
        if court_name not in self.config["courts"]:
            self.config["courts"][court_name] = {}
        
        if '.' not in key:
            self.config["courts"][court_name][key] = value
            return
        
        parts = key.split('.')
        current = self.config["courts"][court_name]
        
        # Navigate to the nested dictionary
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
    
    def save_config(self, config_file: str) -> bool:
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            
            # Determine file type from extension
            _, ext = os.path.splitext(config_file)
            
            if ext.lower() in ['.yaml', '.yml']:
                with open(config_file, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif ext.lower() == '.json':
                with open(config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                logger.error(f"Unsupported configuration file format: {ext}")
                return False
            
            logger.info(f"Saved configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {config_file}: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary with all configuration values
        """
        return self.config.copy()
    
    def get_court_config(self, court_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get court-specific configuration.
        
        Args:
            court_name: Name of the court (defaults to self.court_name)
        
        Returns:
            Dictionary with court-specific configuration
        """
        if court_name is None:
            court_name = self.court_name
        
        if not court_name:
            return {}
        
        return self.config.get("courts", {}).get(court_name, {}).copy()
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
        
        Returns:
            Configuration value
        
        Raises:
            KeyError: If key not found
        """
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a configuration key exists.
        
        Args:
            key: Configuration key
        
        Returns:
            True if key exists, False otherwise
        """
        return self.get(key) is not None
