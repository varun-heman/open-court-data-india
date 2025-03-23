"""
Utilities for court scrapers.

This package provides utility functions and classes for court scrapers.
"""

# Import scraper utilities
from .scraper_utils import (
    BaseScraper,
    ScraperError,
    RequestError,
    DownloadError,
    ParsingError,
    ContentTypeError,
    get_content_type,
    download_file,
    save_metadata_json,
    save_metadata_csv
)

# Import PDF utilities
from .pdf_utils import (
    extract_text_from_pdf,
    extract_date_from_pdf,
    extract_court_info_from_pdf,
    extract_cases_from_pdf,
    parse_pdf_for_structured_data
)

# Import common utilities
from .common import (
    ensure_directory,
    clean_filename,
    extract_date_from_text,
    build_full_url
)

# Import gemini utilities
from .gemini_utils import (
    setup_gemini_api,
    parse_pdf_with_gemini,
    save_markdown_output
)

__all__ = [
    # Scraper utilities
    'BaseScraper',
    'ScraperError',
    'RequestError',
    'DownloadError',
    'ParsingError',
    'ContentTypeError',
    'get_content_type',
    'download_file',
    'save_metadata_json',
    'save_metadata_csv',
    
    # PDF utilities
    'extract_text_from_pdf',
    'extract_date_from_pdf',
    'extract_court_info_from_pdf',
    'extract_cases_from_pdf',
    'parse_pdf_for_structured_data',
    
    # Common utilities
    'ensure_directory',
    'clean_filename',
    'extract_date_from_text',
    'build_full_url',
    
    # Gemini utilities
    'setup_gemini_api',
    'parse_pdf_with_gemini',
    'save_markdown_output'
]
