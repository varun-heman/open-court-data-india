"""
Utilities for court scrapers.

This package provides utility functions and classes for court scrapers.
"""

# Import common utilities
from .common import (
    ensure_directory,
    clean_filename,
    get_today_formatted,
    build_full_url,
    get_file_hash,
    get_appropriate_extension,
    extract_date_from_text,
    save_json,
    load_json
)

# Import PDF utilities
from .pdf_utils import (
    extract_text_from_pdf,
    extract_date_from_pdf,
    extract_court_info_from_pdf,
    extract_cases_from_pdf,
    parse_pdf_for_structured_data
)

# Import HTML utilities
from .html_utils import (
    extract_text_from_html,
    extract_date_from_html,
    extract_links_from_html,
    is_navigation_page,
    extract_pdf_links_from_html,
    extract_table_data_from_html,
    is_cause_list_page
)

# Import scraper utilities
from .scraper_utils import (
    BaseScraper,
    ScraperError,
    RateLimitExceededError,
    DownloadError,
    ParsingError,
    ContentTypeError,
    get_content_type
)

# Import configuration utilities
from .config import ScraperConfig

# Import logging utilities
from .logger import (
    setup_logger,
    get_logger,
    get_logger_with_context,
    LoggerAdapter
)

# Import caching utilities
from .cache import (
    ScraperCache,
    cached
)

__all__ = [
    # Common utilities
    'ensure_directory',
    'clean_filename',
    'get_today_formatted',
    'build_full_url',
    'get_file_hash',
    'get_appropriate_extension',
    'extract_date_from_text',
    'save_json',
    'load_json',
    
    # PDF utilities
    'extract_text_from_pdf',
    'extract_date_from_pdf',
    'extract_court_info_from_pdf',
    'extract_cases_from_pdf',
    'parse_pdf_for_structured_data',
    
    # HTML utilities
    'extract_text_from_html',
    'extract_date_from_html',
    'extract_links_from_html',
    'is_navigation_page',
    'extract_pdf_links_from_html',
    'extract_table_data_from_html',
    'is_cause_list_page',
    
    # Scraper utilities
    'BaseScraper',
    'ScraperError',
    'RateLimitExceededError',
    'DownloadError',
    'ParsingError',
    'ContentTypeError',
    'get_content_type',
    
    # Configuration utilities
    'ScraperConfig',
    
    # Logging utilities
    'setup_logger',
    'get_logger',
    'get_logger_with_context',
    'LoggerAdapter',
    
    # Caching utilities
    'ScraperCache',
    'cached'
]
