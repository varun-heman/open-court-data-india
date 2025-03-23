"""
Scraper utilities for court scrapers.

This module provides base classes and utilities for court scrapers.
"""
import os
import csv
import json
import time
import hashlib
import requests
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, TypeVar, cast
from urllib.parse import urlparse, urljoin
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import ScraperConfig
from .logger import setup_logger, get_logger_with_context
from .cache import ScraperCache, cached
from .common import ensure_directory, clean_filename, get_today_formatted, build_full_url, get_file_hash


# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

# Set up module logger
logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class RateLimitExceededError(ScraperError):
    """Exception for rate limit exceeded errors."""
    pass


class RequestError(ScraperError):
    """Exception for request errors."""
    pass


class ParsingError(ScraperError):
    """Exception for parsing errors."""
    pass


class DownloadError(ScraperError):
    """Exception for download errors."""
    pass


class ContentTypeError(ScraperError):
    """Exception for content type errors."""
    pass


class BaseScraper:
    """Base class for court scrapers."""
    
    def __init__(
        self,
        court_name: str,
        base_url: str,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize the base scraper.
        
        Args:
            court_name: Name of the court
            base_url: Base URL for the court website
            output_dir: Directory for downloaded files
            config_file: Path to configuration file
        """
        self.court_name = court_name
        self.base_url = base_url
        
        # Load configuration
        self.config = ScraperConfig(config_file, court_name)
        
        # Set up logger
        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get("log_file")
        log_to_console = self.config.get("log_to_console", True)
        log_to_file = self.config.get("log_to_file", True)
        
        setup_logger(
            level=log_level,
            log_file=log_file,
            log_to_console=log_to_console,
            log_to_file=log_to_file
        )
        
        # Get logger with context
        self.logger = get_logger_with_context(
            f"{court_name.lower().replace(' ', '_')}_scraper",
            {"court": court_name}
        )
        
        # Set up cache if enabled
        if self.config.get("cache_enabled", True):
            cache_dir = self.config.get("cache_dir", ".cache")
            cache_expiry = self.config.get("cache_expiry", 86400)
            self.cache = ScraperCache(cache_dir, cache_expiry)
        else:
            self.cache = None
        
        # Set up output directory
        if output_dir is None:
            output_dir = self.config.get("output_dir", "data")
        self.output_dir = ensure_directory(output_dir)
        
        # Create a directory for the court
        self.court_dir = ensure_directory(os.path.join(self.output_dir, clean_filename(court_name)))
        
        # Create a directory for today's date
        today = get_today_formatted()
        self.today_dir = ensure_directory(os.path.join(self.court_dir, today))
        
        # Set up session with retries
        self.session = self._create_session()
        
        # For tracking downloaded files
        self.downloaded_urls: set = set()
        self.downloaded_hashes: set = set()
        self.metadata: List[Dict[str, Any]] = []
        
        # Rate limiting
        self.rate_limit = self.config.get("rate_limit", 1)  # requests per second
        self.rate_limit_enabled = self.config.get("rate_limit_enabled", True)
        self.last_request_time = 0.0
        
        self.logger.info(f"Initialized {court_name} scraper")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Court directory: {self.court_dir}")
        self.logger.info(f"Today's directory: {self.today_dir}")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retries and timeouts.
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Configure retries
        retries = Retry(
            total=self.config.get("retries", 3),
            backoff_factor=self.config.get("backoff_factor", 0.5),
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "HEAD"]
        )
        
        # Mount adapter with retry configuration
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            "User-Agent": self.config.get("user_agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")
        })
        
        return session
    
    def _respect_rate_limit(self) -> None:
        """
        Respect rate limiting by sleeping if necessary.
        """
        if not self.rate_limit_enabled or self.rate_limit <= 0:
            return
        
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # If we've made a request recently, sleep to respect rate limit
        if elapsed < (1.0 / self.rate_limit):
            sleep_time = (1.0 / self.rate_limit) - elapsed
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    @cached(key_prefix="fetch_page")
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage and return its BeautifulSoup object.
        
        Args:
            url: URL to fetch
        
        Returns:
            BeautifulSoup object or None if the request fails
        
        Raises:
            RequestError: If the request fails
        """
        self.logger.info(f"Fetching page: {url}")
        
        try:
            # Respect rate limiting
            self._respect_rate_limit()
            
            # Send request
            response = self.session.get(
                url,
                timeout=self.config.get("timeout", 30),
                verify=self.config.get("verify_ssl", True),
                allow_redirects=self.config.get("follow_redirects", True)
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                self.logger.warning(f"Unexpected content type: {content_type}")
                raise ContentTypeError(f"Unexpected content type: {content_type}")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            self.logger.debug(f"Successfully fetched page: {url}")
            return soup
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            raise RequestError(f"Error fetching page {url}: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error fetching page {url}: {e}")
            raise RequestError(f"Unexpected error fetching page {url}: {e}")
    
    def download_file(
        self,
        url: str,
        filename: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        Download a file from a URL.
        
        Args:
            url: URL to download
            filename: Filename to save as (default: basename of URL)
            output_dir: Directory to save to (default: today's directory)
        
        Returns:
            Path to the downloaded file or None if the download fails
        
        Raises:
            DownloadError: If the download fails
        """
        if url in self.downloaded_urls:
            self.logger.debug(f"Already downloaded: {url}")
            return None
        
        self.logger.info(f"Downloading file: {url}")
        
        try:
            # Respect rate limiting
            self._respect_rate_limit()
            
            # Determine output directory
            if output_dir is None:
                output_dir = self.today_dir
            
            # Ensure output directory exists
            ensure_directory(output_dir)
            
            # Determine filename
            if filename is None:
                # Extract filename from URL
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
                # If filename is empty, use the URL hash
                if not filename:
                    filename = hashlib.md5(url.encode()).hexdigest()
            
            # Clean filename
            filename = clean_filename(filename)
            
            # Add extension if missing
            if not os.path.splitext(filename)[1]:
                # Send HEAD request to get content type
                head_response = self.session.head(
                    url,
                    timeout=self.config.get("timeout", 30),
                    verify=self.config.get("verify_ssl", True),
                    allow_redirects=self.config.get("follow_redirects", True)
                )
                
                # Determine extension from content type
                content_type = head_response.headers.get("Content-Type", "").lower()
                
                if "application/pdf" in content_type:
                    filename += ".pdf"
                elif "text/html" in content_type:
                    filename += ".html"
                elif "application/json" in content_type:
                    filename += ".json"
                elif "text/plain" in content_type:
                    filename += ".txt"
                else:
                    # Default extension
                    filename += ".bin"
            
            # Full path to save file
            filepath = os.path.join(output_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                self.logger.debug(f"File already exists: {filepath}")
                self.downloaded_urls.add(url)
                return filepath
            
            # Download file
            response = self.session.get(
                url,
                stream=True,
                timeout=self.config.get("timeout", 30),
                verify=self.config.get("verify_ssl", True),
                allow_redirects=self.config.get("follow_redirects", True)
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Calculate file hash before saving
            file_hash = hashlib.md5()
            
            # Save file
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_hash.update(chunk)
                        f.write(chunk)
            
            # Get file hash
            hash_digest = file_hash.hexdigest()
            
            # Check if we've already downloaded a file with this hash
            if hash_digest in self.downloaded_hashes:
                self.logger.debug(f"Duplicate file (same hash): {filepath}")
                os.remove(filepath)
                return None
            
            # Add to downloaded sets
            self.downloaded_urls.add(url)
            self.downloaded_hashes.add(hash_digest)
            
            # Add metadata
            metadata = {
                "url": url,
                "filename": filename,
                "filepath": filepath,
                "hash": hash_digest,
                "content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
                "last_modified": response.headers.get("Last-Modified"),
                "download_time": datetime.now().isoformat(),
            }
            self.metadata.append(metadata)
            
            self.logger.info(f"Successfully downloaded file: {filepath}")
            return filepath
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading file {url}: {e}")
            raise DownloadError(f"Error downloading file {url}: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error downloading file {url}: {e}")
            raise DownloadError(f"Unexpected error downloading file {url}: {e}")
    
    def save_metadata(self, filepath: Optional[str] = None, format: str = "json") -> str:
        """
        Save metadata to a file.
        
        Args:
            filepath: Path to save metadata file (default: metadata.<format> in today's directory)
            format: Format to save metadata (json or csv)
        
        Returns:
            Path to the saved metadata file
        """
        if not self.metadata:
            self.logger.warning("No metadata to save")
            return ""
        
        # Determine filepath
        if filepath is None:
            filepath = os.path.join(self.today_dir, f"metadata.{format.lower()}")
        
        try:
            if format.lower() == "json":
                return self._save_metadata_json(filepath)
            elif format.lower() == "csv":
                return self._save_metadata_csv(filepath)
            else:
                self.logger.error(f"Unsupported metadata format: {format}")
                raise ValueError(f"Unsupported metadata format: {format}")
        
        except Exception as e:
            self.logger.error(f"Error saving metadata to {filepath}: {e}")
            raise
    
    def _save_metadata_json(self, filepath: str) -> str:
        """
        Save metadata as JSON.
        
        Args:
            filepath: Path to save JSON file
        
        Returns:
            Path to the saved metadata file
        """
        self.logger.info(f"Saving metadata to JSON: {filepath}")
        
        try:
            with open(filepath, "w") as f:
                json.dump(self.metadata, f, indent=2)
            
            self.logger.info(f"Successfully saved metadata to {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error saving metadata to {filepath}: {e}")
            raise
    
    def _save_metadata_csv(self, filepath: str) -> str:
        """
        Save metadata as CSV.
        
        Args:
            filepath: Path to save CSV file
        
        Returns:
            Path to the saved metadata file
        """
        self.logger.info(f"Saving metadata to CSV: {filepath}")
        
        try:
            # Get all possible field names
            fieldnames = set()
            for item in self.metadata:
                fieldnames.update(item.keys())
            
            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(self.metadata)
            
            self.logger.info(f"Successfully saved metadata to {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error saving metadata to {filepath}: {e}")
            raise
    
    def close(self) -> None:
        """
        Close the scraper and clean up resources.
        """
        self.logger.info("Closing scraper")
        
        # Close session
        self.session.close()
        
        # Save metadata if any
        if self.metadata:
            try:
                self.save_metadata()
            except Exception as e:
                self.logger.error(f"Error saving metadata: {e}")
        
        self.logger.info("Scraper closed")


def get_content_type(url: str, session: Optional[requests.Session] = None) -> Optional[str]:
    """
    Check the content type of a URL without downloading the full file.
    
    Args:
        url: URL to check
        session: Requests session to use (creates a new one if None)
    
    Returns:
        Content type or None if the request fails
    
    Raises:
        RequestError: If the request fails
    """
    logger.info(f"Checking content type: {url}")
    
    # Create session if not provided
    if session is None:
        session = requests.Session()
    
    try:
        # Send HEAD request
        response = session.head(
            url,
            timeout=30,
            allow_redirects=True
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Get content type
        content_type = response.headers.get("Content-Type", "").lower()
        logger.debug(f"Content type: {content_type}")
        
        return content_type
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking content type {url}: {e}")
        raise RequestError(f"Error checking content type {url}: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error checking content type {url}: {e}")
        raise RequestError(f"Unexpected error checking content type {url}: {e}")


def download_file(
    url: str,
    output_dir: str,
    filename: Optional[str] = None,
    session: Optional[requests.Session] = None
) -> str:
    """
    Download a file from a URL.
    
    Args:
        url: URL to download
        output_dir: Directory to save to
        filename: Filename to save as (default: basename of URL)
        session: Requests session to use (creates a new one if None)
    
    Returns:
        Path to the downloaded file
    
    Raises:
        DownloadError: If the download fails
    """
    logger.info(f"Downloading file: {url}")
    
    # Create session if not provided
    if session is None:
        session = requests.Session()
    
    try:
        # Ensure output directory exists
        ensure_directory(output_dir)
        
        # Determine filename
        if filename is None:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # If filename is empty, use the URL hash
            if not filename:
                filename = hashlib.md5(url.encode()).hexdigest()
        
        # Clean filename
        filename = clean_filename(filename)
        
        # Full path to save file
        filepath = os.path.join(output_dir, filename)
        
        # Download file
        response = session.get(
            url,
            stream=True,
            timeout=30,
            allow_redirects=True
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Save file
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Successfully downloaded file: {filepath}")
        return filepath
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file {url}: {e}")
        raise DownloadError(f"Error downloading file {url}: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error downloading file {url}: {e}")
        raise DownloadError(f"Unexpected error downloading file {url}: {e}")


def save_metadata_csv(metadata: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save metadata as CSV.
    
    Args:
        metadata: List of metadata dictionaries
        filepath: Path to save CSV file
    """
    logger.info(f"Saving metadata to CSV: {filepath}")
    
    try:
        # Get all possible field names
        fieldnames = set()
        for item in metadata:
            fieldnames.update(item.keys())
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(metadata)
        
        logger.info(f"Successfully saved metadata to {filepath}")
    
    except Exception as e:
        logger.error(f"Error saving metadata to {filepath}: {e}")
        raise


def save_metadata_json(metadata: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save metadata as JSON.
    
    Args:
        metadata: List of metadata dictionaries
        filepath: Path to save JSON file
    """
    logger.info(f"Saving metadata to JSON: {filepath}")
    
    try:
        with open(filepath, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Successfully saved metadata to {filepath}")
    
    except Exception as e:
        logger.error(f"Error saving metadata to {filepath}: {e}")
        raise
