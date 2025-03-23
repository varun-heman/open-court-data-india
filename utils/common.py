"""
Common utilities for court scrapers.

This module provides general utility functions for court scrapers.
"""
import os
import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from urllib.parse import urljoin, urlparse
from dateutil.parser import parse


def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists.
    
    Args:
        directory: Directory path
    
    Returns:
        Absolute path to the directory
    
    Raises:
        OSError: If directory creation fails
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return os.path.abspath(directory)
    except OSError as e:
        raise OSError(f"Failed to create directory {directory}: {e}")


def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Cleaned filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip().strip('.')
    
    # Limit length to 255 characters
    if len(filename) > 255:
        base, ext = os.path.splitext(filename)
        filename = base[:255 - len(ext)] + ext
    
    return filename


def get_today_formatted() -> str:
    """
    Get today's date formatted as YYYY-MM-DD.
    
    Returns:
        Formatted date string
    """
    return datetime.now().strftime("%Y-%m-%d")


def build_full_url(base_url: str, url: str) -> str:
    """
    Build a full URL from a base URL and a relative URL.
    
    Args:
        base_url: Base URL
        url: Relative or absolute URL
    
    Returns:
        Full URL
    """
    if url.startswith(('http://', 'https://')):
        return url
    
    # Handle both absolute paths and relative paths
    if url.startswith('/'):
        # Get the scheme and netloc from the base URL
        parsed_base = urlparse(base_url)
        base = f"{parsed_base.scheme}://{parsed_base.netloc}"
        return base + url
    else:
        # Relative path, join with base URL
        return urljoin(base_url, url)


def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File hash
    
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there is an error reading the file
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")


def get_appropriate_extension(content_type: str, url: str) -> str:
    """
    Determine the appropriate file extension based on content type and URL.
    
    Args:
        content_type: Content type from HTTP headers
        url: URL of the file
    
    Returns:
        File extension with leading dot
    """
    content_type = content_type.lower()
    
    # Common content types
    content_type_map = {
        'application/pdf': '.pdf',
        'text/html': '.html',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'text/plain': '.txt',
        'application/json': '.json',
        'application/xml': '.xml',
        'text/xml': '.xml'
    }
    
    # Check if content type is in the map
    for ct, ext in content_type_map.items():
        if ct in content_type:
            return ext
    
    # Try to get extension from URL
    url_ext = os.path.splitext(urlparse(url).path)[1].lower()
    if url_ext and len(url_ext) <= 5:  # Reasonable extension length
        return url_ext
    
    # Default to binary data if we can't determine
    return '.bin'


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Extract date from text.
    
    Args:
        text: Text to extract date from
    
    Returns:
        Extracted date in YYYY-MM-DD format or None if no date found
    """
    # Common date patterns
    date_patterns = [
        r'(\d{1,2})[.\s-/](\d{1,2})[.\s-/](20\d{2})',  # DD.MM.YYYY or DD-MM-YYYY
        r'(20\d{2})[.\s-/](\d{1,2})[.\s-/](\d{1,2})',  # YYYY.MM.DD or YYYY-MM-DD
        r'(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([A-Za-z]+)[,\s]+?(20\d{2})'  # 5th January, 2023
    ]
    
    for pattern in date_patterns:
        matches = re.search(pattern, text)
        if matches:
            try:
                date_str = matches.group(0)
                date = parse(date_str, fuzzy=True)
                return date.strftime('%Y-%m-%d')
            except:
                continue
    
    # If no pattern matched, try fuzzy parsing on the first 1000 chars
    try:
        date = parse(text[:1000], fuzzy=True)
        return date.strftime('%Y-%m-%d')
    except:
        return None


def save_json(data: Union[Dict[str, Any], List[Dict[str, Any]]], filepath: str) -> str:
    """
    Save data as JSON.
    
    Args:
        data: Data to save
        filepath: Path to save JSON file
    
    Returns:
        Path to saved JSON file
    
    Raises:
        IOError: If there is an error writing the file
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return filepath
    except IOError as e:
        raise IOError(f"Error writing JSON to {filepath}: {e}")


def load_json(filepath: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Load data from JSON.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Loaded data
    
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {filepath}: {e.msg}", e.doc, e.pos)
